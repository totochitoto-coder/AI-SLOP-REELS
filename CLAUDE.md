# dittttoinfo reel pipeline

Cantonese (Hong Kong) short-form reels for Instagram / TikTok account **dittttoinfo**.
Flat motion-graphics style, code-rendered (no AI images/video), AI voiceover via ElevenLabs.

## Make a video
1. Write `scripts/NN_slug.json` (see `scripts/02_ferrari_effect.json`): `voice`, `sides`, `footnote`, `scenes[]`
   (each with `type`, `narration`, `caption` tokens, optional cues), plus `thumbnail` and `post` blocks.
2. Run `./make_video.sh scripts/NN_slug.json`. Outputs in `videos/`: `NN_slug.mp4`, `NN_slug_thumbnail.png`,
   `NN_slug_caption.txt`. Commit and push them.
3. Send the user the video, thumbnail and caption for review. Nothing is posted without the user's approval.

## Standing rules (from the account owner)
- **Every video ships with a thumbnail (1080x1920) and an Instagram + TikTok caption.** Never deliver a video without both.
- Narration must be **natural spoken Cantonese**, not translated Mandarin. When in doubt, send the user the
  transcript first and let them rewrite it in their own Cantonese.
- Audience is **both men and women**: never address viewers as 靚仔/靚女; use 你.
- **Fact-check every number** with real sources (government data first); put sources in the footnote and caption.
  Hypotheticals must be labelled as such.
- Keep key visuals out of the bottom ~20% and top ~10% of the frame (app UI overlays). Output is 1080x1920.
- Label posts as AI-generated (Instagram "AI label", TikTok "AI-generated content"). The bio does not mention AI.
- Voices: `config/voices/sunny.json` (male, default for new videos, "Sunny D" settings, tempo 1.15) and
  `config/voices/chloe.json` (female, used in video 01). ElevenLabs key is injected by the environment proxy.
- Posting: user is in the UK; HK prime time 8:30pm HKT = 12:30pm UK (GMT; 11:30am UK after clocks change on 29 Mar 2027).
  Instagram 12:30pm UK, TikTok 1:00pm UK.
