"""Seeded film-grain tile (deterministic). Output: assets/tex/grain.png"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

out = Path(__file__).resolve().parent.parent / "assets/tex"
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026_10_16)
n = rng.normal(0, 1, (512, 512))
n = ndimage.gaussian_filter(n, 0.55, mode="wrap")  # soften to silver-halide clumps
n = (n - n.mean()) / n.std()
v = np.clip(128 + n * 64, 0, 255).astype(np.uint8)
Image.fromarray(v, "L").save(out / "grain.png", optimize=True)
