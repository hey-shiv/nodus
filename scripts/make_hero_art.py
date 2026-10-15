"""Generate the home page hero: an original dithered scene (stone gateway, clouds, ground).

Run:  .venv/bin/python scripts/make_hero_art.py
Procedural and seeded: value noise for clouds, stone and ground, then Floyd-Steinberg dithering
per layer, coloured with the site palette. The gateway's opening is left as plain paper so the
headline panel can sit in it.
"""
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 800, 430          # rendered at half size, upscaled 2x (chunky dither grain)
rng = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent.parent / "web" / "public" / "art" / "hero.png"

PAPER = (255, 251, 242)
PERI = (166, 184, 250)
PERI_LIGHT = (214, 224, 255)
INK = (35, 35, 35)
STONE_LIGHT = (232, 226, 210)
EARTH = [(120, 86, 64), (168, 128, 98), (205, 170, 130), (92, 98, 62), (60, 54, 44)]


def value_noise(h, w, scale, octaves=5):
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        grid = rng.random((h // s + 2, w // s + 2))
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((w + 2 * s, h + 2 * s), Image.BICUBIC)
        out += amp * (np.asarray(img, dtype=float)[:h, :w] / 255)
        total += amp
        amp *= 0.5
    return out / total


def dither(gray):
    """Floyd-Steinberg to 1 bit, as a boolean mask (True = ink)."""
    img = Image.fromarray(np.clip(gray * 255, 0, 255).astype(np.uint8)).convert("1")
    return ~np.asarray(img, dtype=bool)


canvas = np.zeros((H, W, 3), dtype=np.uint8)
canvas[:] = PAPER
y = np.linspace(0, 1, H)[:, None]
x = np.linspace(0, 1, W)[None, :]

# clouds: a billowing bank right across the sky, densest just above the horizon
clouds = value_noise(H, W, 120)
billow = np.clip((clouds - 0.30) * 2.6, 0, 1)
band = np.exp(-((y - 0.50) / 0.17) ** 2)
bank = np.clip(billow * band * 1.35, 0, 1)
light = dither(1 - bank * 0.8)
deep = dither(1 - np.clip(bank - 0.30, 0, 1) * 1.7)
canvas[light] = PERI_LIGHT
canvas[deep] = PERI

# ground: rolling earth from about 64% down, with a layered palette
horizon = 0.66 + 0.04 * np.sin(x * 6.0 + 1.0) + 0.05 * (value_noise(H, W, 90)[0:1, :] - 0.5)
ground = y > horizon
tex = value_noise(H, W, 40)
depth = np.clip((y - horizon) / 0.34, 0, 1)
canvas[ground] = EARTH[2]
for i, colour in enumerate([EARTH[1], EARTH[0], EARTH[3], EARTH[4]]):
    layer = dither(np.clip(1.15 - tex * 0.8 - depth * (0.35 + 0.18 * i) + i * 0.05, 0, 1))
    canvas[ground & layer] = colour

# the gateway: ashlar masonry (block courses with offset joints), opening left as paper
gx0, gx1, gy0, gy1 = 260, 540, 50, 350              # outer box (half-size coordinates)
ox0, ox1, oy0 = 320, 480, 122                       # opening
gate = np.zeros((H, W), dtype=bool)
gate[gy0:gy1, gx0:gx1] = True
gate[oy0:gy1, ox0:ox1] = False
yy, xx = np.mgrid[0:H, 0:W]
course = (yy - gy0) // 14
offset = (course % 2) * 11
block_id = course * 1000 + (xx - gx0 + offset) // 22
block_tone = np.random.default_rng(3).random(block_id.max() + 1)[block_id]
grain = value_noise(H, W, 10, 3)
shade = np.clip(0.30 + block_tone * 0.45 + (grain - 0.5) * 0.55, 0, 1)
shade[:, gx0:ox0] -= 0.18                          # left pillar in shadow
shade[gy0:gy0 + 22, :] += 0.15                     # lit cornice
joints = ((yy - gy0) % 14 == 0) | ((xx - gx0 + offset) % 22 == 0)
inked = dither(1 - np.clip(shade, 0, 1))
canvas[gate] = STONE_LIGHT
canvas[gate & inked] = INK
canvas[gate & joints] = INK
canvas[gy0:gy0 + 3, gx0 - 8:gx1 + 8] = INK         # cornice line
canvas[gy0 + 20:gy0 + 22, gx0 - 4:gx1 + 4] = INK
canvas[oy0 - 7:oy0, ox0 - 7:ox1 + 7] = INK          # frame around the opening
canvas[oy0:gy1, ox0 - 7:ox0] = INK
canvas[oy0:gy1, ox1:ox1 + 7] = INK
canvas[oy0:gy1, ox0:ox1] = PAPER
for sy, pad in [(350, 0), (359, 15), (368, 30)]:   # steps
    canvas[sy:sy + 9, gx0 - pad:gx1 + pad] = STONE_LIGHT
    canvas[sy:sy + 1, gx0 - pad:gx1 + pad] = INK
    canvas[sy + 8:sy + 9, gx0 - pad:gx1 + pad] = INK

Image.fromarray(canvas).resize((W * 2, H * 2), Image.NEAREST).save(OUT, optimize=True)
print(f"wrote {OUT.relative_to(OUT.parents[3])} ({OUT.stat().st_size // 1024} KB), "
      f"opening at x {ox0 * 2}-{ox1 * 2}, y {oy0 * 2}-{gy1 * 2} of {W * 2}x{H * 2}")
