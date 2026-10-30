import math, random, re
from engine import core as C
from engine.core import (font, clamp, ease, ease_out, back_out, prog, lerp, mix, ca, rrect, ellipse, text, fit_font, line, wrap,
                         check_icon, x_icon, warn_icon, num_icon, lock_icon, coin, bank_card, person, messenger_icon, shield_icon,
                         chart_icon, tag, qb, arrow, stamp, BOLD, SEMI, REG, BLACK, COLORS, GREEN, RED, YELLOW, BLUE, WHITE, MUTED,
                         DARK, CARD, CARD2)

WEIGHTS = {"black": BLACK, "bold": BOLD, "semi": SEMI, "regular": REG}


class Ctx:
    def __init__(self, starts, ends, dur):
        self.starts, self.ends, self.dur = starts, ends, dur

    def T(self, ref, default=0.0):
        if ref is None:
            return default
        if isinstance(ref, (int, float)):
            return float(ref)
        s = str(ref).replace(" ", "")
        if s == "end":
            return self.dur
        if s == "start":
            return 0.0
        try:
            return float(s)
        except ValueError:
            pass
        m = re.fullmatch(r"s(\d+)(e?)([+-]\d+(?:\.\d+)?)?", s)
        if not m:
            m2 = re.fullmatch(r"end([+-]\d+(?:\.\d+)?)", s)
            if m2:
                return self.dur + float(m2.group(1))
            raise ValueError(f"bad time ref {ref!r}")
        i = max(0, min(int(m.group(1)) - 1, len(self.starts) - 1))
        base = self.ends[i] if m.group(2) else self.starts[i]
        return base + (float(m.group(3)) if m.group(3) else 0.0)

    def col(self, v, t, default=GREEN):
        if v is None:
            return default
        if isinstance(v, str):
            if v.startswith("#") and len(v) == 7:
                return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
            return COLORS.get(v.lower(), default)
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
            cur = self.col(v[0][1], t, default)
            for ref, c in v[1:]:
                ts = self.T(ref)
                cur = mix(cur, self.col(c, t, default), prog(t, ts, ts + 0.4))
            return cur
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return tuple(int(x) for x in v)
        return default

    def num(self, v, t, default=0.0, dur=0.8):
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
            cur = float(v[0][1])
            for ref, x in v[1:]:
                ts = self.T(ref)
                cur = lerp(cur, float(x), ease(prog(t, ts, ts + dur)))
            return cur
        return float(v)

    def state(self, v, t):
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
            cur = v[0]
            for item in v:
                if self.T(item[0]) <= t:
                    cur = item
            return list(cur[1:])
        return [v]

    def vis(self, e, t, fade=0.5):
        tin = self.T(e.get("in", 0))
        fd = e.get("fade", fade)
        o = ease_out(prog(t, tin, tin + fd))
        if "out" in e:
            tout = self.T(e["out"])
            o *= 1 - ease(prog(t, tout - fd, tout))
        return o, ease_out(prog(t, tin, tin + fd * 1.3)), tin


def wfont(e, default="bold"):
    return WEIGHTS.get(e.get("weight", default), BOLD)


def r_section(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    cy = e.get("y", C.H / 2)
    sc = lerp(1.15, 1.0, ease_out(prog(t, tin + 0.1, tin + 0.9)))
    col = X.col(e.get("color", "red"), t)
    kicker = "  ".join(list(e.get("kicker", "SCAM").upper()))
    text(f, (C.W / 2, cy - 210), kicker, font(BOLD, 44), col, o)
    num = e.get("num", "")
    big = f"#{num}" if isinstance(num, int) or str(num).isdigit() else str(num)
    text(f, (C.W / 2, cy - 35), big, fit_font(BLACK, int(250 * sc), big, C.W - 120), col, o, glow=col, go=0.8)
    lw = min(520, C.W - 200) * ease_out(prog(t, tin + 0.4, tin + 1.2))
    rrect(f, [C.W / 2 - lw / 2, cy + 110, C.W / 2 + lw / 2, cy + 120], 5, fill=WHITE, o=o * 0.35)
    k2 = ease_out(prog(t, tin + 0.6, tin + 1.4))
    fn = font(BOLD, e.get("size", 76))
    lines = wrap(e.get("title", ""), fn, C.W - 160)
    for i, l in enumerate(lines):
        text(f, (C.W / 2, cy + 205 + i * fn.size * 1.2 + (1 - k2) * 20), l, fn, WHITE, o * k2)


def r_label(f, e, t, X):
    o, k, _ = X.vis(e, t)
    tag(f, e.get("x", C.W / 2), e.get("y", 90 if C.W > C.H else 150), e["text"], X.col(e.get("color", "green"), t), o, size=e.get("size", 30), fnt=BOLD)


def r_heading(f, e, t, X):
    o, k, _ = X.vis(e, t)
    if o <= 0:
        return
    fn = wfont(e, "black")
    size = e.get("size", 64)
    maxw = e.get("w", C.W - 140)
    fnt = font(fn, size)
    lines = wrap(e["text"], fnt, maxw)
    col = X.col(e.get("color", "white"), t)
    glow = X.col(e["glow"], t) if e.get("glow") else None
    x = e.get("x", C.W / 2)
    y = e.get("y", 150)
    anchor = e.get("anchor", "mm")
    lh = size * 1.18
    y0 = y - (len(lines) - 1) * lh / 2 if anchor[1] == "m" else y
    for i, l in enumerate(lines):
        text(f, (x, y0 + i * lh + (1 - k) * 24), l, fnt, col, o, anchor, glow=glow, go=0.55)


def r_text(f, e, t, X):
    e2 = dict(e)
    e2.setdefault("weight", "semi")
    e2.setdefault("size", 40)
    r_heading(f, e2, t, X)


def r_tag(f, e, t, X):
    o, k, _ = X.vis(e, t)
    tag(f, e["x"], e["y"] + (1 - k) * 16, e["text"], X.col(e.get("color", "green"), t), o, size=e.get("size", 30), anchor=e.get("anchor", "mm"), fnt=wfont(e, "semi"))


def r_rule(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    kind = e.get("kind", "ok")
    col = X.col(e.get("color"), t, GREEN if kind == "ok" else RED)
    size = e.get("size", 40)
    msg = e["text"]
    fn = fit_font(BOLD, size, msg, C.W - 100 - size * 3.2)
    size = fn.size
    tw = fn.getlength(msg)
    hh = size * 2.0
    bw = tw + size * 3.2
    y = e.get("y", C.H - 105 if C.W > C.H else C.H - 330)
    yy = y + (1 - k) * 40
    box = [C.W / 2 - bw / 2, yy - hh / 2, C.W / 2 + bw / 2, yy + hh / 2]
    rrect(f, box, hh / 2, fill=tuple(int(c * 0.14) for c in col), outline=col, w=3, o=o, glow=col, gw=14)
    ix = box[0] + hh / 2
    ik = prog(t, tin + 0.2, tin + 0.6)
    if kind == "ok":
        check_icon(f, ix + 4, yy, size * 0.62, o, col=col, k=ik)
    elif kind == "warn":
        warn_icon(f, ix + 4, yy, size * 0.62, o, col=col, k=ik)
    else:
        x_icon(f, ix + 4, yy, size * 0.62, o, col=col, k=ik)
    text(f, (box[0] + size * 2.2 + tw / 2, yy), msg, fn, WHITE, o)


def r_person(f, e, t, X):
    o, k, _ = X.vis(e, t)
    if o <= 0:
        return
    s = e.get("scale", 1.0)
    x, y = X.num(e.get("x", C.W / 2), t), X.num(e.get("y", C.H / 2), t)
    col = X.col(e.get("color", "green"), t)
    person(f, x, y + (1 - k) * 20, s, o, col, e.get("hood", False))
    if e.get("label"):
        text(f, (x, y + 215 * s), e["label"], font(BOLD, e.get("label_size", 44 * min(1, s + 0.15))), X.col(e.get("label_color", "red" if e.get("hood") else "white"), t), o)


def r_arrow(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.01)
    if o <= 0:
        return
    p0, p2 = e["from"], e["to"]
    p1 = e.get("via", [(p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2])
    draw = e.get("draw", 1.0)
    kk = ease(prog(t, tin, tin + draw))
    col = X.col(e.get("color", "green"), t)
    arrow(f, p0, p1, p2, kk, col, o * e.get("opacity", 1.0), w=e.get("width", 6), head=e.get("head", True), dashed=e.get("dashed", False))
    tr = e.get("traveler")
    if tr:
        kind = tr if isinstance(tr, str) else tr.get("kind", "coin")
        cfg = tr if isinstance(tr, dict) else {}
        n = cfg.get("count", 3 if kind == "coin" else 1)
        st = X.T(cfg.get("in"), tin + 0.1)
        du = cfg.get("dur", 1.6)
        tcol = X.col(cfg.get("color"), t, GREEN if kind == "coin" else BLUE)
        for i in range(n):
            q = prog(t, st + i * 0.18, st + du + i * 0.18)
            if 0 < q < 1:
                x, y = qb(p0, p1, p2, ease(q))
                oo = o * min(1, q * 6) * (1 - prog(q, 0.85, 1.0))
                if kind == "card":
                    bank_card(f, x, y, cfg.get("scale", 0.7), oo, tcol)
                else:
                    coin(f, x, y, cfg.get("size", 26), oo, tcol, cfg.get("symbol", "$"))
    if e.get("warn") is not None:
        wt = X.T(e["warn"])
        x, y = qb(p0, p1, p2, 0.5)
        warn_icon(f, x, y, e.get("warn_size", 34), o, k=prog(t, wt, wt + 0.4))


def r_icon(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.4)
    if o <= 0:
        return
    kind = e.get("kind", "check")
    x, y = X.num(e["x"], t), X.num(e["y"], t)
    r = e.get("size", 40)
    col = X.col(e.get("color"), t, {"check": GREEN, "x": RED, "warn": RED}.get(kind, GREEN))
    pk = prog(t, tin, tin + 0.4)
    if kind == "check":
        check_icon(f, x, y, r, o, col=col, k=pk)
    elif kind == "x":
        x_icon(f, x, y, r, o, col=col, k=pk)
    elif kind == "warn":
        warn_icon(f, x, y, r, o, col=col, k=pk)
    elif kind == "num":
        num_icon(f, x, y, r, e.get("n", 1), o, col=col, k=pk)
    elif kind in ("lock", "unlock"):
        open_k = 1.0 if kind == "unlock" else 0.0
        if "open" in e:
            ot = X.T(e["open"])
            open_k = ease(prog(t, ot, ot + 0.4))
        lock_icon(f, x, y, r / 40 * back_out(pk), o, col=col, open_k=open_k, glow=col)
    elif kind == "coin":
        coin(f, x, y, r * back_out(pk), o, col, e.get("symbol", "$"))
    elif kind == "card":
        bank_card(f, x, y, r / 50 * back_out(pk), o, X.col(e.get("color"), t, BLUE))
    elif kind == "shield":
        shield_icon(f, x, y, r / 100 * back_out(pk), o, col, e.get("check", True))
    elif kind == "messenger":
        sc = r / 100 * back_out(pk)
        messenger_icon(f, x, y, sc, o)
    elif kind in ("chart_up", "chart_down"):
        chart_icon(f, x, y, r / 100 * back_out(pk), o, col, 1 if kind == "chart_up" else -1)
    if e.get("label"):
        text(f, (x, y + r * 1.4 + e.get("label_gap", 30)), e["label"], font(BOLD, e.get("label_size", 36)), X.col(e.get("label_color", "white"), t), o)


def r_stamp(f, e, t, X):
    tin = X.T(e.get("in", 0))
    o = 1.0
    if "out" in e:
        to = X.T(e["out"])
        o = 1 - ease(prog(t, to - 0.4, to))
    stamp(f, e.get("x", C.W / 2), e.get("y", C.H / 2), e["text"], prog(t, tin, tin + 0.4), X.col(e.get("color", "red"), t), e.get("angle", -14), e.get("size", 130), o)


def r_flash(f, e, t, X):
    at = X.T(e.get("at", e.get("in", 0)))
    if at - 0.2 < t < at + 0.8:
        v = math.exp(-((t - at - 0.15) ** 2) / 0.015) * e.get("strength", 0.8)
        if v > f.flash:
            f.flash = v
            c = X.col(e.get("color", "red"), t)
            f.flash_col = tuple(int(x * 0.47) for x in c)


def _widget_vis(X, w, t, o):
    if "in" not in w and "out" not in w:
        return o, 1.0
    a, k, _ = X.vis(w, t, 0.4)
    return o * a, k


def w_header(f, w, box, s, o, t, X, y):
    lx = box[0] + 30 * s
    text(f, (lx, box[1] + 90 * s), w.get("title", "CryptoP2P"), font(BOLD, 30 * s), WHITE, o, "lm")
    text(f, (lx, box[1] + 130 * s), w.get("sub", ""), font(REG, 20 * s), MUTED, o, "lm")
    return y


def w_order(f, w, box, s, o, t, X, y):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    rrect(f, [lx, y, rx, y + 250 * s], 24 * s, fill=CARD, o=o)
    text(f, (lx + 24 * s, y + 40 * s), w.get("label", "Order #48213"), font(SEMI, 20 * s), MUTED, o, "lm")
    text(f, (lx + 24 * s, y + 100 * s), w.get("amount", "500 USDT"), fit_font(BLACK, 48 * s, w.get("amount", "500 USDT"), rx - lx - 48 * s), WHITE, o, "lm")
    text(f, (lx + 24 * s, y + 150 * s), w.get("who", ""), font(REG, 19 * s), MUTED, o, "lm")
    st = X.state(w.get("status", "Pending"), t)
    label = st[0]
    col = X.col(st[1] if len(st) > 1 else "yellow", t)
    fn = font(SEMI, 19 * s)
    pw = fn.getlength(label) + 50 * s
    px, py = lx + 24 * s, y + 185 * s
    rrect(f, [px, py, px + pw, py + 44 * s], 22 * s, fill=tuple(int(c * 0.22) for c in col), outline=col, w=max(1, 2 * s), o=o)
    text(f, (px + pw / 2, py + 22 * s), label, fn, col, o)
    if w.get("check") is not None:
        ct = X.T(w["check"])
        check_icon(f, px + pw + 40 * s, py + 22 * s, 24 * s, o, k=prog(t, ct, ct + 0.4))
    return y + 274 * s


def w_balance(f, w, box, s, o, t, X, y):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    col = X.col(w.get("color", "white"), t)
    bg = X.col(w.get("bg", "card"), t)
    rrect(f, [lx, y, rx, y + 190 * s], 24 * s, fill=bg, o=o)
    text(f, (lx + 24 * s, y + 45 * s), w.get("label", "Balance"), font(SEMI, 20 * s), MUTED, o, "lm")
    v = X.num(w.get("value", 0), t)
    dec = w.get("decimals", 2)
    sv = f"{w.get('prefix', '$')}{v:,.{dec}f}{w.get('suffix', '')}"
    text(f, (lx + 24 * s, y + 115 * s), sv, fit_font(BLACK, 46 * s, sv, rx - lx - 48 * s), col, o, "lm")
    return y + 214 * s


def w_bubbles(f, w, box, s, o, t, X, y):
    for it in w.get("items", []):
        tin = X.T(it.get("in", 0))
        k = ease_out(prog(t, tin, tin + 0.4))
        if k <= 0:
            continue
        side = it.get("side", "l")
        bcol = X.col(it.get("color"), t, CARD2 if side == "l" else (8, 70, 52))
        size = w.get("size", 21)
        fn = font(REG, size * s)
        maxw = (box[2] - box[0]) * 0.7
        lines = wrap(it["text"], fn, maxw)
        lh = size * 1.35 * s
        bw = max(fn.getlength(l) for l in lines) + 36 * s
        bh = lh * len(lines) + 26 * s
        x0 = box[0] + 24 * s if side == "l" else box[2] - 24 * s - bw
        yy = y + (1 - k) * 18 * s
        rrect(f, [x0, yy, x0 + bw, yy + bh], 20 * s, fill=bcol, o=o * k)
        for i, l in enumerate(lines):
            text(f, (x0 + 18 * s, yy + 13 * s + lh * (i + 0.5)), l, fn, WHITE, o * k, "lm")
        if it.get("thumb"):
            ty = yy + bh + 10 * s
            rrect(f, [x0, ty, x0 + 126 * s, ty + 140 * s], 12 * s, fill=(236, 240, 246), o=o * k)
            for j in range(4):
                rrect(f, [x0 + 16 * s, ty + (24 + j * 26) * s, x0 + (106 - j * 12) * s, ty + (34 + j * 26) * s], 4 * s, fill=(180, 186, 198), o=o * k)
            bh += 150 * s
        y += (bh + 16 * s) * k
    return y + 8 * s


def w_rows(f, w, box, s, o, t, X, y):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    for it in w.get("items", []):
        if "in" in it:
            tin = X.T(it["in"])
            k = ease_out(prog(t, tin, tin + 0.4))
        else:
            k = 1.0
        if k <= 0:
            continue
        c = X.col(it.get("color", "muted"), t)
        hi = c != MUTED
        rrect(f, [lx, y, rx, y + 66 * s], 16 * s, fill=CARD, outline=c if hi else None, w=2, o=o * k, glow=c if hi else None, gw=8)
        ellipse(f, lx + 34 * s, y + 33 * s, 16 * s, fill=c if hi else CARD2, o=o * k)
        text(f, (lx + 62 * s, y + 33 * s), it.get("label", ""), fit_font(SEMI, 18 * s, it.get("label", ""), (rx - lx) * 0.55), WHITE, o * k, "lm")
        text(f, (rx - 18 * s, y + 33 * s), it.get("amount", ""), font(BOLD, 20 * s), c if hi else WHITE, o * k, "rm")
        y += 80 * s * k
    return y + 10 * s


def w_skeleton(f, w, box, s, o, t, X, y):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    n = w.get("rows", 3)
    for i in range(n):
        yy = y + i * 52 * s
        rrect(f, [lx, yy, lx + (220 - i * 40) * s, yy + 18 * s], 9 * s, fill=CARD2, o=o)
        rrect(f, [rx - 70 * s, yy, rx, yy + 18 * s], 9 * s, fill=CARD2, o=o)
    return y + n * 52 * s + 10 * s


def w_code(f, w, box, s, o, t, X, y):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    digits = str(w.get("digits", "482916"))
    tin = X.T(w.get("in", 0))
    col = X.col(w.get("color", "muted"), t)
    text(f, (lx, y + 10 * s), w.get("label", "Enter SMS code"), font(SEMI, 19 * s), MUTED, o, "lm")
    yy = y + 40 * s
    n = len(digits)
    cw = (rx - lx - 10 * s * (n - 1)) / n
    for i in range(n):
        x0 = lx + i * (cw + 10 * s)
        rrect(f, [x0, yy, x0 + cw, yy + 70 * s], 14 * s, fill=CARD, outline=col, w=2, o=o)
        if t > tin + 0.3 + i * 0.25:
            text(f, (x0 + cw / 2, yy + 35 * s), digits[i], font(BOLD, 32 * s), WHITE, o)
    return yy + 90 * s


def w_spacer(f, w, box, s, o, t, X, y):
    return y + w.get("h", 40) * s


def w_text(f, w, box, s, o, t, X, y):
    fn = font(WEIGHTS.get(w.get("weight", "semi"), SEMI), w.get("size", 22) * s)
    lines = wrap(w["text"], fn, box[2] - box[0] - 60 * s)
    for l in lines:
        text(f, (box[0] + 30 * s, y + fn.size * 0.6), l, fn, X.col(w.get("color", "white"), t), o, "lm")
        y += fn.size * 1.35
    return y + 10 * s


def w_button(f, w, box, s, o, t, X):
    lx, rx = box[0] + 30 * s, box[2] - 30 * s
    st = X.state(w.get("label", "Release crypto"), t)
    label = st[0]
    col = X.col(st[1] if len(st) > 1 else w.get("color", "green"), t)
    press = 0.0
    if w.get("press") is not None:
        pt = X.T(w["press"])
        press = math.sin(math.pi * prog(t, pt, pt + 0.35))
    by0 = box[3] - 130 * s
    sh = 6 * s * press
    rrect(f, [lx + sh, by0 + sh, rx - sh, by0 + 80 * s - sh], 40 * s, fill=col, o=o, glow=col if w.get("glow", True) and col != COLORS["gray"] else None, gw=12 * s)
    text(f, ((box[0] + box[2]) / 2, by0 + 40 * s), label, font(BOLD, 24 * s), DARK, o)


def w_notification(f, w, box, s, o, t, X):
    tin = X.T(w.get("in", 0))
    k = ease_out(prog(t, tin, tin + 0.6))
    if k <= 0:
        return
    col = X.col(w.get("color", "red"), t)
    ny = lerp(box[1] - 140 * s, box[1] + 60 * s, k)
    nx0, nx1 = box[0] + 18 * s, box[2] - 18 * s
    rrect(f, [nx0, ny, nx1, ny + 120 * s], 26 * s, fill=tuple(int(c * 0.22) for c in col), outline=col, w=max(2, 3 * s), o=o, glow=col, gw=10 * s)
    ix, iy = nx0 + 58 * s, ny + 60 * s
    ellipse(f, ix, iy, 34 * s, fill=col, o=o)
    ic = w.get("icon", "lock")
    if ic == "lock":
        lock_icon(f, ix, iy - 2 * s, 0.5 * s, o, col=(255, 255, 255))
    elif ic == "msg":
        text(f, (ix, iy), w.get("letter", "S"), font(BLACK, 30 * s), WHITE, o)
    else:
        text(f, (ix, iy), "!", font(BLACK, 36 * s), WHITE, o)
    fn = fit_font(BOLD, 24 * s, w.get("title", ""), nx1 - nx0 - 130 * s)
    text(f, (nx0 + 108 * s, ny + 44 * s), w.get("title", ""), fn, WHITE, o, "lm")
    text(f, (nx0 + 108 * s, ny + 80 * s), w.get("sub", ""), font(REG, 18 * s), mix(col, WHITE, 0.6), o, "lm")


def w_chat_header(f, w, box, s, o, t, X, y):
    lx = box[0] + 30 * s
    st = X.state(w.get("name", "Official Support"), t)
    name = st[0]
    col = X.col(st[1] if len(st) > 1 else "blue", t)
    ellipse(f, lx + 32 * s, box[1] + 105 * s, 32 * s, fill=col, o=o)
    text(f, (lx + 32 * s, box[1] + 105 * s), w.get("letter", name[:1]), font(BLACK, 30 * s), WHITE, o)
    fn = font(BOLD, 24 * s)
    text(f, (lx + 80 * s, box[1] + 95 * s), name, fn, WHITE if col == BLUE else col, o, "lm")
    if w.get("verified"):
        bx = lx + 80 * s + fn.getlength(name) + 22 * s
        if col == BLUE:
            check_icon(f, bx, box[1] + 95 * s, 13 * s, o, col=BLUE)
        else:
            x_icon(f, bx, box[1] + 95 * s, 13 * s, o, col=col)
    text(f, (lx + 80 * s, box[1] + 125 * s), w.get("sub", "Private message"), font(REG, 17 * s), MUTED, o, "lm")
    return y


STACK = {"header": w_header, "chat_header": w_chat_header, "order": w_order, "balance": w_balance, "bubbles": w_bubbles, "rows": w_rows,
         "skeleton": w_skeleton, "code": w_code, "spacer": w_spacer, "text": w_text}


def r_phone(f, e, t, X):
    o, k, _ = X.vis(e, t, 0.6)
    if o <= 0:
        return
    s = X.num(e.get("scale", 0.95), t)
    cx = X.num(e.get("x", C.W / 2), t) + f.dx
    cy = X.num(e.get("y", C.H / 2), t) + (1 - k) * 30
    if e.get("shake") is not None:
        st = X.T(e["shake"])
        if st < t < st + 0.6:
            cx += math.sin(t * 110) * 12 * (1 - prog(t, st, st + 0.6))
    accent = X.col(e.get("accent", "green"), t)
    scr = X.col(e.get("screen_color", [12, 18, 28]), t)
    pw, ph = 420 * s, 860 * s
    x0, y0, x1, y1 = cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2
    f.g.rounded_rectangle([x0 - 6 * s, y0 - 6 * s, x1 + 6 * s, y1 + 6 * s], radius=66 * s, outline=ca(accent, o), width=max(1, int(14 * s)))
    f.d.rounded_rectangle([x0, y0, x1, y1], radius=60 * s, fill=ca((10, 12, 18), o), outline=ca((60, 68, 86), o), width=max(2, int(4 * s)))
    box = (x0 + 16 * s, y0 + 16 * s, x1 - 16 * s, y1 - 16 * s)
    f.d.rounded_rectangle(box, radius=46 * s, fill=ca(scr, o))
    screens = e.get("screens") or [{"widgets": e.get("widgets", [])}]
    for sc in screens:
        so, _ = _widget_vis(X, sc, t, o)
        if so <= 0:
            continue
        y = box[1] + 175 * s
        overlays = []
        for w in sc.get("widgets", []):
            wo, _ = _widget_vis(X, w, t, so)
            typ = w.get("type")
            if typ in ("button", "notification"):
                overlays.append((w, wo))
                continue
            fn = STACK.get(typ)
            if fn is None:
                continue
            if wo <= 0 and typ not in ("header", "chat_header"):
                continue
            y = fn(f, w, box, s, wo, t, X, y)
        for w, wo in overlays:
            if wo > 0:
                (w_button if w["type"] == "button" else w_notification)(f, w, box, s, wo, t, X)
    f.d.rounded_rectangle([cx - 60 * s, box[1] + 14 * s, cx + 60 * s, box[1] + 44 * s], radius=15 * s, fill=ca((0, 0, 0), o))


def r_checklist(f, e, t, X):
    x = e.get("x", 330 if C.W > C.H else 60)
    w = e.get("w", C.W - 2 * x)
    y = e.get("y", 300)
    rh = e.get("row_h", 128)
    size = e.get("size", 40)
    for i, it in enumerate(e.get("items", [])):
        tin = X.T(it.get("in", 0))
        k = ease_out(prog(t, tin, tin + 0.5))
        if "out" in e:
            to = X.T(e["out"])
            k *= 1 - ease(prog(t, to - 0.5, to))
        if k <= 0:
            continue
        yy = y + i * rh
        x0 = x + (1 - k) * 40
        done = prog(t, X.T(it["done"]), X.T(it["done"]) + 0.4) if it.get("done") is not None else 0
        dcol = X.col(it.get("color"), t, GREEN)
        hh = rh * 0.39
        rrect(f, [x0, yy - hh, x0 + w, yy + hh], 26, fill=CARD, outline=mix(CARD2, dcol, done), w=2, o=k, glow=dcol if done > 0 else None, gw=8)
        ellipse(f, x0 + 60, yy, 30, fill=mix(CARD2, dcol, done), o=k)
        text(f, (x0 + 60, yy), str(it.get("n", i + 1)), font(BLACK, 30), WHITE if done < 0.5 else DARK, k)
        fn = fit_font(SEMI, size, it["text"], w - 200)
        text(f, (x0 + 115, yy), it["text"], fn, WHITE, k, "lm")
        if it.get("kind", "check") == "x":
            x_icon(f, x0 + w - 60, yy, 30, k, k=done)
        else:
            check_icon(f, x0 + w - 60, yy, 30, k, col=dcol, k=done)


def r_bullets(f, e, t, X):
    x = e.get("x", 1110)
    y = e.get("y", 380)
    gap = e.get("gap", 115)
    size = e.get("size", 44)
    maxw = e.get("w", C.W - x - 120)
    if e.get("title"):
        o, k, _ = X.vis({"in": e.get("in", 0), **({"out": e["out"]} if "out" in e else {})}, t)
        text(f, (x - 30, y - gap - 15), e["title"], fit_font(BOLD, e.get("title_size", 56), e["title"], maxw + 60), WHITE, o, "lm")
    for i, it in enumerate(e.get("items", [])):
        tin = X.T(it.get("in", 0))
        k = ease_out(prog(t, tin, tin + 0.5))
        if "out" in e:
            to = X.T(e["out"])
            k *= 1 - ease(prog(t, to - 0.5, to))
        if k <= 0:
            continue
        yy = y + i * gap
        kind = it.get("kind", e.get("kind", "x"))
        if kind == "check":
            check_icon(f, x, yy, 32, k, k=k)
        elif kind == "warn":
            warn_icon(f, x, yy, 32, k, k=k)
        elif kind == "num":
            num_icon(f, x, yy, 32, i + 1, k, k=k)
        else:
            x_icon(f, x, yy, 32, k, k=k)
        col = X.col(it.get("color", "white"), t)
        fn = fit_font(SEMI, size, it["text"], maxw)
        text(f, (x + 60, yy), it["text"], fn, col, k, "lm", glow=col if it.get("glow") else None, go=0.5)


def r_card(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    x, y = e["x"], e["y"] + (1 - k) * 30
    w, h = e.get("w", 560), e.get("h", 230)
    col = X.col(e.get("color", "muted"), t)
    glow = col if e.get("glow", True) and col != MUTED else None
    rrect(f, [x, y, x + w, y + h], e.get("radius", 28), fill=X.col(e.get("bg", "card"), t), outline=col, w=3, o=o, glow=glow, gw=12)
    cy = y + 30
    ax = x + 40
    if e.get("avatar"):
        av = e["avatar"]
        acol = X.col(av.get("color", "green"), t)
        ellipse(f, x + 100, y + 105, 52, fill=acol, o=o)
        person(f, x + 100, y + 98, 0.42, o, DARK if acol != CARD2 else MUTED)
        if av.get("name"):
            text(f, (x + 180, y + 105), av["name"], font(BOLD, 40), WHITE, o, "lm")
        cy = y + 180
    for ln in e.get("lines", []):
        size = ln.get("size", 40)
        fn = fit_font(WEIGHTS.get(ln.get("weight", "bold"), BOLD), size, ln["text"], w - 80)
        cy += ln.get("dy", fn.size * 0.75)
        lc = X.col(ln.get("color", "white"), t)
        text(f, (ax, cy), ln["text"], fn, lc, o, "lm", glow=lc if ln.get("glow") else None, go=0.6)
        cy += fn.size * 0.75 + ln.get("gap", 14)
    if e.get("badge"):
        b = e["badge"]
        tag(f, ax, y + h - 60, b["text"], X.col(b.get("color", "green"), t), o, size=30, anchor="lm", fnt=BOLD)


def r_counter(f, e, t, X):
    o, k, _ = X.vis(e, t)
    if o <= 0:
        return
    v = X.num(e.get("value", 0), t, dur=e.get("dur", 0.9))
    dec = e.get("decimals", 0)
    s = f"{e.get('prefix', '')}{v:,.{dec}f}{e.get('suffix', '')}"
    col = X.col(e.get("color", "white"), t)
    text(f, (e.get("x", C.W / 2), e.get("y", C.H / 2) + (1 - k) * 20), s, font(wfont(e, "black"), e.get("size", 120)), col, o, e.get("anchor", "mm"), glow=col if e.get("glow", True) else None, go=0.6)


def r_escrow(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.7)
    if o <= 0:
        return
    x, y = e.get("x", C.W / 2), e.get("y", C.H / 2)
    acc = X.col(e.get("color", "green"), t)
    sc = lerp(0.7, 1.0, back_out(prog(t, tin, tin + 0.7))) * e.get("scale", 1.0)
    bw, bh = 150 * sc, 115 * sc
    rrect(f, [x - bw, y - bh, x + bw, y + bh], 28 * sc, fill=CARD, outline=acc, w=4, o=o, glow=acc, gw=14)
    lv = e.get("locked", [[0, False]])
    if not isinstance(lv, list):
        lv = [[0, bool(lv)]]
    lk = X.num([[r, 1.0 if v else 0.0] for r, v in lv], t, dur=0.5)
    if e.get("coins"):
        a, b = X.T(e["coins"][0]), X.T(e["coins"][1])
        held = prog(t, a, a + 0.3) * (1 - prog(t, b, b + 0.3))
        for i in range(3):
            coin(f, x - 50 * sc + i * 50 * sc, y + 62 * sc, 20 * sc, o * held, GREEN)
    lock_icon(f, x, y - 10 * sc, 1.25 * sc, o, col=acc, open_k=1 - lk, glow=acc)
    text(f, (x, y + bh + 50), e.get("label", "Escrow"), font(BOLD, 44), WHITE, o)
    if e.get("sub"):
        text(f, (x, y + bh + 97), e["sub"], font(REG, 30), MUTED, o)


def r_receipt(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.7)
    if o <= 0:
        return
    s = e.get("scale", 1.0) * lerp(0.6, 1.0, k)
    cx, cy = e.get("x", C.W / 2), e.get("y", C.H / 2)
    w, h = 520 * s, 640 * s
    x0, y0 = cx - w / 2, cy - h / 2
    rrect(f, [x0, y0, x0 + w, y0 + h], 26 * s, fill=(236, 240, 246), o=o, glow=WHITE, gw=10)
    d = (30, 36, 48)
    text(f, (cx, y0 + 70 * s), e.get("title", "Bank transfer"), font(BOLD, 34 * s), d, o)
    ellipse(f, cx, y0 + 160 * s, 46 * s, fill=(20, 190, 110), o=o)
    line(f, [(cx - 20 * s, y0 + 162 * s), (cx - 6 * s, y0 + 178 * s), (cx + 22 * s, y0 + 144 * s)], (255, 255, 255), 9 * s, o)
    text(f, (cx, y0 + 240 * s), e.get("status", "Payment successful"), font(SEMI, 26 * s), (20, 150, 90), o)
    rows = e.get("rows", [["Amount", "$500.00"], ["To", "Your account"], ["Date", "Today, 14:32"], ["Status", "Completed"]])
    for i, (a, b) in enumerate(rows[:4]):
        yy = y0 + (320 + i * 70) * s
        f.d.line([x0 + 40 * s, yy - 32 * s, x0 + w - 40 * s, yy - 32 * s], fill=ca((210, 214, 222), o), width=2)
        text(f, (x0 + 40 * s, yy), a, font(REG, 24 * s), (110, 118, 134), o, "lm")
        text(f, (x0 + w - 40 * s, yy), b, font(BOLD, 26 * s) if i == 0 else font(SEMI, 24 * s), d, o, "rm")
    for i, ref in enumerate(e.get("checks", [])):
        tt = X.T(ref)
        yy = y0 + (320 + i * 70) * s
        check_icon(f, x0 + w + 50 * s, yy, 24 * s, o, k=prog(t, tt, tt + 0.4))
    if e.get("edit"):
        a, b = X.T(e["edit"][0]), X.T(e["edit"][1])
        ek = prog(t, a, a + 0.3) * (1 - prog(t, b - 0.3, b))
        if ek > 0:
            yy = y0 + 320 * s
            rrect(f, [x0 + w - 190 * s, yy - 26 * s, x0 + w - 30 * s, yy + 26 * s], 6, fill=BLUE, o=ek * 0.35)
            if int(t * 3) % 2 == 0:
                f.d.line([x0 + w - 30 * s, yy - 30 * s, x0 + w - 30 * s, yy + 30 * s], fill=ca((30, 90, 220), ek), width=4)


_GRID = {}


def r_phone_grid(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    cols, rows = e.get("cols", 9 if C.W > C.H else 4), e.get("rows", 3 if C.W > C.H else 5)
    key = (cols, rows, e.get("seed", 7))
    if key not in _GRID:
        rnd = random.Random(e.get("seed", 7))
        _GRID[key] = [(c, r, rnd.random() < e.get("ratio", 0.45), rnd.random()) for r in range(rows) for c in range(cols)]
    a, b = X.T(e.get("turn_from", tin + 1.5)), X.T(e.get("turn_to", tin + 4.0))
    zoom = lerp(1.0, 0.92, prog(t, tin, X.T(e.get("out", "end"))))
    pw, ph = 120 * zoom, 240 * zoom
    gap = 70 * zoom
    tw = cols * pw + (cols - 1) * gap
    th = rows * ph + (rows - 1) * gap
    ox, oy = C.W / 2 - tw / 2, C.H / 2 - th / 2
    turn_col = X.col(e.get("turn_color", "red"), t)
    for c, r, turns, rr in _GRID[key]:
        x0 = ox + c * (pw + gap)
        y0 = oy + r * (ph + gap)
        ap = ease_out(prog(t, tin + (c + r) * 0.06, tin + 0.8 + (c + r) * 0.06))
        if ap <= 0:
            continue
        tt = lerp(a, b, rr)
        rk = ease(prog(t, tt, tt + 0.35)) if turns else 0
        col = mix(GREEN, turn_col, rk)
        yy = y0 + (1 - ap) * 40
        al = o * ap
        rrect(f, [x0, yy, x0 + pw, yy + ph], 18 * zoom, fill=(10, 12, 18), outline=(60, 68, 86), w=2, o=al)
        rrect(f, [x0 + 8 * zoom, yy + 8 * zoom, x0 + pw - 8 * zoom, yy + ph - 8 * zoom], 12 * zoom, fill=mix((12, 18, 28), tuple(int(v * 0.25) for v in turn_col), rk), o=al)
        rrect(f, [x0 + 18 * zoom, yy + 40 * zoom, x0 + pw - 18 * zoom, yy + 100 * zoom], 8 * zoom, fill=CARD, o=al)
        rrect(f, [x0 + 18 * zoom, yy + ph - 50 * zoom, x0 + pw - 18 * zoom, yy + ph - 26 * zoom], 12 * zoom, fill=col, o=al)
        f.g.rounded_rectangle([x0 - 3, yy - 3, x0 + pw + 3, yy + ph + 3], radius=20 * zoom, outline=ca(col, al * (0.5 + 0.5 * rk)), width=6)
        if rk > 0.5:
            warn_icon(f, x0 + pw / 2, yy + 140 * zoom, 18 * zoom, al, col=turn_col)


def r_bigtitle(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.9)
    if o <= 0:
        return
    y = e.get("y", C.H / 2 - 40) + (1 - k) * 30
    col = X.col(e.get("glow", "green"), t)
    fn = fit_font(BLACK, e.get("size", 190), e["text"], C.W - 120)
    text(f, (C.W / 2, y), e["text"], fn, WHITE, o, glow=col, go=0.9)
    k2 = ease_out(prog(t, tin + 0.8, tin + 1.7))
    if k2 > 0 and e.get("underline", "red"):
        uc = X.col(e.get("underline", "red"), t)
        lw = min(760, C.W - 200) * k2
        uy = y + fn.size * 0.63
        rrect(f, [C.W / 2 - lw / 2, uy, C.W / 2 + lw / 2, uy + 12], 6, fill=uc, o=o, glow=uc, gfill=True)
    k3 = ease_out(prog(t, tin + 1.4, tin + 2.3))
    if k3 > 0 and e.get("sub"):
        sf = fit_font(SEMI, e.get("sub_size", 56), e["sub"], C.W - 120)
        text(f, (C.W / 2, y + fn.size * 0.63 + 80 + (1 - k3) * 20), e["sub"], sf, MUTED, o * k3)


def r_ring(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    x, y = X.num(e.get("x", C.W / 2), t), X.num(e.get("y", C.H / 2), t)
    rx, ry = e.get("rx", 300), e.get("ry", 455)
    col = X.col(e.get("color", "green"), t)
    sh = X.T(e["shatter"]) if e.get("shatter") is not None else None
    if sh is not None and t >= sh:
        if e.get("reform") is not None:
            rf = X.T(e["reform"])
            o *= ease_out(prog(t, rf, rf + 0.8))
        else:
            o = 0
        ks = prog(t, sh, sh + 1.8)
        if 0 < ks < 1:
            rnd = random.Random(11)
            for _ in range(28):
                ang, sz, sp, rot = rnd.uniform(0, 2 * math.pi), rnd.uniform(14, 30), rnd.uniform(260, 620), rnd.uniform(-4, 4)
                bx = x + rx * math.cos(ang)
                by = y + ry * math.sin(ang)
                dist = sp * ease_out(ks)
                px = bx + math.cos(ang) * dist
                py = by + math.sin(ang) * dist + 500 * ks * ks
                a = rot * ks * 3 + ang
                pts = [(px + sz * math.cos(a + j * 2.1), py + sz * math.sin(a + j * 2.1)) for j in range(3)]
                cc = mix(col, RED, ks * 2)
                f.d.polygon(pts, fill=ca(cc, 1 - ks))
                f.g.polygon(pts, fill=ca(cc, 1 - ks))
    if o <= 0:
        return
    f.d.ellipse([x - rx, y - ry, x + rx, y + ry], outline=ca(col, o * 0.9), width=5)
    f.g.ellipse([x - rx, y - ry, x + rx, y + ry], outline=ca(col, o), width=22)
    f.d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=ca(col, o * 0.04))


def r_subscribe(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    x, y = e.get("x", C.W / 2), e.get("y", 500)
    click = X.T(e.get("click", tin + 2.0))
    subbed = t > click + 0.1
    press = math.sin(math.pi * prog(t, click, click + 0.25))
    bw, bh = 440 - press * 16, 104 - press * 8
    bc = (70, 76, 92) if subbed else RED
    rrect(f, [x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], bh / 2, fill=bc, o=o, glow=None if subbed else RED, gfill=True)
    text(f, (x, y), "SUBSCRIBED" if subbed else "SUBSCRIBE", font(BLACK, 42), WHITE, o)
    ck = prog(t, click - 1.1, click)
    co = o * (1 - ease(prog(t, click + 0.8, click + 1.4)))
    if ck > 0 and co > 0:
        cx = lerp(x + 340, x + 50, ease(ck))
        cy = lerp(y + 220, y + 20, ease(ck))
        f.d.polygon([(cx, cy), (cx, cy + 52), (cx + 14, cy + 40), (cx + 26, cy + 64), (cx + 36, cy + 58), (cx + 24, cy + 36), (cx + 42, cy + 36)], fill=ca(WHITE, co), outline=ca(DARK, co))


def r_endscreen(f, e, t, X):
    o, k, _ = X.vis(e, t, 0.8)
    if o <= 0:
        return
    text(f, (C.W / 2, 190), e.get("title", "Watch next"), font(BLACK, 64), WHITE, o, glow=GREEN, go=0.4)
    ellipse(f, 560, 580, 170, fill=CARD, o=o * 0.6)
    for a in range(0, 360, 12):
        f.d.arc([390, 410, 730, 750], a, a + 7, fill=ca(MUTED, o), width=4)
    text(f, (560, 580), "Subscribe", font(SEMI, 30), MUTED, o * 0.7)
    rrect(f, [960, 400, 1600, 760], 24, fill=CARD, o=o * 0.6)
    for x in range(960, 1600, 24):
        f.d.line([x, 400, min(x + 12, 1600), 400], fill=ca(MUTED, o), width=4)
        f.d.line([x, 760, min(x + 12, 1600), 760], fill=ca(MUTED, o), width=4)
    for y in range(400, 760, 24):
        f.d.line([960, y, 960, min(y + 12, 760)], fill=ca(MUTED, o), width=4)
        f.d.line([1600, y, 1600, min(y + 12, 760)], fill=ca(MUTED, o), width=4)
    text(f, (1280, 580), "Next video", font(SEMI, 30), MUTED, o * 0.7)


def r_comment(f, e, t, X):
    o, k, _ = X.vis(e, t, 0.6)
    if o <= 0:
        return
    fn = fit_font(SEMI, e.get("size", 40), e["text"], C.W - 200)
    tw = fn.getlength(e["text"])
    x0 = C.W / 2 - tw / 2 - 40
    y = e.get("y", 920) + (1 - k) * 20
    rrect(f, [x0, y - 40, x0 + tw + 80, y + 40], 40, fill=CARD, outline=CARD2, w=2, o=o)
    f.d.polygon([(x0 + 60, y + 38), (x0 + 50, y + 70), (x0 + 95, y + 38)], fill=ca(CARD, o))
    text(f, (C.W / 2, y), e["text"], fn, WHITE, o)


def r_words(f, e, t, X):
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    words = e.get("words", [])
    cols = e.get("cols", 4)
    x, y, w = e.get("x", 360), e.get("y", 280), e.get("w", C.W - 720)
    gap = 18
    cw = (w - gap * (cols - 1)) / cols
    ch = e.get("cell_h", 86)
    col = X.col(e.get("color", "green"), t)
    blur = X.T(e["hide"]) if e.get("hide") is not None else None
    for i, wd in enumerate(words):
        r, c = divmod(i, cols)
        cx0 = x + c * (cw + gap)
        cy0 = y + r * (ch + gap)
        kk = ease_out(prog(t, tin + i * 0.08, tin + 0.4 + i * 0.08))
        if kk <= 0:
            continue
        rrect(f, [cx0, cy0, cx0 + cw, cy0 + ch], 18, fill=CARD, outline=mix(CARD2, col, 0.6), w=2, o=o * kk)
        text(f, (cx0 + 34, cy0 + ch / 2), str(i + e.get("start", 1)), font(BOLD, 24), MUTED, o * kk)
        hk = prog(t, blur, blur + 0.5) if blur is not None else 0
        if hk < 1:
            text(f, (cx0 + 64, cy0 + ch / 2), wd, fit_font(SEMI, 34, wd, cw - 80), WHITE, o * kk * (1 - hk), "lm")
        if hk > 0:
            rrect(f, [cx0 + 60, cy0 + ch / 2 - 10, cx0 + cw - 24, cy0 + ch / 2 + 10], 10, fill=CARD2, o=o * kk * hk)


def _state_lines(X, v, t, default_col="white"):
    """screen text: a string, a state list [[ref, text, color], ...] or a list of those (one per line)."""
    if v is None:
        return []
    if isinstance(v, str):
        return [(v, X.col(default_col, t))]
    if isinstance(v, list) and v and isinstance(v[0], list) and v[0] and isinstance(v[0][0], list):
        out = []
        for st in v:
            out += _state_lines(X, st, t, default_col)
        return out
    cur = X.state(v, t)
    txt = cur[0] if cur else ""
    col = X.col(cur[1] if len(cur) > 1 else default_col, t)
    return [(txt, col)] if txt else []


def r_device(f, e, t, X):
    """Hardware wallet (kind "hw", default) or a laptop (kind "laptop") with a small text screen."""
    o, k, tin = X.vis(e, t, 0.6)
    if o <= 0:
        return
    s = X.num(e.get("scale", 1.0), t)
    x = X.num(e.get("x", C.W / 2), t)
    y = X.num(e.get("y", C.H / 2), t) + (1 - k) * 30
    if e.get("shake") is not None:
        st = X.T(e["shake"])
        if st < t < st + 0.6:
            x += math.sin(t * 110) * 12 * (1 - prog(t, st, st + 0.6))
    acc = X.col(e.get("color", "green"), t)
    lines = _state_lines(X, e.get("screen"), t)
    if e.get("kind", "hw") == "laptop":
        w, h = 620 * s, 380 * s
        box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
        rrect(f, box, 22 * s, fill=(26, 32, 46), outline=acc, w=max(2, int(5 * s)), o=o, glow=acc, gw=10)
        inner = [box[0] + 22 * s, box[1] + 22 * s, box[2] - 22 * s, box[3] - 22 * s]
        rrect(f, inner, 10 * s, fill=(12, 18, 28), o=o)
        rrect(f, [inner[0], inner[1], inner[2], inner[1] + 40 * s], 10 * s, fill=CARD2, o=o)
        for i, c in enumerate((RED, YELLOW, GREEN)):
            ellipse(f, inner[0] + (26 + i * 30) * s, inner[1] + 20 * s, 8 * s, fill=c, o=o * 0.8)
        base = [(x - w / 2 - 50 * s, y + h / 2 + 34 * s), (x + w / 2 + 50 * s, y + h / 2 + 34 * s), (x + w / 2, y + h / 2 + 4 * s), (x - w / 2, y + h / 2 + 4 * s)]
        f.d.polygon(base, fill=ca((52, 60, 78), o))
        n = max(1, len(lines))
        size = e.get("size", 44) * s
        cy0 = (inner[1] + 40 * s + inner[3]) / 2 - (n - 1) * size * 0.65
        for i, (txt, col) in enumerate(lines):
            fn = fit_font(BOLD, size, txt, inner[2] - inner[0] - 40 * s)
            text(f, (x, cy0 + i * size * 1.3), txt, fn, col, o)
    else:
        w, h = 400 * s, 270 * s
        box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
        rrect(f, box, 46 * s, fill=(30, 36, 52), outline=acc, w=max(2, int(6 * s)), o=o, glow=acc, gw=12)
        scr = [box[0] + 36 * s, box[1] + 32 * s, box[2] - 36 * s, box[1] + 162 * s]
        rrect(f, scr, 14 * s, fill=(6, 8, 12), outline=CARD2, w=2, o=o)
        n = max(1, len(lines))
        size = e.get("size", 34) * s
        cy0 = (scr[1] + scr[3]) / 2 - (n - 1) * size * 0.62
        for i, (txt, col) in enumerate(lines):
            fn = fit_font(BOLD, size, txt, scr[2] - scr[0] - 24 * s)
            text(f, (x, cy0 + i * size * 1.24), txt, fn, col, o)
        pk = 0.0
        if e.get("press") is not None:
            pt = X.T(e["press"])
            pk = math.sin(math.pi * prog(t, pt, pt + 0.35))
            done = t > pt + 0.2
        else:
            done = False
        by = box[1] + 215 * s
        ellipse(f, x - 80 * s, by, 26 * s, fill=CARD2, o=o)
        x_icon(f, x - 80 * s, by, 12 * s, o, col=MUTED)
        bc = acc if done else CARD2
        ellipse(f, x + 80 * s, by + pk * 4 * s, (26 - pk * 4) * s, fill=bc, o=o, glow=acc if done else None)
        check_icon(f, x + 80 * s, by + pk * 4 * s, 12 * s, o, col=DARK if done else MUTED)
        if pk > 0:
            ellipse(f, x + 80 * s, by, 40 * s, outline=acc, w=3, o=o * pk)
    if e.get("label"):
        ly = y + (h / 2 + (90 if e.get("kind") == "laptop" else 60) * s)
        text(f, (x, ly), e["label"], font(BOLD, e.get("label_size", 38)), X.col(e.get("label_color", "white"), t), o)


RENDER = {"words": r_words, "device": r_device,
"section": r_section, "label": r_label, "heading": r_heading, "text": r_text, "tag": r_tag, "rule": r_rule, "person": r_person,
          "arrow": r_arrow, "icon": r_icon, "stamp": r_stamp, "flash": r_flash, "phone": r_phone, "checklist": r_checklist,
          "bullets": r_bullets, "card": r_card, "counter": r_counter, "escrow": r_escrow, "receipt": r_receipt, "phone_grid": r_phone_grid,
          "bigtitle": r_bigtitle, "ring": r_ring, "subscribe": r_subscribe, "endscreen": r_endscreen, "comment": r_comment}


def draw_scene(elements, t, X):
    f = C.F()
    for e in elements:
        fn = RENDER.get(e.get("type"))
        if fn is None:
            raise ValueError(f"unknown element type {e.get('type')!r}")
        fn(f, e, t, X)
    return f


def caption_chunks(sc, max_words=3, max_chars=20):
    out = []
    for sent, st, en in zip(sc["sentences"], sc["starts"], sc["ends"]):
        words = sent.split()
        total = sum(len(w) + 1 for w in words) or 1
        t = st
        chunk, ch_words = [], []
        for w in words:
            dt = (en - st) * (len(w) + 1) / total
            ch_words.append((w, t, t + dt))
            t += dt
            if len(ch_words) >= max_words or sum(len(x[0]) + 1 for x in ch_words) >= max_chars or w[-1] in ".,!?:;":
                chunk.append(ch_words)
                ch_words = []
        if ch_words:
            chunk.append(ch_words)
        out.extend(chunk)
    return out


def draw_captions(f, sc, t, cfg):
    key = "_cap_chunks"
    if key not in sc:
        sc[key] = caption_chunks(sc, cfg.get("words", 3), cfg.get("chars", 20))
    cur = None
    for ch in sc[key]:
        if ch[0][1] - 0.05 <= t <= ch[-1][2] + 0.25:
            cur = ch
    if cur is None:
        return
    short = C.W < C.H
    size = cfg.get("size", 70 if short else 52)
    y = cfg.get("y", 1360 if short else C.H - 60)
    cx = cfg.get("x", 455 if short else C.W / 2)
    maxw = cfg.get("w", 800 if short else C.W - 80)
    fn = font(BLACK, size)
    words = [w for w, _, _ in cur]
    gap = size * 0.28
    widths = [fn.getlength(w) for w in words]
    tw = sum(widths) + gap * (len(words) - 1)
    if tw > maxw:
        fn = font(BLACK, size * maxw / tw)
        widths = [fn.getlength(w) for w in words]
        gap = fn.size * 0.28
        tw = sum(widths) + gap * (len(words) - 1)
    k = ease_out(prog(t, cur[0][1] - 0.05, cur[0][1] + 0.12))
    x = cx - tw / 2
    hi = COLORS.get(cfg.get("color", "yellow"), YELLOW)
    stroke = max(3, int(fn.size * 0.12))
    for w, (word, a, b), wd in zip(words, cur, widths):
        active = a <= t <= b + 0.05
        col = hi if active else WHITE
        cy = y - (6 if active else 0) * k
        f.d.text((x + wd / 2, cy), word, font=fn, fill=ca(col, k), anchor="mm", stroke_width=stroke, stroke_fill=ca((0, 0, 0), k))
        if active:
            f.g.text((x + wd / 2, cy), word, font=fn, fill=ca(hi, 0.45 * k), anchor="mm")
        x += wd + gap
