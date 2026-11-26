#!/usr/bin/env bash
# One command per video: voice -> render -> thumbnail -> captions, finals copied to videos/.
# Usage: ./make_video.sh scripts/02_ferrari_effect.json
set -euo pipefail
script="$1"; name="$(basename "$script" .json)"; work="out/$name"
mkdir -p "$work" videos
python3 -I build_voice.py "$script" "$work"
node render.mjs "$work/timed.json" "$work/$name.mp4" --voice "$work/voice.wav"
rm -f "$work/${name}_silent.mp4" "$work/$name.wav"
cp "$work/$name.mp4" "videos/$name.mp4"
node thumbnail.mjs "$script" "videos/${name}_thumbnail.png"
python3 -I - "$script" "videos/${name}_caption.txt" <<'PY'
import json, sys
S = json.load(open(sys.argv[1], encoding="utf-8")); post = S.get("post", {})
with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write("=== Instagram ===\n" + post.get("instagram", "") + "\n\n=== TikTok ===\n" + post.get("tiktok", "") + "\n")
print("caption:", sys.argv[2])
PY
echo "done: videos/$name.mp4"
