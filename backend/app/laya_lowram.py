"""Optional low-RAM loader for Laya (PAPERFORGE_LAYA_LOW_RAM=1): streams the safetensors weights in bf16 so the
421M English checkpoint loads in about 1.5 GB RAM (the default loader needs more and is OOM-killed on a 2 GB machine).
Applied before laya.load(); has no effect unless enabled."""
import ctypes, json, os, struct


def apply():
    os.environ.setdefault("LAYA_CPU_AMP", "bf16")
    import numpy as np
    import torch
    try:
        libc = ctypes.CDLL("libc.so.6")
    except OSError:
        libc = None

    def _trim():
        if libc is not None:
            libc.malloc_trim(0)

    torch.set_default_dtype(torch.bfloat16)
    from safetensors import safe_open
    import safetensors.torch as _st
    # --- streaming safetensors reader: plain file reads, one tensor at a time ---
    from safetensors import safe_open
    import safetensors.torch as _st

    class StreamWeights(dict):
        def __init__(self, path):
            self._fh = open(path, "rb")
            try:
                os.posix_fadvise(self._fh.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)
            except (AttributeError, OSError) as e:
                print("fadvise init failed:", e, flush=True)
            hlen = struct.unpack("<Q", self._fh.read(8))[0]
            header = json.loads(self._fh.read(hlen))
            self._base = 8 + hlen
            self._meta = {k: v for k, v in header.items() if k != "__metadata__"}
        def keys(self): return list(self._meta.keys())
        def __contains__(self, k): return k in self._meta
        def __getitem__(self, k): return self.get_tensor(k)
        def __iter__(self): return iter(self._meta)
        def __len__(self): return len(self._meta)
        def get_tensor(self, k):
            m = self._meta[k]
            s, e = m["data_offsets"]
            self._fh.seek(self._base + s)
            raw = self._fh.read(e - s)
            try:
                os.posix_fadvise(self._fh.fileno(), self._base + s, e - s, os.POSIX_FADV_DONTNEED)
            except (AttributeError, OSError):
                pass
            dt, shape = m["dtype"], m["shape"]
            if dt == "BF16":
                u16 = np.frombuffer(raw, dtype=np.uint16)
                return torch.from_numpy(u16).view(torch.bfloat16).clone().reshape(shape)
            if dt == "F32":
                return torch.from_numpy(np.frombuffer(raw, dtype=np.float32).copy()).to(torch.bfloat16).reshape(shape)
            if dt == "F16":
                return torch.from_numpy(np.frombuffer(raw, dtype=np.float16).copy()).to(torch.bfloat16).reshape(shape)
            raise ValueError(f"unsupported dtype {dt}")

    def _stream_load_file(path, device="cpu"):
        return StreamWeights(path)
    _st.load_file = _stream_load_file

    _orig_lsd = torch.nn.Module.load_state_dict
    def _streaming_lsd(self, state_dict, strict=True):
        if isinstance(state_dict, StreamWeights):
            pass
            file_keys = set(state_dict.keys()); model_keys = set(self.state_dict().keys())
            missing = sorted(model_keys - file_keys); unexpected = sorted(file_keys - model_keys)
            if strict and (missing or unexpected):
                raise RuntimeError(f"missing={missing[:5]} unexpected={unexpected[:5]}")
            with torch.no_grad():
                sd = self.state_dict()
                keys = sorted(model_keys & file_keys)
                for i, k in enumerate(keys):
                    t = state_dict.get_tensor(k); p = sd[k]
                    if p.shape != t.shape:
                        raise RuntimeError(f"shape mismatch {k}: {tuple(p.shape)} vs {tuple(t.shape)}")
                    p.copy_(t.to(p.dtype)); del t
                    _trim()
            pass
            return torch.nn.modules.module._IncompatibleKeys([], [])
        return _orig_lsd(self, state_dict, strict)
    torch.nn.Module.load_state_dict = _streaming_lsd

    # force bf16 model construction (encoder config pins fp32, which OOMs this 2GB sandbox)
    from transformers import AutoModel
    _orig_from_config = AutoModel.from_config
    def _bf16_from_config(config, **kwargs):
        kwargs["dtype"] = torch.bfloat16
        return _orig_from_config(config, **kwargs)
    AutoModel.from_config = _bf16_from_config

