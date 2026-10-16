"""Synthesised stand-ins for the two assets that could not be downloaded.

  assets/music/bed.mp3          150 BPM phonk/trap bed, arranged to the film's cuts
  assets/sfx/falcon-screech.mp3 raptor scream ("kee-eeee-arr"), sharp onset at t=0

Everything is generated from seeded noise and oscillators: deterministic, no samples,
no third-party audio. Replace either file with a real recording at any time and re-run
tools/finalize.sh.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(16_10_2026)

BPM = 150
BEAT = 60 / BPM  # 0.4 s
STEP = BEAT / 4  # 16th = 0.1 s
LEN = 10.0


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def place(buf, clip, at, gain=1.0):
    i = int(round(at * SR))
    if i >= buf.shape[-1]:
        return
    n = min(clip.shape[-1], buf.shape[-1] - i)
    buf[..., i : i + n] += gain * clip[..., :n]


def reverb_ir(dur, decay, seed):
    r = np.random.default_rng(seed)
    t = t_axis(dur)
    ir = r.normal(0, 1, (2, t.size)) * np.exp(-t / decay)
    ir = lp(ir, 6000)
    return ir / np.sqrt((ir**2).sum(axis=1, keepdims=True))


def convolve_st(x_mono, ir):
    return np.stack([signal.fftconvolve(x_mono, ir[c])[: x_mono.size] for c in range(2)])


# ------------------------------------------------------------------ instruments
F1 = 43.65  # F1 — the 808 root (F minor)


def kick808(dur=0.9, note=F1, punch=1.0):
    t = t_axis(dur)
    f = note + (165 - note) * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t / (dur * 0.45)) * (1 - np.exp(-t / 0.0015))
    x = np.sin(ph) * env
    click = hp(rng.normal(0, 1, t.size), 2500) * np.exp(-t / 0.004) * 0.35 * punch
    x = np.tanh(2.2 * (x + click)) / np.tanh(2.2)  # harmonics so it reads on phone speakers
    return x


def clap(dur=0.35):
    t = t_axis(dur)
    n = rng.normal(0, 1, t.size)
    env = np.zeros_like(t)
    for k, o in enumerate((0.0, 0.009, 0.019, 0.03)):
        e = np.where(t >= o, np.exp(-(t - o) / (0.006 if k < 3 else 0.09)), 0)
        env = np.maximum(env, e)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.03) * 0.5
    x = bp(n, 900, 5200) * env + body
    return x / np.abs(x).max()


def hat(dur=0.06, open_=False):
    t = t_axis(0.35 if open_ else dur)
    n = rng.normal(0, 1, t.size)
    # metallic: bank of square partials + noise
    met = sum(signal.square(2 * np.pi * f * t) for f in (3150, 4020, 5330, 6780, 8190)) / 5
    x = hp(0.6 * n + 0.6 * met, 7200, 3) * np.exp(-t / (0.11 if open_ else 0.018))
    return x / np.abs(x).max()


def cowbell(f, dur=0.28):
    t = t_axis(dur)
    x = signal.square(2 * np.pi * f * t, 0.5) + signal.square(2 * np.pi * f * 1.4814 * t, 0.5)
    x = bp(x, f * 0.8, f * 3.2) * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.001))
    return x / np.abs(x).max()


def pad(freqs, dur, cutoff=900.0):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.11, 0.0, 0.13):
            ph0 = rng.uniform(0, 1)
            x += signal.sawtooth(2 * np.pi * (f * 2 ** (det / 12)) * t + ph0 * 2 * np.pi)
    x = lp(x, cutoff, 4)
    att = np.clip(t / 0.25, 0, 1)
    rel = np.clip((dur - t) / 0.3, 0, 1)
    return x * att * rel / np.abs(x).max()


def crash(dur=3.0):
    t = t_axis(dur)
    n = rng.normal(0, 1, (2, t.size))
    met = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3510, 4680, 5870, 7210, 9050, 11030)) / 6
    x = hp(n + 0.5 * met, 4200, 2) * np.exp(-t / 0.9)
    return x / np.abs(x).max()


def riser(dur):
    t = t_axis(dur)
    n = rng.normal(0, 1, t.size)
    out = np.zeros_like(t)
    seg = int(0.05 * SR)
    for i in range(0, t.size, seg):
        fc = 400 * (12000 / 400) ** (i / t.size)
        out[i : i + seg] = bp(n[i : i + seg + 2000], fc * 0.7, min(fc * 1.4, 20000))[: min(seg, t.size - i)]
    return out * (t / dur) ** 2.2


# ------------------------------------------------------------------ music bed
def make_bed():
    L = np.zeros((2, int(LEN * SR)))
    drums = np.zeros_like(L)
    bass = np.zeros_like(L)
    mel = np.zeros(int(LEN * SR))
    pads = np.zeros_like(L)
    duck = np.ones(int(LEN * SR))

    def kick_at(at, note=F1, dur=0.75, g=1.0):
        k = kick808(dur, note)
        place(bass, np.stack([k, k]), at, g)
        # sidechain the pad under each kick
        i = int(at * SR)
        n = min(int(0.3 * SR), duck.size - i)
        if n > 0:
            duck[i : i + n] = np.minimum(duck[i : i + n], 1 - 0.65 * np.exp(-np.arange(n) / (0.09 * SR)))

    # --- hook 0.0–1.2: one heavy 808 on the rip, hats tick in
    kick_at(0.0, F1, 1.1, 1.0)
    for s in range(4, 12, 2):
        h = hat()
        place(drums, np.stack([h * 0.8, h]), s * STEP, 0.22)

    # --- groove 1.2–6.6 (cards). 16-step bar = 1.6 s.
    notes = {"F": 698.46, "Ab": 830.61, "C": 1046.5, "Bb": 932.33, "G": 783.99, "Eb": 622.25, "Db": 554.37}
    # phonk cowbell figure, two-bar phrase (step, note)
    phrase = [(0, "F"), (3, "F"), (6, "Ab"), (8, "G"), (10, "F"), (11, "Eb"), (14, "C"),
              (16, "F"), (19, "F"), (22, "C"), (24, "Bb"), (26, "Ab"), (27, "G"), (30, "Eb")]
    kick_steps = [0, 7, 10]  # trap 808 pattern per bar
    kick_notes = [F1, F1, F1 * 2 ** (3 / 12)]  # F, F, Ab glide feel
    g0 = 1.2
    bar = 16 * STEP
    for b in range(4):  # 1.2 → 7.6 (truncated at 6.6)
        b0 = g0 + b * bar
        for s, nn in zip(kick_steps, kick_notes):
            at = b0 + s * STEP
            if at < 6.6:
                kick_at(at, nn, 0.7 if s else 0.85, 0.95)
        at = b0 + 8 * STEP  # half-time snare on 3
        if at < 6.6:
            c = clap()
            place(drums, np.stack([c, c]), at, 0.55)
        for s in range(16):
            at = b0 + s * STEP
            if at >= 6.6:
                break
            vel = 0.75 + 0.25 * rng.uniform()
            h = hat()
            pan = 0.85 if s % 4 else 1.0
            place(drums, np.stack([h * pan, h]), at, 0.2 * vel * (1.0 if s % 2 == 0 else 0.6))
            if s in (13, 15) and b % 2 == 1:  # 32nd rolls
                place(drums, np.stack([h, h * 0.8]), at + STEP / 2, 0.12)
        if b % 2 == 1:
            oh = hat(open_=True)
            at = b0 + 14 * STEP
            if at < 6.6:
                place(drums, np.stack([oh, oh * 0.9]), at, 0.16)
    for s, nn in phrase * 2:
        at = g0 + s * STEP
        if at < 6.6:
            place(mel, cowbell(notes[nn]), at, 0.5)
            place(mel, cowbell(notes[nn] * 2), at, 0.08)
    # pad: F minor → Db major → Eb major, under the roll-call
    chords = [(1.2, [174.61, 207.65, 261.63]), (2.8, [138.59, 174.61, 207.65]), (4.4, [155.56, 196.0, 233.08])]
    for at, fr in chords:
        p = pad(fr, 1.6 + 0.35, 1100)
        place(pads, np.stack([p, np.roll(p, 240)]), at, 0.16)

    # --- statement 6.6–7.55: build (no kick), accelerating snare roll + riser
    r = riser(0.95)
    place(drums, np.stack([r, np.roll(r, 120)]), 6.6, 0.22)
    t = 6.6
    i = 0
    while t < 7.5:
        rate = STEP if t < 7.0 else (STEP / 2 if t < 7.3 else STEP / 4)
        c = clap(0.12)
        g = 0.18 + 0.32 * (t - 6.6) / 0.9
        place(drums, np.stack([c, c]), t, g)
        t += rate
        i += 1
    p = pad([174.61, 207.65, 261.63, 349.23], 0.95, 2400)
    place(pads, np.stack([p, np.roll(p, 240)]), 6.6, 0.14)
    # 7.55–8.15: dead air (tension gap; the falcon owns 7.80)

    # --- final hit 8.15 → ring-out
    kick_at(8.15, F1, 1.85, 1.15)
    cr = crash(1.85)
    place(drums, cr, 8.15, 0.32)
    c = clap()
    place(drums, np.stack([c, c]), 8.15, 0.5)
    p = pad([87.31, 174.61, 207.65, 261.63, 349.23], 1.85, 1600)
    place(pads, np.stack([p, np.roll(p, 300)]), 8.15, 0.2)

    # --- mix
    mel_st = np.stack([mel, np.roll(mel, int(0.0125 * SR))])
    space = convolve_st(mel * 0.35 + pads.mean(axis=0) * 0.2, reverb_ir(1.6, 0.45, 7))
    mix = 1.0 * bass + 0.9 * drums + 0.55 * mel_st + pads * duck + 0.5 * space
    mix = hp(mix, 28)
    mix[:, int(7.55 * SR) : int(8.15 * SR)] *= 0.0  # hard gap, belt and braces
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)  # glue
    return mix / np.abs(mix).max() * 0.78


# ------------------------------------------------------------------ falcon
def make_falcon():
    dur = 1.6
    t = t_axis(dur)
    # pitch contour: short "kee" grace note, then a long descending scream that cracks into "arr"
    f0 = np.interp(t, [0, 0.03, 0.09, 0.12, 0.16, 0.26, 0.6, 1.0, 1.25, 1.45, 1.6],
                      [2550, 3350, 3500, 2900, 3250, 3600, 3300, 2700, 2250, 1850, 1700])
    jitter = lp(rng.normal(0, 1, t.size), 25) * 60
    vib = 45 * np.sin(2 * np.pi * 6.5 * t)
    f = f0 + jitter + vib
    ph = 2 * np.pi * np.cumsum(f) / SR
    # bright, buzzy harmonic stack
    amps = [1.0, 0.55, 0.38, 0.22, 0.12, 0.07]
    tone = sum(a * np.sin((k + 1) * ph + 0.3 * k) for k, a in enumerate(amps))
    # rasp: irregular glottal-ish amplitude roughness, growing toward the end
    rough_depth = np.interp(t, [0, 0.3, 0.9, 1.6], [0.35, 0.45, 0.7, 0.9])
    rasp = lp(rng.normal(0, 1, t.size), 180)
    rasp = rasp / np.abs(rasp).max()
    sub = 0.5 * (1 + np.sin(ph / 2 + 2 * rasp))  # subharmonic flutter
    tone = tone * (1 - rough_depth * (0.5 + 0.5 * rasp)) * (0.7 + 0.3 * sub)
    # breath: noise band riding the fundamental (ring-modulated narrowband noise)
    nb = lp(rng.normal(0, 1, t.size), 420)
    breath = nb / np.abs(nb).max() * np.sin(ph) + 0.4 * nb / np.abs(nb).max() * np.sin(2 * ph)
    x = tone + 0.55 * breath
    # envelope: grace note, tiny gap, long scream
    env = np.interp(t, [0, 0.006, 0.08, 0.115, 0.135, 0.15, 0.24, 0.9, 1.3, 1.55, 1.6],
                       [0, 0.85, 0.75, 0.15, 0.1, 0.8, 1.0, 0.92, 0.7, 0.12, 0])
    x = x * env
    x = hp(x, 900, 3)
    x = np.tanh(1.6 * x / np.abs(x).max()) / np.tanh(1.6)
    # open-sky space: short pre-delay, airy tail
    ir = reverb_ir(1.2, 0.32, 3)
    wet = convolve_st(np.concatenate([np.zeros(int(0.018 * SR)), x])[: x.size], ir)
    st = np.stack([x, x]) * 0.9 + 0.32 * wet
    st = st / np.abs(st).max() * 0.94
    return st


def write_mp3(st, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(st, -1, 1).T * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "320k", str(path)], input=pcm, check=True)


if __name__ == "__main__":
    write_mp3(make_bed(), ROOT / "assets/music/bed.mp3")
    write_mp3(make_falcon(), ROOT / "assets/sfx/falcon-screech.mp3")
    print("wrote assets/music/bed.mp3, assets/sfx/falcon-screech.mp3", file=sys.stderr)
