"""Design candidate Cantonese voices with ElevenLabs Voice Design and save previews."""
import base64, json, os, sys, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1/text-to-voice/design"
KEY = os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")  # proxy injects the real key
OUT = sys.argv[1] if len(sys.argv) > 1 else "out/voices"
TEXT = ("喂，你哋知唔知呀？住劏房一個月五千五，返深圳住只係三千蚊！平咗一半喎！"
        "但係……你每日要過關返工，來回九十蚊，一個月二千蚊車費。仲要每日喺路上多三粒鐘！"
        "即係話，你每個鐘慳七蚊。七蚊呀！買杯奶茶都唔夠啦！")
CANDIDATES = {
    "gossip": "Young Hong Kong man in his late 20s speaking fast, colloquial Hong Kong Cantonese. Cheeky, sarcastic and playful, like gossiping with friends at a cha chaan teng. Slightly nasal, very expressive, great comedic timing.",
    "drama": "Over-the-top dramatic Hong Kong Cantonese male narrator, a parody of a soap-opera trailer voice. Deep, theatrical, exaggerated pauses, comedic.",
    "hyper": "High-energy Hong Kong Cantonese guy in his early 20s, excited and loud, talks very fast, laughs between sentences, YouTuber vibe.",
    "uncle": "Middle-aged Hong Kong uncle speaking Cantonese, deadpan and unimpressed, sarcastic, slightly raspy, like a grumpy taxi driver complaining.",
}
os.makedirs(OUT, exist_ok=True)
model = os.environ.get("TTV_MODEL", "eleven_ttv_v3")
meta = {}
for name, desc in CANDIDATES.items():
    body = json.dumps({"voice_description": desc, "text": TEXT, "model_id": model}).encode()
    req = urllib.request.Request(API, body, {"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        print(name, "ERROR", e.code, e.read().decode()[:400]); continue
    for i, p in enumerate(d.get("previews", [])[:2]):
        fn = f"{OUT}/{name}_{i+1}.mp3"
        open(fn, "wb").write(base64.b64decode(p["audio_base_64"]))
        meta[f"{name}_{i+1}"] = {"generated_voice_id": p["generated_voice_id"], "description": desc}
        print("saved", fn)
json.dump(meta, open(f"{OUT}/candidates.json", "w"), ensure_ascii=False, indent=2)
