"""Cut the anchors' raw phone clips into per-line files: assets/footage/<id>.mp4.

Usage: python3 tools/prep_footage.py cuts.json
cuts.json: {"A1": {"src": "raw/aditya_01.mp4", "in": 1.84, "out": 3.9}, ...}

Each cut is scaled to cover 1080x1920 (centre crop), 30 fps, with the voice cleaned
(high-pass, light denoise) and levelled to -16 LUFS so home and airport audio match.
A little room is kept on both sides (0.08 s) so words aren't clipped.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAD = 0.08

cuts = json.loads(Path(sys.argv[1]).read_text())
for lid, c in cuts.items():
    src = Path(c["src"])
    t_in = max(0.0, c["in"] - PAD)
    dur = c["out"] + PAD - t_in
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
    af = "highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000"
    out = ROOT / "assets/footage" / f"{lid}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_in:.3f}", "-i", str(src), "-t", f"{dur:.3f}",
                    "-vf", vf, "-af", af, "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ac", "2", str(out)], check=True)
    print(f"{lid}: {src.name} {c['in']:.2f}-{c['out']:.2f}s -> {out.name} ({dur:.2f}s)")
