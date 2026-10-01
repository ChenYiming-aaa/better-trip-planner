# 地图与导航（境内版）

目标：计划里的每一跳都可点击——在手机上打开高德/百度的转弯导航——每天有一条
逐跳链接链和一份离线兜底（trip.kml）。与 scheduling.md 一起阅读，配合 Phase 4
时间线组装使用。本 skill 仅支持境内行程：地图 provider 只有 **amap | baidu**。

## The workflow

0. **Destination check**: 目的地必须在中国大陆（港澳台同样停止）。确认无误后再
   运行 `check` / `links` / `kml`；境内全部使用 `links --provider amap`（默认）
   或 `--provider baidu`。
1. Write the plan JSON — **name it `plan.geo.json` from the start**, because geocode
   edits a file with that stem in place and every later command then reads the one
   file that has everything. It feeds the maps, the KML and the final HTML, which is
   what keeps them from drifting apart:
   ```json
   {"trip": "hangzhou-apr",
    "days": [{"date": "2026-04-11", "label": "西湖东线",
              "stops": [{"name": "断桥残雪", "query": "断桥残雪, 杭州"},
                        {"name": "雷峰塔", "lat": 30.2318, "lon": 120.1489}]}]}
   ```
   `query` defaults to `name`; pre-filled `lat`/`lon` skip geocoding; `label` is the
   day's theme line, same field name everywhere. Add `"mode"` to a stop whenever the
   hop **into** it is ridden (or walked against the distance guess) — vocabulary
   `walk | transit | fly | drive | boat | train | bus` — because 1.4 km can be a
   two-stop metro ride or a pleasant walk, and only the plan knows which; the field
   decides the walking total, which directions the tappable link opens, and whether
   a 45 km boat or a 1,500 km flight is a declared long hop or a clustering mistake.
   **A signature walk longer than 1.6 km must carry `mode: walk`** or `check` counts
   it as ridden and the day's on-foot total silently reads 0 (the 西湖苏堤 case: 2.8 km
   步行没标 `mode: walk`，全天步行数读作 0)。**`stops` must mirror that day's
   anchors plus any modelled strolls, in visit order** — every map artifact and the
   walking total are computed from it, so a `stops` list that disagrees with the
   timeline ships a map of a different day.
   Give every stop-to-stop transition its own `kind: hop` row, even a two-minute one
   out the door: N stops ⇒ N-1 hop rows is what lets `links --write` put each URL on
   the right row by itself. Model a long stroll as a stop at its midpoint or its
   kilometres never reach the walking total. (render_plan.py adds more keys to
   the same file — see its docstring.)

   **Two ways that count goes wrong on ordinary days** (both found by testers on
   their first unfamiliar trip; both let `links --write` line up by accident and
   put the wrong directions on a row):
   - **The day's first hop (lodging → first stop) and last hop (→ lodging).** They
     are real hop rows in the timeline but the lodging is not a stop, so the row
     count is off by one or two. Either mark those rows `"map": false`, or —
     recommended — put the lodging into `stops[0]` / `stops[-1]` (a name plus
     `lat`/`lon` is enough). Writing it in fixes the count *and* gives the day chain
     its true start and end.
   - **A displacement written as an anchor.** A lake cruise (西湖游船), a scenic
     railway (建水小火车), a ferry crossing (厦门→鼓浪屿), a coach transfer inside
     a tour (九寨沟一日团): the ride is the day's main sight, so it lands in the
     timeline as `kind: anchor` — and then it is not a hop row, while its two ends
     are two stops. Keep the anchor row (that is what the traveller reads) but
     **add a `kind: hop` row for the displacement itself**, e.g.
     `游船 花港观鱼→三潭印月 20分`, and put `"mode": "boat"` (or `train`/`bus`/
     `drive`/`fly`) on the arriving stop so `check` stops guessing. Leave the row
     mappable (no `map:false`) when both ends are in `stops` — that is what pairs it
     with the geometry hop between them. Same rule for a coach that moves you
     between cities mid-day.
   - **Intercity rail / flight rows — the `map:false` truth** (two testers were
     misled by an older sentence that said "legs rows take `map:false`"; the rule is
     about the *stops*, not the row): if **both stations/airports are in that day's
     `stops`** (西安北 → 北京西, both written as stops), the hop **exists
     in the geometry chain**, so the row **stays mappable** — it gets no link (long
     leg, see below) but it holds its place and the count stays aligned. Only a row
     whose ends are **not** in `stops` — the leg is described by `legs[]` alone and
     the timeline hop row is just a reminder — takes `"map": false`, so it drops out
     of the count. Getting this backwards on a day with a rail leg parks every link
     of that day (`N rows vs N+1 hops`).
   - **A day that returns the way it came** (one road in and out, up the valley and
     back — 庐山牯岭镇原路往返, 恩施大峡谷一炷香折返): only the outbound chain
     rows stay mappable; every retraced return row takes `"map": false` — its
     geometry already exists in the forward direction, so a mappable return row
     would demand a hop the day's chain does not have.
   **Three more shapes that go quietly wrong** (all three on one 山西路 day — 13
   links parked on the first `--write`, then every later pairing off by one; the
   command itself was green):
   - **One row covering two hops.** `大同南站 → 应县木塔 → 悬空寺` written as one
     line while `stops` has all three places ⇒ 3 stops, 1 row. Correct: two hop rows
     (`大同南→应县木塔`, `应县木塔→悬空寺`), or drop the middle place from
     `stops` if nothing happens there.
   - **Out-and-back with no return row.** Walk up to 颐和园佛香阁 and
     back down: the return is not a new stop, so it feels like no hop — but if the
     viewpoint is in `stops` and the next stop is back at the gate, the walk down
     *is* the hop into that stop and needs its own `步行 佛香阁→东宫门 …` row.
     (Alternative: keep the viewpoint out of `stops` and mark the whole excursion a
     `kind: anchor` block; then no rows either way.)
   - **The 100 m hop that doesn't feel like one.** 五台山五爷庙 → 塔院寺 is two
     stops in `stops`, so it is one hop and needs a row even if it is a two-minute
     stroll (`步行 五爷庙→塔院寺 0.2 km · 3分`). Any consecutive pair in `stops`
     with no row between them shifts every pairing after it.
   Rule of thumb: walk the timeline top to bottom, and for every consecutive pair in
   `stops` there must be exactly one hop row between them, and that row's `what`
   should carry both stop names (`A→B`) — `links --write` prints the pairing it
   made so you can see it, and parks a row whose text names a *different* stop of
   the day. Declared `fly`/`boat` rows and legs over 100 km stay in the
   count and simply get no link (a declared `train`/`bus` under 100 km still gets a transit link) (the script says so per row) — do **not** answer
   that note by adding `map:false`, or every pairing after it shifts.
2. `python3 scripts/route_tools.py geocode plan.geo.json` — 境内双源：高德 restapi
   优先（`AMAP_KEY` / `--amap-key`，GCJ02 结果自动回算 WGS84），无 key 或高德失败
   自动回退百度 geocoding v3（`BAIDU_MAP_AK`，结果同样回算 WGS84）。脚本内置缓存
   （`geocache.json`），逐站打印解析结果——命中错误城市一眼可见。中文地名在高德
   命中率极高；命中后脚本按查询头 token（前 2 个汉字）比对显示名，不含则 **WARN**
   ——WARN 意为"人工核对"，不是报错。A miss is usually a bad query string:
   re-query with 行政区划前缀 (`南锣鼓巷, 北京市东城区`) and drop the venue suffix
   before spending a browser trip. Only then copy coordinates from the 高德/百度地图
   place card into `plan.geo.json`（取 GCJ02 坐标即可——脚本对高德源自动回算 WGS84，
   手填坐标建议也按 WGS84 填，或直接在 plan 里改用 `query` 让 `geocode` 自动解析）
   — a re-run preserves anything already filled in
   there. **Hand-filling `lat/lon` for anything famous, marked `est`, is the
   normal path, not a workaround** — 景区内的亭台/观景台常缺 POI 记录，从
   高德/百度坐标拾取器取点预填 ±100 m 是标准做法; `geocode` then runs as a no-op.
3. `... check plan.geo.json` — distances with walk/transit duration estimates. It
   flags hops >1.6 km (take transit), >12 km with no declared mode (probably a
   clustering mistake), a declared walk / transit hop over 60 km (a city ride does
   not cross 60 km — a mis-geocoded stop, or a train / bus / boat / drive / fly that
   must say so), and days over 8 km on foot, and exits non-zero when a day
   is broken — **exit 0 is the acceptance bar before rendering** (SKILL.md Phase 4),
   the same way `links` accepts only `parked 0 / suspicious 0`. Declared `fly/drive/boat/train/bus` hops are reported as such, not as
   suspicious. Its transit estimate is a distance formula: for any transit hop
   **>20 km** it prints "use the operator timetable" instead of a number — obey it
   (大兴机场线 草桥→大兴机场 is 19 min; the formula gave 40-60 min). Catch these
   BEFORE scheduling, not after.
4. `... links plan.geo.json --write [--provider amap|baidu]` — per-hop deep
   links (mode from each stop's `mode`, else guessed from distance), written straight
   into the timeline's hop rows. CN 版默认 amap（大陆可点开）；两个 provider 都只出
   逐跳链接（无多点 day chain 形式）。Use `--write`: transcribing
   180-character URLs by hand is the most error-prone step in the pipeline, and a
   mis-paste puts the wrong directions on a stop with nothing to catch it.
   **Read its output, don't just look for "wrote"** — the first unfamiliar-trip
   tests each shipped a day where the row count matched by coincidence and a
   `西单→前门` row got the airport link. Since then `--write`:
   - prints, for every hop row it is about to fill, `row "<what>"  ←  <origin name>
     → <destination name>` — scan that column: the two names on the right must be
     the two names in the row text on the left;
   - **refuses to write a row whose text names another stop of the day** (the words
     around the arrow mention a stop that is not this hop's origin/destination —
     the classic one-off shift) — that URL is **parked** in `day["hop_links"]`
     (rendered as a hop-by-hop maps row) instead of being written to the wrong
     line, and the row is named so you can fix it (add the missing stop, mark the
     lodging/legs row `map:false`, or correct the names) and re-run. A row that
     names *neither* endpoint is still written — that is why the printed pairing
     must be read;
   - writes **no link at all for legs over 100 km or declared `fly`/`boat`** (a
     transit link across 1,200 km is never right): the row is kept in
     the count for alignment and gets a per-row note; nothing is parked;
   - ends the run with `wrote N / parked M / suspicious K; long legs kept unlinked
     (expected): L`. Anything other than `parked 0 / suspicious 0` is a to-do, not
     a warning to scroll past; `L` is **not** a failure counter — it is the number
     of rail/boat/flight rows that correctly got no link (a tester read the older
     `(long legs without link: 1)` as a fourth kind of error; it never was).
     **`parked > 0` still exits 0** — the plan is renderable, the links just moved
     to the hop-by-hop maps row — but stderr carries a loud `WARN` block naming
     each parked row; go back and read it before rendering. `check` will not catch
     this later, and the page degrades silently from tappable rows to a bare
     per-hop list.
   - How the name check matches (so you can predict a park instead of discovering
     it): stop names of the day are tried **longest first**; a CJK stop name that
     is a **substring of this hop's own endpoint name does not count as "another
     stop"** (`西栅` inside `西栅景区→乌镇剧院` is fine). What still
     parks a row: an *unrelated* stop of the day named in the arrow context. So keep
     street names, hotel names and asides out of the arrow context — after ` · ` or
     in parentheses — and prefer distinct names for the day's stops: **stop names on
     one day should not be prefixes/substrings of each other** (Chinese place names
     love shared prefixes — 乌镇 / 西栅 / 西栅景区; write 乌镇西栅, or add the
     venue word). Generic tokens (`广场`, `公园`, `游客中心`) as a whole stop name
     are the same trap.
   After it runs, spot-check by opening two links per day on the browser pane — a
   deep link is the one artifact the reader taps blind on the street.
5. `... kml plan.geo.json -o trip.kml` — numbered pins + a route line per day.
   Deliver the KML next to the HTML plan.
6. Browser-verify the load-bearing hops (rules below), then write the hop rows into
   the timeline.

## Link recipes（境内 — route_tools 默认输出）

默认 provider 是 **amap**（可用 `--provider` 或环境变量
`TRIP_MAP_PROVIDER` 切换 baidu）。

- Single hop（amap 默认）:
  `https://uri.amap.com/navigation?from={lon},{lat},{名称}&to={lon},{lat},{名称}&mode=walk|bus|car&src=trip-planner-cn`
  —— 注意高德是 **经度,纬度** 顺序；境内坐标已由脚本自动 WGS84→GCJ-02 纠偏，图钉
  落点准确。Coordinates beat names in these links — names can match the wrong branch/city.
- Single hop（baidu）:
  `https://api.map.baidu.com/direction?origin={lat},{lon}&destination={lat},{lon}&mode=walking|transit|driving&coord_type=wgs84&output=html&src=trip-planner-cn`
- Whole-day chain: **无** — 高德/百度均无 keyless 多点导航 URL 形式，两个 provider
  都只出逐跳链接，`day_map` 留空并说明。（离线总览由 trip.kml 兜底。）

## Which provider when（境内决策表）

- **默认 `amap`**：大陆用户点开即用（H5 拉起高德 App），iOS/Android 通吃；
  逐跳链接是路上真正用的导航入口。
- `--provider baidu`：traveller 用百度地图习惯时的等价替代。
- 无论 provider：**trip KML（Organic Maps 离线）是硬兜底**——不依赖网络与厂商；
  境内山区/景区（黄山、九寨沟、稻城亚丁等）经常无信号或信号漂移，plan 的
  connectivity note 写"离线地图 + 提前截图关键路段"。

## Hop-row format (canonical — scheduling.md and output-template.md follow this)

`模式 线路名(往…方向) 站数/分钟 票价 · 上车站→下车站 · 出口号` — in the plan's
language: mode, line (toward …), stops/minutes, fare · boarding→alighting stop ·
exit number. zh e.g. `地铁 4号线(往天宫院方向) 4站/12分 ¥4 · 北京南站→西单 · 出口C`
Buses have no exit numbers and the stop count means nothing to a rider, so swap the
last field for the walk off the stop:
bus, line (toward …), ~minutes, fare · boarding→alighting stop · walk-off time;
zh e.g. `公交 游2路(往灵隐寺) ~35分 ¥3 · 城站火车站→灵隐东 · 下车步行6分`.
Walking hops shorten to walk, from→to, km · minutes — zh e.g.
`步行 断桥残雪→平湖秋月 1.2 km · 16分`.

Exit numbers matter: in 北京西站/虹桥站这类大型枢纽 the wrong exit costs 10 minutes.
Capture the exit when you browser-verify a hop. Every hop carries a verification
marker — `(verified)` or `(est.)` — in its own `verify` field in the day object
(`"verify": "verified"|"est"`), never mixed into the `tag` field, which holds only
pinned/opener/skippable/swap→X; a flight/rail hop row carries `"map": false` **only
when its two ends are not in that day's `stops`** (see the `map:false` truth in
step 1) — with both stations in `stops` the row stays mappable and simply gets no
link. Keeping these separate is what lets parallel city blocks merge without
hand-editing.

## Verify vs estimate

Browser-verify in 高德/百度 **at the hour the plan uses it** (frequency and routing
change by time of day):
- airport / 高铁站 ↔ hotel, both ends of the trip
- any hop feeding a timed-entry ticket (博物馆预约场) or an intercity departure
- late-evening hops — also capture the **last departure time** (末班地铁/末班公交)
  and write it in the plan
Everything else: route_tools estimate + `(est.)` marker. Don't burn browser time
verifying a 600 m walk. Browser map lookups do **not** count against the web-search
budget — they are not searches. If the browser is unavailable entirely, every hop
ships as a **range** with `(est.)` and lands in the ⚠️ unverified list; never convert
an estimate into a single confident number just because it looks tidier.

## Which app where（境内）

- **高德地图**：默认推荐——公交/驾车/步行导航全覆盖，实时路况最好，iOS/Android
  通吃；与默认链接 provider 一致。
- **百度地图**：等价替代；部分城市公交/骑行数据略有差异，按 traveller 习惯选。
- **12306 / 携程铁路**：跨城火车正晚点与站台信息。
- **车来了 / 网约车（滴滴/高德打车）**：市内公交到站实时与夜间接驳兜底。
- **景区接驳**：很多景区（黄山、九寨沟、张家界）内部强制换乘景交车——班次与
  末班车时间写在景区公众号，用 `(verified)` 标注并写进 timeline。

## Offline fallback

- **Organic Maps** (free, OSM): imports the trip KML — numbered pins + day lines work
  fully offline. Recommend it in every plan footer with a one-line import hint
  (download 省级离线地图 → bookmarks → import KML)。
- **高德/百度离线地图包**：按城市下载基础包 + 公交包；离线态下步行/驾车导航可用，
  公交实时到站不可用——依赖实时公交的跳点在 plan 里标注。

## Geocoding discipline

高德/百度都是共享配额服务。The script already does this correctly — on-disk cache
next to the plan (`geocache.json`)、失败自动回退百度——不要绕过缓存并行调用，
单次行程几十个 POI 远低于两家免费配额。Resolved stops are
cached, so re-running is nearly free; misses are deliberately **not** cached, because
a miss is almost always a fixable query string and caching it would make the retry
impossible.

Expect **景区内 POIs to miss** (观景台/亭子/步道节点…): 手工取点预填 `est` 坐标即
可——示意图与 KML 需要 ±100 m, not survey grade — mark the day's map `est` and only
chase exact coordinates when a hop calculation actually depends on them. City venues
stay on the re-query-then-browser path.

Expect **同名地名冲突**（全国重名/近似地名极多——"太平"有 20+ 个乡镇级地名，西湖/东湖
在几十个城市出现）: a famous name may hard-fail (loud, fine), but a station or
a lane can land on the wrong city silently.
`geocode` prints a **WARN when the resolved `display_name` does not contain the
query's head token** (前 2 个汉字); treat it as "open the coordinates and look", and
prefer pre-filled `est` coordinates plus an 行政区划前缀 re-query (`太平老街, 长沙市`
rather than `太平`) over trusting the first hit.
