# Phase 3 — 交通与城际段（境内版·procedure）

Read this at the start of Phase 3, before the first transport scan. SKILL.md Phase 3 is the
contract — inputs, outputs, and the gates that decide pass/fail; this file is the whole
procedure it points at: the plan shape, 机票与高铁（价格来源、车站/机场选择、行李算术），
城际铁公机抉择，自驾段，and what every
leg row records.

Inputs: the chosen route skeleton (Phase 2), `prefs.travel_style`, the Phase 1
预约/健康/预警 facts. Outputs: `legs[]` rows — one pick + one backup
per leg — the checklist rows for flights, date-locked rail and rentals, the budget rows
they imply, and the baggage walkthrough for multi-leg trips.

## Write to the plan shape

From here on you are writing `plan.geo.json`. **`assets/plan.example.json` is the single
source of truth for the plan's top-level shape** — `legs`, `checklist`, `budget`,
`hotels`, `brief`, `days[]`… — so open it (or output-template.md §Top-level plan
skeleton, copied from it) before writing a field. `budget` is a list of
`{cat, per_person, total, note}` rows, not `{note, rows}`; `legs` rows use
`from/to/dep/arr`. A wrong shape does not fail loudly: the renderers WARN and print an
empty section (they used to crash — the 云南 test lost both themed pages to it).

## 机票（境内航班）

- Run `scripts/flight_scan.py`（境内深链生成器：输出携程/Trip.com/去哪儿机票深链
  网格 + 携程火车票深链；国内无免钥票价 API，**价格一律由打开链接核对**，leg 行
  价格写 "—, check the flight_scan deep link"）覆盖日期窗口与两个 open-jaw 方向
  （`--oneway` 单程、`--flex ±3 天`、`--no-rail` 只出机票）。
- 人工核对：开携程 + 去哪儿或航司官网（国航/东航/南航/春秋官网 App）比价；
  **每一条 pick 与 backup 以 ≥ 2 来源核对**（data-sources.md §机票）；`legs.note`
  写明来源与 as-of 日期，> 10 % 分歧按价格区间写。No browser pane →
  深链网格 alone, and `legs.note` says "single source — link grid only".
- Multi-airport cities: compare fare + ground transfer cost + time（上海虹桥 vs
  浦东、北京首都 vs 大兴——虹桥/首都离市区近得多，省下的地面时间常值回票价）。
  A ¥200-cheaper fare into a far airport often loses.
- 廉航行李算术：春秋/西部/九元等 LCC 的票价不含托运行李——加购行李费后再比较，
  "便宜"票价 + ¥200 行李袋常常不便宜；免费手提额度按航司规则核实后写进 leg 行。
- 时刻表核验：深链打开后核对实际起降时刻与经停（境内支线航班经停常见），
  `verified` 才能写死时刻。

## 城际（高铁/火车/汽车）

- Mode rule: 高铁 wins under ~5 h station-to-station（市中心到市中心，无机场
  buffer——沪杭 45 分、京沪 4.5 h、京西 6 h 是步行距离以外的门槛）；fly beyond
  that or where rail does not reach（新疆/西藏/海南跨海）；夜间动卧只对省预算的
  行程开放。
- Price on **12306** — 唯一官方渠道（App/官网/车站窗口），第三方平台默认加价或
  捆绑加速包。起售时间点、候补规则、学生票/儿童票规则按 12306 官方说明
  （data-sources.md §城际）；高峰期放票即抢，车次表写进 checklist 的 T-14/T-7 阶梯。
- `trains.ctrip.com` 深链由 `flight_scan.py --rail` 生成，用于交付页的"点开核对"
  入口；出票仍以 12306 为准。

## Driving legs（自驾段）

- A 自然风光大区 without a car is a bus-tour compromise — decide that explicitly with
  the user, never by default（新疆环线、青海湖、川西、滇西北基本是 car-first）。A
  rental is its own leg: pick-up/drop-off at airports/高铁站, one-way drop fees noted
  （异地还车费常见 ¥300-800/次），and the airport↔景区 drive budgeted honestly
  （兰州→青海湖 ≈ 3 h，西宁→青海湖 ≈ 2.5 h；"地图上的近"常是半天的山路）。
- Record per driving leg: pick-up/drop point + counter hours（神州/一嗨/携程租车，
  柜台常在机场停车楼）, one-way drop fee, 景区↔机场 drive time (budgeted honestly),
  car class, price + as-of date, insurance note（基本险不含轮胎/玻璃，逐条读）,
  fuel estimate（油价按当前价+山区溢价）, 高速通行费估算, and 景区停车费
  （5A 景区停车 ¥20-40/天常见）。Driver licence: 中国驾照 + 驾龄要求按平台规则；
  **边防证**（西藏部分边境区域）是提前办理的 checklist 行，不是驾照问题。
- Gateway towns run out of cars and rooms in season — the rental and the first night
  go on the booking checklist, not the "later" pile. 雨季/冬季进山路线（独库公路
  封路季）在 season 卡点名。

## Record for every leg

**Record for every leg**: carrier/train number, date, dep/arr local times, price
（人民币 + as-of date）, **checked-bag policy**（全服务航司 20 kg 托运常见；LCC
按档位另购——4 段廉航是一笔真实预算行；高铁无行李重量限制，仅超规需托运）,
refund/change class（机票舱位退改规则逐档写明）, deep link. Multi-leg trips get a
**baggage walkthrough**: where the big bag physically is on every tour/venue day
（一日游 = bag stays at hotel；景区寄存点写明；2 日游常是过夜包）. Output 1 pick +
1 backup per leg.

## Exit criteria — tick every line before Phase 4

- [ ] `legs`, `budget`, `checklist` follow `assets/plan.example.json` shapes (budget is
      a list of rows; legs use from / to / dep / arr).
- [ ] Every pick and backup is priced in ≥ 2 sources, `legs.note` names
      them with the as-of date (or says "single source — no browser"), a > 10 %
      disagreement prints as a band；无票价的行写 "—, check the flight_scan deep
      link" 而不是编数字。
- [ ] 每一条 date-locked 高铁/机票行的起售/开售时间点在 checklist 上（T-14/T-7
      阶梯覆盖）。
- [ ] Every leg row: carrier · date · dep / arr local · price + as-of ·
      行李政策 · refund / change class · deep link; one pick + one backup.
- [ ] Self-drive: the rental is its own leg with pick-up / drop-off, counter hours, car
      class, price + as-of, one-way drop fee, 景区↔机场 drive time, insurance note,
      fuel, 高速费, 景区停车费; the
      rental and the first gateway night are on the checklist；需边防证的区域能
      提前办的行已入 checklist。
- [ ] Multi-leg trips carry the baggage walkthrough (where the big bag is on every tour
      / venue day).
