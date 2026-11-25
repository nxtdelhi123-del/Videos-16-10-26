"""Stand-in clips (assets/footage/<id>.mp4) so the reel previews before the real footage lands.
Real clips replace these files one for one (tools/prep_footage.py)."""
import subprocess
from pathlib import Path

from timeline import LINES, NAMES, TAIL

ROOT = Path(__file__).resolve().parent.parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SAY = {
    "A1": "Delhi, ek zaroori announcement.", "V1": "Aapka sofa career... aaj se khatam.",
    "A2": "Kyunki Delhi mein aa gaya hai...", "V2": "N-X-T.", "A3": "FC.", "V3": "Valorant.",
    "A4": "Counter-Strike 2.", "V4": "Rocket League.", "A5": "BGMI.", "V5": "Call of Duty.",
    "A6": "Tekken 8.", "V6": "Ek hi arena.", "A7": "Tournaments.", "V7": "Leagues.",
    "A8": "Aur poori community.", "V8": "Toh mummy ko bata do...", "A9": "...aaj dinner pe late aaoge.",
    "V9": "Every game.", "A10": "Your esports.", "A11": "N-X-T. The next arena is here.",
    "V10": "N-X-T. The next arena is here.",
}


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


for lid, who, _s, dur, _m, _lay, _c in LINES:
    d = max(dur, TAIL.get(lid, 0)) + 0.2
    bg = "0x23252b" if who == "aditya" else "0x2b2326"
    name = NAMES[who][0]
    vf = (
        f"drawbox=x=340:y=420:w=400:h=520:color=0x3a3d45:t=fill,"
        f"drawtext=fontfile={FONT}:text='{esc(name)}':fontcolor=0xf4f5f6:fontsize=64:x=(w-tw)/2:y=1000,"
        f"drawtext=fontfile={FONT}:text='{lid}  (placeholder)':fontcolor=0xe1060f:fontsize=40:x=(w-tw)/2:y=1090,"
        f"drawtext=fontfile={FONT}:text='{esc(SAY[lid])}':fontcolor=0xc9cdd2:fontsize=40:x=(w-tw)/2:y=1160"
    )
    out = ROOT / "assets/footage" / f"{lid}.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={bg}:s=1080x1920:r=30:d={d}",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(d), "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out)], check=True)
print("placeholders written")
