#!/usr/bin/env bash
# One command once assets/sfx/falcon-screech.mp3 and assets/music/bed.mp3 exist:
# wires both into the mix, renders 9:16 + 4:5, and reports loudness / true peak.
set -euo pipefail
cd "$(dirname "$0")/.."
for f in assets/sfx/falcon-screech.mp3 assets/music/bed.mp3; do [ -f "$f" ] || { echo "missing $f"; exit 1; }; done
FALCON_IN="${FALCON_IN:-0}"   # seconds into the file where the sharpest screech starts
BED_VOL="${BED_VOL:-0.42}"
FALCON_VOL="${FALCON_VOL:-0.5}"
python3 - "$FALCON_IN" "$BED_VOL" "$FALCON_VOL" <<'PY'
import sys, json, html
fin, vol, fvol = sys.argv[1], sys.argv[2], sys.argv[3]
g = float(vol)  # the volume lane overrides data-volume, so the bed level lives in the lane
lane = {"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": g}, {"t": 7.55, "v": g}, {"t": 7.5667, "v": 0},   # 4-frame tension gap
    {"t": 8.15, "v": 0}, {"t": 8.1667, "v": g * 0.5},                # back for the final hit, -6 dB under the falcon
    {"t": 9.6, "v": g * 0.5}, {"t": 10, "v": 0}]}]}                  # fade over the last 0.4 s
auto = html.escape(json.dumps(lane, separators=(",", ":")), quote=True)
bed = f'<audio id="music-bed" src="assets/music/bed.mp3" data-start="0" data-duration="10" data-track-index="29" data-volume="{vol}" data-automation="{auto}"></audio>'
falcon = f'<audio id="sfx-falcon" src="assets/sfx/falcon-screech.mp3" data-start="7.8" data-duration="1.5" data-media-start="{fin}" data-track-index="33" data-volume="{fvol}"></audio>'
p = "index.html"; s = open(p).read()
import re
s = re.sub(r'<!--AUDIO:BED-->|<audio id="music-bed"[^>]*></audio>', bed, s)
s = re.sub(r'<!--AUDIO:FALCON-->|<audio id="sfx-falcon"[^>]*></audio>', falcon, s)
open(p, "w").write(s)
PY
python3 -I tools/make_4x5.py
npx -y hyperframes@0.8.164 render -o out/NXT_Intro_10s_9x16.mp4 --quality delivery --skill motion-graphics
(cd variants/4x5 && npx -y hyperframes@0.8.164 render -o ../../out/NXT_Intro_10s_4x5.mp4 --skill motion-graphics)
for f in out/NXT_Intro_10s_9x16.mp4 out/NXT_Intro_10s_4x5.mp4; do
  echo "== $f"; ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
done
echo "Target: I ≈ -14 LUFS, peak ≤ -1 dBTP. Adjust BED_VOL and re-run if off."
