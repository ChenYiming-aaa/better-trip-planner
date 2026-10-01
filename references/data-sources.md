# Data sources & URL recipes（境内版）

Fallback order everywhere: bundled script / keyless API → browser pane → web search →
deep link marked "verify on click". Statuses marked ✓ were live-tested 2026-08-01.

> **境内版（domestic-China-only build）**：本 skill 仅支持中国大陆境内行程，所有
> 境外服务与配方（Google/Skyscanner/Booking/Nominatim/sunrise-sunset.org/领事与外国
> 预警/汇率换算/签证）已整体移除，不存在任何境外选项或入口。地图链接只有高德/百度
> （`route_tools links`，默认 amap，境内坐标自动 WGS84→GCJ02 纠偏）；地理编码走高德
> （`AMAP_KEY`）+ 百度回退（`BAIDU_MAP_AK`）；日照为本地 NOAA 天文计算（零网络）；
> 机票/火车价格经 `flight_scan.py` 深链由用户点开核对（国内无免钥票价 API，绝不猜价）；
> 假日调休查国务院公告 + timor.tech；安全与天气预警查中央气象台/景区官方公告。

## 机票（境内航班）
- **【境内可用·首选】** `python3 scripts/flight_scan.py --from PVG --to PEK --depart
  2026-10-01 --nights 7 --flex 2` — 零依赖零网络，输出日期网格的携程 / Trip.com /
  去哪儿机票深链 + 携程火车票深链（单程/往返/±flex 都支持；`--rail` 只要火车）。
  **国内没有可用的免钥票价 API**（携程/去哪儿无公开 fare 接口，页面有 bot 墙），
  所以价格必须由用户打开链接核对；plan 中的价格字段照旧写 "—，点链接核对"，
  不要凭搜索结果猜测。
- **价格核验规则**：每个航段至少 2 个来源（携程 + 去哪儿 / 航司官网 / Trip.com 任选二），
  `legs.note` 记录来源 + as-of；两源差 >10% 写区间。**Cheapest-by-price hides usable
  flights**：低价行常是红眼/次日到达，喂给 pinned 事件的航段人工核对到达时刻。
- **【境内可用】Browser 深链**（打开即查）：
  - 携程（单程）`https://flights.ctrip.com/online/list/oneway-{orig}-{dest}?depdate={YYYY-MM-DD}`
  - 携程（往返）`https://flights.ctrip.com/online/list/roundtrip-{orig}-{dest}?depdate={…}&retdate={…}`
    （机场码小写，如 `pvg-pek`；人工核对出发时段、行李与退改）
  - Trip.com `https://www.trip.com/flights/showfarefirst?dcity={ORIG}&acity={DEST}&ddate={YYYY-MM-DD}&triptype=OW|RT&quantity={N}`
  - 去哪儿 `https://flight.qunar.com/`（站内搜出发点-目的地 + 日期）
- **【境内可用】** 廉航官网直查：春秋、西部航空、中联航等（行李/退改规则更严，
  比价时单独列一行）。
- **Never** curl airline/OTA sites — instant bot-block, wasted call.（不变）

## Group tours (跟团) — when the traveller prefers not to self-drive
The tour product replaces flights+car+hotel for its days, so research it FIRST — its
schedule dictates the surrounding legs, not the other way around.
- **Where to look**: operator sites first (prices/terms authoritative), then
  aggregators (携程/飞猪度假、美团/大众点评跟团;
  境内 OTA 的跟团频道——同一产品比 2 个渠道的总价与成团状态)。

## Hotels
No good keyless API exists — use browser + deep links; recommend neighborhoods and
2-3 properties with a price band, and let the user's click show live prices.
- **Compare on the checkout screen's all-in total, never the list price**:
  resort/amenity/urban fees ($30-56/night on resort strips, common in NYC) plus
  ~19% taxes sit between the two — sometimes inside the list price, sometimes
  payable at the property; only the final screen settles which. Calibrate scores
  to the destination's baseline (an ageing resort strip's 8.0 ≈ a mainland
  boutique's 8.5), and when the itinerary has pre-dawn starts, read the RECENT
  low reviews for the three sleep-killers — AC, street/door noise, slow
  elevators — before price breaks the tie. **Cross-validate the score on a second
  platform with a different reviewer base** (携程 ↔ 美团/飞猪;
  tie-break): the bases weight cleanliness, noise and breakfast differently, so
  agreement adds confidence and a gap >0.5 is itself a finding — read that
  hotel's low reviews before shortlisting it. The cross-check applies to PRICE
  too: platforms contract different rates for the same room (Agoda often
  undercuts for Asia-market users by tens of dollars a night) — compare
  like-for-like (same room, refundable vs non-refundable) before paying, and
  remember the cancellation terms you get are the booking platform's, not the
  cheapest platform's.
- **【境内可用·首选】** 携程酒店 `https://hotels.ctrip.com/hotels/list?city={cityId}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}`（cityId 用站内搜索获取，或直接浏览器搜"城市+酒店"后带日期复制链接）、飞猪 `https://hotel.fliggy.com/`、美团/大众点评（境内游）、Agoda `https://www.agoda.com/zh-cn/`（亚洲库存深，大陆可直连）。深链模板（Agoda 可带日期）：
  `https://www.agoda.com/zh-cn/search?city=18343&checkIn={YYYY-MM-DD}&checkOut={YYYY-MM-DD}&rooms=1&adults={N}`（city 参数为 Agoda 城市 ID，浏览器搜索后从 URL 复制）。
- **【已移除】** Google Hotels / Booking.com 等境外酒店渠道不再提供（境内-only）。
  `https://www.booking.com/searchresults.html?ss={CITY}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&group_adults={N}&order=review_score_and_price`
  —— 大陆可达性时好时坏（Booking 有时跳转慢或要求验证），仅作第二评分来源使用；
  在页面 UI 里**先设日期再读价**（URL 日期参数会被静默忽略——页面默认显示近期底价，
  曾被当成 9 月价实际是 8 月价）。

## Travel insurance (旅行险)

- **Three layers, and the numbers live in the last one**: the product page's
  coverage table sells, the clause PDFs define, and the issued policy schedule
  (保单) decides — on the audited product, clause after clause read
  "以保险单载明为准" for exactly the numbers that matter (illness waiting
  period, deductible and payout ratio, delay-hour thresholds, per-category
  sub-limits). Verification does not end at the purchase screen: the picker
  lookalikes and the waiting-period question bite BEFORE buying; the rest is
  read off the issued policy (the user supplies it). Four checks — the
  destination list (the purchase flow's picker, on the user's side, has
  lookalikes of its own: "United States Minor Outlying Islands" is NOT Hawaii
  — Hawaii lives under "United States"), the illness waiting period (a 15-day
  trip dies on a 30-day wait), deductible/payout ratio, and the assistance
  hotline, which may appear nowhere else (live case: the clause docs named no
  provider at all; the hotline existed only on the schedule).
- **Buy before the world moves**: trip-change/cancellation cover excludes events
  already announced or occurred at purchase time (declared strikes, named
  storms, an erupting volcano, announced epidemics). When the plan carries a
  monitored natural-hazard gate, the insurance row's deadline is NOW, not
  "before departure" (the user buys — SKILL.md Hard rule 1) — every day of
  delay is a day the exclusion can crystallise.
- **Match the itinerary's activities against the exclusion list by name**: main
  policies exclude a defined high-risk-sports list — horse riding/马术 commonly
  sits on it (it did here), alongside diving and climbing; the fix is a product
  whose high-risk extension names the activity — and the extension's claim
  rules bind (live case): the operator booking voucher plus an incident
  certificate FROM THE ORGANISER were required claim documents, so the plan's
  day note says to keep them. Guided sessions inside a licensed commercial
  venue usually satisfy the organised-activity carve-out; the same activity
  self-organised often does not.
- **Riders can carry purchase-time windows**: an event-ticket cancellation rider
  demanded insuring within a day of paying for the ticket — tickets bought
  before the policy can never be covered by it, and a ticket bought at a later
  gate needs the same-day insurance linkage written on that gate's checklist
  row. Read which clause actually carries each prepaid item's risk: a delay
  rider quietly covered missed-event ticket loss the cancellation rider could
  not.
- **A self-drive day is a stack, and travel insurance is the thin layer**: the
  personal-liability rider excludes motor vehicles wholesale, and on the
  audited policy the rental-car rider was a gap-filler paying only on top of
  the rental counter's own CDW/theft/third-party cover — declining the
  counter's coverage leaves the rider paying nothing (check whether the user's
  policy is excess-only or primary). Say it on the self-drive day itself:
  third-party cover comes
  from the rental counter, not the travel policy; and watch the policy's
  blood-alcohol line (20 mg/100 mL ≈ one drink on the audited policy — it
  voids the whole day, not just the drive).
- **Once bought, the 保险 brief becomes an operating card, not a purchase
  reminder**: assistance hotline + policy number, the first-call rule
  (approval-first clauses are common — on the audited policy, medical
  transport arranged without the assistance company's approval was not
  reimbursed), and the evidence discipline — hospital ER over standalone
  clinics (the medical-facility definition can exclude urgent-care
  storefronts), itemized bill before leaving, police report within the
  policy's window (24 h here) for theft, PIR at the baggage belt, and
  jewellery is often an excluded or sub-limited property class, so advise
  leaving it home.

## Intercity rail / bus / local transit
- **【境内可用·首选】** 时长与接驳用高德/百度网页版路线规划核对：
  高德 `https://ditu.amap.com/dir?from={lon,lat}&to={lon,lat}&mode=bus|car|walk`、
  百度 `https://map.baidu.com/dir/{A}/{B}@…&mode=transit`（浏览器操作即可）；交付给
  用户的跳转链接统一由 `route_tools links --provider amap|baidu` 生成（默认 amap，
  见 navigation.md）。
- **【境内可用·首选】** 12306 官网/App（12306.cn，实名账号；查询余票、时刻、
  经停）。Real-name rules（每人一张实名票、候补/起售时间点）、预售期与进站安检
  （电子票刷身份证闸机）按 12306 官方说明执行；高峰期放票节点见 phase-1-brief.md
  的行前阶梯。
- 汽车票/城际巴士：携程汽车票、当地客运站公众号或小程序；地铁/市内公交接驳用
  高德/百度路线规划核对（上面的深链即可）。

## Geocoding & day-route sanity — ✓
Venue-level coordinates via `scripts/route_tools.py geocode` — CN-adapted order:
**preset coords > geocache > 高德 restapi（需 `AMAP_KEY` 环境变量或 `--amap-key`；结果
自动 GCJ02→WGS84 回写，计划文件里始终只存 WGS84 一种基准）> 百度 geocoding v3
（`BAIDU_MAP_AK`）**。
高德在国内快且稳，中文地名命中率极高（key 免费申请：
lbs.amap.com → Web 服务）；无 key 或高德失败时自动回退百度（
缓存，脚本已内置，勿并行调用）。Misses: 在高德/百度网页版地图查地点，从链接或
坐标拾取器取 WGS84/GCJ02 坐标手工填入计划 JSON（GCJ02 填入前先换算，或用
route_tools 的 amap 源自动处理）。高德对生僻地名/新景区偶尔查不到时，换百度源重试，
或直接用网页版地图的坐标拾取器手工取点（百度拾取坐标系为 GCJ02，需换算）。
Then `check` (distance/clustering sanity), `links` (per-hop + whole-day deep links —
**`--provider amap|baidu`**，**默认 amap**（境内直连，坐标自动
WGS84→GCJ02 纠偏）；两者都只出逐跳链接、无 day chain), `kml` (offline pins for Organic Maps
/ My Maps — the provider-independent fallback), `sun` (civil dawn / sunrise / sunset
per day, **本地 NOAA 天文计算，零网络（境内版唯一路径）**，written
as `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · 本地天文计算`，en 页为 `NOAA local solar
model` — `--lang zh|en` > `plan.lang` > `plan.meta.lang` > zh; renderers accept both).
Details: references/navigation.md.
- `check` reads a per-stop `mode` from the vocabulary **`walk | transit | fly |
  drive | boat | train | bus`** (the hop *into* that stop). Anything undeclared is
  guessed from distance, and a guess is silent: a 1.7 km coastal walk becomes
  "transit" and the day's on-foot total reads 0 — declare signature walks. Declared
  fly/drive/boat/train/bus hops are listed as long hops, not `SUSPICIOUS`, so a
  plan with a flight or a reef boat can pass `check` cleanly.
- `check`'s transit durations are a distance formula with no knowledge of tunnels,
  express lines or airport trains: **for any transit hop >20 km it says "use the
  operator timetable" — do that** (大兴机场线 草桥→大兴机场 is 19 min; the formula
  gave 40-60). Timetable = 12306（铁路/城际）或当地地铁/公交官方 App 与小程序
  （北京地铁、Metro 大都会、车来了等），按计划实际乘坐时段核对。

## Venues, tours, tickets
- Hours/closures: official venue site first; 高德/百度地图 place card second
  （【境内可用】App 内看"营业时间/临时闭馆"标签；博物馆/景区以官方公众号或
  小程序的预约公告为准）；blogs last and only if <12 months old.
- Ticket platforms for comparison + booking links（【境内可用】）:
  携程景点/门票 `https://you.ctrip.com/` · 美团/大众点评（境内游首选）·
  飞猪度假 · 美团/大众点评（本地玩法与当日票主力）。
  Platforms sometimes cost MORE than the official site — compare before recommending.

## 灵感与攻略来源（境内）
- **马蜂窝 / 小红书**：**只作灵感来源，不作事实来源**——开放时间、票价、预约
  规则一律回到官方公众号/景区官网与美团实价复核。小红书"绝美机位/出片攻略"类
  内容时效与真实性差（滤镜机位、已停业店铺常见），引用任何具体事实前必须
  二次核实并标注 as-of 日期；笔记里提到的"避开人流时段"可作为排程假设，
  但写入计划前用官方预约数据交叉验证。
- 硬规则不变：**绝不把 UGC 内容当作票价/时刻/政策的依据**（SKILL.md 硬规则 2）。

## Public holidays — ✓
- **【境内可用·中国大陆目的地】** timor.tech 节假日 API：
  `curl -s "https://timor.tech/api/holiday/info/{YYYY-MM-DD}"`（单日，含调休上班判断）；
  年度表 `https://timor.tech/api/holiday/year/{YYYY}`。国务院办公厅公布的放假日历
  人工核对一遍（API 是社区维护，闰年/新公告以官方为准）。
- **【不稳定，国际目的地】** Nager.Date：
  `curl -s "https://date.nager.at/api/v3/PublicHolidays/{year}/{ISO2}"` (keyless,
  大陆可达性时好时坏——失败时用浏览器开 date.nager.at 或 timeanddate.com
  `https://www.timeanddate.com/calendar/?country={code}&year={YYYY}`【境内可用】).
  Long weekends near the trip = domestic-tourist crowds even without a direct
  collision — check the adjacent weeks too.
**It lists fixed-date secular / statutory holidays only.** In Muslim-majority
countries the lunar-calendar holidays — Eid al-Fitr, Eid al-Adha, Mawlid, Islamic New
Year, and Ramadan itself — are **absent** (2026/MA returned 10 rows, every one a
fixed civic date, zero Eids); Buddhist-calendar holidays in Thailand, Laos, Myanmar,
Sri Lanka (Vesak, Asalha Puja, Khao Phansa…) and the Lunar New Year cluster across
East/Southeast Asia are patchy or missing the same way. Spend one budgeted search on
them: the country's official gazette / government holiday page, or a religious-
holiday calendar page (timeanddate-style) for the year — and put the dates in
`brief.holidays` with that source. Eid dates are moon-dependent and published as
"expected" until ~1 day before: mark them ± 1 day.

## Weather — ✓ (archive call can take ~10 s on first hit)
**【不稳定→可用】Open-Meteo 各端点大陆均可直连**（未被封但偶有慢/超时），保留为
默认气象源；失败或需要中文预报时的替代：**【境内可用】和风天气 QWeather**
（dev.qweather.com，免费 key）或高德天气 API（`AMAP_KEY` 复用，仅国内城市）。
日期超出 16 天预报窗口时的历史同期/气候态仍用 Open-Meteo 的 2a/2b 两路。
1. Geocode the city: `curl -s "https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"`
2. **Normals for dates beyond the forecast window — two calls, never one year's
   sample.** Last year's same dates is one draw (one typhoon week rewrites "October
   on the coast"); use both of these and write what they agree on:
   - 2a. Five-year archive window, one call per city (✓ 2026-09-02: the call spans the
     whole {dates-5y}→{dates-1y} range — 1,471 daily rows for a 10-day trip, of which
     only the rows whose month-day falls inside the trip's dates are used;
     on 2026-09-03 the endpoint answered 502 to every
     window for an hour — transient: retry with `--max-time 90`, and fall back to 2b
     alone if it stays down; the three extra variables ⚡ re-verify on first use):
     `curl -s --max-time 90 "https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={dates-5y}&end_date={dates-1y}&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,precipitation_sum,precipitation_hours,wind_gusts_10m_max&timezone=auto"`
     Keep only the rows whose month-day lies inside the trip window (5 per date),
     then aggregate per month-day: median max / min, the share of
     rain days (≥ 1 mm), the wettest day, the gustiest day.
   - 2b. Climate-model normals, three models averaged (✓ 2026-09-03, keyless, any
     future date):
     `curl -s --max-time 90 "https://climate-api.open-meteo.com/v1/climate?latitude={lat}&longitude={lon}&start_date={dates}&end_date={dates}&models=EC_Earth3P_HR,MRI_AGCM3_2_S,MPI_ESM1_2_XR&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"`
     The response carries one column per model (`temperature_2m_max_EC_Earth3P_HR` …):
     **average them and never quote a single model** — two models put 5 mm and 70 mm
     on the same day in testing.
3. Trip dates within 16 days of today → the real forecast for those dates (✓
   2026-09-03 with every variable below):
   `curl -s --max-time 90 "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,precipitation_probability_max,uv_index_max,wind_gusts_10m_max&timezone=auto&forecast_days=16"`
   `apparent_temperature_max` + `uv_index_max` (heat), `wind_gusts_10m_max` (wind),
   `precipitation_probability_max` (rain) and `temperature_2m_min` (cold) are what
   scheduling.md rule 10 reads.
   **Per-day source selection**: a date ≤ today + 15 → forecast; any later date →
   normals (2a + 2b); a trip that straddles the boundary gets both, each day labelled.
   **Every weather line is stamped** with its mode and date — `… · Open-Meteo
   forecast · as-of 2026-09-02` or `… · 5-yr normals + climate model · as-of
   2026-09-02` — in `brief.weather` and in any per-day weather note; the T-7 row of
   the pre-departure ladder (output-template.md) re-runs step 3 and re-applies rule 10.
   Run all of these with `--max-time 90`, one city per call, and assert the body is
   non-empty JSON before reading numbers out of it — an empty 200 looks identical
   to a stall.
4. Sunrise/sunset for golden-hour scheduling — preferred path is
   `python3 scripts/route_tools.py sun plan.geo.json --write`（**CN-adapted: 默认本地
   NOAA 天文计算，零网络请求，国内无障碍**；结果与原 API 值差 ±1-2 分钟）。per-day
   value keyed on the day's first stop — the **last** stop on a moving day, or the
   day's `sun_stop` when set —, canonical `sun` string written into the plan, a WARN
   per skipped/rejected day with its date and a **non-zero exit** when there is any;
   see scheduling.md rule 7. Redirect its output to a file rather than piping — a
   pipe makes `$?` the last command's exit and loses sun's non-zero signal
   (scheduling.md rule 7). **Run it before writing any sunrise/golden-hour prose**:
   境内统一 UTC+8 无夏令时，但**经度差极大**（乌鲁木齐日落比上海晚约两小时）——
   凭感觉手写时刻必然出错，历史测试中手写时刻曾连续十天偏一小时；
   `sun`'s output is the truth, prose follows it.
   `--api` cross-check mode（原版行为，仅用户有代理或需对账时使用）走
   （境内版已移除境外日照 API——本地天文模型是唯一路径，无需对账。）

## 安全与预警（境内）
- **中央气象台** `https://www.nmc.cn/` — 城市预报与预警信号（暴雨橙色/红色、台风、
  暴雪、地质灾害）。橙/红色预警触发改期建议并与用户确认；蓝/黄色照常排程但户外块
  进 rain_alt。
- **景区公告** — 限流、预约告罄、临时闭园：各景区官方公众号/官网（browser pane）。
- **应急预警** — 国家预警发布 12379；属地应急管理部门公告。
- **旅游服务** — 12301（投诉/咨询）、12345（属地政务）。
- 等级行为映射（境内版）：橙/红色预警 = 停下来问用户；蓝/黄色 = 排程继续 + 备选；
  "部分区域"预警 → 逐 base/leg/day-trip 核对。

## 健康（境内）
- **中国疾控中心** `https://www.chinacdc.cn/` 健康提示 — 当季传染病/防蚊/防暑要点。
- **就医路径**：三甲医院急诊（每个基地写 1 家进 emergency 卡）；药店连锁
  （国大/同仁堂/老百姓等）常备药。
- **高原线**（川西/西藏/青海）：高反提示 + 阶梯适应 + 药品自备清单，保险须含高原。
- **无需国际旅行接种**；野外徒步提示蜱虫/防晒。
- 计划永远不开药方：写"自备药清单"与"就近三甲医院"，不写诊疗建议。

## 灾害与季节（境内）
季节表与 hazard gate 见 phase-1-brief.md §Hazard line。实时核查走：
- **中央气象台** `nmc.cn`（台风路径/暴雨预警）· 浙江台风网 `slt.zj.gov.cn`（台风路径图）
- **中国地震台网** `ceic.ac.cn`（近期地震）
- **国家预警发布** 12379 / 属地应急管理公告
- T-14 / T-7 / T-3 阶梯各复查一次（phase-1-brief.md）。

## Optional keyed upgrades (only if the user already has env vars set)
- `AMAP_KEY` — 高德 Web 服务 key（geocode 首选源；`check --live` 实时时距、
  `poi` 周边搜索、天气 API 均复用）。**个人开发者完全免费**；**未配置时须先向
  用户提示免费申请**（三步流程见 cn-domestic.md §5），配置前不阻塞（百度回退/
  手工坐标）。key 只放环境变量或 git-ignored 的 `.env`，**绝不提交入库**。
  **CN 版推荐默认配置**。
- `DASHSCOPE_API_KEY` — 阿里云百炼（通义万相生图），`themes/gen.py --provider
  dashscope` 用。
- `SILICONFLOW_API_KEY` — 硅基流动（Kolors 生图），`themes/gen.py --provider siliconflow`。
- `BAIDU_MAP_AK` — 百度地图开放平台 key（geocode 回退源；lbsyun.baidu.com 免费申请）。
Never ask the user to sign up for keys mid-plan; the keyless path is the default.
