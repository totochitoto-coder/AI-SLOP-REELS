# Automation plan (saved for later — not started yet)

Flow: topic list -> Claude makes video (script, voice, video, thumbnail, caption) -> owner reviews on phone
-> Claude schedules via Buffer at HK prime time -> Buffer posts to Instagram + TikTok.

## Owner's one-time setup (~15 min)
1. Free Buffer account (buffer.com); connect Instagram dittttoinfo (Professional account) and TikTok.
2. claude.ai -> Settings -> Connectors -> add Buffer.
3. Decide cadence (daily / 3 a week / 2 a day).

## Claude's side
- `topics.md` queue (owner + Claude add ideas).
- Scheduled task wakes a Claude session on a timer, makes the next video with ./make_video.sh, pushes it,
  and notifies the owner with video + transcript + thumbnail + caption.
- On approval: schedule in Buffer for the next slot (IG 12:30 UK, TikTok 13:00 UK).

## Open questions to verify once Buffer is connected
- Whether Buffer needs a public video URL (repo is likely private -> small public media folder/repo).
- Whether Buffer can set Instagram's AI label; if not, owner toggles it after posting.
