"""Render the same Cantonese test line with several library voices on the Cantonese-capable model."""
import json, os, sys, urllib.request, urllib.error

KEY = "proxy-injected"  # the session proxy injects the real ElevenLabs key
OUT = sys.argv[1] if len(sys.argv) > 1 else "out/voices_v2"
MODEL = os.environ.get("TTS_MODEL", "eleven_v4")
TEXT = ("喂，你哋知唔知呀？住劏房，一個月五千五。返深圳住呢？三千蚊咋！平成半喎！"
        "但係……你日日要過關返工，來回九十蚊，一個月成二千蚊車錢。仲要日日喺路上嘥多三粒鐘！"
        "即係話，你每個鐘慳七蚊。七蚊呀大佬！一杯凍奶茶都唔夠啦！")
VOICES = {
    "1_tung_funny": "OjkyUe8dIihIFvOisuvM",
    "2_suuny_energetic": "pu1tF8vhX5qEx1v7a6UV",
    "3_alan_chinglish": "kWb73BrEnNOO40EVbd2k",
    "4_lucky_dramatic": "cHDwXsKG0qHMNLIjOusN",
    "5_cy_casual": "SPRXwABrRtJGzRFBpO1H",
    "6_chloe_fast_female": "n4xdXKggn5lFcXFYE4TA",
}
os.makedirs(OUT, exist_ok=True)

def call(url, body=None):
    req = urllib.request.Request(url, json.dumps(body).encode() if body is not None else None,
                                 {"xi-api-key": KEY, "Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=180).read()

for name, vid in VOICES.items():
    body = {"text": TEXT, "model_id": MODEL, "language_code": "yue"}
    try:
        audio = call(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128", body)
    except urllib.error.HTTPError as e:
        print(name, "ERROR", e.code, e.read().decode()[:300]); continue
    open(f"{OUT}/{name}.mp3", "wb").write(audio)
    print("saved", name)
