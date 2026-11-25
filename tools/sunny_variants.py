"""Try more expressive delivery settings on the Suuny Su voice."""
import json, os, sys, urllib.request, urllib.error

KEY = "proxy-injected"  # session proxy injects the real key
VID = "pu1tF8vhX5qEx1v7a6UV"  # Suuny Su (ElevenLabs voice library)
OUT = sys.argv[1] if len(sys.argv) > 1 else "out/sunny"
os.makedirs(OUT, exist_ok=True)
PLAIN = ("喂，你哋知唔知呀？住劏房，一個月五千五。返深圳住呢？三千蚊咋！平成半喎！"
         "但係……你日日要過關返工，來回九十蚊，一個月成二千蚊車錢。仲要日日喺路上嘥多三粒鐘！"
         "即係話，你每個鐘慳七蚊。七蚊呀大佬！一杯凍奶茶都唔夠啦！")
PUNCHY = ("喂喂喂！你哋知唔知呀？！住劏房——一個月，五千五！返深圳住呢？三千蚊咋！平成半喎！嘩！"
          "但係……等陣先！你日日要過關返工喎！來回九十蚊，一個月——成二千蚊車錢！"
          "仲要日日喺路上，嘥多三粒鐘！即係話……你每個鐘，慳七蚊。七蚊呀大佬！！一杯凍奶茶都唔夠啦！")
TAGGED = ("[excited] 喂喂喂！你哋知唔知呀？！住劏房——一個月，五千五！[gasps] 返深圳住呢？三千蚊咋！平成半喎！"
          "[suspicious] 但係……等陣先！你日日要過關返工喎！來回九十蚊，一個月——成二千蚊車錢！"
          "[frustrated] 仲要日日喺路上，嘥多三粒鐘！[sarcastic] 即係話……你每個鐘，慳七蚊。[laughs] 七蚊呀大佬！！一杯凍奶茶都唔夠啦！")
VARIANTS = {
    "A_lively":        (PLAIN,  {"stability": 0.30, "similarity_boost": 0.80, "style": 0.55, "speed": 1.10}),
    "B_hype":          (PUNCHY, {"stability": 0.20, "similarity_boost": 0.75, "style": 0.85, "speed": 1.15}),
    "C_hype_emotions": (TAGGED, {"stability": 0.20, "similarity_boost": 0.75, "style": 0.85, "speed": 1.15}),
    "D_max_chaos":     (TAGGED, {"stability": 0.05, "similarity_boost": 0.70, "style": 1.00, "speed": 1.20}),
}
for name, (text, vs) in VARIANTS.items():
    body = {"text": text, "model_id": "eleven_v4", "language_code": "yue", "voice_settings": vs}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",
                                 json.dumps(body).encode(), {"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        open(f"{OUT}/sunny_{name}.mp3", "wb").write(urllib.request.urlopen(req, timeout=180).read())
        print("saved", name)
    except urllib.error.HTTPError as e:
        print(name, "ERROR", e.code, e.read().decode()[:300])
