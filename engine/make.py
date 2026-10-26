import argparse, json, os, re, subprocess, sys, math
from multiprocessing import Pool
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import core as C
from engine import elements as E
from engine import voice as V

SPEC = None
SCENES = None
OUT = None
CAPTIONS = None
CAMERA = 0.045


def canvas(fmt):
    if fmt == "short":
        C.setup(1080, 1920)
    else:
        C.setup(1920, 1080)


def build_audio(spec, speed):
    scenes = []
    voice = spec.get("voice", "blend")
    for i, sc in enumerate(spec["scenes"]):
        sents = sc["narration"]
        if isinstance(sents, str):
            sents = [sents]
        pad = sc.get("pad", 0.55)
        a, st, en, dur = V.scene_audio(sents, voice, speed * sc.get("speed", 1.0), pad=pad, min_dur=sc.get("min_dur", 0))
        dur += sc.get("hold", 0)
        if len(a) < int(dur * V.SR):
            a = np.concatenate([a, np.zeros(int(dur * V.SR) - len(a), dtype=np.float32)])
        scenes.append({"audio": a, "starts": st, "ends": en, "dur": dur, "elements": sc["elements"], "name": sc.get("name", f"scene{i+1}"), "sentences": sents})
    return scenes


def scene_frame(idx, t):
    sc = SCENES[idx]
    X = E.Ctx(sc["starts"], sc["ends"], sc["dur"])
    f = E.draw_scene(sc["elements"], t, X)
    if CAPTIONS is not None:
        E.draw_captions(f, sc, t, CAPTIONS)
    fade = max(1 - C.prog(t, 0, 0.18), C.prog(t, sc["dur"] - 0.25, sc["dur"]))
    return f.finish(fade)


REF_RE = re.compile(r"^(s\d+e?|end|start)([+-]\d+(\.\d+)?)?$")
TIME_KEYS = {"in", "out", "at", "done", "press", "click", "shake", "shatter", "reform", "hide", "open", "check", "warn", "turn_from", "turn_to"}


def dynamic_windows(sc):
    X = E.Ctx(sc["starts"], sc["ends"], sc["dur"])
    win = [(0, 0.6), (sc["dur"] - 0.8, sc["dur"] + 1)]

    def add(ref, before=1.5, after=3.0):
        try:
            t = X.T(ref)
        except Exception:
            return
        win.append((t - before, t + after))

    def walk(v, key=None):
        if isinstance(v, dict):
            if v.get("type") == "phone_grid":
                win.append((X.T(v.get("in", 0)) - 1, X.T(v.get("out", "end")) + 1))
            if v.get("type") == "receipt" and v.get("edit"):
                win.append((X.T(v["edit"][0]) - 1, X.T(v["edit"][1]) + 1))
            if v.get("type") == "arrow":
                tr = v.get("traveler")
                du = tr.get("dur", 1.6) if isinstance(tr, dict) else 1.6
                add(v.get("in", 0), 1.0, v.get("draw", 1.0) + du + 2.5)
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            if v and isinstance(v[0], list):
                for item in v:
                    if item:
                        add(item[0])
            for x in v:
                walk(x, key)
        elif isinstance(v, str) and REF_RE.match(v.replace(" ", "")):
            add(v)
        elif isinstance(v, (int, float)) and not isinstance(v, bool) and key in TIME_KEYS:
            add(v)

    walk(sc["elements"])
    win.sort()
    merged = []
    for a, b in win:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def camera(img, idx, t):
    if not CAMERA:
        return img
    sc = SCENES[idx]
    k = t / max(sc["dur"], 0.1)
    z = 1.0 + CAMERA * (k if idx % 2 == 0 else 1 - k)
    d = 1 if (idx // 2) % 2 == 0 else -1
    w, h = C.W / z, C.H / z
    cx = C.W / 2 + d * (C.W - w) / 2 * 0.6 * (k - 0.5) * 2
    cx = min(max(cx, w / 2), C.W - w / 2)
    cy = C.H / 2
    return img.resize((C.W, C.H), Image.BILINEAR, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


def render_scene(idx):
    sc = SCENES[idx]
    out = os.path.join(OUT, f"scene{idx+1:02d}.mp4")
    n = int(round(sc["dur"] * C.FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{C.W}x{C.H}", "-r", str(C.FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    wins = [(0, sc["dur"] + 1)] if CAPTIONS is not None else dynamic_windows(sc)
    base, last_static = None, False
    for i in range(n):
        t = i / C.FPS
        static = not any(a <= t <= b for a, b in wins)
        if not (static and last_static and base is not None):
            base = scene_frame(idx, t)
        last_static = static
        p.stdin.write(camera(base, idx, t).tobytes())
    p.stdin.close()
    p.wait()
    print(f"rendered {sc['name']} ({sc['dur']:.1f}s)", flush=True)
    return out


def preview(sheet_cols=None):
    paths = []
    for idx, sc in enumerate(SCENES):
        X = E.Ctx(sc["starts"], sc["ends"], sc["dur"])
        ts = set()
        for e in sc["elements"]:
            for key in ("in", "at"):
                if key in e:
                    ts.add(round(X.T(e[key]) + 0.9, 2))
        for st in sc["starts"]:
            ts.add(round(st + 0.9, 2))
        ts.add(round(sc["dur"] - 0.8, 2))
        ts = sorted(x for x in ts if 0 < x < sc["dur"])
        cap = 12
        if len(ts) > cap:
            step = len(ts) / cap
            ts = [ts[int(i * step)] for i in range(cap)]
        cols = sheet_cols or (2 if C.W > C.H else 4)
        tw = 960 if C.W > C.H else 360
        th = int(tw * C.H / C.W)
        rows = math.ceil(len(ts) / cols)
        sheet = Image.new("RGB", (cols * tw, rows * (th + 40)), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for i, t in enumerate(ts):
            im = scene_frame(idx, t).resize((tw, th))
            x, y = (i % cols) * tw, (i // cols) * (th + 40)
            sheet.paste(im, (x, y + 40))
            d.text((x + 10, y + 8), f"{sc['name']}  t={t:.1f}s", fill=(255, 255, 0), font=C.font(C.BOLD, 22))
        p = os.path.join(OUT, f"preview_{idx+1:02d}.png")
        sheet.save(p)
        paths.append(p)
    return paths


def thumbnail(spec):
    th = spec.get("thumbnail")
    if not th or C.W < C.H:
        return None
    idx = th.get("scene", 0)
    sc = SCENES[idx]
    X = E.Ctx(sc["starts"], sc["ends"], sc["dur"])
    t = X.T(th.get("at", "s1+1"))
    f = E.draw_scene(sc["elements"], t, X)
    src = f.finish(0)
    img = C.BG.copy()
    shift = th.get("shift", 300)
    if shift > 0:
        img.paste(src.crop((shift, 0, C.W, C.H)), (0, 0))
    else:
        img = src
    img = Image.blend(img, Image.new("RGB", (C.W, C.H), (0, 0, 0)), th.get("darken", 0.3))
    g = C.F()
    g.img = img
    g.d = ImageDraw.Draw(img, "RGBA")
    x = th.get("x", 1400)
    for ln in th.get("lines", []):
        col = X.col(ln.get("color", "white"), 0)
        glow = X.col(ln["glow"], 0) if ln.get("glow") else None
        fn = C.fit_font(C.BLACK, ln.get("size", 180), ln["text"], th.get("maxw", 900))
        C.text(g, (x, ln["y"]), ln["text"], fn, col, 1, glow=glow, go=1)
    p = os.path.join(OUT, "thumb.jpg")
    g.finish().save(p, quality=92)
    return p


def main():
    global SPEC, SCENES, OUT, CAPTIONS, CAMERA
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", default=None)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--speed", type=float, default=1.0)
    args = ap.parse_args()
    SPEC = json.load(open(args.spec))
    fmt = SPEC.get("format", "long")
    canvas(fmt)
    cam = SPEC.get("camera", True)
    CAMERA = 0.045 if cam is True else (float(cam) if cam else 0.0)
    cap = SPEC.get("captions", fmt == "short")
    if cap:
        CAPTIONS = cap if isinstance(cap, dict) else {}
    OUT = args.out or os.path.join("build", SPEC["id"])
    os.makedirs(OUT, exist_ok=True)
    speed = args.speed * SPEC.get("speed", 1.1)
    SCENES = build_audio(SPEC, speed)
    total = sum(s["dur"] for s in SCENES)
    if fmt == "short" and total > 58.5:
        speed *= min(1.2, total / 57.5)
        SCENES = build_audio(SPEC, speed)
        total = sum(s["dur"] for s in SCENES)
        if total > 59.5:
            sys.exit(f"ERROR: short is {total:.1f}s even at speed {speed:.2f}; cut narration")
    timings = [{"name": s["name"], "dur": round(s["dur"], 2), "sentences": [[round(a, 2), round(b, 2)] for a, b in zip(s["starts"], s["ends"])]} for s in SCENES]
    json.dump({"total": round(total, 2), "speed": speed, "scenes": timings}, open(os.path.join(OUT, "timings.json"), "w"), indent=1)
    print(f"total {total:.1f}s, {len(SCENES)} scenes", flush=True)
    if args.preview:
        for p in preview():
            print("preview", p)
        t = thumbnail(SPEC)
        if t:
            print("thumb", t)
        return
    with Pool(2) as pool:
        parts = pool.map(render_scene, range(len(SCENES)))
    lst = os.path.join(OUT, "list.txt")
    with open(lst, "w") as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    vid = os.path.join(OUT, "video_noaudio.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    voice = np.concatenate([s["audio"] for s in SCENES])
    voice = voice / (np.max(np.abs(voice)) or 1) * 0.89
    if SPEC.get("music", True):
        mb = V.music_bed(len(voice) / V.SR + 0.1)[: len(voice)]
        if len(mb) < len(voice):
            mb = np.concatenate([mb, np.zeros(len(voice) - len(mb), dtype=np.float32)])
        voice = voice + mb * SPEC.get("music_level", 0.07)
        voice = np.clip(voice, -0.98, 0.98)
    wav = os.path.join(OUT, "audio.wav")
    sf.write(wav, voice, V.SR)
    final = os.path.join(OUT, "final.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    thumbnail(SPEC)
    print("final", final, flush=True)


if __name__ == "__main__":
    main()
