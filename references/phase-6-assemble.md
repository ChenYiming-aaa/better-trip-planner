# Phase 6 — Assemble, self-check, deliver (the procedure)

Read this at the start of Phase 6, before the final `plan.geo.json` is written.
SKILL.md Phase 6 is the contract — inputs, outputs, and the gates that decide pass/fail;
this file is the whole procedure it points at. Nothing here is optional: the self-check
list runs in full, the acceptance bars are exit codes and eyes, and the exit criteria at
the bottom are ticked before the chat summary goes out.

Inputs: `plan.geo.json` assembled per references/output-template.md, plus Phase 0's
`prefs.theme` / `prefs.pictures` / `plan.lang`. Outputs, three things every time: (1) the
chat summary — route one-liner, total budget, the 3 biggest decisions made for the user;
(2) `trip-<theme>.html`; (3) `trip.kml` — plus the
gates `.ics`, always (the pre-departure ladder rows are date-locked gates).


## Assembly order

Assemble per references/output-template.md: overview → decisions made for the user →
booking checklist → flights/intercity table → day-by-day cards → hotels → budget
rollup → country brief.

## Cover title

**Cover title (bilingual)**: when the deliverable is a rendered page, pick or adapt a
poetic display title from references/cover-titles.md — zh 2-6 characters + an English
line, matched to the trip archetype (road-trip / island / mountain / city / coast).
Never ship a literal placeholder like "X国行"; never use the clichés on that file's
blacklist. Cite the allusion honestly (the source line in the subtitle or a small
credit line).

## Adversarial self-check

**Adversarial self-check** — run this list against the finished plan and **fix what it
catches silently**: 坐标纠错、行程衔接修正、里程重算、清单补全等修正直接体现在正文里。
**Do not write any self-check record** — no `meta.self_check`, no self-check line in
`decisions[]`, nothing about the fixes in the chat reply; the user sees only the
corrected plan:
- Closure scan: every anchor's closed-days vs its scheduled date (Mondays! holidays
  from Phase 1 — including "closed Tue when Mon is a holiday" rules), **and** the
  classes the holiday feed misses: festivals overlapping the window, seasonal
  operating windows, venue maintenance shutdowns, 民族节日与宗教礼拜时段 closures
  （清真寺/寺院开放时间）(scheduling.md §Traps). Rain alternatives get scanned too — an alternative
  that is closed on the day it backs up is the bug this scan exists to catch.
- Open-jaw direction consistent across flights, hotels, and day order
- Arrival/departure days respect Phase 2 §3; airport buffer = 2 h domestic + real
  city→airport transfer time
- Every intercity leg: plausible duration; 值机/安检按 2 h 预算； rail connections ≥ 30 min — except a **timed meet** (a 景交车/游船 that waits for the
  train, e.g. 张家界火车站 → 森林公园班线车)：keep it, name it as
  a meet in the hop note, and give the next timed ticket the slack instead
- Last-entry time vs planned arrival for each anchor
- Timeline checks from scheduling.md §verification: chain arithmetic (block start ≥
  prev end + hop + buffer), day walking totals ≤ 8 km, late hops vs last departures,
  golden-hour blocks vs actual sunset — and every sunrise / sunset / dark-start time
  in the prose was written **after** `sun --write`, matching `days[].sun` (the
  script exited 0; any `sun_stop` override is on the right day); `route_tools check`
  exits 0 (no BROKEN or SUSPICIOUS hops survived into the render)
- 跨零点日期归属（红眼航班/夜班火车"次日到达"的 day-number arithmetic）
- No day exceeds pace; **an intercity moving day carries ≤2 anchors, and only when
  the bags are solved before the first anchor (checked / stored / hotel-held);
  otherwise 1** (same sentence in scheduling.md §Day types)
- Every price has source + as-of date; every bookable line has a link — and the
  link carries its dates and a disambiguated place name; hotel rows state explicit
  local check-in→check-out calendar dates, with past-midnight-arrival and
  date-line nights flagged (output-template §Booking-artifact conventions)
- **Language**: `plan.lang` matches the language the user asked in, and every
  reader-facing string in the plan (day titles, notes, tips, checklist rows,
  decisions, hotel blurbs) is in that language — an English fragment copied verbatim
  from a source into a zh plan gets translated, not shipped. Proper nouns stay in
  their native form with a gloss where useful (拙政园 Humble Administrator's
  Garden); machine fields are exempt (`stops[].query` stays geocoder-friendly,
  `kind`/`tag`/`verify` keep their
  English enum words)

## Deliver

**Deliver — the deliverable is a themed page, never a plain text one.** Render
`plan.geo.json` through the theme chosen in Phase 0 (`prefs.theme`, default
**illustrated**) — see *Themed renders* below — and hand over: a chat summary (route
one-liner, total budget, the 3 biggest decisions made for the user) + `trip-<theme>.html`, one self-contained, phone-friendly
file with its own share/export buttons and the appendix (checklist, legs, hotels,
budget, brief). Publish through whatever artifact / file hand-off tool the harness
has (in Claude Code: Artifact, else SendUserFile); otherwise save the file and give
its absolute path. Ship the trip KML (`scripts/route_tools.py kml plan.geo.json -o
trip.kml`) alongside for offline map apps, and the gates `.ics` — always, because the
ladder rows are date-locked gates (output-template.md §Pre-departure re-check ladder
and §Booking-artifact
conventions) — `python3 scripts/route_tools.py ics plan.geo.json -o gates.ics` writes it
from the checklist rows (ISO dates or `T-N` markers in `deadline`; bump `--sequence`
on every plan change). Before any renderer runs, **`python3 scripts/plan_lint.py
plan.geo.json --strict` must exit 0**: it is the machine gate for what the plan says —
brief present and in canonical order, no placeholder or "awaiting" text, art placeholders
filled, the gates `.ics` and `trip.kml` beside the plan,
every day with at least one stop and a `sun` that `sun --write` wrote. The gate
tolerates nothing: any FAIL line is fixed before rendering, and `sun` 字符串永远
手写补不了——缺哪天就修 stop/tz 后重跑 `sun --write --only DATE`。 `check` proves the geography and `qc.py` the HTML; neither looks at the
words. The plain
`scripts/render_plan.py plan.geo.json
-o trip.html` page (printable, checkbox checklist, offline route sketch per day) is an
**extra** — add it when the user asks for a printable/plain version, or as the last
resort if the theme renderer still fails after one honest fix attempt (then say so in
the summary). **`plan.geo.json` is the single editable source** for all of it — every
command above reads that one file — so a later "把第 3 天挪到乌镇" is a JSON edit
plus geocode → check → links → kml → render, not a rewrite. The page chrome (section
names, buttons, pills, weekdays) speaks `plan.lang` (set in Phase 0, `zh` default);
`--lang zh|en` on any renderer overrides it, plan content prints as written.

## Themed renders

**Themed renders** — the same `plan.geo.json` through one of the seven themes in
`themes/`. Themes: **illustrated 插画** (a painted book on paper — the default) ·
**clay 黏土** (one continuous clay landscape with a road) · **noir 夜航** (a single
night-negative tracking shot) · **glass 玻璃** (liquid-glass panes over crossfading
photos) · **journal 手账** (a vintage travel journal: tape, stamps, polaroids) ·
**zine** (torn riso-poster collage) · **splash 闪屏** (game-splash floating islands,
chained sky gradients). `render_picker.py` renders a one-page style chooser of all of
them. Flow:
1. Write `<plan>.art.json` next to the plan (contract: `themes/ART-SCHEMA.md`) — the
   **common** block first (cover poem title from references/cover-titles.md, `kick`,
   `home`, `end`, and per day `theme` 4 chars / `en` / `mark`), then one block per
   theme you render. Pictures — **素材库优先**，by `prefs.pictures` (Phase 0):
   - **stock — first choice: the stock kit has a suitable picture → use it, no
     generation.** 先跑 `stock_art.py` 看逐日匹配结果（country match / day keyword
     match / generic props，见下）；素材库能覆盖封面与每日配图，就不要调用生图。
     Two commands, both from the skill root (absolute paths when your cwd is the
     trip folder):
     ```
     python3 <skill>/themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
         # also --theme clay · --lang zh|en · --country ISO2 (when the plan's own words
         # do not name the destination) · --index PATH · --force (overwrite)
     python3 <skill>/themes/render_theme2.py plan.geo.json --art plan.art.json \
         --assets <skill>/themes/assets/stock -o trip-illustrated.html
         # --assets is REQUIRED in stock mode: data_uri() does not look inside
         # themes/assets/stock on its own — without it the page renders, qc passes,
         # and the stock pictures are silently missing. The script prints this exact
         # render line on its last stderr line; paste it.
     ```
     `stock_art.py` builds the picture side of the art file from `themes/assets/stock/`
     (region cover paintings, landmark and generic-scene cut-outs, matched to the
     plan's country and each day's stops; `themes/assets/stock/README.md`) plus the
     shared library's same-country pictures and generic props. It leaves the **words**
     to you — fill `cover` title (references/cover-titles.md), each day's `theme` /
     `en` / `mark`, captions and the closing line before rendering; a page shipped
     with the script's placeholders is a defect. **`cover.credit` and `end.fine` stay
     EMPTY** — pages never carry any picture-source or capability note; a poem
     citation (source line) is the only thing that may occupy `cover.credit`.
     `prefs.pictures` is set to `stock` the moment `stock_art.py` runs.
   - **native / key — only when the stock kit has NO suitable picture AND the agent
     has native generation (or a configured key).** The cover / hero / title sticker /
     terrain bands are destination scenery and are ALWAYS generated for this trip, in
     the theme's own style — priority: the trip's actual sights (西安城墙, 长城) > a
     national landmark > a neutral scene, but never blank and never
     another trip's band (a page once opened on a default band of a different
     city — a logged defect). The same ladder applies to `end.hero` / the tail cover,
     with one twist: that picture is the **return to the departure city** (home skyline
     at landing, not another destination view) — generated for this trip too. "Reuse
     first" applies only to generic props: `themes/assets/` 通用件（tape、seal、
     ticket 等道具）
     lists what any trip may use; generate the rest — **with the agent's own native
     image generation if it has one (no key to configure; same specs, same
     prompts-as-style-anchors, same split/cutout/webp/manifest steps — ART-SCHEMA.md
     §Generator choice), otherwise `gen.py` 走境内生图（dashscope 通义万相 /
     siliconflow Kolors）** — using the
     sheet recipe in ART-SCHEMA.md (title stickers: one centred sticker, symmetric
     lines, no icons inside the letters), then `towebp.py`, and keep the webp beside
     the plan (or pass `--assets DIR`). 定制生成后同样**不写任何图片来源说明**。
2. `python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html`
   (`--art F|none`, `--assets DIR`, `--lang zh|en`); a missing art file must still
   render. Renderer files: illustrated = `render_theme2.py`, clay = `render_clay2.py`,
   noir = `render_noir2.py`, glass = `render_glass2.py`; journal / zine / splash use
   their own name (`render_journal.py` …). All seven themes and the picker render in **en** as well as zh: the UI
   shell (buttons, tags, section names, weekdays, cover fallbacks) follows
   `plan.lang` / `--lang`, art copy renders in whatever language it was written
   (ART-SCHEMA.md §language; English cover titles: references/cover-titles.md).
3. `python3 themes/qc.py trip-<theme>.html` must exit 0, then
   `themes/xprobe.sh trip-<theme>.html module '#d5' out.png` and **look at the PNG**
   — a green probe title is not proof; blank icons and cropped tails only show visually.
   No headless Chrome in this environment → open the HTML in whatever browser tool
   you have (a browser pane may refuse `file://` — serve the folder with
   `python3 -m http.server` and open `http://localhost:8000/trip-<theme>.html`) and
   look at the cover and one day; if you have none, say so in the summary.
Each of the seven themes carries its own share buttons (保存这一天 / 保存附录 /
生成长图 — Save this day / Save appendix / Save long image in en), offline, no
dependencies; noir and glass export day modules only.
Details, per-theme limits and the new-theme
manual: references/themes.md.


## Exit criteria — tick every line before the chat summary goes out

- [ ] `python3 scripts/plan_lint.py plan.geo.json --strict` exited 0 before rendering
      (brief present and in order, no placeholders, art filled, `.ics`
      and `trip.kml` beside the plan, a stop and a `sun --write` string on every day) —
      任何 FAIL 行都修到绿，不手写 `sun` 字符串。
- [ ] Adversarial self-check ran in full and was fixed **silently** — 修正已体现在正文，
      且任何地方都没有自检记录（`meta.self_check`、`decisions[]`、聊天回复）。
- [ ] `route_tools check` exited 0 before rendering; every sunrise / sunset / dark-start
      time in the prose was written after `sun --write` and matches `days[].sun`.
- [ ] `plan.lang` matches the user's language; no untranslated source fragments.
- [ ] Every price carries source + 查证日期（写成"2026-10-02 查证"这类自然中文，
      不用 `as-of`）: every bookable line has a link that carries
      its dates and a disambiguated place; hotel rows state check-in→check-out dates.
- [ ] `trip-<theme>.html` rendered through the Phase 0 theme; `themes/qc.py` exited 0;
      the export probe PNG or the page in a browser was looked at (none available → the
      summary says so).
- [ ] Cover title from references/cover-titles.md — never a placeholder, never a
      blacklisted cliché; the allusion is credited.
- [ ] 图片策略（素材库优先）已执行；页面与聊天回复中**没有任何**图片来源或能力说明，
      且每个脚本占位词都换成了真实文案。
- [ ] 语言规范（output-template.md §语言规范）通过：无 `as-of`/`T-N`/`est`/`OTA` 等
      内部代号，无生硬措辞，全部面向用户的文字是自然的用户语言。
- [ ] `brief` keys in the canonical order with the required cards present
      (output-template.md §Brief templates), every card titled in `BRIEF_TITLES`;
      `brief.weather` and every weather line carry the mode (forecast / normals /
      climate model) + as-of.
- [ ] Phase 1 still holds at delivery: `brief.safety` line 0 carries level · source ·
      date and no base sits in an avoid area; 健康提示按 chinacdc.cn / 属地卫健委
      页面落实；
      the hazard gate exists when the window hits a season; the 高反/健康咨询 row
      exists when the health page recommends anything (phase-1-brief.md exit criteria).
- [ ] The pre-departure re-check ladder (T-14 / T-7 / T-3 / T-1) closes the checklist
      and shipped as the gates `.ics`.
- [ ] **出发前 24h 检查（境内版交付项，随 T-1 行写入 checklist）**：身份证原件
      （全员，与门票/车票同一证件）· 各景区预约成功截图（二维码/订单号）·
      12306/航司值机确认 · 充电宝（共享充电宝节假日常缺、景区归还点少）·
      自驾线加油/充电桩规划（高德充电地图，服务区充电节假日排队）·
      离线包（高德/百度离线地图包下载，山区无信号）· 天气预警复查
      （中央气象台 + 属地，橙红信号触发改期流程见 phase-1-brief.md）。
- [ ] `trip.kml` shipped (the gates `.ics` is covered by the ladder line above — every
      plan has gates now).
- [ ] The chat summary carries the route one-liner, total budget and the 3 biggest
      decisions made for the user.
