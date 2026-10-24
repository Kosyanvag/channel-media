import os, subprocess
import numpy as np

SR = 24000
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))
BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = {"kokoro-v1.0.onnx": 300_000_000, "voices-v1.0.bin": 25_000_000}
_k = None


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name, min_size in FILES.items():
        p = os.path.join(MODEL_DIR, name)
        if not os.path.exists(p) or os.path.getsize(p) < min_size:
            subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "900", "-o", p, BASE + name], check=True)
    return os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin")


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        m, v = ensure_model()
        _k = Kokoro(m, v)
    return _k


def trim(a, thr=0.012, keep=0.04):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(keep * SR))
    e = min(len(a), idx[-1] + int(keep * SR))
    return a[s:e]


def tts(text, voice="am_michael", speed=1.0):
    a, sr = kokoro().create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR
    return trim(np.asarray(a, dtype=np.float32))


def scene_audio(sentences, voice="am_michael", speed=1.0, lead=0.45, gap=0.32, pad=1.2, min_dur=0.0):
    parts, starts, ends = [], [], []
    cur = lead
    for s in sentences:
        a = tts(s, voice, speed)
        starts.append(cur)
        cur += len(a) / SR
        ends.append(cur)
        parts.append(a)
        cur += gap
    dur = max(cur - gap + pad, min_dur)
    out = np.zeros(int(round(dur * SR)), dtype=np.float32)
    for a, st in zip(parts, starts):
        i = int(st * SR)
        out[i:i + len(a)] += a[: len(out) - i]
    return out, starts, ends, dur


def music_bed(dur, seed=3):
    t = np.arange(int(dur * SR)) / SR
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 196.0, 261.63], [196.0, 246.94, 293.66]]
    seg = 4.0
    out = np.zeros_like(t)
    for i, ch in enumerate(chords * int(dur // (seg * 4) + 2)):
        a, b = i * seg, i * seg + seg + 1.0
        if a > dur:
            break
        m = (t >= a) & (t < b)
        tt = t[m] - a
        env = np.clip(tt / 1.2, 0, 1) * np.clip((b - a - tt) / 1.2, 0, 1)
        for fq in ch:
            out[m] += env * (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(2 * np.pi * fq * 2 * tt) + 0.5 * np.sin(2 * np.pi * fq / 2 * tt))
    lfo = 0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t)
    out *= lfo
    k = 64
    out = np.convolve(out, np.ones(k) / k, mode="same")
    out /= (np.max(np.abs(out)) or 1)
    fade = np.clip(t / 2.0, 0, 1) * np.clip((dur - t) / 2.5, 0, 1)
    return (out * fade).astype(np.float32)
