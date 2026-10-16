"""4x AI upscale (Real-ESRGAN x4plus via ncnn, CPU) for the game key art.

usage: python3 -I tools/upscale.py MODEL_DIR IN.jpg OUT.png
Tiles the image with an overlap so memory stays flat and seams never show.
"""
import sys

import ncnn
import numpy as np
from PIL import Image

model_dir, src, dst = sys.argv[1:4]
TILE, PAD, S = 160, 12, 4

net = ncnn.Net()
net.opt.use_vulkan_compute = False
net.opt.num_threads = 4
net.load_param(f"{model_dir}/realesrgan-x4plus.param")
net.load_model(f"{model_dir}/realesrgan-x4plus.bin")

img = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
h, w, _ = img.shape
out = np.zeros((h * S, w * S, 3), np.float32)
padded = np.pad(img, ((PAD, PAD), (PAD, PAD), (0, 0)), mode="reflect")

for y in range(0, h, TILE):
    for x in range(0, w, TILE):
        th, tw = min(TILE, h - y), min(TILE, w - x)
        tile = padded[y : y + th + 2 * PAD, x : x + tw + 2 * PAD]
        chw = np.ascontiguousarray(tile.transpose(2, 0, 1))
        ex = net.create_extractor()
        ex.input("data", ncnn.Mat(chw))
        _, o = ex.extract("output")
        o = np.array(o).transpose(1, 2, 0)
        out[y * S : (y + th) * S, x * S : (x + tw) * S] = o[PAD * S : (PAD + th) * S, PAD * S : (PAD + tw) * S]
    print(f"  row {y // TILE + 1}/{(h + TILE - 1) // TILE}", file=sys.stderr, flush=True)

Image.fromarray((np.clip(out, 0, 1) * 255).round().astype(np.uint8)).save(dst)
print(dst, out.shape[1], "x", out.shape[0])
