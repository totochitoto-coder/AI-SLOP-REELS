"""Generate a simple music bed + UI sound effects synced to the script timeline.
Placeholder until the Cantonese voiceover is plugged in.
Usage: python3 audio.py <script.json> <out.wav>
"""
import json
import sys
import wave

import numpy as np

SR = 44100
script = json.load(open(sys.argv[1], encoding="utf-8"))
total = sum(s["dur"] for s in script["scenes"]) + 0.5
n = int(total * SR)
t = np.arange(n) / SR
mix = np.zeros(n)


def add(sig, at):
    i = int(at * SR)
    j = min(n, i + len(sig))
    if i < n:
        mix[i:j] += sig[: j - i]


def env(length, attack=0.005, decay=0.2):
    tt = np.arange(int(length * SR)) / SR
    return np.minimum(1, tt / attack) * np.exp(-tt / decay)


# --- pad: Am - F - C - G, 4s per chord
chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 261.63, 329.63], [196.0, 246.94, 293.66]]
pad = np.zeros(n)
for k in range(int(total / 4) + 1):
    seg = (t >= k * 4) & (t < k * 4 + 4)
    for f in chords[k % 4]:
        for det in (-0.6, 0.6):
            pad[seg] += np.sin(2 * np.pi * (f + det) * t[seg])
pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t - np.pi / 2) ** 2  # gentle swell per chord
mix += pad * 0.018

# --- soft pulse at 100 bpm
beat = 60 / 100
kick_len = 0.25
kt = np.arange(int(kick_len * SR)) / SR
kick = np.sin(2 * np.pi * (50 + 70 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)
hat = np.random.default_rng(1).standard_normal(int(0.05 * SR)) * env(0.05, 0.001, 0.012)
b = 0.0
while b < total - 1:
    add(kick * 0.22, b)
    add(hat * 0.05, b + beat / 2)
    b += beat

# --- sfx: tick on every caption token, pop on every scene start
start = 0.0
for sc in script["scenes"]:
    pop_t = np.arange(int(0.18 * SR)) / SR
    pop = np.sin(2 * np.pi * (500 + 900 * np.exp(-pop_t * 25)) * pop_t) * env(0.18, 0.002, 0.05)
    add(pop * 0.25, start)
    toks = sc["caption"]
    step = sc["dur"] * 0.85 / len(toks)
    for i in range(len(toks)):
        tick = np.sin(2 * np.pi * 1800 * np.arange(int(0.03 * SR)) / SR) * env(0.03, 0.001, 0.008)
        add(tick * 0.08, start + i * step)
    start += sc["dur"]

# fade in/out and normalise
fade = int(0.4 * SR)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / max(1e-9, np.abs(mix).max()) * 0.8
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
