# Channel pipeline

**Crypto Safe Zone** — faceless English YouTube channel about crypto safety and beginner how-tos. Owner: Vagh. Every video is made here end to end: topic → script → animated scenes → voice → render → publish via Metricool → state update. The owner reviews after publishing and deletes anything bad himself, so a run never waits for approval, but it must never publish something broken or wrong.

* Repo: `Kosyanvag/channel-media`, working copy `/home/claude/channel-media`.
* Metricool brand `blogId` **7630681**, timezone **Asia/Yerevan**, network `youtube`.
* Voice: Kokoro `am_michael` (free, open licence). Visual language and every element: `ELEMENTS.md`.
* Reference specs: `specs/2026-10-26-first-bitcoin.json` (long), `specs/short-fake-exchange-site.json` (short). Read the matching one before writing a new spec.

## 0. Start of every run

1. If `/home/claude/channel-media` is missing: attach the repo with the add-repo tool (owner `Kosyanvag`, repo `channel-media`, access `push`), then `git clone --depth 1 https://github.com/Kosyanvag/channel-media /home/claude/channel-media`.
2. `cd /home/claude/channel-media && git pull -q && bash scripts/setup.sh` (installs Kokoro and downloads the voice model, ~1–2 min).
3. Load the Metricool tools with ToolSearch (`metricool scheduled post`).
4. Read `state/topics.json`, `state/log.json`, `state/shorts_queue.json` and `state/insights.md` (if present) and follow the rules in insights.

## A. Long video (Mon / Wed / Fri)

0. If `state/log.json` already has a `video` entry dated today (scheduled or published), stop: nothing to do.
1. **Topic**: the first `todo` in `state/topics.json`. If fewer than 5 `todo` remain, research and append new ones first. Prefer **search-driven** topics people actually type into YouTube ("how to …", "is … safe", "… explained", "… scam"): check YouTube/Google autocomplete-style phrasing with web searches and phrase the `idea` as that query. Beginner crypto safety, scams, how-tos only; never price predictions, coin picks or "how to get rich".
2. **Research**: run a few web searches so every fact is current and correct (fees, how a scam works today, what features exist). No invented statistics; if a number isn't verifiable, say it qualitatively.
3. **Script** — **1300–1700 words** of narration, 12–18 scenes, about **8–11 minutes** (watch time is what unlocks monetization, so depth matters, but never pad):
   * Scene 1 hook (15–25 s): a concrete situation where someone loses money, then the promise of the video. No "hey guys", no channel intro.
   * Scene 2: a 20–30 s "why this matters" or "how it works" explainer so a total beginner can follow.
   * Then one or two scenes per step / scam / point, each opening with a `section` card (`kicker` STEP / SCAM / MYTH / TIP / RULE, numbered). For every point give: what it is, a concrete example (with an invented app), how to spot it, what to do. Add one "real-life story" style scene (clearly a hypothetical: "Imagine Alex…") somewhere in the middle.
   * Every ~2 minutes add a retention line that previews what's coming ("The next one is the hardest to spot.").
   * A recap scene with a `checklist`.
   * Outro: subscribe + name the NEXT `todo` topic as the next video + a comment question, then `endscreen` with `hold: 11`.
   * Short sentences (6–18 words), spoken style, second person ("you"). One sentence = one beat on screen.
   * Educational only: no financial advice, no guaranteed returns, no real exchange names; say "your exchange", "a licensed exchange".
   * YouTube rules: the content must be original, informative and specific to the topic (this is what keeps AI-voiced channels monetizable). No misleading titles or thumbnails: the thumbnail and title must describe what the video actually shows. No clickbait that the video doesn't pay off, no fake urgency, no sub-for-sub, no asking for likes in exchange for anything.
4. **Spec**: write `specs/<YYYY-MM-DD>-<slug>.json` (date = publish date) following `ELEMENTS.md`. Visuals must change with the narration; reuse the phone / cards / bullets / arrows / stamps patterns from the reference spec, but build each scene for its content.
   * `publish`: title ≤ 70 chars, curiosity + clear benefit ("How to…", "X scams that…", "Stop doing…"); description 2–3 sentences + `{chapters}` + the line "This video is for educational purposes only and is not financial advice." + 3 hashtags; 6–10 tags (first tag = the exact search phrase; title must contain it too); `category` `EDUCATION`; `chapters` one label per scene (outro scene gets no label).
   * `thumbnail`: 2–3 short uppercase lines (max ~4 words total), one in red or green, over a striking frame (`shift` 300 so the frame sits left).
5. **Preview**: `python3 engine/make.py specs/<id>.json --preview`. Read EVERY `build/<id>/preview_*.png` and `thumb.jpg`. Fix overlaps, text running off screen, empty screens, elements appearing at the wrong sentence. Repeat until clean (usually 2–3 rounds).
6. **Render**: `python3 engine/make.py specs/<id>.json` (roughly 4–6 min per minute of video, so 40–60 min for a long video; run it in the background and wait for it, do not stop early). Then `python3 scripts/meta.py specs/<id>.json` → `build/<id>/publish.json`. Grab 3 frames with ffmpeg from the final video and look at them.
7. **Shorts from this video**: write 3–4 vertical short specs into `specs/shorts/<id>-<n>.json` (see section B for the short format), each one self-contained tip from the video, and append their paths to `state/shorts_queue.json`. Preview each once and fix it; do not render them now.
8. **Publish**:
   * `bash scripts/upload.sh build/<id>/<id>.mp4 build/<id>/<id>.jpg` → prints the two public URLs.
   * Metricool `createScheduledPost`: `blogId` 7630681, `date` = today 21:30 Asia/Yerevan (or now + 20 min if that has passed), `info`:
     `{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "media": [<video url>], "videoThumbnailUrl": <thumb url>, "mediaAltText": [], "providers": [{"network": "youtube"}], "publicationDate": {"dateTime": "<same as date, no offset>", "timezone": "Asia/Yerevan"}, "shortener": false, "smartLinkData": {"ids": []}, "text": <description>, "youtubeData": {"title": <title>, "type": "video", "privacy": "public", "tags": [...], "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": false}}`
   * `isAiGeneratedContent` stays false: the videos are animated graphics, not realistic synthetic people or events, which is what YouTube's disclosure is for. If a video ever shows a realistic-looking person, place or event that didn't happen, set it to true.
   * If the thumbnail is rejected, retry once without `videoThumbnailUrl`.
9. **State**: set the topic `status` to `scheduled` with `video` and `date`; append to `state/log.json` (date, type, id, title, Metricool post id, status). Commit the spec, shorts specs and state (never `build/`), `git pull --rebase -q && git push -q`.

## B. Short (every day)

0. If `state/log.json` already has a `short` entry dated today, stop.
1. **News check first** (about 5 minutes): web-search crypto scam / hack / fraud / phishing news from the last 48 hours. If there is a significant event covered by at least two reputable news sources, and `state/log.json` shows fewer than 3 news shorts in the last 7 days, make today's short about it: what happened (facts only, from the sources, no speculation or blame beyond what they report), then the one lesson viewers should take from it. Name real companies only as the sources do; on screen still use invented apps. Title starts with the hook, not the brand. Put `"news": true` and the source URLs under `publish.sources` in the spec, and log it with `"type": "short", "news": true`. The queue stays untouched that day.
   Otherwise take the first path from `state/shorts_queue.json`. If the queue is empty, write a new short yourself from a topic already covered in `state/log.json` (one tip, 20–45 s).
2. Short format: `"format": "short"`, ONE scene, 5–8 sentences, 70–110 words, 20–45 s.
   * Sentence 1 is the hook (a claim or a shock: "This website is fake."). Last sentence: "Follow for one crypto safety tip every day."
   * Burned-in word captions are added automatically for shorts at y ≈ 1500: keep y 1420–1580 free of other elements.
   * Big visuals: phone at `scale` 1.1 centred (x 540, y 930), `label` "CRYPTO SAFETY TIP" at the top (switch to "FOLLOW FOR DAILY TIPS" on the last sentence), the takeaway as a centred `heading` + `icon` after the phone fades out. Keep inside the short safe area.
   * `publish`: title ≤ 60 chars ending with `#shorts`; description 1–2 sentences + (if the short came from a long video in `state/log.json` that is already published) "Full video on the channel: search \"<long video title>\"" + "Educational content, not financial advice." + hashtags; 4–6 tags.
   * Also set Metricool `firstCommentText` to "Full breakdown in the long video on our channel 👆" when the short came from a long video.
3. Preview, read the sheet, fix, then render. Check `timings.json` total < 59 s.
4. Publish exactly like A.8 but with `youtubeData.type` `"short"`, no `videoThumbnailUrl`, no `category`, and `date` = today 19:00 Asia/Yerevan (or now + 15 min if passed).
5. Remove the path from the queue, append to `state/log.json`, commit and push.

## If something breaks

* Never publish a video you have not looked at, or one with a missing voice, black frames or cut-off text.
* If rendering or publishing fails after two fixes, publish nothing, write the error into `state/log.json` with `status: "failed"`, commit and push, and end the run with a short summary of what failed.
* Engine bugs: fix them in `engine/` (keep the element API backwards compatible) and commit the fix with the video.

## Style that stays the same

Dark navy background with a faint grid, neon green = safe, neon red = scam/danger, yellow = caution, blue = money/bank. Inter font. Fictional apps (CryptoApp, CryptoP2P, MyBank). Calm male narrator, no hype words ("insane", "to the moon").

## C. Weekly review (Sunday)

1. Load the Metricool tools (ToolSearch "metricool analytics"). Use `getAnalyticsAvailableMetrics` for network `youtube`, then `getAnalyticsDataByMetrics` for blogId 7630681 over the last 7 and last 28 days: views, watch time, average view duration, subscribers gained, per-video numbers where available.
2. Compare videos and shorts: which topics, titles, thumbnails and hooks did best and worst (views per day since publishing, average view duration, subs gained).
3. Write `state/insights.md` (replace the file): date, a short table of the last 28 days, 3–5 concrete takeaways, and the rules future runs must follow because of them (e.g. "scam-story hooks beat how-to hooks: open with a loss"). Keep it under 60 lines. Long-video and short runs read this file in step 0 and follow its rules.
4. Reorder the `todo` topics in `state/topics.json` so the most promising come first, and add new search-driven topics in the directions that worked.
5. Commit and push. End with a short summary in Russian for Vagh: subscribers, total watch hours (toward 4000), best video, what changes this week.
