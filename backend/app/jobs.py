"""A Job is one assistant turn. It accumulates assistant-ui message parts and can be replayed to late subscribers."""

import json, threading, time
from . import db


class Job:
    def __init__(self, tid, mid):
        self.tid, self.mid = tid, mid
        self.parts = []
        self.events = []
        self.done = False
        self.cond = threading.Condition()
        self._ids = 0
        self._last_save = 0

    # --- part helpers ---
    def _push(self, ev):
        with self.cond:
            self.events.append(ev)
            self.cond.notify_all()
        if time.time() - self._last_save > 2 or ev["t"] in ("done", "error"):
            self.save()

    def save(self):
        self._last_save = time.time()
        db.add_message(self.tid, "assistant", self.parts, self.mid)

    def snapshot(self):
        self._push({"t": "parts", "parts": json.loads(json.dumps(self.parts))})

    def text(self, s):
        if self.parts and self.parts[-1]["type"] == "text":
            self.parts[-1]["text"] += s
        else:
            self.parts.append({"type": "text", "text": s})
        self.snapshot()

    def tool_start(self, name, args):
        self._ids += 1
        tcid = f"{self.mid}-{self._ids}"
        self.parts.append(
            {
                "type": "tool-call",
                "toolCallId": tcid,
                "toolName": name,
                "args": args,
                "argsText": json.dumps(args),
            }
        )
        self.snapshot()
        return tcid

    def tool_done(self, tcid, result, error=False):
        for p in self.parts:
            if p.get("toolCallId") == tcid:
                p["result"] = result
                p["isError"] = error
        self.snapshot()

    def finish(self, error=None):
        if error:
            self.text(("\n\n" if self.parts else "") + f"**Stopped:** {error}")
        self.save()
        with self.cond:
            self.done = True
            self.events.append({"t": "done"})
            self.cond.notify_all()

    def stream(self):
        i = 0
        while True:
            with self.cond:
                while i >= len(self.events) and not self.done:
                    self.cond.wait(timeout=15)
                if i >= len(self.events):
                    return
                batch = self.events[i:]
                i = len(self.events)
            # only the newest snapshot matters; always forward control events
            last_parts = None
            for ev in batch:
                if ev["t"] == "parts":
                    last_parts = ev
                else:
                    if last_parts:
                        yield last_parts
                        last_parts = None
                    yield ev
            if last_parts:
                yield last_parts
            if batch and batch[-1]["t"] == "done":
                return


RUNNING = {}  # thread_id -> Job
