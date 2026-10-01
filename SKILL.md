---
name: trip-planner-cn
description: >-
  境内旅游计划全流程制作（仅支持中国大陆境内行程 / domestic-China-only build）:
  把"我想去某地玩 N 天"变成经过核验、逐项可预订的行程——城市路线骨架,高铁/机票/自驾
  交通决策(12306 与携程/Trip.com/去哪儿深链),小时级每日时间线(开放时间、停留时长、
  假日调休冲突、高德/百度逐跳导航链接+离线KML),按街区筛选的住宿,预算汇总,带深链的
  预订清单,以及把成品渲染成设计页面(七种主题:illustrated / clay / noir / glass /
  journal / zine / splash — 插画/黏土/夜航/玻璃/手账/Zine/闪屏,全部纯图文、无视频)。
  Use this whenever the user asks to plan a domestic trip (境内游/周边游/自驾游/高铁游),
  排一个旅行日的小时级时间表,填一个空闲时段("我在 X 附近有 2 小时空档"),or turn a
  finished plan into a designed page, or asks 旅行规划/行程安排/机票火车票比价/去某地玩
  N 天怎么安排/把行程做成好看的网页 — even if they only mention one piece, the playbook
  and verification rules here still apply. 境外行程不在本 skill 范围内(被明确排除)。
---

# Trip Planner（境内版 · domestic-China only）

把模糊的旅行想法变成一份用户可以逐条点链接核验的行程。交付物是**经过核验、可预订**的,
不是种草文:每个价格和开放时间都带来源 + as-of 日期,或显式"点链接核对"标记。AI 旅行
工具死于过期数据而不是文笔——修掉这一点就是本 skill 的工作,所以核验本身就是工作本体。

**境内版边界(硬边界):本 skill 只做中国大陆境内的行程。** 一切境外旅游功能——护照/
签证、国际机票、外币汇率、领事与外国预警、境外地图/搜索服务——均已删除,不存在任何
入口或选项;用户提出出境需求时,明确告知本 skill 仅支持境内行程。全部页面为图文形式,
视频展示/嵌入/生成能力已整体移除。

## Hard rules

1. **Never book, pay, hold, or enter personal data anywhere.** Produce deep links and a
   checklist; the human books. This is what keeps the skill safe to run autonomously.
2. **Prices and hours come from tools, never from memory.** Model memory is fine for
   geography and "what's worth seeing"; anything bookable or closable gets checked.
   国内没有免钥票价 API(携程/去哪儿不开放公开票价端点):机票价格一律写
   "—, 点链接核对" 并给 `flight_scan.py` 深链;火车票价可用 12306/携程火车票公开价格。
   绝不猜价。
3. **Cheap before expensive**: bundled script + keyless APIs first (see
   references/data-sources.md), browser automation second and only for what scripts
   can't get (酒店 OTA 实价、冷门场馆). Never curl OTA/airline sites —
   they bot-block instantly; browser pane only. Pace requests like one polite human.
4. **Search budgets are real**: ~25 web searches for your own orchestration work
   (交通、假日调休、酒店、汇总) — separate from, not inclusive of, the ≤8 written into
   each parallel city subagent's prompt. Unbounded research agents hang and burn money,
   so the cap goes in the prompt every time. Budget exhausted → ship with the
   least-verified items flagged rather than digging further.
5. Reply in the language the user asked in; the plan's money is **人民币**(境内行程无
   汇率环节)。页面语言 `lang` 默认 zh(`--lang` 可覆盖),计划内容同样用用户的语言写。
6. Track the phases as todos (whatever task/todo tool the harness has; none → a
   short checklist at the top of your working notes) so a long plan survives
   interruptions and stays visible.
7. **交付纯度——只给用户真正关心的行程内容，不留内部痕迹**（细则见
   references/output-template.md §语言规范）:
   - **静默自检**：坐标纠错、行程衔接修正、里程重算、清单补全等自检修复在后台完成，
     修正结果直接体现在正文；不写自检记录、不向用户展示修复过程。
   - **语言规范**：面向用户的文字全部用自然中文（用户用英文则英文），不用 `as-of`、
     `est`、`OTA`、`verify`、`pattern`、`D1/D5` 之类内部缩写（网址与代码除外）；
     `T-14/T-7` 等代号写成"出发前两周（2026-10-12 前）"这类用户能直接读懂的形式。
   - **措辞**：不用"钉死/可砍/开门冲"等生硬词——用"必做/可跳过/开门就去"。
   - **图片来源与能力说明一律不出现**（详见 Phase 0 图片策略门）。

## Interaction contract

Three moments at most, usually two: (0) **one intake message, only if a core fact is
missing and can't be inferred** (Phase 0 — most requests need none); (a) after Phase 2 —
present 2-3 route skeletons, get a pick; (b) final delivery. Everything else runs without
questions. If the user says "一次到位 / don't ask, just plan" or the session is clearly
headless, skip (0) and (a): assume, pick the best skeleton yourself and state every
assumption prominently at the top of the output.

## Quick modes (no full pipeline)

- **Gap filler** — "我在 X 附近有 2 小时空档": offer 2-3 options within a 15-min
  radius, one per energy level (a sight / food / a sit-down), each with walk time, a
  map link, a turn-back deadline, and — the one thing worth a search — confirmation
  that it is open right now. ≤3 searches; answer in minutes, not a report.
- **Single day** — "我们在某城有一天,怎么玩?": run Phase 1's holiday + 调休
  check, Phase 4 for that one day, and the Phase 6 self-check. Skip route
  skeletons, transport scans and hotels entirely; read scheduling.md and navigation.md and
  leave the rest closed. This is the most common request that is not a whole trip.
- **Live replan** — "赶不上车了 / 下暴雨": rebuild only the affected day
  from its degradation tags (`[skippable]`/`[swap→…]`/late_cut line) instead of
  re-planning the trip. `[pinned]` blocks hold; `[opener]` may move but costs a queue;
  re-verify only the hops that changed.

## Phase 0 — Intake (one message, or none)

**Read `references/phase-0-intake.md` now, before you decide whether to ask the user
anything** — it is the whole procedure for this phase (what counts as a core fact, the
intake message format and its rules, what goes into `prefs`, the picture-strategy
check, the style line and the plan language, the exit criteria). This section is only
the contract; do not compose an intake message from memory of the format.

Inputs: the user's request and anything said earlier. Outputs: the plan's top-level
`prefs` block and `lang`, `prefs.pictures` (stock | native | key | custom), the assumptions block
for checkpoint (a) — and at most one intake message.

Gates — these decide pass/fail and do not move into the reference file:
- **One message, or none.** Ask only when a core fact (出发地 · 目的地 · 何时/多久 ·
  页面风格) is missing **and** cannot be inferred; ask for everything in
  ONE message in the intake format (core first, optional after, each optional line
  with its default, one "all defaults" line); anything the user already stated is settled and
  never re-asked; never a follow-up "just one more thing".
- **目的地必须在中国大陆** — 用户给出境外目的地时,告知本 skill 仅支持境内行程并停止;
  目的地为港澳台时同样停止(本 skill 的地图/交通/预约体系不覆盖)。
- **The picture-strategy check runs silently before styles are mentioned**: 素材库
  优先——先用 `themes/assets/stock`（含逐日匹配的 `stock_art.py`）为行程选图，**素材库
  有合适图片就直接用，不调用生图**；仅当素材库无合适图片 **且** 模型自身具备生图能力
  （或用户已配 `DASHSCOPE_API_KEY`/`SILICONFLOW_API_KEY`）时，才为本次行程定制生成。
  **任何情况下都不向用户解释图片来源或生图能力**——"图片来自内置素材库""本次未接入
  生图能力"这类说明禁止出现在页面和聊天回复里。
  无生图能力且素材库无合适图时仍交付主题页（illustrated 或 clay 走 stock 通用图）；
  五个需要生成图片的主题此时不提供——a plain text page is never the deliverable.
- **`lang` follows the language the user asked in** — it drives the page chrome only
  (`--lang` overrides); every content string in the plan is written in the user's
  language too.

## Phase 1 — 行前简报 (once per destination)

**Read `references/phase-1-brief.md` now, before any fact about the destination is
written** — it is the whole procedure for this phase (where each fact comes from; the
假日调休 / 天气 / 支付 / 保险 / 安全 lines; the safety line, the emergency card, the
health line; the exit criteria). This section is only the contract; never answer a
Phase 1 fact from memory of the procedure or of the place. In chat, Phase 1 is ≤ 10
lines — the `brief` cards themselves follow output-template.md §Brief templates.

Inputs: destination(s), dates, the skeleton candidates. Outputs: the `brief` cards in
canonical order (emergency · safety · health · holidays · weather · money ·
connectivity · insurance), the Phase 1 checklist rows (身份证/证件 · 景区预约窗口 ·
保险 · 恶劣天气 gate · T 阶梯), and the facts later phases inherit.

Gates — these decide pass/fail and do not move into the reference file:
- **Every Phase 1 fact is the assembler's alone** — 安全提示、天气预警、预约窗口、保险:
  city agents never decide them, and anything they say is overwritten.
- **Official sources only, never memory** — 景区/场馆官网与官方小程序、国务院办公厅
  放假安排、中央气象台预警 — each line stamped source + as-of; nothing found →
  "n/a — see safety", not a guess. The plan never 给医疗建议: it writes 就近三甲医院
  与药品自备清单。
- **天气预警与限流驱动排程**: 暴雨橙色/台风红色等预警触发改期建议;景区预约不可得
  (放票即罄)时停止并告知用户改期或换景,绝不写"到现场碰运气"。
- **调休与黄金周**: 行程日期撞上法定假日 → 错峰规则进 plan(scheduling.md);撞上调休
  补班日 → 反而是错峰好日子,写进行程说明。
- **User-named events are verified before anything else is planned.**

## Phase 2 — Route skeleton → checkpoint (a)

1. Longlist cities/areas scored against the user's ranked interests and
   `prefs.scenery` (nature / city / beach / forest / lake / mountain); shortlist by
   geography — order as a line or loop, never a star with backtracking. `prefs.travel_style`
   shapes the legs: self-drive → a rental/self-drive leg and park/countryside bases
   (Phase 3 §Driving legs); group tour → the tour's own schedule is the spine (Phase 4).
2. Nights allocation: ≥2 nights per base (each 1-night stay burns a half day on packing
   and transit); prefer "base + day-trips" over hotel-hopping when the day-trip is
   <90 min each way. 10-15 days ≈ 8-13 usable days ≈ 2-4 bases, and 2-3 beats 4.
3. Day-count honesty: 出发/抵达当日按半天计(15:00 前抵达=半个游览日,更晚=零游览日——
   晚上仍留一个免费步行块 near the hotel, scheduling.md §Arrival day); departure day = zero
   unless the flight/train leaves after 18:00.
4. Prefer **open-jaw**(第一个基地进、最后一个基地出)——高铁环线/不同城市进出通常比
   原路返回省一整天;两端交通都在 Phase 3 核对。
5. Present 2-3 skeletons (e.g. classic / nature-lean / relaxed): city order, nights per
   base, intercity legs with rough mode + duration, one-line pace verdict. Recommend one.

## Phase 3 — 交通: 高铁/机票/自驾

**Read `references/phase-3-legs.md` now, before the first transport scan** — it is the
whole procedure for this phase (the plan shape, the deep-link ladder, 高铁 vs 飞机 vs
自驾 decisions, what every leg row records, the exit criteria). This section is only
the contract; do not price a leg from memory of the procedure.

Inputs: the chosen skeleton (Phase 2), `prefs.travel_style`, the Phase 1 预约/假日
facts. Outputs: `legs[]` — one pick + one backup per leg — the checklist rows for
date-locked rail/flights and rentals, and their budget rows.

Gates — these decide pass/fail and do not move into the reference file:
- **`assets/plan.example.json` is the single source of truth for the plan's shape** —
  open it before writing a field; a wrong shape does not fail loudly — the renderers
  WARN and print an empty section.
- **价格阶梯(CN order)**: 火车 — 12306/携程火车票公开价可直写; 机票 —
  `flight_scan.py` 深链网格(携程/Trip.com/去哪儿,价格点开核对,计划先写
  "—, 点链接核对") + 备选航司/去哪儿作第二来源; 自驾 — 高德路径规划估时+油费/过路费
  区间,不猜价。`legs.note` names the sources with the as-of date; > 10 % disagreement
  prints as a band. "Price unverified" only when every source fails.
- **高铁 wins under ~5 h station-to-station**(京沪/京广等走廊 4-4.5 h 内高铁通常优于
  飞机——门到门时间与准点率); 15 天预售、候补优先于捡漏,开售日写进 checklist。
- **A park without a car is decided with the user, never by default.**
- **Every leg row carries price + currency + as-of, the checked-bag/行李额度, the refund /
  change class and a deep link**; one pick + one backup per leg.

## Phase 4 — City day-plans

**Read `references/phase-4-days.md` now, before any city is planned or any city agent
is launched** — it is the whole procedure for this phase (the city-agent contract, the
six per-city steps, the route_tools order, the `sun` / `check` rules, and the exit
criteria). This section is only the contract; do not plan a city from memory of the
procedure, and build every city-agent prompt from that file's §City-agent contract
(paste its lines, or pass the file's absolute path — the agent never sees SKILL.md).

Inputs: the chosen skeleton (Phase 2), the legs table (Phase 3), the Phase 1 brief
facts and `prefs`. Outputs: per city, plan-JSON day objects insertable verbatim into
`days[]` (output-template.md §city-block) — `stops`, hour-level `timeline`,
`hop_links`, `sun`, `rain_alt`, `ribbon` — plus the city's `checklist_items`.

Gates — these decide pass/fail and do not move into the reference file:
- **City agents never make 预约 / 安全 / 天气预警 / 保险 calls.** Those
  facts are the assembler's Phase 1 job and override anything a city block says; a
  city agent's prompt carries **search budget ≤ 8**, an explicit **"do not run
  geocoding"** line, the plan language, the §city-block return format, and the
  预约/实名 hard rule as its last line.
- **Hour-level timelines are the default deliverable**; day-level only when the user
  asks for a rough cut.
- **景区预约先行**: 故宫/国博等放票即罄的景点,预约窗口(提前 N 天、放票时刻、官方
  小程序)写进 checklist 与 timeline;约不上 = 改期或换景,与用户确认。
- **`route_tools.py check` exits 0 before rendering** — a BROKEN or SUSPICIOUS hop is
  fixed in the plan, never explained away in prose. A SUSPICIOUS hop has exactly two
  fixes: a vehicle really runs it (fly / drive / boat / train / bus) → declare that
  `mode` on the arriving stop and give it its `legs[]` row (add the row if the leg has
  none); nothing runs it (a 250 km hop inside one city is a mis-geocoded stop) → fix
  the stop, never the `mode`.
- **`sun --write` runs before any sunrise / golden-hour / dark-start prose**, after
  the stops carry coordinates; 境内统一北京时间,但新疆/西藏日出日落晚约 2 h —— `sun`
  的本地天文计算值是对的,不要"自我纠正"。
- Every day has its rain alternative, its food area and its `ribbon`; anchors are
  chosen per interest-fit, ≤ pace + 1 optional per day.

## Phase 5 — Hotels

Per base: pick 1-2 neighborhoods with reasons (near the rail hub actually used, safe
after dark, luggage-friendly), in the lodging type and band from `prefs.lodging`
(default mid-range hotel; 民宿/度假酒店偏好 changes which properties you list).
Browser spot-check 携程/美团/飞猪 with the real dates for a price band, then list
2-3 concrete properties: name, area, band per night, deep link with dates baked in
(recipes in data-sources.md). Advise: book refundable now, re-shop 2-3 weeks out.

## Phase 6 — Assemble, self-check, deliver

**Read `references/phase-6-assemble.md` now, before the final `plan.geo.json` is
written** — it is the whole procedure for this phase (assembly order, cover title, the
adversarial self-check list, delivery, the themed-render flow incl. stock mode, and the
exit criteria). This section is only the contract; do not assemble or render from memory
of the procedure.

Inputs: `plan.geo.json` assembled per references/output-template.md — the single
editable source — plus Phase 0's `prefs.theme` / `prefs.pictures` / `plan.lang`.
Outputs — three things every time, handed over through the harness's artifact / file
tool: (1) the **chat summary** — route one-liner, total budget, the 3 biggest decisions
made for the user; (2) `trip-<theme>.html`;
(3) `trip.kml` — plus the gates `.ics`, always: the pre-departure ladder rows are
date-locked gates (output-template.md §Pre-departure re-check ladder).

Gates — these decide pass/fail and do not move into the reference file:
- **The deliverable is a themed page (纯图文), never a plain text one.** The plain
  `render_plan.py` page is an extra: on request for a printable version, or as the last
  resort after one honest fix attempt of the theme renderer — and then the summary says so.
  本版本无任何视频主题;页面内不出现 video/iframe 视频/视频推荐。
- **The adversarial self-check runs in full before delivery** and fixes what it
  catches — **silently**: 坐标纠错、行程衔接修正、里程重算、清单补全等修复直接体现在
  正文里，不向用户展示任何自检记录（不写 `meta.self_check`、不把自检写进
  `decisions[]`、聊天回复里不提）。The list lives in the reference file; a skipped
  item is a defect, not a shortcut.
- **Acceptance bars are exit codes and eyes, not prose**: `route_tools check` and
  `scripts/plan_lint.py --strict` exit 0 before rendering (the only tolerated FAIL: a
  polar day's `sun`, PLN-11), `themes/qc.py` exits 0 after, and the export-probe PNG
  or the page in a browser was actually looked at — none available → say so in the
  summary.
- **`plan.geo.json` stays the single editable source**: a later "move day 3 to 洛阳"
  is a JSON edit plus geocode → check → links → kml → render, never a rewrite.
- **Cover title** comes from references/cover-titles.md — never a literal placeholder,
  never a blacklisted cliché.

## When things fail

- 深链点开后价格/班次与计划不符 → 以链接为准回改计划;所有来源都失败才标
  "price unverified",继续推进。火车票候补失败 → 改签相邻日期或换飞机段。
- A venue's hours survive 2 searches unverified → schedule it flagged "confirm on
  arrival"; don't burn more budget.
- 景区预约失败(放票即罄)→ 与用户确认改期或换景;绝不写"到现场碰运气"。
- Anything still unverified at delivery gets a ⚠️ in the plan — visible honesty beats
  quiet confidence.

## Bundled resources

Paths below are relative to the skill root (the directory holding this SKILL.md) —
resolve it once and call the scripts by absolute path, because a subagent's working
directory is not the skill directory and shell cwd does not persist between calls.

- `references/data-sources.md` — read before Phase 1: every API/URL recipe + fallback
  chain (交通、酒店、场馆、天气、假日调休、地理编码) — **plus the booking-judgment
  rules that decide plans**: §Group tours (weekday grids, min-party,
  calendar-vs-marketing, zero-cost holds and booking order) and §Hotels (checkout
  all-in pricing). Not just a curl cookbook.
- `references/cn-domestic.md` — read before Phase 4 venue research: 景区预约制清单
  （故宫 7 天 20:00 / 莫高窟 30 天等放票规则与官方渠道）、实名制（一人一证一票，
  证件号提前收）、门票复核阶梯、KML→高德收藏点。Phase 4 的 "official venue
  site first" 在国内场景下指向本文件。
- `references/output-template.md` — read before Phase 4 fan-out (city-block format)
  and Phase 6 (deliverable structure).
- `references/scheduling.md` — read before building any hour-level timeline: dwell
  times, buffers, meals, energy curve, degradation tags, timeline verification,
  调休/黄金周错峰规则.
- `references/navigation.md` — read with it: hop-link recipes (高德/百度), transit-row
  format, exit numbers, verify-vs-estimate policy, offline-maps (KML) workflow.
- `references/cover-titles.md` — bilingual poetic cover-title case library (poetry /
  prose / classic-literature sources + trip-archetype fit + cliché blacklist); read
  at Phase 6 when rendering.
- `references/phase-0-intake.md` — read at the start of Phase 0, before deciding whether
  to ask anything: core vs optional facts and their defaults, the intake message format
  and rules (zh sample inline, en in output-template.md), the `prefs` block, the
  picture-strategy check (stock | native | key, 素材库优先), the style line and plan language,
  and the exit criteria. SKILL.md Phase 0 is only the contract; this file is the
  procedure.
- `references/phase-1-brief.md` — read at the start of Phase 1, before any destination
  fact is written: where each fact comes from, the 假日调休 / 天气 / 支付 / 保险 / 安全
  lines, the safety line (预警 → 排程行为), the emergency card, the health line, and
  the exit criteria. SKILL.md Phase 1 is only the contract; this file is the procedure.
- `references/phase-3-legs.md` — read at the start of Phase 3, before the first
  transport scan: the plan shape and its two traps, the deep-link ladder, 高铁/机票/
  自驾 decisions, the fields every leg row records, the baggage walkthrough, and the
  exit criteria. SKILL.md Phase 3 is only the contract; this file is the procedure.
- `references/phase-4-days.md` — read at the start of Phase 4, before any city is
  planned: the city-agent contract (what every fan-out prompt must carry), the six
  per-city steps, the route_tools order (geocode → tz → sun → links → check → kml),
  the `sun` / `check` acceptance rules, and the exit criteria. SKILL.md Phase 4 is
  only the contract; this file is the procedure.
- `references/phase-6-assemble.md` — read at the start of Phase 6, before the final
  plan is written: assembly order, cover title, the full adversarial self-check list,
  delivery (themed page + KML + gates .ics), the themed-render flow incl. stock mode,
  the qc / export-probe acceptance bars, and the exit criteria. SKILL.md Phase 6 is
  only the contract; this file is the procedure.
- `scripts/flight_scan.py` — 境内交通深链网格生成器(零依赖零网络): 机票(携程/Trip.com/
  去哪儿)+ 火车(携程火车票;12306 官方 App/小程序)深链,价格点开核对(`--help` 先行)。
- `scripts/route_tools.py` — geocode stops(高德优先 `AMAP_KEY`/`--amap-key`,自动
  GCJ02→WGS84;百度回退 `BAIDU_MAP_AK`/`--baidu-ak`), distance-check clustering, emit
  per-hop map links and the trip KML; subcommands geocode / check (`--live` 用高德
  direction API 真实驾车/公交分钟数替代 (est),缓存 routecache.json,跨城公交降级
  驾车×1.25 折算) / links / kml / ics (the gates `.ics` from the checklist's dated
  rows — `-o gates.ics`, bump `--sequence` on every plan change) /
  poi (周边 POI 搜索 `--at 止名|纬度,经度 --kw 地铁站|餐饮 --radius`,结果 WGS84
  坐标可直接填回 plan;需 key) /
  **未配置 AMAP_KEY 时先向用户提示免费申请**（cn-domestic.md §5 三步，个人免费，
  不阻塞流程；key 存环境变量或 git-ignored 的 `.env`，绝不入库）/
  sun (civil dawn + sunrise/sunset per day, **本地 NOAA 天文计算零网络**,境内统一北京
  时间自动兜底; written into `days[].sun` in the canonical format; point = first stop,
  last stop on a moving day, or the day's `sun_stop` when set; non-zero exit = a day
  was skipped/rejected). links 的深链 provider 默认 **amap**(`--provider baidu` 或
  env `TRIP_MAP_PROVIDER` 可换;仅 amap/baidu 两种)。
- `scripts/render_plan.py` — turn the plan JSON into the final self-contained HTML.
  It reads the same file route_tools does, so write the plan once and render often.
- `scripts/plan_lint.py` — the plan's **content** gate, run with `--strict` before any
  renderer (exit = FAIL count, like qc.py): brief present, non-empty and canonical
  order; no placeholder / "awaiting" text; no markdown headings in cells; no
  user-facing internal traces (`as-of`/`T-14`/`钉死` 之类按 references/output-template.md
  §语言规范 检查); art placeholders filled and `prefs.pictures`
  matching how the art was made; the gates `.ics` and `trip.kml` beside the plan;
  under `--strict` every day has at least one stop and a `sun` written by `sun --write`.
  `check` proves the geography and `qc.py` the HTML — this proves the words.
- `assets/plan.example.json` — runnable schema example **and the single source of
  truth for the plan's top-level keys** (`prefs`/`budget`/`legs`/`checklist`/`hotels`/
  `brief`/`days[]`… shapes; output-template.md §Top-level plan skeleton mirrors it):
  copy it, replace the placeholders, and both scripts work on it immediately.
- `references/themes.md` — the themed-render manual: what each of the seven themes
  is, its art fields and known limits, how to add a theme, the recurring-defect
  checklist and the verification discipline. Read before rendering any theme.
- `themes/` — the themed renderers (`render_journal.py`, `render_noir2.py`,
  `render_theme2.py` = illustrated, `render_clay2.py`, `render_glass2.py`,
  `render_zine.py`, `render_splash.py`, `render_picker.py`; **无视频主题**)
  plus `theme_common.py`（境内版:页内地图嵌入默认关闭）, `qc.py` (static QC, exit
  code = FAIL count), `xprobe.sh` / `xt.sh` (headless export probes), `towebp.py` /
  `gen.py` / `split_sheet.py` / `cutout.py` (asset pipeline; `gen.py`:
  `--provider dashscope|siliconflow` 国内直连生图,env key 优先), `ART-SCHEMA.md`
  (the one authoritative art.json contract) and `themes/README.md`.
- `themes/assets/` — the shared picture library: all embeddable webp, the Caveat
  webfont, `manifest.json` (prompt per generated asset) and `stock/` — the
  **stock kit** (region cover paintings + generic-scene cut-outs in the illustrated
  style, `stock/index.json` + `stock/README.md`) that `themes/stock_art.py` uses to
  build an art file when the session has no image generator and no key.
- `themes/stock_art.py` — `plan.geo.json --theme illustrated|clay [--lang zh|en]
  [--country ISO2] [--index PATH] [--force] -o plan.art.json`: fills the picture slots
  from the stock kit + shared library (country match, day keyword match, generic
  props); you write the words; render with `--assets themes/assets/stock`. Stock mode
  only (Phase 0).
- `examples/china-2026/` — 境内示例行程(上海→北京→西安→北京→上海,8 天): 计划 JSON、
  art JSON、gates.ics、trip.kml 与已渲染的 splash/clay 主题页;`plan_lint --strict`
  通过,是格式与新契约的活样板。
