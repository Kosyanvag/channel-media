# Scene spec reference

A video is one JSON file in `specs/`. The engine turns it into voice, animation and a finished MP4:

```
python3 engine/make.py specs/<id>.json --preview   # contact sheets + thumbnail, fast
python3 engine/make.py specs/<id>.json             # full render -> build/<id>/final.mp4 (+ thumb.jpg)
```

## Top level

| key | meaning |
| --- | --- |
| `id` | file stem, also the build folder name |
| `format` | `long` (1920x1080) or `short` (1080x1920, must end up under 59 s) |
| `topic` | slug of the topic from `state/topics.json` |
| `voice` | Kokoro voice, always `blend` for this channel (`speed` defaults to 1.1; `camera` zoom defaults to 0.045, `false` to disable) |
| `publish` | `title`, `description` (may contain `{chapters}`), `tags`, `category`, `chapters` (one label per scene, long only; scenes sharing a label are merged) |
| `captions` | burned-in word-by-word captions: default on for `short`, off for `long`; `false` to disable, or `{"y": 1500, "size": 78, "color": "yellow", "words": 3}` |
| `thumbnail` | long only: `scene` index, `at` time ref, `shift` px to move the frame left, `x` centre of the text, `lines` [{text, y, size, color, glow}] |
| `scenes` | list of scenes |

## Scene

```json
{"name": "step1", "narration": ["Sentence one.", "Sentence two."], "elements": [...], "pad": 1.2, "hold": 0}
```

* Every sentence is voiced separately, so the animation can be keyed to it.
* `pad` seconds of silence after the last sentence (default 1.2). `hold` extra seconds at the very end (end screen).
* Scenes fade in and out automatically.

## Time references (`in`, `out`, `at`, `done`, `press`, state lists ...)

| ref | meaning |
| --- | --- |
| `0`, `2.5` | seconds from scene start |
| `"s3"` | when sentence 3 starts (1-based) |
| `"s3e"` | when sentence 3 ends |
| `"s3+0.6"`, `"s2e-0.3"` | with an offset in seconds |
| `"end"`, `"end-1"` | scene end |

Put the visual on the word it illustrates: a list item at the sentence that names it, a red flash on the sentence with the twist.

## Animated values

* Colour: a name (`green red yellow blue purple orange white muted gray card card2`), `"#rrggbb"`, or a timeline `[[0, "green"], ["s2", "red"]]` (0.4 s cross-fade).
* Number (x, y, scale, value): a number or a timeline `[[0, 0], ["s2+0.5", 100]]` (0.8 s ease).
* State (labels with colour): `[[0, "Pending", "yellow"], ["s3", "Paid", "green"]]`.

Every element accepts `in` (default 0), `out` (optional, fades out there) and `fade` (seconds).

## Canvas and safe areas

* Long: 1920x1080. Keep content inside x 120–1800, y 60–1030. `rule` sits at y 975, `label` at y 90, a `heading` at y ~150–230.
* Short: 1080x1920. Keep content inside x 60–960, y 120–1540 (YouTube covers the bottom ~380 px and the right edge). `label` at y 150.
* Typical long layouts: phone left (x 600) + text/bullets right (x 1110+); two cards side by side (x 330 and 1030, w 560); centred diagram.
* One idea per screen. Never stack more than ~6 things on screen at once.

## Element types

| type | keys |
| --- | --- |
| `section` | `kicker` (STEP / SCAM / MYTH / TIP), `num`, `title`, `color`. Full-screen chapter card; give it `out` at the 2nd sentence |
| `label` | `text`, `color`, `y` — small pill at the top |
| `heading` | `text`, `x`, `y`, `size` (64), `weight` (black/bold/semi), `color`, `glow`, `w` (wrap width), `anchor` (mm/lm) |
| `text` | same as heading, defaults size 40 semi |
| `tag` | `text`, `x`, `y`, `color`, `size`, `anchor` — outlined pill |
| `rule` | `text`, `kind` ok/bad/warn, `y` — big takeaway pill at the bottom |
| `bigtitle` | `text`, `sub`, `glow`, `underline` (colour or null), `y` — hook title |
| `person` | `x`, `y`, `scale`, `color`, `hood` (scammer), `label` |
| `arrow` | `from` [x,y], `via` [x,y], `to` [x,y], `color`, `width`, `draw` (s), `dashed`, `head`, `warn` (time ref → warning icon at middle), `traveler` `"coin"`/`"card"` or {kind, count, dur, in, color, symbol} |
| `icon` | `kind` check/x/warn/num/lock/unlock/coin/card/shield/messenger/chart_up/chart_down, `x`, `y`, `size`, `color`, `label`, `open` (time ref, lock opens), `n` (num) |
| `stamp` | `text`, `x`, `y`, `size`, `angle`, `color` — slammed rubber stamp |
| `flash` | `at`, `color`, `strength` — screen flash, pair with stamps / twists |
| `card` | `x`, `y`, `w`, `h`, `color`, `bg`, `lines` [{text, size, weight, color, glow}], `badge` {text, color}, `avatar` {color, name} |
| `bullets` | `x`, `y`, `gap`, `size`, `title`, `items` [{text, in, kind x/check/warn/num, color, glow}] |
| `checklist` | `x`, `y`, `w`, `row_h`, `items` [{text, in, done, kind}] — numbered rows that get ticked |
| `counter` | `x`, `y`, `size`, `prefix`, `suffix`, `decimals`, `value` (number timeline), `color` |
| `escrow` | `x`, `y`, `color`, `locked` [[ref, true/false]...], `coins` [show_ref, hide_ref], `label`, `sub` |
| `receipt` | `x`, `y`, `scale`, `title`, `status`, `rows` [[label, value]x4], `checks` [refs], `edit` [from_ref, to_ref] |
| `words` | `words` (seed phrase list), `x`, `y`, `w`, `cols`, `hide` (ref → words blur out) |
| `phone_grid` | `turn_from`, `turn_to`, `ratio`, `turn_color` — wall of phones turning red ("thousands of people") |
| `ring` | `x`, `y`, `rx`, `ry`, `color`, `shatter` (ref), `reform` (ref) — protective shield around a phone |
| `subscribe` | `x`, `y`, `click` (ref) — button with cursor click |
| `comment` | `text`, `y` — comment bubble |
| `endscreen` | placeholders for YouTube end-screen elements, last ~10 s of a long video |
| `phone` | see below |

### phone

```json
{"type": "phone", "x": 600, "y": 545, "scale": 0.95, "accent": [[0, "green"], ["s3", "red"]], "shake": "s3",
 "widgets": [...]}
```

Or `"screens": [{"in": 0, "out": "s4", "widgets": [...]}, {"in": "s4", "widgets": [...]}]` to switch apps.

Widgets stack top to bottom under the header; `button` is pinned to the bottom and `notification` slides over the top. Each widget may have `in` / `out`.

| widget | keys |
| --- | --- |
| `header` | `title` (app name, invented: CryptoApp, CryptoP2P, MyBank), `sub` |
| `chat_header` | `name` (state list for name + colour), `verified`, `sub` |
| `order` | `label`, `amount`, `who`, `status` (state list), `check` (ref) |
| `balance` | `label`, `value` (number timeline), `prefix`, `decimals`, `color`, `bg` |
| `bubbles` | `items` [{text, in, side l/r, color, thumb}] |
| `rows` | `items` [{label, amount, color, in}] — transactions / settings rows |
| `skeleton` | `rows` — grey placeholder lines |
| `code` | `digits`, `in`, `label`, `color` — SMS code boxes typed in |
| `text` | `text`, `size`, `color`, `weight` |
| `spacer` | `h` |
| `button` | `label` (state list), `press` (ref), `glow` |
| `notification` | `in`, `title`, `sub`, `color`, `icon` lock/warn/msg |

## Rules for good scenes

* Invented brands only (CryptoApp, CryptoP2P, MyBank, cryptoapp.com). Never a real exchange name or logo.
* Numbers in visuals must match the narration.
* Something changes on screen at least every 3–4 seconds.
* Always run `--preview` and look at every sheet before the full render: nothing overlapping, nothing cut off, no empty screen while the voice talks.
