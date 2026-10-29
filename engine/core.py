import math, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 1920, 1080, 30

FD = "/usr/share/fonts/opentype/inter/"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BOLD, SEMI, REG, BLACK = FD + "Inter-Bold.otf", FD + "Inter-SemiBold.otf", FD + "Inter-Regular.otf", FD + "Inter-Black.otf"

GREEN = (0, 255, 156)
RED = (255, 48, 72)
YELLOW = (255, 196, 0)
BLUE = (70, 150, 255)
PURPLE = (170, 110, 255)
ORANGE = (255, 140, 40)
BG1 = (6, 8, 14)
BG2 = (14, 20, 32)
CARD = (22, 28, 42)
CARD2 = (34, 42, 60)
MUTED = (120, 132, 156)
WHITE = (240, 244, 250)
DARK = (8, 12, 18)

COLORS = {"green": GREEN, "red": RED, "yellow": YELLOW, "blue": BLUE, "purple": PURPLE, "orange": ORANGE, "white": WHITE, "muted": MUTED, "dark": DARK, "card": CARD, "card2": CARD2, "gray": (70, 76, 92)}


@lru_cache(None)
def font(path, size):
    try:
        return ImageFont.truetype(path, max(6, int(size)))
    except OSError:
        return ImageFont.truetype(FALLBACK, max(6, int(size)))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back_out(x):
    x = clamp(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def prog(t, a, b):
    if b <= a:
        return 1.0 if t >= a else 0.0
    return clamp((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(lerp(c1[i], c2[i], clamp(k))) for i in range(3))


def ca(c, o):
    return tuple(c[:3]) + (int(255 * clamp(o)),)


def _bg():
    bg = Image.new("RGB", (W, H), BG1)
    d = ImageDraw.Draw(bg)
    rmax = int(max(W, H) * 0.47)
    for r in range(rmax, 0, -6):
        k = 1 - r / rmax
        if W >= H:
            d.ellipse([W / 2 - r * 1.6, H / 2 - r, W / 2 + r * 1.6, H / 2 + r], fill=mix(BG1, BG2, k))
        else:
            d.ellipse([W / 2 - r, H / 2 - r * 1.6, W / 2 + r, H / 2 + r * 1.6], fill=mix(BG1, BG2, k))
    d = ImageDraw.Draw(bg, "RGBA")
    for x in range(0, W, 80):
        d.line([x, 0, x, H], fill=(255, 255, 255, 8))
    for y in range(0, H, 80):
        d.line([0, y, W, y], fill=(255, 255, 255, 8))
    return bg


def _vig():
    v = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(v)
    for i in range(40):
        k = i / 40
        d.ellipse([-W * 0.25 + k * W * 0.25, -H * 0.3 + k * H * 0.3, W * 1.25 - k * W * 0.25, H * 1.3 - k * H * 0.3], fill=int(255 * k))
    v = v.filter(ImageFilter.GaussianBlur(60))
    v = v.point(lambda p: int(255 - (255 - p) * 0.55))
    return Image.merge("RGB", (v, v, v))


BG = VIG = BLACKIMG = None


def setup(w, h):
    global W, H, BG, VIG, BLACKIMG
    W, H = w, h
    BG = _bg()
    VIG = _vig()
    BLACKIMG = Image.new("RGB", (W, H), (0, 0, 0))


class F:
    def __init__(self):
        self.img = BG.copy()
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.gimg = Image.new("RGB", (W, H), (0, 0, 0))
        self.g = ImageDraw.Draw(self.gimg, "RGBA")
        self.flash = 0
        self.flash_col = (120, 0, 16)
        self.dx = 0

    def finish(self, fade=0.0, vignette=True):
        small = self.gimg.resize((W // 4, H // 4), Image.BILINEAR)
        if small.getbbox():
            b = ImageChops.add(small.filter(ImageFilter.GaussianBlur(5)), small.filter(ImageFilter.GaussianBlur(16)))
            out = ImageChops.add(self.img, b.resize((W, H), Image.BILINEAR))
        else:
            out = self.img
        if self.flash > 0:
            out = Image.blend(out, Image.new("RGB", (W, H), self.flash_col), 0.35 * clamp(self.flash))
        if vignette:
            out = ImageChops.multiply(out, VIG)
        if fade > 0:
            out = Image.blend(out, BLACKIMG, clamp(fade))
        return out


def rrect(f, box, r, fill=None, outline=None, w=2, o=1.0, glow=None, gw=10, gfill=False):
    if o <= 0:
        return
    box = [min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])]
    r = max(0, min(r, (box[2] - box[0]) / 2, (box[3] - box[1]) / 2))
    f.d.rounded_rectangle(box, radius=r, fill=ca(fill, o) if fill else None, outline=ca(outline, o) if outline else None, width=max(1, int(w)))
    if glow:
        if gfill:
            f.g.rounded_rectangle(box, radius=r, fill=ca(glow, o * 0.5))
        else:
            f.g.rounded_rectangle(box, radius=r, outline=ca(glow, o), width=max(1, int(gw)))


def ellipse(f, cx, cy, r, fill=None, outline=None, w=2, o=1.0, glow=None, gr=1.3):
    if o <= 0 or r <= 0:
        return
    f.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ca(fill, o) if fill else None, outline=ca(outline, o) if outline else None, width=max(1, int(w)))
    if glow:
        f.g.ellipse([cx - r * gr, cy - r * gr, cx + r * gr, cy + r * gr], fill=ca(glow, o * 0.8))


def text(f, xy, s, fnt, col, o=1.0, anchor="mm", glow=None, go=0.9):
    if o <= 0 or not s:
        return
    if glow:
        f.g.text(xy, s, font=fnt, fill=ca(glow, o * go), anchor=anchor)
    f.d.text(xy, s, font=fnt, fill=ca(col, o), anchor=anchor)


def fit_font(path, size, s, maxw):
    fn = font(path, size)
    while size > 14 and fn.getlength(s) > maxw:
        size -= 2
        fn = font(path, size)
    return fn


def line(f, pts, col, w, o=1.0, glow=None, gw=None):
    if o <= 0:
        return
    f.d.line(pts, fill=ca(col, o), width=max(1, int(w)), joint="curve")
    if glow:
        f.g.line(pts, fill=ca(glow, o), width=max(1, int(gw or w * 2.5)), joint="curve")


def wrap(s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        nxt = (cur + " " + wd).strip()
        if fnt.getlength(nxt) <= maxw or not cur:
            cur = nxt
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def check_icon(f, cx, cy, r, o=1.0, col=GREEN, k=1.0):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return
    rr = r * back_out(k)
    ellipse(f, cx, cy, rr, fill=col, o=o)
    f.g.ellipse([cx - rr * 1.15, cy - rr * 1.15, cx + rr * 1.15, cy + rr * 1.15], outline=ca(col, o), width=max(2, int(rr * 0.35)))
    if k > 0.5:
        line(f, [(cx - rr * 0.42, cy + rr * 0.02), (cx - rr * 0.12, cy + rr * 0.34), (cx + rr * 0.45, cy - rr * 0.35)], DARK, rr * 0.2, o)


def x_icon(f, cx, cy, r, o=1.0, col=RED, k=1.0):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return
    rr = r * back_out(k)
    ellipse(f, cx, cy, rr, fill=col, o=o)
    f.g.ellipse([cx - rr * 1.15, cy - rr * 1.15, cx + rr * 1.15, cy + rr * 1.15], outline=ca(col, o), width=max(2, int(rr * 0.35)))
    if k > 0.5:
        a = rr * 0.36
        line(f, [(cx - a, cy - a), (cx + a, cy + a)], (255, 255, 255), rr * 0.2, o)
        line(f, [(cx - a, cy + a), (cx + a, cy - a)], (255, 255, 255), rr * 0.2, o)


def warn_icon(f, cx, cy, r, o=1.0, col=RED, k=1.0):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return
    rr = r * back_out(k)
    ellipse(f, cx, cy, rr, fill=col, o=o)
    f.g.ellipse([cx - rr * 1.15, cy - rr * 1.15, cx + rr * 1.15, cy + rr * 1.15], outline=ca(col, o), width=max(2, int(rr * 0.35)))
    if k > 0.5:
        rrect(f, [cx - rr * 0.11, cy - rr * 0.55, cx + rr * 0.11, cy + rr * 0.15], rr * 0.1, fill=(255, 255, 255), o=o)
        ellipse(f, cx, cy + rr * 0.42, rr * 0.13, fill=(255, 255, 255), o=o)


def num_icon(f, cx, cy, r, n, o=1.0, col=GREEN, k=1.0):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return
    rr = r * back_out(k)
    ellipse(f, cx, cy, rr, fill=col, o=o)
    f.g.ellipse([cx - rr * 1.15, cy - rr * 1.15, cx + rr * 1.15, cy + rr * 1.15], outline=ca(col, o), width=max(2, int(rr * 0.35)))
    text(f, (cx, cy), str(n), font(BLACK, rr * 1.0), DARK, o)


def lock_icon(f, cx, cy, s, o=1.0, col=(255, 255, 255), open_k=0.0, glow=None):
    if o <= 0:
        return
    lift = 16 * s * clamp(open_k)
    f.d.arc([cx - 22 * s, cy - 46 * s - lift, cx + 22 * s, cy - 2 * s - lift], 180, 360, fill=ca(col, o), width=max(2, int(8 * s)))
    f.d.line([cx - 18 * s, cy - 24 * s - lift, cx - 18 * s, cy - 4 * s - lift * (1 - clamp(open_k))], fill=ca(col, o), width=max(2, int(8 * s)))
    f.d.line([cx + 18 * s, cy - 24 * s - lift, cx + 18 * s, cy - 4 * s], fill=ca(col, o), width=max(2, int(8 * s)))
    rrect(f, [cx - 32 * s, cy - 8 * s, cx + 32 * s, cy + 40 * s], 8 * s, fill=col, o=o, glow=glow, gw=10 * s)
    ellipse(f, cx, cy + 14 * s, 6 * s, fill=DARK, o=o)


def coin(f, cx, cy, r, o=1.0, col=GREEN, sym="$"):
    if o <= 0:
        return
    ellipse(f, cx, cy, r, fill=mix(col, DARK, 0.25), o=o, glow=col, gr=1.25)
    ellipse(f, cx, cy, r * 0.78, outline=DARK, w=max(1, r * 0.08), o=o * 0.6)
    text(f, (cx, cy + r * 0.04), sym, font(BLACK, r * 1.05), DARK, o)


def bank_card(f, cx, cy, s, o=1.0, col=BLUE):
    if o <= 0:
        return
    rrect(f, [cx - 70 * s, cy - 45 * s, cx + 70 * s, cy + 45 * s], 12 * s, fill=col, o=o, glow=col, gw=8 * s)
    rrect(f, [cx - 70 * s, cy - 25 * s, cx + 70 * s, cy - 8 * s], 0, fill=DARK, o=o * 0.7)
    rrect(f, [cx - 52 * s, cy + 6 * s, cx - 24 * s, cy + 26 * s], 4 * s, fill=YELLOW, o=o)


def person(f, cx, cy, s, o=1.0, col=GREEN, hood=False):
    if o <= 0:
        return
    if hood:
        f.d.pieslice([cx - 80 * s, cy + 10 * s, cx + 80 * s, cy + 170 * s], 180, 360, fill=ca((30, 10, 16), o))
        f.g.pieslice([cx - 84 * s, cy + 6 * s, cx + 84 * s, cy + 174 * s], 180, 360, fill=ca(col, o * 0.6))
        f.d.ellipse([cx - 52 * s, cy - 66 * s, cx + 52 * s, cy + 46 * s], fill=ca((30, 10, 16), o))
        f.g.ellipse([cx - 56 * s, cy - 70 * s, cx + 56 * s, cy + 50 * s], fill=ca(col, o * 0.6))
        f.d.ellipse([cx - 34 * s, cy - 40 * s, cx + 34 * s, cy + 34 * s], fill=ca((4, 4, 6), o))
        for ex in (-12, 12):
            ellipse(f, cx + ex * s, cy - 4 * s, 5 * s, fill=col, o=o, glow=col, gr=2)
    else:
        f.d.pieslice([cx - 70 * s, cy + 30 * s, cx + 70 * s, cy + 170 * s], 180, 360, fill=ca(col, o))
        f.g.pieslice([cx - 74 * s, cy + 26 * s, cx + 74 * s, cy + 174 * s], 180, 360, fill=ca(col, o * 0.5))
        ellipse(f, cx, cy - 10 * s, 38 * s, fill=col, o=o, glow=col, gr=1.15)


def messenger_icon(f, cx, cy, s, o=1.0, col=(40, 70, 130)):
    if o <= 0:
        return
    rrect(f, [cx - 110 * s, cy - 110 * s, cx + 110 * s, cy + 110 * s], 50 * s, fill=col, o=o, glow=BLUE, gw=14 * s)
    rrect(f, [cx - 60 * s, cy - 45 * s, cx + 60 * s, cy + 30 * s], 22 * s, fill=WHITE, o=o)
    f.d.polygon([(cx - 30 * s, cy + 25 * s), (cx - 45 * s, cy + 60 * s), (cx - 5 * s, cy + 28 * s)], fill=ca(WHITE, o))
    for j in range(3):
        ellipse(f, cx - 28 * s + j * 28 * s, cy - 8 * s, 8 * s, fill=col, o=o)


def shield_icon(f, cx, cy, s, o=1.0, col=GREEN, check=True):
    if o <= 0:
        return
    pts = [(cx, cy - 110 * s), (cx + 95 * s, cy - 70 * s), (cx + 85 * s, cy + 40 * s), (cx, cy + 115 * s), (cx - 85 * s, cy + 40 * s), (cx - 95 * s, cy - 70 * s)]
    f.g.line(pts + [pts[0]], fill=ca(col, o), width=max(2, int(18 * s)), joint="curve")
    f.d.polygon(pts, fill=ca(mix(col, DARK, 0.15), o))
    if check:
        line(f, [(cx - 38 * s, cy + 2 * s), (cx - 10 * s, cy + 32 * s), (cx + 42 * s, cy - 30 * s)], DARK, 16 * s, o)


def chart_icon(f, cx, cy, s, o=1.0, col=GREEN, trend=1):
    if o <= 0:
        return
    rrect(f, [cx - 110 * s, cy - 80 * s, cx + 110 * s, cy + 80 * s], 20 * s, fill=CARD, outline=col, w=3 * s, o=o, glow=col, gw=10 * s)
    pts = [(-80, 40), (-40, 10), (0, 25), (40, -15), (80, -45)] if trend >= 0 else [(-80, -45), (-40, -15), (0, -25), (40, 10), (80, 40)]
    line(f, [(cx + x * s, cy + y * s) for x, y in pts], col, 7 * s, o, glow=col)


def tag(f, x, y, s, col, o=1.0, size=30, anchor="mm", bg=None, fnt=SEMI):
    if o <= 0:
        return None
    fn = fit_font(fnt, size, s, W - 120)
    size = fn.size
    tw = fn.getlength(s)
    h = size * 1.75
    pad = size * 0.8
    if anchor == "mm":
        x0 = x - tw / 2 - pad
    elif anchor == "lm":
        x0 = x
    else:
        x0 = x - tw - 2 * pad
    box = [x0, y - h / 2, x0 + tw + 2 * pad, y + h / 2]
    rrect(f, box, h / 2, fill=bg or tuple(int(c * 0.18) for c in col), outline=col, w=max(2, size / 12), o=o, glow=col, gw=size / 3)
    text(f, ((box[0] + box[2]) / 2, y), s, fn, col, o)
    return box


def qb(p0, p1, p2, k):
    a = (1 - k) ** 2
    b = 2 * (1 - k) * k
    c = k * k
    return (a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1])


def arrow(f, p0, p1, p2, k, col, o=1.0, w=6, head=True, dashed=False):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return None
    n = max(2, int(60 * k))
    pts = [qb(p0, p1, p2, k * i / n) for i in range(n + 1)]
    if dashed:
        for i in range(0, len(pts) - 1, 2):
            line(f, [pts[i], pts[i + 1]], col, w, o * 0.8)
    else:
        line(f, pts, col, w, o, glow=col, gw=w * 2.4)
    tip = pts[-1]
    if head and k > 0.05:
        bx, by = pts[-2]
        ang = math.atan2(tip[1] - by, tip[0] - bx)
        L = w * 4.2
        a1 = (tip[0] - L * math.cos(ang - 0.5), tip[1] - L * math.sin(ang - 0.5))
        a2 = (tip[0] - L * math.cos(ang + 0.5), tip[1] - L * math.sin(ang + 0.5))
        f.d.polygon([tip, a1, a2], fill=ca(col, o))
        f.g.polygon([tip, a1, a2], fill=ca(col, o))
    return tip


def stamp(f, cx, cy, word, k, col=RED, angle=-14, size=130, o=1.0):
    k = clamp(k)
    if k <= 0 or o <= 0:
        return
    sc = lerp(1.8, 1.0, ease_out(k))
    a = o * clamp(k * 2)
    fn = font(BLACK, int(size * sc))
    tw = fn.getlength(word)
    th = size * sc * 1.15
    pad = int(32 * sc)
    im = Image.new("RGBA", (int(tw + 2 * pad), int(th + 2 * pad)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([6, 6, im.width - 6, im.height - 6], radius=int(20 * sc), outline=col + (255,), width=max(2, int(10 * sc)))
    dd.text((im.width / 2, im.height / 2), word, font=fn, fill=col + (255,), anchor="mm")
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if a < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    pos = (int(cx - im.width / 2), int(cy - im.height / 2))
    f.img.paste(im.convert("RGB"), pos, im)
    f.gimg.paste(im.convert("RGB"), pos, im.getchannel("A").point(lambda v: int(v * 0.7)))
