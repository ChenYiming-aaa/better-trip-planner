# Hour-level scheduling

Read this before assembling any day into a timeline. Hour-level timelines are the
default deliverable; deliver day-level granularity only when the user explicitly wants
a rough cut.

Contents: dwell times · assembly method · day types · traps · verification · format.

## Dwell-time defaults (first visit, tourist median)

| Venue type | Time |
|---|---|
| Flagship museum (Louvre/Vatican/British class) | 3-4 h |
| Standard museum / gallery | 2 h |
| Small museum / single exhibition | 1-1.5 h |
| Temple, shrine, church, mosque (a visit) | 30-45 min — active worship sites: see Traps |
| Headliner temple with an approach street (Kiyomizu, Kinkaku-ji, Todai-ji) | 1-1.5 h incl. the approach |
| Open-air heritage site (殷墟, 交河故城, 良渚遗址公园) | 1.5-3 h, +30% if hilly and unshaded |
| 大型遗址公园 (圆明园, 大明宫国家遗址公园) | 1-1.5 h |
| Major complex (故宫中轴线+珍宝馆全程, 莫高窟 A 票, 布达拉宫) | 2-3 h |
| Castle / palace | 1.5-2.5 h |
| Observation deck / viewpoint | 45-60 min + queue |
| Market / food street | 60-90 min |
| Historic district stroll | 1.5-2 h |
| Garden / park | 45-90 min |
| Aquarium / zoo | 2.5-3 h |
| Theme park | full day |
| Photo-stop landmark | 15-20 min |

These are defaults, not answers: whenever a venue is a headliner for this user,
research its realistic visit time and note the source. Scale by pace: relaxed ×1.3,
packed ×0.8, kids or mobility flags ×1.3.

## Assembly method (per day)

1. **Pin the immovables first**: timed-entry tickets, reserved meals/shows, intercity
   departures, sunrise/sunset shots — these are `[pinned]`, contractually immovable.
   The crowd-window opener from rule 2 is different: it is `[opener]` — movable, but
   moving it costs an hour of queueing. Degradation and live-replan key off this
   distinction, so keep the two tags apart. Everything else schedules around them.
   Early-arrival margin is **tiered**, because a timed ticket buys a place in the
   security line, not entry: 15 min at ordinary venues; **30-45 min wherever there is
   security screening or an ID check** (故宫, 国家博物馆, 布达拉宫, 莫高窟——
   全部要预约+安检+证件核验, 渠道见 cn-domestic.md). And never plan to buy at the door at a flagship — ticket-office
   queues run 30-60+ min against near-zero online. If it can be bought online, even
   same-day, that IS the plan; an unavoidable door purchase gets its own +45 min block
   in the chain so the arithmetic sees it.
2. **Anchor the opener**: put the day's most crowd-sensitive venue at its opening
   time. Top sites are empty in their first hour; the same visit at 11:00 costs
   30-60 min of queueing. Crowd calendar beats the clock, though: put flagships on
   weekdays and save parks/markets/neighborhood walks for the weekend; check each
   headliner for **free-admission days** (commonly the first Sunday; Vatican Museums
   the last Sunday) — the free day is the busiest day of the month, so avoid it or
   treat opening-time arrival as mandatory; and the day after a venue's weekly closure
   day (Tuesday after a Monday closure) carries spillover crowds. When the date is
   fixed and lands on a weekend anyway — a layover, a city break, "we have Sunday
   free" — the rule still has a move: give the flagship the day's **first** entry
   slot, take the top of its arrival-margin tier (45 min), and name the weekend tax in
   the plan instead of pretending it isn't there.
3. **Chain by geography** in the day's cluster order: compute every hop with
   scripts/route_tools.py and verify the load-bearing hops per navigation.md. Each
   block = arrival + dwell + buffer.
4. **Buffers are policy, not padding.** "Hop time" means **door to door**: access
   walk + worst-case headway + in-vehicle + egress walk — and *then* the buffer
   (+10 min per urban hop; +15 min per unfamiliar interchange; +30 min after any
   luggage move). Counting only the ride is how a 25-minute block swallows a
   29-minute journey. The corollary is worth knowing: under roughly 1.2 km in a city,
   walking beats a one-stop metro once the wait is counted — so don't schedule the
   ride. Jet lag is real even when the user says it isn't (see Day types).
5. **Meals**: lunch 11:30-13:30, dinner 18:00-20:30（旅游城市晚市偏晚, 按当地
   实际核对；景区内餐厅普遍 14:00 后歇市, 错峰在 11:00 前或 13:30 后）, placed in a food area within 10 min of the adjacent cluster,
   60-90 min per meal.
6. **Energy curve**: at most 2 heavy anchors (>2 h) per day and never back-to-back,
   **and never more than ~3.5 h of continuous on-feet anchor time without a sit-down
   block** — the second test is the one that matters, because shaving two anchors
   from 2 h to 1 h 45 satisfies the first while leaving four unbroken hours on stone.
   One low-effort block (garden, café, shopping street) mid-afternoon — but see the
   siesta trap before putting shopping there; cap time-on-feet at ~8 h (6 h with kids
   or mobility flags).
7. **Golden hour**: run `python3 scripts/route_tools.py sun plan.geo.json --write`
   once the days have a city-level coordinate (any stop's `lat/lon`, or the
   Open-Meteo geocode from Phase 1 dropped into `stops[0]` — a venue 5 km away moves
   sunset by well under a minute) — and run it **before you write a single sunrise /
   golden-hour / dark-start sentence**, not after. 境内统一北京时间（UTC+8，无夏令
   时），但**经度差异极大**：乌鲁木齐的日落比上海晚约两小时（同样挂北京时间），所
   以"夏天 19:00 天还亮着"在西部是常态——prose 必须以 `sun --write` 的输出为准，
   凭习惯写时刻必然出错，且没有任何下游（`check`, `qc.py`, the renderers）会把
   prose 与 `days[].sun` 对账。Order:
   coordinates → `sun --write` → read the values → write the prose.
   It computes civil dawn / sunrise / sunset per day **locally with the built-in NOAA
   solar model（CN 适配版：零网络请求，大陆可用）** — keyed on **that day's first stop
   with coordinates** + date + tz — **except on a moving
   day, where it takes the day's LAST stop with coordinates**. A day is "moving"
   when it carries `"travel_day": true` **or** its first and last stops with
   coordinates are more than **150 km** apart; the script prints which rule fired
   ("last stop, first->last 1,090 km" / "(travel_day)"). Reason: the evening anchor
   and the sunset that matters are where you sleep, not where you woke up — the
   China test's Xi'an→Beijing day reported Xi'an's 17:41 against a Beijing anchor
   at 16:59 sunset, 42 min wrong on exactly the day that squeezes in an evening
   block. Order the moving day's `stops` in visit order with the arrival city last
   and the rule does the right thing. **When the day's sun-critical anchor is at the
   first stop instead** — 黄山山顶的日出（当天下午下山赴宏村）、泸沽湖的日出
   （环湖赴丽江）—— the last-stop default is 25 min
   wrong on exactly the block that cares, so override it: set the day's
   `"sun_stop"` to that stop's `name` (or its 0-based index in `stops`) and `sun`
   keys the day there. The header still prints one 天亮 for the whole day, so on a
   long east–west move say in the day note that the other city's dawn/dusk
   differs),
   **sanity-checks the answer**（`--api` 模式下沿用原校验：rejects `status≠OK`、two
   cities or two dates returning identical times, and a day length that cannot belong
   to that latitude and month — the failure mode that once returned equatorial
   12 h 09 m for Norway in October with `status: OK`；本地模式无此风险，模型直接按
   坐标+日期计算）, and writes each day's `sun` string in place.
   **Read the tail of its output**: after the "N request(s), N day(s) written" line
   it prints — and repeats as a `WARN` on stderr — `skipped/failed (N): <date>
   (reason), …` naming **every day it did not write** — the reasons are: no ISO
   date; no stop with coordinates; `tz approximate` (fix: set `days[].tz`, a
   plan-level `tz`, or pass `--tz Area/City` — the longitude guess is wrong
   wherever zones bend); request failed — plus one `sun REJECTED — …` WARN per
   day the sanity checks refused. A run that says "6 written" on a 7-day plan now names
   the missing date, so you re-run `--only DATE` instead of counting `sun` fields
   by hand (历史测试 F5) — and it **exits non-zero (1)** whenever that list is
   non-empty, so a "9/10 written" run cannot pass unnoticed in a pipeline (历史
   测试 F6: one TLS failure, exit 0, nearly shipped). The written days are kept;
   fix the named ones with `--only` and re-run until it exits 0. Exit **3** = a day
   was REJECTED by the sanity checks (look before retrying — a "polar day/night"
   rejection is not retried: remove that day's `sun` key (absent — not `null`, not
   `""`), output-template.md §`sun`, PLN-11). A day with **no stops
   at all** (pure travel/rest day) is informational only here — not counted, no exit 1 —
   but `plan_lint --strict` fails a stop-less day, so give a move day its airport stop.
   **Redirect sun's output to a file rather than piping it** (`… sun plan.geo.json
   --write > sun.log 2>&1`, then read the file) — a pipe makes `$?` the *last*
   command's exit and loses sun's non-zero signal. A transient TLS failure on one
   day is expected, not breakage: re-run with `--only DATE` for the day it names.
   Canonical `sun` format — the renderers parse it, so keep the shape:
   `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · 本地天文计算`
   e.g. `天亮 05:28 · ☀ 05:53 / 🌇 17:38 · CST · 本地天文计算` —
   `plan_lint --strict` accepts this shape only; never hand-write it.
   （境内版只有本地天文计算一条路径，`--api` 模式已移除；尾标只能是
   `本地天文计算` / `NOAA local solar model`。）
   (TZ may be a numeric offset like `-05` where the zone has no abbreviation — normal).
   The dawn word follows the plan language: `sun --write` picks it from `--lang` >
   `plan.lang` > `plan.meta.lang` > zh, so an `en` plan gets
   `dawn HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · NOAA local solar model`
   e.g. `dawn 05:28 · ☀ 05:53 / 🌇 17:38 · CST · NOAA local solar model`; the renderers
   accept either spelling (zh output is unchanged).
   **A space always follows a time**; never glue a bracket to it — `🌇 18:00(AEST`
   is what the "golden hour ≈ …" margin line showed when a tester wrote
   `18:00(AEST · …)`. Extra words go after a ` · ` separator.
   （境内无夏令时切换，无需跨切换日取值；跨省长途把每天的日出日落按当日所在
   城市分别核对即可——脚本是逐日计算的）。
   Manual fallback only when python itself cannot run (then `plan_lint` cannot run
   either): `sun` 的本地模型本身离线可用——真正无法跑 python 时手算民用晨光/
   日出日落（公式或任意天文页面），按 canonical shape 填写、尾标注 `本地天文计算`
   并给该日 note 标 "sun hand-fetched"。
   The response carries `civil_twilight_begin/end` — that is 天亮/天黑 as a
   traveller experiences it, ~25-30 min outside sunrise/sunset. Pre-dawn departures
   and sunrise hikes schedule against **civil dawn**, not sunrise: a 06:00 trailhead
   entry for an 06:22 sunrise is a dark-start (headlamp) only if civil dawn is 06:01.
   Any day that starts before civil dawn gets the 天亮 time printed in its header and
   a "prebooked car, no street-hailing in the dark" note.
   Photography interest → schedule one viewpoint or walk at golden hour. Always check
   evening blocks against sunset: an unlit garden at 19:30 in November is a bug; a
   night-view deck is a feature — know which one you scheduled.
8. **Degradation plan**: tag every block that is neither `[pinned]` nor `[opener]`
   as `[skippable]` or `[swap → alternative]`, and give each day one line: "running
   >1 h late → cut X". On-the-ground plans fail; a plan without a failure mode is the
   failure. Swap targets get the same closure check as anchors — a fallback that is
   shut on the day it backs up is worse than none.
9. **Resolution**: quarter-hour granularity ("14:00-15:30") for anything you
   estimated — false precision like "14:07" destroys trust in the honest numbers.
   Verified timetabled departures and arrivals are the exception and keep their
   published minutes ("09:15-11:31"), because that is exactly where the extra digits
   carry real information.
10. **Weather shapes the day** — read the day's forecast or climate line
    (data-sources.md §Weather) before ordering the blocks:
    - **Heat** — max ≥ 32 °C, apparent max ≥ 35 °C or UV index ≥ 8 (UV exists only
      in forecast mode; in normals mode a country note such as "UV extreme" is the
      trigger): no unshaded
      open-air anchor (ruins, markets, hikes) between 11:00 and 16:00 — they take the
      opener slot or start after 16:30, and the early afternoon holds an indoor or
      air-conditioned anchor or a long lunch; open-air dwell ×1.3 (the "hilly and
      unshaded" surcharge above folds into it); the continuous on-feet cap drops from
      3.5 h to 3 h; the day note carries "water · shade · hat".
    - **Rain** — precipitation probability ≥ 60 %, or a rainy-season base (≥ 7 rain
      days in 10 on the climate line): the `rain_alt` becomes the main line and the
      outdoor version becomes the `[swap → …]`; every boat, cable-car and balloon
      anchor carries "weather cancellation → backup date" in its note.
    - **Wind** — gusts ≥ 50 km/h: balloons, boats, open decks and high towers get the
      cancellation-risk note and a named fallback.
    - **Cold** — min ≤ 5 °C, or min ≤ 0 °C at a dawn anchor (`temperature_2m_min`;
      no recipe fetches an apparent minimum): shorter outdoor
      blocks, lunch indoors, the dawn temperature printed in the day header note.
    The same thresholds are what the T-7 re-check re-applies (output-template.md
    §Pre-departure re-check ladder).

## Day types that need a different structure

- **调休补班日与黄金周首末日（境内独有）** — 调休补班的周六（上班日）周边游
  反而是错峰好日子：景区/高速比正常周末空——把「补班周六」排户外主行程、
  正常周日排城市行程是常见的省人流组合。黄金周**首日与末日**是高速/高铁最堵
  点：骨架选日期避开首末日出发，避不开就注明「早 7 点前出发」，且首日不排
  任何预约制场馆（长途晚点会作废预约）。假期拼假窗口见 phase-1-brief.md。
- **Arrival day** — landing before 15:00 = half a sightseeing day, later = **zero
  sightseeing days for the count** — but the evening still gets one free, walkable,
  unticketed block near the hotel (same rule in SKILL.md Phase 2 §3). The
  first morning after a long-haul arrival starts no earlier than 10:00. Plan the first
  evening within walking distance of the hotel; nothing ticketed.
- **Moving day (base change)** — luggage-encumbered from checkout (10:00-11:00) to
  next check-in (~15:00), so this is a day-structure problem, not a buffer problem.
  Solve bags before scheduling anything: (a) store at the departing hotel and loop
  back, (b) coin lockers or staffed storage at the rail hub actually used — large
  lockers at major stations sell out by mid-morning, so name a fallback, (c) 酒店
  间行李寄送/闪送同城（大城市可代办, 先电话确认时效）, 隔夜随身包随身带。 Never schedule an anchor with bags in tow — rule 2
  (opener at opening time) is suspended on a checkout day unless bags are already
  stored. **An intercity moving day carries ≤2 anchors, and only when the bags are
  solved before the first anchor (checked / stored / hotel-held); otherwise 1** (same
  sentence in references/phase-6-assemble.md §Adversarial self-check). Two is for the day whose train leaves at
  16:00 and whose bags went into a locker at 09:00 (上午莫高窟 + 鸣沙山, 傍晚
  火车进疆); a day that drags a suitcase to the first
  sight is a one-anchor day whatever the timetable says. Third case,
  **transfer-day-as-itinerary** — the bags ride locked in a private vehicle door to
  door (a hired car with driver, a private tour van), never dragged and never stored:
  then the anchor cap is the pace cap, not 2, and the surviving constraint is the
  energy curve (rule 6). If the sunrise anchor is at
  the *first* stop, set `sun_stop` (rule 7).
- **Departure day** — zero sightseeing unless the flight leaves after 18:00. Work
  backwards from the airport-arrival deadline (3 h international) through the real
  city→airport transfer time, and put the luggage solution in writing again.
  **Return-flight time unknown** (`flight_scan.py` lists outbound legs only, and the
  deep link may not show it statically): pick a plausible departure `T` from the
  carrier's published schedule (or the outbound's mirror), and write the day
  backwards from it as a formula the reader can re-run: **T = takeoff → T−3 h at the
  airport (international; 2 h domestic) → T−4 h 30 leave the hotel** — e.g.
  `T ≈ 12:30 → 09:30 at IST → 08:00 out of the hotel`. The `legs` row carries
  `"dep": "⚠️ ~12:30 — verify"` (not a bare time), the timeline blocks say "T−4h30"
  next to the clock, and `unverified` gets one line: "return flight departure time
  not confirmed — day 10 timeline is built on T ≈ 12:30". A confidently wrong 08:00
  taxi is worse than an honest formula.
- **Tour day (跟团日)** — the pickup is `[pinned]` with a 10-15 min margin, and the
  operator owns the clock: no `late_cut` authority inside the tour, so the day's
  degradation plan covers only what the traveller controls (meals, the evening, the
  next morning's buffer). The evening BEFORE a tour day carries its own pins: buy
  provisions, pack per the tour's luggage rule (2-day tours are often
  overnight-bag-only), sleep early enough for the pickup. A "free activity" block
  inside a tour = the bus waits for latecomers — schedule an alarm, not an itinerary.
- **Dateline day** — a westbound trans-Pacific return to East Asia consumes **two
  calendar days** (depart HNL Oct 5 → land Oct 7); eastbound you land the same day
  you left. Lock the return leg FIRST and allocate the final city's days from it —
  planned the other way round, the dateline silently deletes a day from the last
  stop (learned live: it cost Hawaii its circle-island day).

## Traps that break otherwise-correct timelines

- **宗教场所与周一闭馆 — 全国通用，大城市也不例外。** 清真寺在五番礼拜时段
  （约 30-45 min，每日偏移）与周五主麻不对非礼拜者开放——按当日礼拜时间核对；
  寺庙的法会/早晚课时段大殿不接待，进殿着装一处一句（不过肩不过膝）；
  **博物馆/纪念馆周一闭馆是全国默认**（法定节假日除外），排 day 时先对表，
  撞上的那天改公园/街区/市场——这是计划最常漏的一半。
- **县城与小城镇午休歇业 — 西北/西南县域普遍。** 部分餐馆、独立小店 13:30-15:00
  左右关门午休；午后的板块必须安排确定营业的点（大馆、园林、咖啡馆、宽午餐），
  购物与逛街挪到 15:00 后。未核实营业时间的小店一律按午休闭门假设。
- **周末集市/早市歇业**：城市菜市场与周末集市是周日陷阱（部分摊主周日休息、
  早市仅清晨开）。若美食是用户明说兴趣，围绕集市建餐前先核实其一周开市日。
- **Closures the holiday API can't see**: local festivals (streets closed, hotels 3×),
  seasonal operating windows (cable cars, mountain huts, gardens, boats), per-venue
  annual maintenance, and Ramadan in Muslim-majority destinations. SKILL.md Phase 1
  budgets a search for these; the Phase 6 closure scan re-checks them.

## Timeline verification (runs inside the Phase 6 self-check)

- Chain arithmetic: every block starts ≥ previous block end + hop time + buffer
- Anchors: arrival ≥ opening; arrival ≤ last entry; planned exit ≤ closing
- Pinned tickets: arrival margin matches the tier in rule 1 (15 vs 30-45 min)
- No more than ~3.5 h of continuous on-feet anchor time without a sit-down block
- Walking total ≤ 8 km, counted honestly: `check`'s **on-foot** line ×1.3 (its ridden
  line is not walking — mark those hops `"mode": "transit"` so it can tell), **plus**
  in-venue walking and any stroll segments. A stroll is invisible to `check` unless
  you model it as a stop at its midpoint — so model it, and show the arithmetic in
  `walking_km: {total, how}` rather than asserting a bare number.
- Late evenings: last planned hop vs the line's last departure (verify, don't assume).
  If lodging isn't in scope, say "day starts at {first block} / ends at {last block};
  add your hotel hops" and mark this check N/A rather than passed.
- Meal blocks exist and actually sit near the clusters they claim
- Moving days: bags solved in writing, no anchor before storage; ≤2 anchors only if
  the bags are solved before the first one, otherwise ≤1 (§Day types)
- Departure day with an unconfirmed return time: the T-formula is visible in the
  timeline, `legs.dep` carries ⚠️, `unverified` names it (§Day types)
- Worship/siesta/free-day traps checked for every affected block
- Weather rule 10 applied: a heat day has no unshaded open-air anchor 11:00-16:00, a
  wet day's main line is the indoor version, wind-sensitive anchors carry the
  cancellation note and a fallback

## Scheduled-day format

Hop rows use the canonical format from navigation.md, and every hop is marked
`(verified)` or `(est.)` so the reader knows which durations were actually checked.
**The arithmetic below is meant to be copied**: every block starts at the previous
block's end plus the hop plus its buffer, and this day passes the whole verification
list above. If you catch yourself writing a 0-minute gap between two places 1 km
apart, that is the bug this example exists to prevent.

```
2026-10-05 (周一) — 杭州·西湖东线    天亮 05:28 · ☀ 05:53 / 🌇 17:38 · CST · 本地天文计算
08:00-09:15  灵隐寺 ¥45 — 06:30 开门,首小时人最少                     [opener]
09:15-09:45  步行 灵隐寺→法镜寺 0.7 km ~10分(+街景停留)              (est.)
09:45-10:45  法镜寺 ¥10 — 09:00-17:00,最晚入场 17:00
10:45-11:00  步行 法镜寺→龙井村 0.4 km ~5分                          (est.)
11:00-12:00  龙井村茶歇/午餐 · 农家茶楼一带                          [swap → 楼外楼]
12:00-12:30  公交 87 路(往黄龙洞) 8站/28分 ¥2 · 龙井茶室→浙大附中 · 下车步行6分  (est.)
12:30-14:00  步行 植物园→曲院风荷 1.1 km ~16分                        (est.)
14:00-15:30  断桥残雪→平湖秋月→湖滨散步 ~3.0 km(按站点建模,否则不计入步行总量) [skippable]
交通算账:公交 1 段 ¥2 + 步行为主 < 西湖游船 ¥70 → 陆路走东线
步行合计:check 2.6 km×1.3 + 湖滨 3.0 ≈ 6.5 km < 8 km ✓
迟到 >1h → 先砍法镜寺,再砍湖滨段;灵隐寺须 17:30 前入场
雨备:浙江省博物馆之江馆(室内,周一开放 — 已核实)。⚠️ 勿用中国茶叶博物馆双峰馆:周一闭馆
时刻/票价为 2026-08-01 查得的季节性数据,出行前两周复查
```
