# Output formats（境内版）

Two formats, two jobs: **§city-block** is the machine hand-off from a city researcher
to the assembler, and the scheduling.md block is the human-facing rendering of the
same day. Both examples are written in mixed Chinese/English purely because that is
the sample trip — the deliverable always follows the user's own language. The
assembled file itself follows the **§Top-level plan skeleton** just below.

## §Top-level plan skeleton — the assembled `plan.geo.json`

`assets/plan.example.json` is the single source of truth for these keys (it runs
through every script as-is); the shape below is copied from it and from the schema
comment at the top of `scripts/render_plan.py`, which reads exactly these names.
Every key is optional except `days[].date` — an unfilled section simply does not
render — but a section of the **wrong shape** is not "optional": it renders as an
empty table with a WARN on stderr pointing here (the 云南 test wrote `budget` as
`{note, rows[{item,pp,total}]}` and `legs` with invented keys — both renderers used
to crash on it, and `legs` still prints every cell blank).

```json
{
 "trip": "云南 8 天",
 "lang": "zh",                                  // zh | en — see §Plan language
 "tz": "Asia/Shanghai",                         // 境内统一北京时间（UTC+8）；days[].tz
                                                // 可覆盖——设置了 tz 的 `sun` 才会写入
 "prefs": {"theme", "pictures", "travel_style", "lodging", "scenery", "pace", "budget",
           "notes"},                            // Phase 0 intake — see §Intake prefs
 "meta": {"dates", "party", "route", "budget_total", "generated"},   // self_check 已废弃——自检静默化，不写任何自检记录
 "decisions": ["one line per decision made for the traveller — each vetoable", ...],
 "checklist": [{"item", "deadline", "price", "link", "link_text", "note"}],
 "legs":      [{"type", "date", "carrier", "from", "to", "dep", "arr", "price", "bags",
                "link", "note", "backup"}],
 "days": [{"date", "city", "label", "sun", "sun_stop", "day_map", "ribbon", "rain_alt",
           "late_cut", "walking_km", "travel_day", "tz",
           "timeline": [{"t", "what", "kind", "price", "note", "tag", "verify",
                         "link", "map"}],
           "hop_links": ["url", ...],           // written by links --write when parked
           "stops": [{"name", "query", "lat", "lon", "mode"}]}],
 "hotels": [{"base", "area", "why", "options": [{"name", "band", "link"}]}],
 "budget": [{"cat", "per_person", "total", "note"}],   // a LIST of rows, not {rows:[]}
 "brief":  {"emergency", "safety", "health", "holidays", "weather", "money",
            "connectivity", "insurance", "baggage"},   // in this order — §Brief templates;
                                                // extra keys become their own card
                                                // inside the 行前简报 section;
                                                // titles from theme_common.BRIEF_TITLES
                                                // (fallback: the raw key; art
                                                // brief_titles overrides) — see
                                                // §Booking-artifact conventions
 "unverified": ["anything that survived two searches unverified", ...]
}
```

- `budget` rows are `{cat, per_person, total, note}` — **一律人民币（¥），无汇率
  行、无 FX 字段**（the buffer line is a row like any other). `legs` rows spell the
  stations/airports `from`/`to` and the clock `dep`/`arr`; `backup` is a free-text
  second choice（价格拿不准就写 "—, 见 flight_scan 深链核对"）。
- `checklist` (top level, `{item, deadline, price, link, link_text, note}`) is the
  merged, urgency-sorted list; the city block's `checklist_items` (same row shape,
  minus `link_text`) is its **input** — the assembler copies those rows into
  `checklist` (renderers never read `checklist_items`), so both names are correct,
  each in its own file. 预约/门票/健康 rows never come from a city block
  (SKILL Phase 1/4)。
- `days[].sun_stop` (optional) — the `name` or 0-based index of the stop `sun --write`
  should key the day on, overriding its default (first stop; last stop on a moving
  day). Set it on a moving day whose sunrise anchor is at the *first* stop
  （黄山山顶看日出 → 当天下午下山赴宏村；泸沽湖日出 → 环湖赴丽江）。
- `days[].tz` (optional, IANA name) overrides the plan-level `tz` for `sun` —
  境内行程一般不设；非 Asia/Shanghai 系时区名会在 Windows 上退化为 approximate
  并让 `sun` 拒写。
- Field-level meaning of the `days[]` object (timeline `kind`/`tag`/`verify`,
  `map:false`, `stops` ↔ hop rows) is in §city-block right below — the day objects
  are byte-identical in both places.

### §Brief templates — canonical order, required keys, and the fixed-line cards

`brief` renders in **insertion order**, one card per key, titled from
`theme_common.BRIEF_TITLES` — so write the keys in this order and keep every card
≤ 8 lines: **emergency → safety → health → holidays → weather → money →
connectivity → insurance → baggage**, then the triggered cards (`season`, `altitude`,
`navigation`, `lookalikes`, `packing`) only when the trip has the trigger. Required
on every plan: `safety`, `holidays`, `weather`, `money`, `connectivity`,
`insurance`, `emergency`, `health`.
**Sources for `emergency` and `health`** (phase-1-brief.md §Emergency card and §Health
line): 官方应急号码（110/120/119/12301）、目的地卫健委/疾控页面、医院官方挂号渠道、
保险公司条款与浏览器里高德/百度地图的医院 place card（ER only）are the only
sources; a fact none of them carries → that line
reads "n/a — see 官方来源" next to the URL it read, never numbers from memory.
A key that is not in `BRIEF_TITLES` prints as its raw English key on a zh page —
add the title there (or via the art file's `brief_titles`) before inventing a key.

Three cards have fixed lines. Fill every line; "n/a" is an answer, silence is not.

**`brief.money` — five lines（境内无外币/汇率问题，重点是支付方式分层）**
1. 移动支付：微信支付/支付宝全程可用；出行前确认两张卡都绑了卡且免密额度没关。
2. 备用现金：一个数字——"随身备 ≈ ¥X 应对 {N} 天小额与无信号场景"——按目的地
   现金浓度定（古镇/集市/乡村民宿常见只收现金或信号差）。
3. 景区支付：多数 5A 景区门票走官方小程序或 OTA 预约支付；现场窗口排队的
   场景写明（把预约二维码截图存相册，防山上无信号）。
4. 优惠证件：学生证/教师证/老年证/军人证件的半价或免票规则，各景区执行不一，
   写一条总提示（以景区现场规则为准）。
5. 报销/发票：OTA 订票要电子发票的提前开（部分渠道离店后 30 天截止）。
The recipes behind these lines: data-sources.md §Money safety。

**`brief.connectivity` — 信号与离线，然后数字安全行**：
境内游的 connectivity 核心是**离线准备**：离线地图包提前下（高德/百度/Organic
Maps+trip.kml）；山区/景区无信号段点名（写进对应 day）；预约二维码/车票截图存
相册；充电宝 ≥2 万 mAh 且符合民航/高铁携带规定；公用 Wi-Fi 不做支付与登录；
身份证、保单留云 + 离线副本（截图即可）。

**`brief.safety` — the 预警 line, then six named lines** (one set per trip, with
per-base detail where the bases differ):
0. 预警：`{级别} · 中央气象台/应急管理部 · {date} 查证（第二来源：{级别}）` —
   phase-1-brief.md §Safety line；橙色/红色预警 hit never reaches this
   card, it stops the pipeline（蓝/黄预警降级为 rain_alt 与 packing 提示）。
1. Named scams: the destination's 2-3 current scams by name, with the tell
   （低价一日游/黑导游/寺庙"功德"套路/照相搭讪收费——按目的地当前真实存在的写）。
2. Pickpocket hotspots: the specific lines, stations and squares（火车站/步行街/
   早市高峰段）。
3. Taxi rule: 用滴滴/高德打车或站点官方候车队；机场/高铁站不去 arrivals-hall
   拉客的"黑车"。
4. After-dark avoid list, per base, and the door-to-door rule for night moves
   （山区民宿夜路点名）。
5. When it happens: 110 报警并索要报警回执——回执编号是保险理赔的关键凭证；
   急救 120 与道路救援电话见 `brief.emergency`。
6. Legal & customs red lines: 无人机禁飞区（景区/机场/边境多禁飞，需实名报备）·
   自然保护区核心区禁入 · 文物/宗教场所拍摄规则 · 边境地区通行证要求（如
   西藏部分区域需边防证）——≤ 3 lines，来源为官方公告或"无额外限制"。
Sources per line: phase-1-brief.md §Safety line 与目的地官方渠道（景区公众号/
政府网），不用自媒体帖子当来源。

**`brief.emergency` — six lines, every number stamped with its 查证日期, none from memory**
(phase-1-brief.md §Emergency card): 1 报警 110 · 急救 120 · 火警 119 · 交通事故
122 · 2 全国旅游服务热线 12301 与目的地 12345 · 3 每个 base 一家三甲医院急诊
（名称·地址·电话·夜诊情况·链接）· 4 保险公司救援热线 + 保单号占位 + 先打救援
电话再垫付的规则 · 5 身份证遗失补办流程（异地受理：就近派出所/户政大厅 +
12306 临时乘车证明）· 6 每个 base 一家 24h 药房 + "药店"与常用药品的说法；
a base > 2 h from an ER says so in the day note.

**`brief.health` — five lines from official pages** (phase-1-brief.md §Health line):
1 高原反应（目的地海拔 ≥2500 m 才触发：红景天争议、渐进海拔、布洛芬对症、
   何时下撤就医——计划不下处方）· 2 蚊媒与季节性疾病（南方夏季登革热注意区）·
   3 饮水与饮食（生水/生食/路边摊的提示）· 4 动物接触与狂犬（投喂猴群/流浪犬
   风险与伤口处理）· 5 notice level + 查证日期 + 页面 URL（chinacdc.cn 或属地卫健委）。
Yellow-fever 类国际疫苗要求不适用于境内行程，不写。

**`brief.season` — triggered only** (phase-1-brief.md §Hazard line): the hazard · its
months · the official source URL · what the plan does about it (buffer day, refundable
rows, the gate) — ≤ 5 lines, absent when the window hits nothing.

### §Intake prefs — top-level `prefs`

What Phase 0 (Intake) learned or **assumed**, written down once so Phases 2-6 and any
later replan read one place instead of re-asking the user. Renderers ignore the whole
block (it is not in `theme_common.PLAN_SHAPE`, and adding it leaves every rendered page
byte-identical) — it is a note the planning agent leaves for itself.

```json
"prefs": {
  "theme": "illustrated",
  "pictures": "key",
  "travel_style": "public",
  "lodging": "hotel · mid-range, refundable",
  "scenery": ["city", "nature"],
  "pace": 3,
  "budget": "mid",
  "notes": "assumed origin 上海 (zh request, no origin given)"
}
```

- `theme` ∈ `illustrated|clay|noir|glass|journal|zine|splash` — which of the
  seven themed pages is the deliverable. Default **illustrated 插画版**.
- `pictures` ∈ `stock|native|key|custom` — how the pictures were produced (Phase 0's
  picture-strategy check, **素材库优先**): 内置素材库有合适图 → `stock`（不生成）·
  素材库无合适图且模型有原生生图 → `native` · 境内生图渠道（阿里云百炼 dashscope 或
  硅基流动 siliconflow 的 key，放在环境变量，never read or printed）→ `key` ·
  行程目录里放定制生成的图片 → `custom`。它只决定 Phase 6 的 art 文件怎么建——
  **任何取值下都不向用户解释图片来源或能力**。
- `travel_style` ∈ `public|self-drive|group-tour|mixed` (default `public`) — Phase 2
  shapes the legs from it and Phase 3 adds a rental leg for `self-drive`.
- `lodging` — free text: type + band (default mid-range hotel, refundable), read by
  Phase 5.
- `scenery` ⊂ `nature|city|beach|forest|lake|mountain` — Phase 2 scores the longlist
  against it.
- `pace` — anchors per day (2/3/4, default 3); `budget` — a band word or a number.
- `notes` — every value that was **inferred rather than told**, in one string, so the
  assumptions block at checkpoint (a) can be written straight from this object.

Only what is known or defensibly assumed goes in; a key the user never touched and the
agent never needed is simply absent. An intake that asked nothing (the request already
carried destination + dates) still fills `prefs` — from the defaults it chose.

### §Intake message — the one question block (only when a core fact is missing)

Shape: a bold one-line lead, **必答 / Must answer** then **选答 / Optional**, numbered
continuously, one option list per line with the default named, and at most two footer
lines (ℹ️ stock-picture note, only in stock mode; 💡 "all defaults" shortcut, only when
optional items are shown). **Only items the user has not already given** appear — a
heading with nothing under it is dropped. A guessed core value is asked as a
confirmation, not an open question. One message, never a follow-up. Markdown, in the
user's language.

**zh sample** — request was "帮我规划一次云南之旅" (destination known, everything else
missing, no image generator in the session):

```
**先确认几件事 —— 一条消息回我,写序号+答案;没写的按默认**

**必答**
1. 出发城市 —— 我猜是上海(你用中文问的),对吗?
2. 玩多久、大概什么时候 —— 例:10.1–10.7,或「7 天 · 10 月 · 前后可挪 2 天」

**选答(不答走默认)**
3. 页面风格:插画(默认)· 黏土 · 夜航 · 玻璃 · 手账 · Zine · 闪屏 —— 样子见 examples/ 各行程的已渲染页面
4. 出行方式:公共交通+步行(默认)· 自驾 · 跟团
5. 住宿:中档酒店(默认)· 青旅 · 民宿 · 公寓 · 度假酒店
6. 偏好:城市 · 自然风光 · 湖泊 · 雪山 · 古镇 —— 默认按目的地定
7. 人数 / 预算 / 节奏:默认 2 成人 · 中档 · 每天 3 个主要点

ℹ️ 本次会话没有生图能力,页面会用内置插画素材(仍是成品页,只是不如定制图贴合);有阿里云百炼或硅基流动的 key 的话放进环境变量再告诉我,就能为这趟生成。
💡 回「默认」= 全部按默认,直接开工。
```

**en sample** — request was "Plan me 8 days in Yunnan in May, we're a family of four,
self-driving" (destination, duration, month, party and travel style already given → none
of them is asked; the session has a native image generator → no ℹ️ line):

```
**Two quick things before I plan — reply in one message, number + answer; anything you skip uses the default**

**Must answer**
1. Departure city — I'm guessing Shanghai (your request is in English but the trip is domestic); right?

**Optional (skip = default)**
2. Page style: illustrated (default) · clay · noir · glass · journal · zine · splash — see examples/ (local rendered pages)
3. Lodging: mid-range hotel (default) · hostel · B&B / guesthouse · apartment
4. Taste: city · nature · lake · mountain · old towns — default: read from the destination
5. Budget / pace: default mid-range · 3 main stops a day

💡 Reply "defaults" and I start right away.
```

Answers land in `prefs` (above); what was guessed and not corrected goes into
`prefs.notes` and the assumptions block at checkpoint (a).

## §city-block — what each city researcher returns (fan-out or sequential)

Return **plan-JSON fragments, not a parallel dialect**. The assembler inserts your
`days` array elements into the plan file verbatim — on the first real multi-city run
the researchers returned YAML with different field names (`theme` for `label`,
`anchors` beside `timeline`, `book_ahead_list` for checklist rows) and every block had
to be transcribed by hand, which is exactly where errors breed. The day objects below
follow `scripts/render_plan.py`'s schema field-for-field.

```json
{
 "days": [
  {"date": "2026-10-05", "city": "杭州", "label": "西湖东线经典",
   "sun": "天亮 05:28 · ☀ 05:53 / 🌇 17:38 · CST · 本地天文计算",
   "travel_day": false,
   "rain_alt": "浙江省博物馆之江馆(室内,当日开放情况已核)",
   "late_cut": "晚点 >1 h → 砍掉柳浪闻莺",
   "ribbon": "断桥残雪 →步行16′→ 平湖秋月 →公交20′→ 雷峰塔",
   "walking_km": {"total": 5.4, "how": "on-foot 2.4×1.3 + 散步 1.5 + 馆内 ~0.8"},
   "timeline": [
    {"t": "09:00-11:00", "what": "灵隐寺", "kind": "anchor", "price": "¥45",
     "note": "开门即到避人流;最晚入场 17:30 — 官方公众号核 2026-08-01", "tag": "opener"},
    {"t": "11:00-11:25", "what": "步行 灵隐寺→法镜寺 1.2 km · 25分", "kind": "hop",
     "verify": "est"},
    {"t": "12:00-13:15", "what": "午餐 · 灵隐寺素面/龙井村", "kind": "meal",
     "tag": "swap→绿茶餐厅"},
    {"t": "13:15-13:45", "what": "公交 7 路(往城站火车站) 9站/35分 ¥2 · 灵隐→湖滨 · 下车步行5分",
     "kind": "hop", "verify": "verified"},
    {"t": "15:55", "what": "G7352 次发车 → 上海虹桥", "kind": "hop", "verify": "verified",
     "map": false}
   ],
   "stops": [
    {"name": "灵隐寺", "query": "灵隐寺, 杭州市"},
    {"name": "雷峰塔", "query": "雷峰塔, 杭州市", "mode": "transit"}
   ]}
 ],
 "hotels": [
  {"base": "杭州 3 晚", "area": "湖滨/龙翔桥", "why": "…",
   "options": [{"name": "…", "band": "…", "link": "…deep link with dates…"}]}
 ],
 "tour_options": [
  {"name": "…",
   "price": "…include 单房差 / 费用包含明细 / 门票是否含 / 小费基础…",
   "schedule": "departure days — with a
    browser, page the pricing calendar and read each date cell before giving a
    verified conclusion (the marketing '天天发团' blurb doesn't count);
    without one, ship the calendar link marked unverified", "pickup": "…", "link": "…"}
 ],
 "checklist_items": [
  {"item": "…", "deadline": "…", "price": "…", "link": "…", "note": "…"}
 ],
 "unverified": ["anything that survived 2 searches unverified"],
 "searches_used": 7
}
```

Field discipline (the merge breaks without it):
- `checklist_items` = sell-outs, timed tickets, date-locked rail, tours — things the
  city researcher verified. **No 预约政策/健康/预警/保险 rows beyond what the venue
  itself requires**: the assembler owns those facts (SKILL Phase 1) and overwrites any
  city-block claim about them (an agent once shipped an outdated "需边防证" as
  item #1 for a route that no longer required it). The assembler merges these
  rows into the top-level `checklist` (§Top-level plan skeleton).
- `sun` is filled by the assembler's `sun --write`, not by you; if the day's sunrise
  anchor is at its first stop on a moving day, add `"sun_stop": "<that stop's name>"`
  so the assembler's run keys the day there.
- `timeline` rows: `kind` = anchor|hop|meal|free;anchors/meals carry `tag`
  (pinned|opener|skippable|swap→X);hops carry `verify` (verified|est);flight/rail
  hops already covered by the legs table carry `"map": false`. Never mix tag/verify.
- N mapped `stops` ⇒ N−1 hop rows without `map:false` — that alignment is what lets
  `links --write` place every URL automatically. Lodging→first-stop and
  last-stop→lodging rows, and rides that are themselves the sight (游船, 景交车,
  轮渡) are the two places this slips — see navigation.md step 1.
- `sun` is written by `route_tools.py sun --write` in the canonical shape
  `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · CST · 本地天文计算` — for an `en` plan
  (`plan.lang`, or `sun --lang en`) the dawn word is `dawn`:
  `dawn HH:MM · ☀ HH:MM / 🌇 HH:MM · CST · NOAA local solar model`; the renderers
  accept either spelling. Never hand-write it — `plan_lint --strict` fails any other
  shape; a day `sun --write` skipped is re-run with `--only DATE` once the day has a
  stop. 极昼/极夜不发生在境内；`sun --write` 拒写的原因只会是时区 approximate 或
  当日无 stop——补 stop 或确认 `tz` 为 Asia/Shanghai 后重跑。
- `walking_km` is the honest total (`{"total", "how"}` form preferred).
- Do NOT run geocoding — the assembler runs route_tools once, centrally (五路并行
  会撞缓存写坏 `geocache.json`；配额方面几十个 POI 也在高德/百度免费额度内).
- Verified facts carry source + 查证日期（如"2026-10-02 查证"）in `note`; everything else is `est` and,
  if load-bearing, also listed in `unverified`.

## Plan language — top-level `"lang"`

The assembled plan JSON carries one top-level key `"lang": "zh" | "en"` (default
`zh` when absent; `meta.lang` is read as a fallback). It is a **plan fact**: set it
in Phase 0 from the language the user asked in, and never mix it with the content —
`lang` only says which language the rendered page's own chrome speaks (section names,
buttons, tags, weekdays, the "天亮/dawn" word, `<html lang>`), while every string you
wrote into the plan (labels, notes, stops, brief) is printed exactly as written.
`scripts/render_plan.py`, every `themes/render_*.py` and `route_tools.py sun --write`
read it (`--lang zh|en` overrides per run); the shared word table lives in
`themes/theme_common.STRINGS`. An `en` plan gets the `dawn …` form from `sun --write`
(see the `sun` bullet above).

```json
{"trip": "云南 8 天", "lang": "en", "meta": {"dates": "…", "route": "…"}, "days": [ … ]}
```

## Final deliverable

**A themed HTML page, never a plain text one.** Phase 6 renders `plan.geo.json` through
the theme picked in Phase 0 (`prefs.theme`, default **illustrated 插画版**) into
`trip-<theme>.html` — one self-contained file (pictures inlined as data URIs, no
network, opens by double-click), phone-friendly, carrying its own share/export buttons
and the appendix — and ships the trip KML beside it for offline map apps
(`scripts/route_tools.py kml plan.geo.json -o trip.kml`). Details of the seven themes
and the art file: `references/themes.md`, `themes/ART-SCHEMA.md`.

The plain `scripts/render_plan.py` page — printable, checkbox checklist, a small offline
route sketch per day — is an **extra**, not the deliverable: render it when the user asks
for a printable or plain version, or as the last resort if the theme renderer still fails
after one honest fix attempt (then say which it is in the summary). `plan.geo.json` is
the single editable source for both, so a later change is a JSON edit plus
geocode → check → links → kml → render, never a rewrite; there is no separate Markdown
copy to keep in sync.

Both pages present the same material in the same order:

1. **Header**: route one-liner, dates, party, total budget in **人民币**（无汇率行）.
2. **Decisions made for you**: 3-5 bullets (jaw direction, pass math, pace calls…) —
   each one vetoable by the user.
3. **Booking checklist** (the action list lives near the top on purpose), sorted by
   urgency: 景区预约/门票秒杀 → 高反等健康事项 → 车票起售（date-locked rail） →
   机票涨价 → refundable hotels → the rest (the pre-departure ladder closes the
   list). Each row: item · deadline/lead time · price + 查证日期 · deep link ·
   checkbox.
4. **Flights & intercity table**: pick + backup per leg with all Phase 3 fields.
5. **Day-by-day cards**: one card per day — header (date/city/label + sunrise/sunset),
   then the hour-level timeline as a two-column table: 时间 · 内容 (time · activity).
   Hops are their own rows, styled dimmer, written in the canonical hop-row format
   from navigation.md (mode, line (toward …), stops/minutes, fare ·
   boarding→alighting stop · exit number) with the tappable link on the row; price
   and notes sit under the activity
   name; tags ([pinned]/[opener]/[skippable]/[swap→…]) and hop markers
   ((verified)/(est.)) render as pills at the end of the row.
   render_plan.py also draws a small offline route schematic per day straight from
   `stops` — one more reason to fill `stops` even for days you already mapped.
   Below the table: the whole-day map link, the honest walking total, the rain
   alternative, the `ribbon` one-liner (Stop1 →walk 12′→ Stop2 →metro 9′→ …
   authored by the planner in Phase 4 — no script writes it; the renderers only
   print it) and the late_cut line. Travel days are marked visually by `travel_day: true`.
6. **Hotels**: per base — neighborhood rationale, 2-3 properties, band, dated links.
7. **Budget table**: category rows (flights/lodging/intercity/local/entries/food),
   per-person and total columns, 10-15% 机动预留 line, 查证日期（人民币，无汇率行）.
8. **行前简报 (Trip brief)**: cards in the canonical order of §Brief templates —
   emergency · safety · health · holidays · weather · money · connectivity ·
   insurance · baggage — then the triggered cards (season, altitude, navigation,
   lookalikes, packing) only when the trip has the trigger.
9. **Footer**: generation date · "prices move — links are the source of truth" ·
   ⚠️ unverified list · offline tip:
   import the delivered trip.kml into Organic Maps · data credits
   （日出日落来自本地天文计算，无外部服务依赖；地理编码来自高德/百度开放平台）.
   **不打印自检结果**（自检静默化，见 §语言规范）。

## 语言规范（境内版 · 交付纯度）

最终交付的计划（页面 + 聊天回复 + 附件说明）**只包含用户真正关心的行程内容，
语言通顺自然，不留任何内部痕迹**：

- **自检静默**：坐标纠错、行程衔接修正、里程重算、清单补全等自检与修复在后台完成，
  修正结果直接体现在正文；不写 `meta.self_check`、不把自检写进 `decisions[]`、
  聊天回复不提修复过程。
- **不用内部缩写/代号**：`as-of`→"2026-10-02 查证"；`est`/`verify`→"约/以出票为准"；
  `OTA`→"在线平台"；`pattern`→"开放时间（季节性）"；`on-foot`→"步行约 X 公里"；
  `buffer`→"机动预留"；`D1/D5`→"第 1/5 天"；机场用中文全称不用 IATA 码
  （网址与代码本身除外，如 nmc.cn）。`T-17/T-14/T-7/T-3/T-1`→"尽早（2026-10-09 前）/
  出发前两周（2026-10-12 前）/出发前一周（2026-10-19 前）/出发前 3 天（2026-10-23 前）/
  出发前 1 天（2026-10-25 前）"——中文说明 + 完整 ISO 日期，日历工具照常解析。
- **不用生硬措辞**：`钉死`→"必做"；`可砍`→"可跳过"；`开门冲`→"开门就去"；
  `swap→X`→"可换·X"；里程与时间说明写成完整自然的句子，不堆系数记号（如 2.4×1.3）。
- **不解释能力与来源**：页面与回复中不出现"图片来自内置素材库""本次未接入生图能力"
  "由 AI 生成"等说明；图片来源是内部决策，用户只看到配图本身。
  唯一例外：封面引用诗句时可保留其出处署名（那是内容，不是能力说明）。

The accompanying chat summary: route one-liner, total budget, the 3 biggest decisions,
which checklist item needs the user's action first — and **no picture-source or
capability note of any kind**（图片来自素材库/未接入生图能力这类话禁止出现在聊天回复；
详见 §语言规范）.

**The assumptions block at checkpoint (a)** — one block at the top of the route-skeleton
message, written from `prefs`: the inferred origin (and what it was inferred from) and
every optional field that fell back to a default（图片策略是内部决策，**不写进假设块**）.
It exists so a wrong guess costs the user one line to correct instead of a round trip of
questions. In "一次到位 / don't ask" mode there is no checkpoint (a), so the same block
goes at the top of the delivery instead.

HTML style of the **plain** page: system font stack, max-width 720px, day cards with a
left border, the checklist as a real `<table>`, print CSS (no shadows; page breaks
between days are fine). No JS required; a tiny inline script persisting checkbox state to
localStorage is welcome. The themed pages own their own visual language — do not restyle
them toward this one.

### §Booking-artifact conventions (checklist + hotels rows)

- **Dates ride inside every booking link** (`checkin=`/`checkout=` on hotel
  searches, date params on flight/train links) and place names carry their disambiguator
  (state / prefecture / full property name) — a link the user can mis-city is a
  bug, not a convenience. When the route contains collision-prone names
  (同名城市区县、一字之差的高铁站——杭州东 vs 杭州西, same-name hotels inside one
  scenic area), the brief gets a `lookalikes` entry naming each trap.
  Themed renderers title brief cards from `theme_common.BRIEF_TITLES` (fallback:
  the raw key; the art file's `brief_titles` overrides) — `lookalikes` is not in
  that table, so give it its display title via `brief_titles` (zh: 重名陷阱), or on
  a zh-only plan simply key the entry 重名陷阱 — unlike `altitude` and `navigation`,
  which are built-in `BRIEF_TITLES` keys and need no override. The destination
  researcher carries the known traps for the route.
- **Hotel stays are explicit local calendar dates** ("check-in D1 → check-out D3"
  = the nights of D1 and D2). Booking sites use the hotel's local calendar and
  never convert timezones — the mis-bookings are human, so pre-chew the two
  classics wherever the plan contains them, on the checklist row itself and not
  only in prose: a past-midnight arrival still sleeps the PREVIOUS calendar night
  (book the landing date + a "late arrival" note, never the clock date the guest
  walks in on); a date-line crossing books the ARRIVAL-local calendar date, not
  the departure date. 境内无跨时区问题，但跨零点到达（红眼航班/夜班高铁）同样
  容易订错首晚。
- **Date-locked rows also ship as a calendar file**: when the checklist carries
  gates (a ticket-release instant, a decision deadline, an on-trip re-check),
  offer a `.ics` beside the page (worked example: `examples/gates-sample.ics`)
  — one VEVENT per gate, with the FULL action
  list in DESCRIPTION (the user acts from the alarm, not from memory: what to
  do, the fallback if it fails, the linked bookings by number), two VALARMs
  (`-P1D` and `-PT30M`), and stable UIDs with an incremented SEQUENCE and
  fresh DTSTAMP on every plan change. Write times as FLOATING local times (no
  `Z`, no `TZID`): a pre-trip gate then fires on home wall-clock, and an
  on-trip gate at that hour in whatever timezone the traveller is standing in
  — which is what an on-trip re-check wants. The exception is a fixed-instant
  gate (a ticket drop at home-timezone clock time): schedule it on a pre-trip
  date when it is one, and when it can fall mid-trip give that one VEVENT a
  TZID-anchored DTSTART with its VTIMEZONE — RFC 5545 allows mixing anchored
  and floating events in one file. File mechanics are strict
  (RFC 5545): escape DESCRIPTION newlines as `\n`, fold long content lines at
  75 octets, include VERSION/PRODID and a DTSTAMP per event. Client caveats
  belong on the page, not in the user's lap: 手机系统日历与微信/QQ 导入对浮动
  时间的处理不一（有的钉死在导入设备时区、有的跳过同 UID 重复导入而不是更新、
  有的用自带默认提醒替换 VALARM）——so open each DESCRIPTION
  with the intended hour ("09:00 local, wherever you are"), and after a plan
  change instruct
  "delete the old events, then import the new file".

### §Pre-departure re-check ladder — four fixed checklist rows, always with the .ics

Every plan's checklist ends with the same four rows, each naming what it re-checks
(the brief lines and the `legs` by number), so re-verification is one ladder instead
of five unrelated "re-confirm" lines. They are date-locked gates, so the ladder alone
makes the gates `.ics` mandatory (floating 09:00, rules above) — generated with
`python3 scripts/route_tools.py ics plan.geo.json -o gates.ics`, which reads each row's
ISO date (deadlines are written as `出发前两周（2026-10-31 前）` — 中文说明 + 完整
ISO 日期，用户直接可读，`ics` 取 ISO 部分解析; for `route_tools ics` to parse the
deadline the ISO date must appear in it).

| row | re-checks | how |
|---|---|---|
| **出发前两周** | opening hours + fees of every anchor (seasonal ones first) · 预约与门票政策（是否需实名/分时段） · ticket-release dates still ahead（12306 起售日） | the row lists the anchors and the `legs` numbers it covers |
| **出发前一周** | weather: re-run the forecast recipe (data-sources.md §Weather) for every base and re-apply scheduling.md rule 10 to hot / wet / windy days · the route's hazard sources (season card) | swap rain alternatives into the main line where the odds say so; note the swaps in `decisions[]` |
| **出发前 3 天** | 停运/检修/景区临时闭园公告（12306 + 景区/城市交通官方通知） · forecast once more · timed tickets in the wallet | one line per moving day |
| **出发前 1 天** | 离线地图包已下 · 预约二维码截图进相册 · paper + cloud copies（身份证/保单） · cash in hand per `brief.money` · cards unblocked（绑卡/免密正常） | — |

A **hazard gate** (phase-1-brief.md §Hazard line) is a fifth, named row when the
window hits a hazard season: it carries the official source URL and the decision it
gates, and gets its own VEVENT beside the ladder's.

Write the rows as `{item, deadline: "出发前两周（<ISO 日期> 前）", note: <what it covers>}`, keep
them last as a block (anything else due inside the two-week window — 离线地图、现金、绑卡确认 — is
folded into the matching ladder row, not kept as its own row; a ticket drop inside
the window stays its own gate and sorts by date ahead of the block), and do not add a
separate "re-confirm opening hours" row — the two-week row is that row. `assets/plan.example.json` carries the four rows as
placeholders.
