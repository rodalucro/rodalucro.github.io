"""Renders draped silk-satin images (procedural, no photos) for the landing page.

Usage: python3 tools/seta.py   -> writes img/seta-*.webp
Each image is a height field of soft folds shaded with a satin-like sheen.
"""
import numpy as np
from PIL import Image
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'img')

COLORS = {  # name: (base rgb, highlight rgb)
    'champagne': ((190, 152, 104), (255, 236, 200)),
    'avorio': ((222, 211, 190), (255, 252, 244)),
    'rosa-cipria': ((206, 150, 150), (255, 226, 222)),
    'grigio-perla': ((160, 160, 162), (246, 246, 248)),
    'verde-salvia': ((120, 140, 118), (226, 238, 220)),
    'blu-notte': ((40, 52, 84), (170, 190, 230)),
}


def height_field(w, h, seed, angle, folds, warp):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x /= w; y /= w
    # domain warp: low-frequency wobble so folds curve like real fabric
    wx = sum(rng.uniform(.02, .06) * np.sin(2 * np.pi * (rng.uniform(.4, 1.4) * x + rng.uniform(.4, 1.4) * y) + rng.uniform(0, 6)) for _ in range(4))
    wy = sum(rng.uniform(.02, .06) * np.sin(2 * np.pi * (rng.uniform(.4, 1.4) * x - rng.uniform(.4, 1.4) * y) + rng.uniform(0, 6)) for _ in range(4))
    x2, y2 = x + warp * wx, y + warp * wy
    hgt = np.zeros_like(x)
    for i in range(folds):
        a = angle + rng.normal(0, .22)
        u = np.cos(a) * x2 + np.sin(a) * y2
        v = -np.sin(a) * x2 + np.cos(a) * y2
        f = rng.uniform(.7, 2.6)
        amp = rng.uniform(.4, 1.0) / (1 + .25 * i)
        # fold amplitude fades along its length so folds start and end softly
        env = .55 + .45 * np.sin(2 * np.pi * (rng.uniform(.3, .9) * v) + rng.uniform(0, 6))
        hgt += amp * env * (1 - np.abs(np.cos(np.pi * f * u + rng.uniform(0, 6)))) ** 2.2
    return hgt


def blur(a, r):
    """Approximate gaussian blur in float (three box passes per axis), so the folds stay free of banding."""
    for axis in (0, 1):
        for _ in range(3):
            c = np.cumsum(np.pad(a, [(r + 1, r) if i == axis else (0, 0) for i in range(2)], mode='edge'), axis=axis)
            a = (np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis) - np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)) / (2 * r + 1)
    return a


def render(name, base, hi, w=1400, h=1750, seed=1, angle=.9, folds=6, warp=1.1, light=(-.45, -.6, .66)):
    hgt = height_field(w, h, seed, angle, folds, warp)
    hgt = blur(hgt / hgt.max(), 5)
    gy, gx = np.gradient(hgt * 38)
    n = np.dstack([-gx, -gy, np.ones_like(hgt)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    V = np.array([0, 0, 1], np.float32)
    H = (L + V); H /= np.linalg.norm(H)
    diff = np.clip(n @ L, 0, 1)
    spec = np.clip(n @ H, 0, 1)
    sheen = spec ** 40 * 1.1 + spec ** 8 * .45          # tight satin highlight + broad glow
    ao = .55 + .45 * (hgt / hgt.max()) ** .7            # fold valleys darker
    yy = np.linspace(0, 1, h)[:, None]; xx = np.linspace(0, 1, w)[None, :]
    vign = 1 - .32 * ((xx - .42) ** 2 + (yy - .38) ** 2)  # soft warm window light from top-left
    base = np.array(base, np.float32) / 255; hi = np.array(hi, np.float32) / 255
    shade = (.28 + .72 * diff) * ao * vign
    img = base[None, None] * shade[..., None] + (hi[None, None] - base[None, None] * .3) * sheen[..., None] * vign[..., None]
    img = np.clip(img, 0, 1) ** .95
    grain = np.random.default_rng(seed + 99).normal(0, .006, img.shape[:2])[..., None]
    img = np.clip(img + grain, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8))
    im.save(os.path.join(OUT, f'seta-{name}.webp'), quality=82)
    return im


if __name__ == '__main__':
    for i, (name, (b, hi)) in enumerate(COLORS.items()):
        render(name, b, hi, seed=10 + i)
    # extra shots for the detail sections (champagne, different drapes / crops)
    b, hi = COLORS['champagne']
    render('macro', b, hi, w=1200, h=1200, seed=42, angle=.3, folds=6, warp=1.2)
    render('onde', b, hi, w=1600, h=1000, seed=7, angle=1.4, folds=12, warp=1.6)
    b, hi = COLORS['avorio']
    render('luce', b, hi, w=1200, h=1200, seed=5, angle=2.2, folds=7, warp=1.8, light=(.5, -.5, .7))
    b, hi = COLORS['blu-notte']
    render('notte', b, hi, w=1800, h=900, seed=3, angle=.6, folds=10, warp=1.4, light=(.6, -.3, .5))
    print('ok')
