# channel-media

Automated faceless YouTube channel: crypto safety and beginner how-tos.

* `PIPELINE.md` — what a scheduled run does, step by step (long videos Mon/Wed/Fri, one short every day).
* `ELEMENTS.md` — the scene spec language used to animate videos.
* `engine/` — renderer (Pillow + ffmpeg), voice (Kokoro blend of am_michael + am_fenrir), music bed.
* `specs/` — one JSON per video; `specs/shorts/` — queued shorts.
* `state/` — topic backlog, publish log, shorts queue.
* `scripts/` — setup, media upload (the `media` branch holds only the files being published), publish metadata.

Quick start: `bash scripts/setup.sh && python3 engine/make.py specs/2026-10-26-first-bitcoin.json --preview`
