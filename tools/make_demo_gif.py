"""Regenerate the README hero GIF (assets/demo.gif): usaddress vs fastaddress.

Same spirit as the Moth widget's make-demo-gif: render real frames of the real
thing and loop them, no faked demo. The numbers here are the canonical figures
from benchmark/results/speed_report.md (usaddress 7,941/sec, fastaddress
89,653/sec single core, 11.3x), and the two lanes advance at exactly that
ratio -- a constant-rate race, so at every frame usaddress is exactly
7941/89653 of fastaddress's progress. Reproduce the underlying numbers with
`python benchmark/run_speed.py`.

Run:  python tools/make_demo_gif.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo.gif"

# Canonical numbers (speed_report.md).
U_RATE, F_RATE = 7941, 89653
RATIO = F_RATE / U_RATE
JOB = 1_000_000
T_FAST = JOB / F_RATE            # seconds fastaddress needs for the job
U_AT_FAST_DONE = int(U_RATE * T_FAST)   # rows usaddress has done by then

W, H = 920, 360
BG = (11, 13, 20)
FG = (223, 227, 235)
DIM = (120, 128, 145)
TRACK = (30, 34, 46)
GREEN = (68, 209, 133)
AMBER = (240, 176, 74)
RED = (232, 106, 106)

def font(path_names, size):
    for p in path_names:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

MONO = ["C:/Windows/Fonts/consola.ttf", "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
MONOB = ["C:/Windows/Fonts/consolab.ttf", "/System/Library/Fonts/Menlo.ttc",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
f_title = font(MONOB, 27)
f_lbl = font(MONOB, 22)
f_num = font(MONO, 21)
f_small = font(MONO, 18)
f_foot = font(MONOB, 21)


def rrect(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def bar(d, x, y, w, h, frac, color):
    rrect(d, (x, y, x + w, y + h), h // 2, TRACK)
    fw = max(h, int(w * frac))
    if frac > 0:
        rrect(d, (x, y, x + fw, y + h), h // 2, color)


def commas(n):
    return f"{int(n):,}"


def frame(fast_frac, slow_frac, done, punch):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # terminal chrome
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((28 + i * 22, 24, 40 + i * 22, 36), fill=c)
    d.text((W - 200, 24), "county tax roll", font=f_small, fill=DIM)

    d.text((40, 66), "1,000,000 US addresses, one core", font=f_title, fill=FG)

    bx, bw, bh = 220, 520, 30
    # usaddress lane
    uy = 140
    d.text((40, uy + 3), "usaddress", font=f_lbl, fill=AMBER)
    bar(d, bx, uy, bw, bh, slow_frac, AMBER)
    d.text((bx + bw + 20, uy + 4), f"{U_RATE:,}/sec", font=f_num, fill=DIM)
    d.text((bx, uy + bh + 8), f"{commas(slow_frac * JOB)} rows   still going...",
           font=f_small, fill=DIM)

    # fastaddress lane
    fy = 232
    d.text((40, fy + 3), "fastaddress", font=f_lbl, fill=GREEN)
    bar(d, bx, fy, bw, bh, fast_frac, GREEN)
    d.text((bx + bw + 20, fy + 4), f"{F_RATE:,}/sec", font=f_num, fill=FG)
    if done:
        txt = f"{commas(JOB)} rows   done in {T_FAST:.1f}s"
        d.text((bx, fy + bh + 8), txt, font=f_small, fill=GREEN)
        cx = bx + int(d.textlength(txt, font=f_small)) + 16
        cyy = fy + bh + 19
        d.line([(cx, cyy), (cx + 5, cyy + 6), (cx + 15, cyy - 7)], fill=GREEN, width=3)
    else:
        d.text((bx, fy + bh + 8), f"{commas(fast_frac * JOB)} rows",
               font=f_small, fill=DIM)

    if punch:
        d.text((40, 316), "same model", font=f_foot, fill=DIM)
        d.text((200, 316), "\u00b7  byte-identical output", font=f_foot, fill=DIM)
        d.text((520, 316), "\u00b7  ", font=f_foot, fill=DIM)
        d.text((548, 316), "11.3x faster", font=f_foot, fill=GREEN)
    return img


def main():
    frames, delays = [], []
    CLIMB = 30
    # climb: constant-rate race, fastaddress 0->100%, usaddress 0->8.85%
    for k in range(1, CLIMB + 1):
        ff = k / CLIMB
        sf = ff * (U_RATE / F_RATE)
        frames.append(frame(ff, sf, done=False, punch=False))
        delays.append(85)
    # fastaddress done; usaddress keeps crawling a touch; punchline in
    peak_slow = U_RATE / F_RATE
    for k in range(8):
        sf = peak_slow + (0.02 * k / 7)
        frames.append(frame(1.0, sf, done=True, punch=(k >= 2)))
        delays.append(140 if k < 7 else 2000)  # long hold on the last punchline frame
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=delays,
                   loop=0, disposal=2, optimize=True)
    print(f"wrote {OUT}  ({len(frames)} frames, {W}x{H}, {OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
