"""Generate the voiceover for a script and time the video to it.

For every scene: TTS with character timestamps -> scene duration follows the voice,
caption tokens are highlighted exactly when they are spoken.

Usage: python3 build_voice.py <script.json> <workdir>
Writes <workdir>/timed.json (script with dur/tokenTimes/cue times) and <workdir>/voice.wav.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

import numpy as np

SR = 44100
LEAD = 0.15   # silence before each scene's line
TAIL = 0.30   # breathing room after each line
KEY = os.environ.get("ELEVENLABS_API_KEY") or "proxy-injected"  # proxy injects the real key in this environment

script_path, work = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(script_path, encoding="utf-8"))
cfg = json.load(open(os.path.join(here, "config", "voices", S.get("voice", "chloe") + ".json"), encoding="utf-8"))
os.makedirs(os.path.join(work, "voice"), exist_ok=True)

PUNCT = re.compile(r"[\s，。！？、…～~,.!?$＄：:「」]")


def tts(text, prev_text, next_text, overrides=None):
    vs = {**cfg["voice_settings"], **(overrides or {})}
    body = {"text": text, "model_id": cfg["model_id"], "language_code": cfg["language_code"],
            "voice_settings": vs}
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}/with-timestamps?output_format=mp3_44100_128"
    req = urllib.request.Request(url, json.dumps(body).encode(), {"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        sys.exit(f"TTS failed ({e.code}): {e.read().decode()[:300]}")


TEMPO = float(cfg.get("tempo", 1.0))  # extra speed-up after TTS (pitch preserved)


def decode(mp3_path):
    af = ["-af", f"atempo={TEMPO}"] if TEMPO != 1.0 else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3_path, *af, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


TAG = re.compile(r"\[[^\]]*\]")
CLAUSE_END = "，。！？、…～：,.!?"


def auto_caption(narration, max_len=5):
    """Split spoken text into short caption chunks; English words stay whole, punctuation sticks to the chunk."""
    text = TAG.sub("", narration).strip()
    units = re.findall(r"[A-Za-z][A-Za-z0-9']*(?:\s+\d+)?|\d+|[零一二三四五六七八九十百千萬兩]+|[^\sA-Za-z\d]", text)
    out, cur = [], ""
    for u in units:
        if u in CLAUSE_END:
            cur += u
            if cur.strip(CLAUSE_END):
                out.append(cur)
            elif out:
                out[-1] += u
            cur = ""
            continue
        if re.match(r"[A-Za-z]", u):
            if cur:
                out.append(cur)
            out.append(u); cur = ""
            continue
        cur += u
        if len(cur) >= max_len and not re.match(r"[零一二三四五六七八九十百千萬兩]+$", u[-1:]):
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    # glue a trailing punctuation-only piece or a dangling single char to its neighbour
    merged = []
    for t in out:
        if merged and (len(PUNCT.sub("", t)) <= 1 and not re.match(r"[A-Za-z]", t)) and not re.match(r"[A-Za-z]", merged[-1]):
            merged[-1] += t
        else:
            merged.append(t)
    return merged


def phrase_time(phrase, chars, starts):
    spoken = "".join(chars)
    i = spoken.find(phrase)
    return starts[i] if i >= 0 else None


def token_times(tokens, chars, starts):
    """Find each caption token in the spoken character stream (in order); interpolate the misses."""
    spoken = "".join(chars)
    times, pos = [], 0
    for tok in tokens:
        key = PUNCT.sub("", tok)
        i = spoken.find(key, pos) if key else -1
        if i >= 0:
            times.append(starts[i]); pos = i + len(key)
        else:
            times.append(None)
    # interpolate unknowns between known neighbours
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    end = starts[-1] if starts else 0
    for i, t in enumerate(times):
        if t is None:
            prev = max([k for k in known if k[0] < i], default=(-1, 0.0), key=lambda k: k[0])
            nxt = min([k for k in known if k[0] > i], default=(len(times), end), key=lambda k: k[0])
            times[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / (nxt[0] - prev[0])
    return times


track, t0 = [], 0.0
scenes = S["scenes"]
for n, sc in enumerate(scenes):
    prev_text = scenes[n - 1].get("narration", "") if n else ""
    next_text = scenes[n + 1].get("narration", "") if n + 1 < len(scenes) else ""
    # cache: only call the API when this line (or its voice settings) changed
    key = hashlib.sha1(json.dumps([sc["narration"], prev_text, next_text, cfg["voice_id"], cfg["model_id"],
                                   cfg["voice_settings"], sc.get("voice_overrides")], ensure_ascii=False).encode()).hexdigest()
    cache = os.path.join(work, "voice", f"scene{n + 1}.json")
    cached = json.load(open(cache)) if os.path.exists(cache) else {}
    if cached.get("key") == key:
        res = cached["res"]
    else:
        res = tts(sc["narration"], prev_text, next_text, sc.get("voice_overrides"))
        json.dump({"key": key, "res": res}, open(cache, "w"))
    mp3 = os.path.join(work, "voice", f"scene{n + 1}.mp3")
    open(mp3, "wb").write(base64.b64decode(res["audio_base64"]))
    pcm = decode(mp3)
    al = res.get("alignment") or res.get("normalized_alignment") or {}
    chars = al.get("characters", [])
    starts = [x / TEMPO for x in al.get("character_start_times_seconds", [])]
    if "caption" not in sc:
        sc["caption"] = auto_caption(sc["narration"])
    tt = token_times(sc["caption"], chars, starts)
    voice_len = len(pcm) / SR
    sc["minDur"] = sc.get("minDur", sc["dur"])
    sc["dur"] = round(max(sc["minDur"], LEAD + voice_len + TAIL), 3)
    sc["tokenTimes"] = [round(LEAD + t, 3) for t in tt]
    for k in ("cue", "cue1", "cue2", "count"):  # token index or spoken phrase -> time
        if k not in sc:
            continue
        if isinstance(sc[k], str):
            t = phrase_time(sc[k], chars, starts)
            if t is None:
                print(f"  warning: cue phrase {sc[k]!r} not found in scene {n + 1}")
                continue
            sc[k + "Time"] = round(LEAD + t, 3)
        else:
            sc[k + "Time"] = sc["tokenTimes"][sc[k]]
    track.append((t0 + LEAD, pcm))
    print(f"scene {n + 1}: voice {voice_len:.1f}s -> scene {sc['dur']:.1f}s")
    t0 += sc["dur"]

out = np.zeros(int((t0 + 0.5) * SR), dtype=np.float32)
for start, pcm in track:
    i = int(start * SR)
    out[i:i + len(pcm)] += pcm
pcm16 = (np.clip(out, -1, 1) * 32767).astype(np.int16)
import wave
with wave.open(os.path.join(work, "voice.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm16.tobytes())
json.dump(S, open(os.path.join(work, "timed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"total {t0:.1f}s")
