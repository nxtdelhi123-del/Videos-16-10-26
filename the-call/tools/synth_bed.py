"""30.4 s music bed for "The Call", arranged to the reel's sections.

Reuses the instruments from nxt-intro/tools/synth_audio.py (same 150 BPM phonk kit as the
brand intro), so the reel and the intro sound like one family. Deterministic: seeded noise
and oscillators only, no samples.

Sections (seconds):
  0.0–5.2   news open: low pad, clock-tick hats, riser into the drop
  5.2–20.8  drop + groove (roll call, pitch)
  20.8–24.8 dip under the "mummy" joke; record-scratch stop at 22.8
  24.8–27.2 groove back, riser
  27.2      final hit, ring out to 30.4
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "nxt-intro" / "tools"))
import synth_audio as S  # noqa: E402

SR = S.SR
LEN = 30.4
STEP = S.STEP  # 0.1 s
BAR = 16 * STEP  # 1.6 s

FM = [174.61, 207.65, 261.63]  # F minor
DB = [138.59, 174.61, 207.65]
EB = [155.56, 196.0, 233.08]
NOTES = {"F": 698.46, "Ab": 830.61, "C": 1046.5, "Bb": 932.33, "G": 783.99, "Eb": 622.25}
PHRASE = [(0, "F"), (3, "F"), (6, "Ab"), (8, "G"), (10, "F"), (11, "Eb"), (14, "C"),
          (16, "F"), (19, "F"), (22, "C"), (24, "Bb"), (26, "Ab"), (27, "G"), (30, "Eb")]


def scratch(dur=0.45):
    t = S.t_axis(dur)
    f = 900 * np.exp(-t / 0.09) + 60
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.6 + S.bp(S.rng.normal(0, 1, t.size), 300, 3000) * 0.5
    env = np.exp(-t / 0.18) * (1 - np.exp(-t / 0.002))
    return x * env


def make():
    n = int(LEN * SR)
    drums = np.zeros((2, n))
    bass = np.zeros((2, n))
    mel = np.zeros(n)
    pads = np.zeros((2, n))
    duck = np.ones(n)

    def kick_at(at, note=S.F1, dur=0.75, g=1.0):
        k = S.kick808(dur, note)
        S.place(bass, np.stack([k, k]), at, g)
        i = int(at * SR)
        m = min(int(0.3 * SR), n - i)
        if m > 0:
            duck[i:i + m] = np.minimum(duck[i:i + m], 1 - 0.65 * np.exp(-np.arange(m) / (0.09 * SR)))

    def pad_at(at, fr, dur, g=0.16, cut=1100):
        p = S.pad(fr, dur, cut)
        S.place(pads, np.stack([p, np.roll(p, 240)]), at, g)

    def groove(t0, t1):
        b = 0
        while True:
            b0 = t0 + b * BAR
            if b0 >= t1:
                break
            for s, nn in zip((0, 7, 10), (S.F1, S.F1, S.F1 * 2 ** (3 / 12))):
                at = b0 + s * STEP
                if at < t1:
                    kick_at(at, nn, 0.7 if s else 0.85, 0.95)
            at = b0 + 8 * STEP
            if at < t1:
                c = S.clap()
                S.place(drums, np.stack([c, c]), at, 0.55)
            for s in range(16):
                at = b0 + s * STEP
                if at >= t1:
                    break
                h = S.hat()
                vel = 0.75 + 0.25 * S.rng.uniform()
                S.place(drums, np.stack([h * (0.85 if s % 4 else 1.0), h]), at,
                        0.2 * vel * (1.0 if s % 2 == 0 else 0.6))
                if s in (13, 15) and b % 2 == 1:
                    S.place(drums, np.stack([h, h * 0.8]), at + STEP / 2, 0.12)
            if b % 2 == 1 and b0 + 14 * STEP < t1:
                oh = S.hat(open_=True)
                S.place(drums, np.stack([oh, oh * 0.9]), b0 + 14 * STEP, 0.16)
            b += 1
        k = 0
        while True:
            p0 = t0 + k * 2 * BAR
            if p0 >= t1:
                break
            for s, nn in PHRASE:
                at = p0 + s * STEP
                if at < t1:
                    S.place(mel, S.cowbell(NOTES[nn]), at, 0.5)
                    S.place(mel, S.cowbell(NOTES[nn] * 2), at, 0.08)
            k += 1
        chords = [FM, DB, EB, FM]
        c = 0
        at = t0
        while at < t1:
            pad_at(at, chords[c % 4], min(BAR, t1 - at) + 0.3)
            at += BAR
            c += 1

    # --- news open 0.0–5.2
    kick_at(0.0, S.F1, 1.4, 0.9)
    pad_at(0.0, [87.31] + FM, 5.2, 0.13, 700)
    for i in range(13):  # clock ticks on the beat
        h = S.hat(0.03)
        S.place(drums, np.stack([h, h * 0.9]), i * 0.4, 0.13)
    r = S.riser(1.2)
    S.place(drums, np.stack([r, np.roll(r, 120)]), 4.0, 0.2)

    # --- drop 5.2
    kick_at(5.2, S.F1, 1.2, 1.1)
    cr = S.crash(2.0)
    S.place(drums, cr, 5.2, 0.3)
    groove(5.2, 20.8)

    # --- dip 20.8–24.8
    pad_at(20.8, FM, 2.1, 0.12, 500)
    for i in range(5):
        h = S.hat(0.03)
        S.place(drums, np.stack([h, h]), 20.8 + i * 0.4, 0.07)
    sc = scratch()
    S.place(drums, np.stack([sc, sc * 0.95]), 22.8, 0.45)
    pad_at(23.3, DB, 1.5, 0.08, 450)

    # --- back 24.8–27.2, riser into the hit
    groove(24.8, 27.2)
    r = S.riser(1.2)
    S.place(drums, np.stack([r, np.roll(r, 120)]), 26.0, 0.24)

    # --- final hit 27.2 → ring out
    kick_at(27.2, S.F1, 2.4, 1.15)
    S.place(drums, S.crash(2.6), 27.2, 0.32)
    c = S.clap()
    S.place(drums, np.stack([c, c]), 27.2, 0.5)
    pad_at(27.2, [87.31, 174.61, 207.65, 261.63, 349.23], 3.2, 0.2, 1600)

    mel_st = np.stack([mel, np.roll(mel, int(0.0125 * SR))])
    space = S.convolve_st(mel * 0.35 + pads.mean(axis=0) * 0.2, S.reverb_ir(1.6, 0.45, 7))
    mix = 1.0 * bass + 0.9 * drums + 0.55 * mel_st + pads * duck + 0.5 * space
    mix = S.hp(mix, 28)
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)
    fade = np.clip((LEN - S.t_axis(LEN)) / 0.6, 0, 1)
    return mix / np.abs(mix).max() * 0.78 * fade


if __name__ == "__main__":
    S.write_mp3(make(), HERE.parent / "assets/music/call-bed.mp3")
    print("wrote assets/music/call-bed.mp3", file=sys.stderr)
