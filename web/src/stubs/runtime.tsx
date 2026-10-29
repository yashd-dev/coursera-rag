"use client";
import { useEffect, useState, useMemo, type ReactNode } from "react";
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  useRemoteThreadListRuntime,
  useAui,
  RuntimeAdapterProvider,
  type ChatModelAdapter,
  type ThreadHistoryAdapter,
} from "@assistant-ui/react";
import { createAssistantStream } from "assistant-stream";

export const templateRef = { current: "ieee" };
function syncTemplate(value: string) {
  templateRef.current = value;
  window.dispatchEvent(
    new CustomEvent("paperforge-template", { detail: value }),
  );
}
const j = async (u: string, init?: RequestInit) => {
  const r = await fetch(u, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};

function makeAdapter(
  getId: () => Promise<string | undefined>,
): ChatModelAdapter {
  return {
    async *run({ messages, abortSignal, unstable_getMessage }) {
      const last = [...messages].reverse().find((m) => m.role === "user");
      const text = (last?.content ?? [])
        .map((p: any) => (p.type === "text" ? p.text : ""))
        .join("");
      let id = await getId();
      if (!id) throw new Error("No thread id");
      const res = await fetch(`/api/threads/${id}/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text, template: templateRef.current }),
        signal: abortSignal,
      });
      if (!res.ok || !res.body)
        throw new Error((await res.text()) || "Request failed");
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, i);
          buf = buf.slice(i + 2);
          if (!chunk.startsWith("data: ")) continue;
          const ev = JSON.parse(chunk.slice(6));
          if (ev.t === "parts") yield { content: ev.parts };
        }
      }
      window.dispatchEvent(new Event("paperforge-job-ended"));
      const updated = await j(`/api/threads/${id}`);
      syncTemplate(updated.template);
    },
  };
}

export function DocsRuntimeProvider({
  children,
}: {
  children: ReactNode;
  [k: string]: any;
}) {
  const runtime = useRemoteThreadListRuntime({
    runtimeHook: function useHook() {
      const aui = useAui();
      const adapter = useMemo(
        () =>
          makeAdapter(async () => {
            const item = aui.threadListItem();
            const initialized = await item.initialize();
            return initialized.remoteId;
          }),
        [aui],
      );
      const history = useMemo<ThreadHistoryAdapter>(
        () => ({
          async load() {
            const id = (aui.threadListItem().getState() as any).remoteId;
            if (!id) return { messages: [] } as any;
            const current = await j(`/api/threads/${id}`);
            syncTemplate(current.template);
            const { messages } = await j(`/api/threads/${id}/messages`);
            return {
              messages: messages.map((m: any, k: number) => ({
                parentId: k ? messages[k - 1].id : null,
                message: {
                  id: m.id,
                  role: m.role,
                  content: m.content,
                  createdAt: new Date(m.created * 1000),
                  status:
                    m.role === "assistant"
                      ? { type: "complete", reason: "stop" }
                      : undefined,
                  metadata: { custom: {} },
                  attachments: [],
                },
              })),
            } as any;
          },
          async append() {},
        }),
        [aui],
      );
      return useLocalRuntime(adapter, { adapters: { history } });
    },
    adapter: {
      async list() {
        const { threads } = await j("/api/threads");
        return {
          threads: threads.map((t: any) => ({
            remoteId: t.id,
            externalId: undefined,
            status: t.status === "archived" ? "archived" : "regular",
            title: t.title || undefined,
            custom: t.custom,
          })),
        };
      },
      async initialize() {
        const t = await j("/api/threads", {
          method: "POST",
          body: JSON.stringify({ template: templateRef.current }),
        });
        return { remoteId: t.id, externalId: undefined };
      },
      async rename(id: string, title: string) {
        await j(`/api/threads/${id}`, {
          method: "PATCH",
          body: JSON.stringify({ title }),
        });
      },
      async archive(id: string) {
        await j(`/api/threads/${id}`, {
          method: "PATCH",
          body: JSON.stringify({ status: "archived" }),
        });
      },
      async unarchive(id: string) {
        await j(`/api/threads/${id}`, {
          method: "PATCH",
          body: JSON.stringify({ status: "regular" }),
        });
      },
      async delete(id: string) {
        await j(`/api/threads/${id}`, { method: "DELETE" });
      },
      async updateCustom(id: string, custom: any) {
        await j(`/api/threads/${id}`, {
          method: "PATCH",
          body: JSON.stringify({ custom }),
        });
      },
      async generateTitle(_id: string, msgs: any) {
        return createAssistantStream(async (c) => {
          const t =
            JSON.stringify(msgs).match(/"text":"([^"]{1,60})/)?.[1] ??
            "New paper";
          c.appendText(t);
        });
      },
      async fetch(id: string) {
        const t = await j(`/api/threads/${id}`).catch(() => null);
        return t
          ? {
              remoteId: t.id,
              status: t.status === "archived" ? "archived" : "regular",
              title: t.title,
              custom: t.custom,
            }
          : undefined;
      },
    } as any,
  });
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <ExecutionStatus />
      {children}
    </AssistantRuntimeProvider>
  );
}

function ExecutionStatus() {
  const aui = useAui();
  const [status, setStatus] = useState<any>(null);
  useEffect(() => {
    let cancelled = false;
    let version = 0;
    const check = async () => {
      const requestVersion = ++version;
      try {
        const id = (aui.threadListItem().getState() as any).remoteId;
        if (!id) {
          if (!cancelled) {
            setStatus(null);
            window.dispatchEvent(
              new CustomEvent("paperforge-execution", { detail: false }),
            );
          }
          return;
        }
        const next = await j(`/api/threads/${id}/messages`);
        if (!cancelled && requestVersion === version) {
          setStatus(next);
          window.dispatchEvent(
            new CustomEvent("paperforge-execution", { detail: next.running }),
          );
        }
      } catch {
        if (!cancelled && requestVersion === version) {
          setStatus({ execution_state: "unavailable" });
          window.dispatchEvent(
            new CustomEvent("paperforge-execution", { detail: true }),
          );
        }
      }
    };
    window.addEventListener("paperforge-job-ended", check);
    check();
    const timer = setInterval(check, 2000);
    return () => {
      cancelled = true;
      clearInterval(timer);
      window.removeEventListener("paperforge-job-ended", check);
    };
  }, [aui]);
  if (!status || status.execution_state === "idle") return null;
  return (
    <div
      role="status"
      className="mb-2 rounded border border-white/10 px-3 py-2 text-sm text-muted-foreground"
    >
      {status.execution_state === "running"
        ? "Work is still running in the local server. Reloading this page does not stop it. Live output may need a refresh after it finishes."
        : status.execution_state === "paused"
          ? "Work is paused or the server process ended. Check the last result before retrying. Restarted processes do not resume automatically."
          : status.execution_state === "unavailable"
            ? "Cannot check the local server. No restart recovery is assumed."
            : "The local server has finished this job. Refresh to load any output completed while disconnected."}
    </div>
  );
}
