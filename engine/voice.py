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


BLENDS = {"blend": [("am_michael", 0.6), ("am_fenrir", 0.4)]}


def resolve_voice(voice):
    if voice in BLENDS:
        k = kokoro()
        return sum(w * k.get_voice_style(v) for v, w in BLENDS[voice])
    return voice


CACHE_DIR = os.environ.get("TTS_CACHE", os.path.expanduser("~/.cache/tts-cache"))


def tts(text, voice="blend", speed=1.0):
    import hashlib
    key = hashlib.sha1(f"{voice}|{speed:.4f}|{text}".encode()).hexdigest()
    cp = os.path.join(CACHE_DIR, key + ".npy")
    if os.path.exists(cp):
        return np.load(cp)
    a, sr = kokoro().create(text, voice=resolve_voice(voice), speed=speed, lang="en-us")
    assert sr == SR
    out = trim(np.asarray(a, dtype=np.float32))
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        np.save(cp, out)
    except OSError:
        pass
    return out


def scene_audio(sentences, voice="blend", speed=1.0, lead=0.2, gap=0.12, pad=0.55, min_dur=0.0):
    full = tts(" ".join(s.strip() for s in sentences), voice, speed)
    if len(sentences) == 1:
        lens = [len(full) / SR]
    else:
        lens = [len(tts(s, voice, speed)) / SR for s in sentences]
    total = len(full) / SR
    scale = total / (sum(lens) or 1)
    starts, ends = [], []
    cur = lead
    for ln in lens:
        starts.append(cur)
        cur += ln * scale
        ends.append(cur)
    dur = max(lead + total + pad, min_dur)
    out = np.zeros(int(round(dur * SR)), dtype=np.float32)
    i = int(lead * SR)
    out[i:i + len(full)] += full[: len(out) - i]
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
