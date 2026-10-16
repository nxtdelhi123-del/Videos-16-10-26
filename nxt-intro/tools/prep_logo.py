"""Prepare the official NXT logo for animation.

Input:  assets/logo/nxt-logo.jpg  (official file, 1600x959, off-white surface)
Output: assets/logo/nxt-logo.png       full logo, transparent bg, 2x
        assets/logo/nxt-eagle.png      eagle head only, 2x
        assets/logo/nxt-wordmark.png   "NXT" only, 2x
        assets/logo/layout.json        crop offsets + eye / X-slash positions

The logo is never redrawn: pixels come straight from the official file.
Near-white is keyed out with color-to-alpha against the paper surface, so
soft drop shadows and the chrome shading survive as partial alpha and the
logo composites back onto --paper identically to the original.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/logo/nxt-logo.jpg"
OUT = ROOT / "assets/logo"
SCALE = 2
BG = 254.0  # measured surface value at the corners
NOISE = 0.014  # alpha floor: kills JPEG noise in the empty surface

img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
h, w, _ = img.shape

# --- colour to alpha against the paper surface -------------------------------
a = np.clip((BG - img) / BG, 0, 1).max(axis=2)
a = np.clip((a - NOISE) / (1 - NOISE), 0, 1)
a = a * a * (3 - 2 * a) * 0.35 + a * 0.65  # gentle feather on the faint edge
safe = np.maximum(a, 1e-6)[..., None]
rgb = np.clip((img - BG * (1 - a[..., None])) / safe, 0, 255)
rgb[a == 0] = 0

# --- split eagle / wordmark ----------------------------------------------------
strong = a > 0.30
lab, n = ndimage.label(strong)
idx = np.arange(1, n + 1)
cy, cx = np.array(ndimage.center_of_mass(strong, lab, idx)).T
sizes = ndimage.sum(strong, lab, idx)
# wordmark = everything whose centroid sits in the lettering band
is_word = (cy > 655) & (cx > 420) & (cx < 1220)
word_seed = np.isin(lab, idx[is_word])
eagle_seed = np.isin(lab, idx[~is_word & (sizes > 20)])
d_word = ndimage.distance_transform_edt(~word_seed)
d_eagle = ndimage.distance_transform_edt(~eagle_seed)
word_px = d_word < d_eagle
# shadows fade out with distance from their own shape; beyond that it is surface
FALL0, FALL1 = 30.0, 70.0
keep = np.clip((FALL1 - np.minimum(d_word, d_eagle)) / (FALL1 - FALL0), 0, 1)
a = a * keep


def save(alpha, name):
    rgba = np.dstack([rgb, alpha * 255]).round().clip(0, 255).astype(np.uint8)
    ys, xs = np.where(alpha > 0.02)
    pad = 6
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    x1, y1 = min(xs.max() + pad, w), min(ys.max() + pad, h)
    im = Image.fromarray(rgba, "RGBA").crop((x0, y0, x1, y1))
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    im.save(OUT / name, optimize=True)
    return {"x": int(x0) * SCALE, "y": int(y0) * SCALE, "w": im.width, "h": im.height}


layout = {"source": {"w": w * SCALE, "h": h * SCALE}}
layout["logo"] = save(a, "nxt-logo.png")
layout["eagle"] = save(np.where(word_px, 0, a), "nxt-eagle.png")
layout["wordmark"] = save(np.where(word_px, a, 0), "nxt-wordmark.png")

# --- landmarks (in 2x source coordinates) -------------------------------------
r, g, b = img[..., 0], img[..., 1], img[..., 2]
red = (r > 150) & (g < 80) & (b < 80)
# eye: red pixels in the head, right of the brow line
eye = red & ~word_px
eye[:, :1080] = False
eye[:260, :] = False
eye[360:, :] = False
ey, ex = np.where(eye)
layout["eye"] = {"x": float(ex.mean()) * SCALE, "y": float(ey.mean()) * SCALE}
# X slash: red pixels in the wordmark; fit the stroke's axis
xs_ = red & word_px
xs_[:, :640] = False   # the N's red accent
xs_[:, 1010:] = False  # the T's red edge
sy, sx = np.where(xs_)
k, c = np.polyfit(sx, sy, 1)
x_lo, x_hi = float(sx.min()), float(sx.max())
layout["xslash"] = {
    "x0": x_lo * SCALE, "y0": (k * x_lo + c) * SCALE,
    "x1": x_hi * SCALE, "y1": (k * x_hi + c) * SCALE,
    "angle_deg": float(np.degrees(np.arctan(k))),
}
(OUT / "layout.json").write_text(json.dumps(layout, indent=2))
json.dump(layout, sys.stdout, indent=2)

# --- X-slash light mask: the logo's own red stroke, used to confine the sweep --
m = (xs_ & (a > 0.5)).astype(np.float64)
m = ndimage.gaussian_filter(m, 0.6)
wm = layout["wordmark"]
mask = Image.fromarray((np.dstack([np.full_like(m, 255)] * 3 + [m * 255])).clip(0, 255).astype(np.uint8), "RGBA")
mask = mask.resize((w * SCALE, h * SCALE), Image.LANCZOS).crop((wm["x"], wm["y"], wm["x"] + wm["w"], wm["y"] + wm["h"]))
mask.save(OUT / "nxt-xslash-mask.png", optimize=True)
