# NXT — "The Call" (intro reel)

30.4 s, 1080×1920, 30 fps. Two sports anchors (Aditya Soni, Vinol Arun) announce N-X-T in short lines; the edit does the rest. Script: the "NXT Intro Reel: Viral Concept and Anchor Scripts" doc (lines A1–A11, V1–V10).

| Time | Section |
| --- | --- |
| 0.0–5.2 | News open: LIVE bug, name straps, BREAKING strap, ticker (A1, V1, A2) |
| 5.2–6.4 | "N-X-T" letter slams (V2), eagle slam from the brand intro |
| 6.4–14.8 | Roll call: 7 game cards on the beat, speaker in a picture-in-picture box |
| 14.8–20.8 | Pitch: ONE ARENA / TOURNAMENTS / LEAGUES / COMMUNITY |
| 20.8–24.8 | The joke: "Mummy" chat pop-up, seen + record scratch (V8, A9) |
| 24.8–27.2 | EVERY GAME. / YOUR ESPORTS. |
| 27.2–28.4 | Split screen, unison "N-X-T. The next arena is here." |
| 28.4–30.4 | Logo end card (from ../nxt-intro), FOLLOW @NXT._ESPORTS |

## Files

- `tools/timeline.py` — every line's slot, trim and caption; the one place to retime.
- `tools/build.py` — writes `index.html` from the timeline (`python3 tools/build.py`). Styles in `tools/style.css`.
- `tools/prep_footage.py cuts.json` — cuts raw phone clips into `assets/footage/<id>.mp4` (crop to 9:16, clean and level voice).
- `tools/make_placeholders.py` — stand-in clips used until real footage is in.
- `tools/synth_bed.py` — the 30 s music bed (same 150 BPM kit as the brand intro).
- `assets/footage/logo-end.mp4` — the brand intro's logo section (rendered from ../nxt-intro, 7.6–10 s).

## Commands

```bash
python3 tools/build.py
npx --yes hyperframes@0.8.164 check
npx --yes hyperframes@0.8.164 render -o renders/NXT_TheCall_30s_9x16.mp4
```
