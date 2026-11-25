"""Flirty/teasing delivery on native HK female library voices, using the 'D' expressive settings."""
import json, os, sys, urllib.request, urllib.error

KEY = "proxy-injected"  # session proxy injects the real key
OUT = sys.argv[1] if len(sys.argv) > 1 else "out/female"
os.makedirs(OUT, exist_ok=True)
TEXT = ("[whispers] 喂……靚仔，你知唔知呀？[flirty] 住劏房，一個月五千五㗎。返深圳住呢？"
        "[giggles] 三千蚊咋，平成半喎～ [teasing] 但係呢……你日日要過關返工喎。"
        "來回九十蚊，一個月成二千蚊車錢。仲要日日喺路上，嘥多三粒鐘……"
        "[sighs] 即係話，你每個鐘，慳七蚊。[laughs] 七蚊呀大佬～ 一杯凍奶茶都唔請得我飲啦！")
VOICES = {
    "1_aki_sassy_deep": "xDISamJf8LV5rG5A2te1",
    "2_nina_sweet_soft": "El018FmI047NtSsCfyrY",
    "3_cathy_expressive": "pyCpQJNpFBywhVAwOzn6",
    "4_chloe_energetic": "n4xdXKggn5lFcXFYE4TA",
    "5_stephanie": "Pi6HrXrDvDZF3ftmE4tC",
}
SETTINGS = {"stability": 0.05, "similarity_boost": 0.70, "style": 1.0, "speed": 1.05}
for name, vid in VOICES.items():
    body = {"text": TEXT, "model_id": "eleven_v4", "language_code": "yue", "voice_settings": SETTINGS}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                                 json.dumps(body).encode(), {"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        open(f"{OUT}/{name}.mp3", "wb").write(urllib.request.urlopen(req, timeout=180).read())
        print("saved", name)
    except urllib.error.HTTPError as e:
        print(name, "ERROR", e.code, e.read().decode()[:300])
