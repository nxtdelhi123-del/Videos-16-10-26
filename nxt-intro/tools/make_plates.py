"""Build the graded, frame-sized background plates for the eight game cards.

Input : assets/games/hd/*.png  (4x Real-ESRGAN upscales; FC 26 is native-res)
Output: assets/games/plates/916/NN.jpg  (1080x1920)
        assets/games/plates/45/NN.jpg   (1080x1350)

Each plate is cropped to keep the subject clear of the card's type zone, then put
through one shared grade so eight different key arts read as one campaign:
black point down to --ink, gentle S-curve, a touch of desaturation, neutral shadows,
and a final unsharp pass after the Lanczos resample.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
HD = ROOT / "assets/games/hd"
INK = np.array([10, 10, 11], np.float64) / 255

# name: {fmt: (sx0, sx1, sy0, dy0[, feather])} — source crop (normalized), dest top px, top fade px
CARDS = {
    "01-fc26":          {"916": (0.13, 0.87, 0.172, 200, 70), "45": (0.13, 0.87, 0.172, 50, 50)},
    "02-fc27":          {"916": (0.32, 0.75, 0.325, 250, 90), "45": (0.28, 0.78, 0.325, 90, 70)},
    "03-valorant":      {"916": (0.15, 0.90, 0.00, 120),  "45": (0.10, 0.95, 0.05, 0)},
    "04-cs2":           {"916": (0.47, 0.92, 0.00, 0),    "45": (0.40, 0.95, 0.00, 0)},
    "05-rocket-league": {"916": (0.40, 0.85, 0.00, 0),    "45": (0.33, 0.88, 0.00, 0)},
    "06-bgmi":          {"916": (0.18, 0.68, 0.00, 200),  "45": (0.12, 0.76, 0.00, 0)},
    "07-cod":           {"916": (0.26, 0.74, 0.00, 120),  "45": (0.20, 0.80, 0.00, 0)},
    "08-tekken8":       {"916": (0.53, 0.98, 0.00, 0),    "45": (0.45, 1.00, 0.00, 0)},
}
SIZES = {"916": (1080, 1920), "45": (1080, 1350)}
LIFT = {"02-fc27": 0.74, "07-cod": 0.85}  # per-art gamma: open up art that is lit very low


def grade(rgb, gamma=1.0):
    x = (rgb.astype(np.float64) / 255) ** gamma
    x = np.clip((x - 0.018) / 0.982, 0, 1)  # black point
    lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    x = lum + (x - lum) * 0.94  # restrain saturation
    s = x * x * (3 - 2 * x)
    x = x + (s - x) * 0.22  # S-curve
    lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    shadow = np.clip(1 - lum / 0.12, 0, 1) ** 2
    x = x + (INK - x) * shadow * 0.2  # shadows sit on --ink
    return (np.clip(x, 0, 1) * 255).round().astype(np.uint8)


def plate(name, fmt):
    W, H = SIZES[fmt]
    sx0, sx1, sy0, dy0, *rest = CARDS[name][fmt]
    feather = rest[0] if rest else 200
    src = Image.open(HD / f"{name}.png").convert("RGB")
    sw, sh = src.size
    x0, x1 = sx0 * sw, sx1 * sw
    scale = W / (x1 - x0)
    y0 = sy0 * sh
    rows = (H - dy0) / scale
    y1 = min(sh, y0 + rows)
    crop = src.crop((round(x0), round(y0), round(x1), round(y1)))
    ph = round((y1 - y0) * scale)
    crop = crop.resize((W, ph), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
    img = grade(np.asarray(crop), LIFT.get(name, 1.0)).astype(np.float64)
    # feather the plate's top (and bottom, if it ends early) into the ink field
    a = np.ones(ph)
    if dy0 > 0:
        f = min(feather, ph)
        a[:f] = np.linspace(0, 1, f) ** 1.6
    if dy0 + ph < H:
        f = min(240, ph)
        a[-f:] = np.minimum(a[-f:], np.linspace(1, 0, f) ** 1.6)
    canvas = np.tile(INK * 255, (H, W, 1))
    region = canvas[dy0 : dy0 + ph]
    canvas[dy0 : dy0 + ph] = region + (img[: region.shape[0]] - region) * a[: region.shape[0], None, None]
    out = ROOT / f"assets/games/plates/{fmt}"
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(canvas.round().clip(0, 255).astype(np.uint8)).save(out / f"{name[:2]}.jpg", quality=93, subsampling=0)


if __name__ == "__main__":
    for n in CARDS:
        for fmt in SIZES:
            plate(n, fmt)
        print("plate", n)
