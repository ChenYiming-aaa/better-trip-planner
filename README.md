[English](README.md) | [简体中文](README.zh-CN.md)

> **Domestic-China-only edition** — this directory is the domestic-travel-only branch of
> trip-planner-skill: destinations must be in mainland China (Hong Kong / Macao / Taiwan
> included in the stop rule); map links are 高德/百度 only, geocoding uses the Amap API
> (`AMAP_KEY`) with Baidu fallback (`BAIDU_MAP_AK`), flights/trains ship as Ctrip/Trip.com/
> Qunar/12306 deep links (`flight_scan.py`), sun times come from a local NOAA solar model
> (zero network), budgets are RMB-only (no FX), and image generation goes through
> DashScope/SiliconFlow (the OpenRouter path was removed). **All video capability (the
> portal theme, genvideo, any embed) has been removed** — deliverables are image-and-text
> only. Adaptation record: [`ADAPTATION.md`](ADAPTATION.md).

# Trip Planner Skill (domestic China edition)

**One sentence in, a verified, hour-by-hour, bookable-as-written domestic itinerary out —
delivered as a designed page in one of seven visual themes.** An open-format Agent Skill
(`SKILL.md`) that runs inside the coding agent you already use — Claude Code, Codex,
Gemini CLI, Cursor, GitHub Copilot, OpenCode, Qwen Code, Goose, Kiro, Roo Code, or any
host that loads Agent Skills: opening hours, prices and holidays are looked up with
tools, never guessed; every booking line ships with a link; nothing is ever booked or
paid on your behalf.

![Agent Skills: open format](https://img.shields.io/badge/Agent%20Skills-open%20format-0A7B83.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Domestic-only](https://img.shields.io/badge/scope-destinations%20in%20China-CE0000.svg)

## Example

[`examples/china-2026/`](examples/) ships one complete worked example: Shanghai → Beijing
→ Xi'an → Beijing → Shanghai, 8 days, from a domestic traveller's point of view
(ID-card entry, 12306 real-name tickets, venue reservations), with two finished themed
pages:

- **clay 黏土** — one continuous clay landscape with a road threading the milestone
  stones. Render: `python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html`
- **splash 闪屏** — a game-splash screen stretched into a scroll: floating day-islands
  under chained sky gradients.

Both pages are self-contained HTML — double-click to open, zero network requests.
`examples/china-2026/` also carries the trip's `gates.ics` (the T-14/T-7/T-3/T-1
pre-departure ladder) and `trip.kml` (40 numbered pins for offline use in Organic Maps).

The plain, un-themed printable page (`scripts/render_plan.py`) is an extra, never the
default deliverable; `themes/render_picker.py` renders a one-page style chooser linking
every rendered edition of a trip as `<prefix>-<theme>.html`.

## What you get

Say *"Yunnan, 8 days in October, mid budget, nature and old towns."* The skill gives you:

- **One intercity route** — 2–3 skeletons to pick from, then flight/rail deep links
  (`flight_scan.py`: Ctrip/Trip.com/Qunar flights + Ctrip rail; there is no keyless fare
  API in China, so prices are checked by opening the links), plus a rail-vs-fly verdict
  per leg.
- **An hour-level plan for every day** — hours and closure days tool-checked, reservation
  policies (Forbidden City / Shaanxi History Museum / Mogao Caves timed real-name slots)
  on the checklist, a tappable Amap/Baidu link on every hop.
- **A designed page, not a wall of text** — the plan renders through one of **seven theme
  renderers** (default **illustrated 插画版**) into one self-contained, phone-friendly
  `trip-<theme>.html`. All seven themes are image-and-text, with offline share-image
  buttons (save this day / save appendix / save long image; noir and glass export day
  modules only).
- **`plan.geo.json`, the single source of truth** — the themed page, the map links and an
  offline KML for Organic Maps all come from this one file.
- **Hotel shortlists per base** (dated deep links, never invented rates), an **RMB-only**
  budget summary, and a **deadline-sorted booking checklist** (reservations / ticket
  drops / 12306 release instants first).
- **A pre-trip brief** — emergency numbers (110/120/119/122/12301), the national
  weather-centre warning line, altitude-sickness guidance, holiday/makeup-workday
  collisions, payment layering, offline-map preparation — all domestic sources.
- **Pictures matched to what your agent can do** — a three-step ladder, checked silently
  before styles come up: the agent's **native** image generation → a domestic **key** in
  the environment (DashScope / SiliconFlow) → the built-in **stock kit**. The last step
  still delivers a themed page and says so.

It does not: book, pay, hold seats, or fill in personal information. You click the links.

## Quick start

**1. Install** — Agent-Skills hosts discover skills by directory: drop this folder into
your skills directory (Claude Code: `~/.claude/skills/trip-planner`). Optional dependency:
Pillow (asset pipeline); everything else is Python 3.9+ standard library.

**30-second test** — no keys, no agent, from this directory:

```bash
python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html \
  && python3 themes/qc.py china-clay.html    # a themed page + its QC (exit 0)
```

**2. Plan a trip** — one sentence to your agent. Travel requests trigger the skill on
their own, or invoke it explicitly:

```
/trip-planner 云南 8 天，10 月出发，中等预算，自然风光和古城，日期前后可挪 2 天
```

The page's UI language follows the language you asked in (`"lang": "zh"|"en"`; every
renderer accepts `--lang`). Four modes:

| Mode | Trigger | What runs |
|---|---|---|
| **Full trip** | "帮我规划云南 8 天" | All phases: intake → brief → skeleton → transport → day plans → hotels → assemble + self-check |
| **Single day** | "我们在杭州有一天" | Holiday/festival check + one day + self-check; skips transport and hotels |
| **Gap fill** | "2 hours free near X" | 2–3 options within a 15-minute radius, each with walk times, map links, turn-back points |
| **On-trip replan** | "train missed / downpour" | Rebuilds only the affected day from the downgrade tags |

**3. The designed page** — render through the theme picked at Phase 0 (default
**illustrated** = `render_theme2.py`); a plain text page is never the deliverable:

```bash
python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html   # theme2 clay2 noir2 glass2 journal zine splash
python3 themes/qc.py trip-<theme>.html                                # exit 0 = clean; exit code = FAIL count
```

The art contract is [`themes/ART-SCHEMA.md`](themes/ART-SCHEMA.md); every field is
optional and an empty art file must still render. Pictures resolve `--assets` → art dir →
plan dir → `themes/assets/`.

**4. Pictures: a three-step ladder, best first (image-and-text only — no video step).**

1. **Native generation** — if the agent generates images natively, use that: art painted
   for this trip, no key to configure (same downstream `split_sheet.py` → `cutout.py` →
   `towebp.py` → trip-manifest steps; contract in ART-SCHEMA.md).
2. **A domestic key** — otherwise set `DASHSCOPE_API_KEY` (Alibaba DashScope Wanxiang)
   or `SILICONFLOW_API_KEY` (SiliconFlow Kolors) in the environment; `themes/gen.py
   --provider auto` detects it. Both are mainland-direct with domestic billing.

   ```bash
   python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json   # --dry-run first
   ```

3. **Stock kit** — neither available: pictures come from the bundled kit and the page
   still ships as a themed page:

   ```bash
   python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
   python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
           --assets themes/assets/stock -o trip-illustrated.html   # --assets is REQUIRED here
   ```

   `stock_art.py` picks covers per destination and one hero per day by keyword scoring;
   the words (cover title, per-day titles, captions) stay with the agent, and the
   stock-kit notice is written into the page's fine print. Coverage: **illustrated**
   complete, **clay** works; the other five themes need generated pictures. Details:
   [`themes/assets/stock/README.md`](themes/assets/stock/README.md).

Destination-bound art (covers, heroes, title stickers, terrain bands) is always generated
for the trip; generic props (tape, seals, tickets, clouds) are shared.

## How it works

**Pipeline.** `SKILL.md` is the script the agent follows: Phase 0 intake (ask only what
is missing, one message) → Phase 1 pre-trip brief (emergency numbers, the national
weather warning line, holiday/makeup API, weather, money layering) → Phase 2 route
skeleton → checkpoint → Phase 3 transport (`scripts/flight_scan.py`: flight/rail deep
links) → Phase 4 per-city day plans (parallel city subagents, fixed search budgets) →
Phase 5 hotels → Phase 6 assembly, adversarial self-check, delivery. At most three
interactions, usually two.

**One file, one source of truth.** `plan.geo.json` is written once and read by
everything: `scripts/route_tools.py` (`geocode` · `check` · `links --write` · `kml` ·
`sun`) builds the map links and the KML from its `stops`; `scripts/render_plan.py` renders
the plain HTML; every theme renderer reads the same file plus its `art.json`. Schema
template: [`assets/plan.example.json`](assets/plan.example.json) — copy it, fill the
PLACEHOLDERs, render.

**Hard rules** (distilled from [`SKILL.md`](SKILL.md) and `references/`):

1. Never book, pay, hold, or fill in personal data — links and checklists only.
2. Prices and hours come from tools, never memory; an uncheckable price is written
   "—, check the link".
3. Keyless first, browser second; never curl OTAs or airline sites.
4. Search budgets are explicit, in every subagent's prompt.
5. Estimates are labelled: transport durations ship as `(est.)` ranges unless verified.
6. Beyond ~3 months nobody publishes that day's hours — verify the seasonal pattern,
   stamp "as of {date}", and put a re-check row on the checklist.
7. The plan passes its self-check before delivery: closure scan, chain arithmetic,
   last-entry times, walking totals.
8. **Destinations must be in mainland China**; international itineraries are out of scope.

**Data sources** — mainland-direct and keyless-first; prices are for comparison, the deep
links in the plan are the source of truth
([`references/data-sources.md`](references/data-sources.md)):

| Source | Used for | Notes |
|---|---|---|
| Amap restapi (`AMAP_KEY`) | venue coordinates (geocode, first pick) | GCJ02 auto-converted to WGS84; free key |
| Baidu geocoding v3 (`BAIDU_MAP_AK`) | geocode fallback | same conversion, automatic |
| Amap/Baidu web deep links | per-hop navigation | amap default, H5 opens the app |
| 12306 / Ctrip / Qunar / Trip.com | flight & rail deep links | `flight_scan.py`; fares checked by opening the link |
| timor.tech + State Council calendar | public holidays & makeup workdays | community API — verify against official notices |
| Open-Meteo | date-matched weather & climate normals | first call may take ~10 s |
| NMC nmc.cn / 12379 | warnings & hazard seasons | orange/red warning = stop-the-pipeline line |
| Local NOAA solar model | sunrise/sunset/civil dawn | zero network, the only sun path in this edition |

## Compatibility

- **A format, not a product integration.** An Agent Skill — one `SKILL.md` script plus
  `references/`, `scripts/` and `themes/`. Any host that loads Agent Skills can run it;
  the scripts are Python 3.9+ standard library.
- **What a host needs.** A shell with Python 3.9+, plus web search/fetch tools (the
  brief, day-plan and hotel phases verify online). Nice to have: subagents (Phase 4),
  browser tooling, native image generation (else a domestic key, else the bundled stock
  kit — the page is themed either way).
- **Any model.** The skill is instructions plus scripts; the model in your host does the
  executing.

## Repository layout

```
README.md  README.zh-CN.md    this page, English and Chinese
THIRD-PARTY-NOTICES.md        full licences for the bundled font & icons (Caveat OFL, Lucide ISC)
SKILL.md                      the script: phases, hard rules, quick modes (domestic gate at Phase 0)
ADAPTATION.md                 adaptation record: restricted-resource list, replacements, the domestic-only conversion log
references/
  data-sources.md             domestic data sources + URL recipes, with fallback chains
  scheduling.md               dwell times, buffers, day types, traps, verification checklist
  navigation.md               Amap/Baidu links, hop-row format, verify-vs-estimate policy
  output-template.md          city-block hand-off format + final deliverable structure
  phase-0-intake.md           Phase 0: core/optional facts, destination gate, intake message, prefs, picture-capability check
  phase-1-brief.md            Phase 1: emergency card, warning line, health line, holidays, hazard seasons, exit criteria
  phase-3-legs.md             Phase 3: flight/rail/self-drive sources and fields, exit criteria
  phase-4-days.md             Phase 4: city-agent contract, six steps per city, route_tools order, exit criteria
  phase-6-assemble.md         Phase 6: assembly, adversarial self-check, delivery, themed-render flow, exit criteria
  cover-titles.md             bilingual poetic cover-title library + cliché blacklist
  themes.md                   the theme manual: seven themes, adding one, defect checklist
scripts/
  flight_scan.py              flight/rail deep-link generator (keyless, zero-network; Ctrip/Trip.com/Qunar + Ctrip rail)
  route_tools.py              geocode → distance check → Amap/Baidu links → KML → gates .ics → sun (local model)
  plan_lint.py                content gate before rendering (--strict exit code = FAIL count)
  render_plan.py              plan JSON → self-contained printable HTML
themes/
  README.md                   what is here, three commands, where pictures come from
  render_theme2.py …          seven renderers: theme2(illustrated)· clay2 · noir2 · glass2 · journal · zine · splash
  render_picker.py            the style-chooser page (links <prefix>-<theme>.html)
  theme_common.py             shared helpers, i18n, offline share-image engine
  qc.py  xprobe.sh  xt.sh     static QC · headless export probes
  gen.py                      domestic image fallback (DashScope Wanxiang / SiliconFlow Kolors)
  stock_art.py                no generator, no key: assemble art.json's picture side from the stock kit
  towebp.py cutout.py split_sheet.py build_manifest.py
                              asset pipeline (png→webp, cut-outs, sheet splitting, manifest)
  ART-SCHEMA.md               the art.json contract (the only copy)
  assets/                     the picture library: webp assets, Caveat font, manifest.json
    stock/                    the stock kit: region covers + generic/landmark cut-outs, index.json, README.md
assets/plan.example.json      schema template (domestic sample data) — copy, fill PLACEHOLDERs, render
examples/
  README.md                   the china-2026 example: two themes, render commands, KML/ICS
  china-2026/                 <plan>.geo.json + <plan>.art.json + two themed pages + gates.ics + trip.kml
```

## Verification

- **Static QC** — `themes/qc.py page.html` checks the offline contract (no network, no
  external requests), no-JS survival, print, focus order and link hygiene; exit code =
  FAIL count.
- **Byte-identical regression** — the example pages re-render byte for byte with the
  commands in [`examples/README.md`](examples/README.md).
- **Export probes** — `themes/xprobe.sh` / `xt.sh` drive headless Chrome to click the
  page's real share button and rasterise the output, so export defects are seen, not
  assumed.
- **Content gate** — `scripts/plan_lint.py --strict`: brief cards present and ordered, no
  placeholder text, the self-check line, a stop and a `sun --write` string on every day;
  exit code = FAIL count.

## Status & limitations

**Requirements.** Python 3.9+; standard library only, plus optional Pillow (asset
pipeline). Rendering any theme with the bundled library or stock kit needs no keys.

**Limitations & non-goals.**

- **Domestic itineraries only.** The destination gate sits at Phase 0 (Hong Kong / Macao /
  Taiwan included in the stop rule); international sources and entry points were removed
  outright.
- **Image-and-text deliverables only.** No video generation, embedding or display of any
  kind.
- **Not real-time.** It plans; it does not track delays or rebook.
- **Prices move.** Every number carries an as-of date — that is the point.

## Credits

- [Caveat](https://fonts.google.com/specimen/Caveat) (SIL Open Font License 1.1) — the
  handwriting webfont embedded in the journal theme (`themes/assets/caveat-vf.woff2`).
- [Lucide](https://lucide.dev/) (ISC) — the icon sprite in `themes/lucide-icons.json`.
  Full licences: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
- Amap Open Platform / Baidu Maps Open Platform — geocoding and navigation deep links
  (user-supplied free keys).
- Open-Meteo, timor.tech — weather and holiday data.
- Image generation: Alibaba DashScope Wanxiang / SiliconFlow Kolors (mainland-direct).

## Licence

MIT — see [LICENSE](LICENSE).
