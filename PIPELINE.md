# Channel pipeline

**Crypto Safe Zone** — faceless English YouTube channel about crypto safety and beginner how-tos. Owner: Vagh. Every video is made here end to end: topic → script → animated scenes → voice → render → publish via Metricool → state update. The owner reviews after publishing and deletes anything bad himself, so a run never waits for approval, but it must never publish something broken or wrong.

* Repo: `Kosyanvag/channel-media`, working copy `/home/claude/channel-media`.
* Metricool brand `blogId` **7630681**, network `youtube`. Audience is the US: all publish times are in **America/New_York**.
* Voice: Kokoro `blend` = 0.6 am_michael + 0.4 am_fenrir at speed 1.1, each scene voiced as one continuous take (free, open licence). Visual language and every element: `ELEMENTS.md`.
* Reference specs: `specs/2026-10-26-first-bitcoin.json` (long), `specs/short-fake-exchange-site.json` (short). Read the matching one before writing a new spec.

## 0. Start of every run

1. If `/home/claude/channel-media` is missing: attach the repo with the add-repo tool (owner `Kosyanvag`, repo `channel-media`, access `push`), then `git clone --depth 1 https://github.com/Kosyanvag/channel-media /home/claude/channel-media`.
2. `cd /home/claude/channel-media && git pull -q && bash scripts/setup.sh` (installs Kokoro and downloads the voice model, ~1–2 min).
3. Load the Metricool tools with ToolSearch (`metricool scheduled post`).
4. Read `state/topics.json`, `state/log.json`, `state/shorts_queue.json` and `state/insights.md` (if present) and follow the rules in insights.

## Post budget (Metricool free plan: 20 posts per calendar month)

* Schedule: long videos Mon + Thu, shorts Tue + Sat, YouTube only (TikTok is not used by the pipeline). That is at most 17 posts a month.
* Before creating any Metricool post, count the entries in `state/log.json` whose post was created in the current calendar month (Asia/Yerevan) and that have a `metricool_post` id. If the count is already 19 or more, do NOT post: log the item with `status: "skipped: monthly post budget"`, keep the spec for next month (put shorts back at the front of the queue), commit, push and say so in the summary. Long videos have priority over shorts.
* Never post the same video twice, never create test posts in Metricool, and never use `updateScheduledPost` unless something is broken (an update may count as a new post).

## TEMPORARY: October 30–31, 2026 only (Asia/Yerevan dates)

Vagh approved using the rest of the October Metricool budget. These rules apply ONLY to runs on 2026-10-30 and 2026-10-31 (Yerevan) and override section B where they differ. From 2026-11-01 ignore this section completely (YouTube only, normal budget rules).

* Every publish time must fall before **2026-10-31 23:45 Asia/Yerevan** (= 15:45 America/New_York on Oct 31), so it counts in October. If a time would fall later, move it earlier the same day.
* The day's main short goes to **YouTube + TikTok** in one Metricool post: `providers` `[{"network": "youtube"}, {"network": "tiktok"}]` plus `"tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": <title without #shorts>, "disableComment": false, "disableDuet": false, "disableStitch": false, "autoAddMusic": false, "commercialContentThirdParty": false, "commercialContentOwnBrand": false, "isAigc": true}`. Publish time: Oct 30 → 18:30 New York; Oct 31 → 15:00 New York.
* Plus **two TikTok-only shorts per day**: next two paths from `state/shorts_queue.json` (or new ones from topics already covered, alternating tip and quiz; never a video already posted on TikTok — the owner posted manually: quiz-fake-exchange-site, news-electrum-fee-bump, news-passport-phishing). Render each (preview + check like any short), upload, and create one Metricool post each with only `{"network": "tiktok"}` and the `tiktokData` above, at 09:00 and 13:00 New York the same day (if already passed: now + 20 min and now + 2 h, still before the October cut-off). TikTok text = the short's description with `#shorts` replaced by `#cryptotok #fyp`. Log them with `"type": "tiktok_short"`.
* Post budget for October: stop creating posts once `state/log.json` has 18 entries with a `metricool_post` id created in October.
* If TikTok rejects a post, keep the YouTube part, log the error and continue.

## A. Long video (Mon / Thu)

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
   * Metricool `createScheduledPost`: `blogId` 7630681, publish at **15:30 America/New_York** on the run day (US audience; Metricool handles daylight saving): `date` = that moment with its New York offset, e.g. `2026-10-28T15:30:00-04:00` (−05:00 after the first Sunday of November); if it has already passed, now + 20 min, `info`:
     `{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false, "media": [<video url>], "videoThumbnailUrl": <thumb url>, "mediaAltText": [], "providers": [{"network": "youtube"}], "publicationDate": {"dateTime": "<same as date, no offset>", "timezone": "America/New_York"}, "shortener": false, "smartLinkData": {"ids": []}, "text": <description>, "youtubeData": {"title": <title>, "type": "video", "privacy": "public", "tags": [...], "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": false}}`
   * `isAiGeneratedContent` stays false: the videos are animated graphics, not realistic synthetic people or events, which is what YouTube's disclosure is for. If a video ever shows a realistic-looking person, place or event that didn't happen, set it to true.
   * If the thumbnail is rejected, retry once without `videoThumbnailUrl`.
9. **State**: set the topic `status` to `scheduled` with `video` and `date`; append to `state/log.json` (date, type, id, title, Metricool post id, status). Commit the spec, shorts specs and state (never `build/`), `git pull --rebase -q && git push -q`.

## B. Short (Tue / Sat)

0. If `state/log.json` already has a `short` entry dated today, stop.
1. **Hook rule (both formats)**: the FIRST sentence and the first frame must be the hook, readable in 1 second (a claim, a loss, or "Real or scam?"). Never open with setup like "You searched for…" or "Here is…". Put the hook text big on screen from frame 1.
   **News check first** (about 5 minutes): web-search crypto scam / hack / fraud / phishing news from the last 48 hours. If there is a significant event covered by at least two reputable news sources that matters to ordinary crypto users (a big exchange, a widespread scam wave, a popular wallet app; not niche hardware makers or developer tools), and `state/log.json` shows fewer than 2 news shorts in the last 7 days, make today's short about it: what happened (facts only, from the sources, no speculation or blame beyond what they report), then the one lesson viewers should take from it. Name real companies only as the sources do; on screen still use invented apps. Title starts with the hook, not the brand. Put `"news": true` and the source URLs under `publish.sources` in the spec, and log it with `"type": "short", "news": true`. The queue stays untouched that day.
   Otherwise take the first path from `state/shorts_queue.json`. If the queue is empty, write a new short yourself from a topic already covered in `state/log.json` (one tip, 20–45 s).
2. Short format: `"format": "short"`, ONE scene, 5–8 sentences, 70–110 words, 20–45 s.
   * Sentence 1 is the hook (a claim or a shock: "This website is fake."). Last sentence: "Follow for one crypto safety tip every day."
   * Alternate formats day by day: (a) **tip** — the format above; (b) **"Real or scam?" quiz** — sentence 1 shows a screen (a message, a site, a payment, an offer) and asks "Real or scam? Decide before I tell you." (tag "REAL OR SCAM?" + a 3-second `counter` countdown 3→0), then the reveal with a `stamp`, then the one clue that gave it away, then "Comment if you got it right." Quizzes make people comment, which pushes shorts; ideas should be ones a beginner could plausibly get wrong.
   * Shorts are rendered into a TikTok+YouTube safe frame automatically: the whole layout is scaled into x 30–880, y 250–1336 and captions sit at y ≈ 1360. The preview sheets show the unsafe UI zones in red; nothing important may sit near the edges of the safe frame.
   * Big visuals: phone at `scale` 1.1 centred (x 540, y 930), `label` "CRYPTO SAFETY TIP" at the top (switch to "FOLLOW FOR DAILY TIPS" on the last sentence), the takeaway as a centred `heading` + `icon` after the phone fades out. Keep inside the short safe area.
   * `publish`: title ≤ 60 chars ending with `#shorts`; description 1–2 sentences + (if the short came from a long video in `state/log.json` that is already published) "Full video on the channel: search \"<long video title>\"" + "Educational content, not financial advice." + hashtags; 4–6 tags.
   * Also set Metricool `firstCommentText` to "Full breakdown in the long video on our channel 👆" when the short came from a long video.
3. Preview, read the sheet, fix, then render. Check `timings.json` total < 59 s.
4. Publish exactly like A.8 but with `youtubeData.type` `"short"`, no `videoThumbnailUrl`, `"videoCoverMilliseconds": 300` (cover = the opening question frame, never the reveal), no `category`, and publish at **18:30 America/New_York** on the run day (`publicationDate.timezone` "America/New_York"; if passed, now + 15 min).
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

## D. Weekly TikTok batch (Saturday, from 2026-10-31)

Vagh posts TikTok himself with TikTok's own scheduler (free, no Metricool). Each Saturday run prepares the **next Sunday–Saturday: 3 videos per day = 21 videos**.

1. Read `state/tiktok_log.json` (create `{"entries": []}` if missing): every video ever given for TikTok. Also already on TikTok (posted by Vagh or Metricool before November): quiz-fake-exchange-site, news-electrum-fee-bump, news-passport-phishing, and every `tiktok_short` / TikTok-provider entry in `state/log.json`. Never repeat any of them.
2. Pick 21 videos in this order: (a) shorts already published on YouTube (from `state/log.json`) that are not yet on TikTok, skipping news older than 7 days; (b) specs in `state/shorts_queue.json` (do NOT remove them from the queue — YouTube still uses them); (c) new specs written now into `specs/tiktok/<date>-<slug>.json`, from topics already covered in the long videos, alternating quiz ("Real or scam?") and tip formats, with a strong first-second hook (section B rules: short format, safe frame, 20–45 s). Spread topics so no two neighbours are the same topic.
3. Preview every spec, look at every sheet, fix problems, render. Rendering 21 shorts takes ~60 min: run renders in the background and wait.
4. Name the files `NN_<id>.mp4` in posting order (01–21) and upload them with `scripts/upload.sh` into the media branch (they land at its root; that is fine).
5. Write `TIKTOK_<sun-date>.md` (also uploaded to the media branch) with a table: NN, file name, post date, time **Asia/Yerevan** (09:00, 13:00 and 19:00 America/New_York converted; e.g. in November 18:00, 22:00, 04:00 next day), and the ready caption (hook sentence + 1 line + `#crypto #cryptoscam #bitcoin #fyp`, ≤ 150 characters). At the top: "In TikTok upload → More options → turn on 'AI-generated content'. Schedule each video at the time in the table."
6. Append the 21 ids to `state/tiktok_log.json` with their planned dates, commit and push (main branch).
7. End with a short summary in Russian for Vagh containing the direct link `https://github.com/Kosyanvag/channel-media/tree/media` and the name of the TIKTOK_*.md file.
