# trip-planner-skill 中国大陆适配优化方案（ADAPTATION.md）

> 本目录 `trip-planner-cn/` 是原 skill 的**完整独立副本 + 适配改造**，原项目未做任何改动。  
> 本文档 = 受限资源完整清单 + 逐项替换对照 + 实施步骤 + 验证方法。

---

## 一、受限资源完整清单（审查范围：SKILL.md、references/ 13 篇、scripts/ 5 个脚本、themes/ 渲染器与工具、examples/、README、CI）

可访问性分级：【受限】= 被屏蔽/不可用；【不稳定】= 可达但慢/间歇失败；【需 key 且境外支付】= 国内无法便捷付费。

| #  | 资源                                                     | 所在文件                                                                                  | 分级          | 受限原因                                     | 影响范围                                       |
| -- | ------------------------------------------------------ | ------------------------------------------------------------------------------------- | ----------- | ---------------------------------------- | ------------------------------------------ |
| 1  | Google Flights / fast-flights（google.com）              | scripts/flight_scan.py、references/data-sources.md、SKILL.md、phase-3-legs.md            | 受限          | Google 服务在大陆被屏蔽，fast-flights 无论是否安装都无法连通 | 机票价格网格扫描全部失效；Phase 3 价格阶梯第一级失效             |
| 2  | Google Maps 深链（google.com/maps/dir）                    | scripts/route_tools.py（默认 provider）、examples/*.geo.json、data-sources.md、navigation.md | 受限          | 同上                                       | 计划页上所有跳转链接大陆用户点不开；route_tools 默认值是 google  |
| 3  | Google Maps 嵌入 iframe（maps.google.com output=embed）    | themes/theme_common.py `day_embed_url`、references/themes.md                           | 受限          | 页面访客在大陆打开时 iframe 加载失败                   | 8 个主题渲染页里"路线地图"折叠块空白卡死                     |
| 4  | Google Hotels（google.com/travel/hotels）                | data-sources.md §Hotels                                                               | 受限          | 同 Google                                 | 酒店比价渠道失效                                   |
| 5  | Nominatim / OSM 地理编码（nominatim.openstreetmap.org）      | scripts/route_tools.py `cmd_geocode`、navigation.md、phase-4                            | 不稳定         | OSM 主站国内可达性差、超时多；CJK 地名命中弱               | Phase 4 地理编码慢/失败，阻塞 geocode→check→links 链  |
| 6  | sunrise-sunset.org 日照 API                              | scripts/route_tools.py `fetch_sun`、scheduling.md、data-sources.md §Weather-4           | 不稳定         | 国外站点，国内可达性差，且有署名要求与 429 限流               | 每个计划的逐日日照（黄金时刻排程）可能整体失败                    |
| 7  | Nager.Date 假日 API（date.nager.at）                       | data-sources.md §PublicHolidays、phase-1-brief.md                                      | 不稳定         | Cloudflare 托管，国内时通时断                     | Phase 1 假日核查可能失败                           |
| 8  | frankfurter.dev 汇率 API                                 | data-sources.md §FX、SKILL.md 硬规则 5                                                    | 不稳定         | 国外站点；且只覆盖 ~30 主流币种                       | 预算折算可能失败或缺币种                               |
| 9  | Skyscanner / Kayak / ITA Matrix / Rome2Rio             | data-sources.md、phase-3-legs.md                                                       | 不稳定         | 可访问但慢、常跳人机验证                             | 第二比价源可用性差                                  |
| 10 | Booking.com / GetYourGuide / Viator                    | data-sources.md、examples                                                              | 不稳定         | 可访问但慢/验证频繁                               | 酒店与活动预订深链体验差                               |
| 11 | OpenRouter（openrouter.ai）生图/生视频                        | themes/gen.py、themes/genvideo.py、ART-SCHEMA.md、SKILL.md Phase 0                       | 需 key 且境外支付 | API 本身可达但需境外信用卡付款                        | 无原生生图能力时图片供应链断档                            |
| 12 | US State Dept / UK FCDO / Smartraveller 旅行预警           | data-sources.md §Travel advisory                                                      | 不稳定         | state.gov/gov.uk 国内可达性一般                 | Phase 1 安全警示线可能拿不到数据                       |
| 13 | CDC / TravelHealthPro / WHO PDF 健康来源                   | data-sources.md §Travel health                                                        | 不稳定         | 同上                                       | 健康与黄热病审计来源不稳                               |
| 14 | GDACS / USGS / NOAA NHC 灾害源                            | data-sources.md §Hazard feeds                                                         | 不稳定         | 同上                                       | 灾害季节卡与 T-7 重查可能失败                          |
| 15 | Google Fonts（fonts.googleapis.com / fonts.gstatic.com） | scripts/build_site.py（演示站 gallery）                                                    | 受限          | Google Fonts 国内节点不稳                      | 演示站字体加载失败（仅影响 demo 站，不影响 skill 功能）         |
| 16 | GitHub / GitHub Pages / release 资产                     | .github/workflows/pages.yml、themes/assets/portal/README.md、README 展示链接                | 不稳定         | github.io 与 release 下载国内间歇阻断             | 演示站、portal 素材恢复命令（curl GitHub release）可能失败 |
| 17 | PyPI 默认源（pip install fast-flights / Pillow）            | README、SKILL.md                                                                       | 不稳定         | 默认源慢/超时                                  | 依赖安装困难（换清华镜像即可，非功能性受限）                     |
| 18 | Open-Meteo（api / archive / climate / geocoding 端点）     | data-sources.md §Weather                                                              | 可用（保留）      | 未被屏蔽，偶有慢                                 | 保留为默认，补充国内替代（和风天气/高德天气）                    |
| 19 | examples/*.geo.json 内的 Google 深链                       | examples/ 7 个行程                                                                       | 受限          | 示例数据由原版流程生成                              | 示例页在大陆演示时链接点不开（示例是静态演示数据，可选择性重生成）          |

---


## 二、逐项替换对照表

| 功能               | 原方案（境外）                           | 适配后方案（境内）                                                                                                                                                               | 修改文件                                                                                                                        | 兼容性                                                                                               |
| ---------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 地图深链（逐跳导航）       | Google Maps dir（默认）               | **高德 URI**（默认）`uri.amap.com/navigation?from=lon,lat,名称&to=…&mode=walk\|bus\|car`；备选百度 `api.map.baidu.com/direction?…&coord_type=wgs84`；apple 保留；google 降为显式选项（仅代理/人在境外） | route_tools.py（`PROVIDERS`、`dir_url`、`DEFAULT_PROVIDER`、`main()`）                                                           | `--provider google\|apple` 原样可用；env `TRIP_MAP_PROVIDER` 可覆盖                                       |
| 坐标基准             | 计划存 WGS84，amap 链接直接用（有偏移）         | 新增标准 **WGS84↔GCJ-02 互转**：amap 链接对境内坐标自动纠偏；高德 geocode 结果自动回算 WGS84 后写回计划（单一基准不变，KML/`check` 不漂移）                                                                         | route_tools.py（`wgs84_to_gcj02`、`gcj02_to_wgs84`）                                                                           | 境外坐标原样透传                                                                                          |
| 地理编码             | Nominatim 唯一                      | **高德 restapi 优先**（`AMAP_KEY` env 或 `--amap-key`；结果 GCJ02→WGS84）→ Nominatim 自动回退                                                                                         | route_tools.py（`_geocode_amap`、`cmd_geocode`）、navigation.md、data-sources.md                                                 | 无 key 时行为=原版                                                                                      |
| 日照计算             | sunrise-sunset.org API（网络+署名+429） | **本地 NOAA 天文模型直接发布值**（复用原校验模型，扩展 zenith=96 算民用晨光；零网络、无署名要求、无 429）；`--api` 保留原路径用于对账                                                                                     | route_tools.py（`cmd_sun` 重构）、scheduling.md、data-sources.md、plan_lint.py                                                     | sun 字符串尾标变为"本地天文计算"/"NOAA local solar model"；`plan_lint SUN_OK` 正则同步接受两种尾标（含旧 sunrise-sunset.org） |
| 机票比价             | fast-flights→Google Flights       | **`flight_scan.py --cn-links`**：输出日期网格的携程/Trip.com/去哪儿深链（fast-flights 缺失/失败时自动降级触发，exit 2）；价格由用户点链接核对（国内无免钥票价 API，诚实标注）；≥2 源规则改为 携程+Trip.com/去哪儿/航司官网                   | flight_scan.py（`cn_links`、`--cn-links`、ImportError 分支）、SKILL.md、phase-3-legs.md、data-sources.md                             | 原扫描器原样保留（有代理时可用）                                                                                  |
| 酒店比价             | Google Hotels + Booking 深链        | 携程酒店/飞猪/Agoda（境内直连）为主；Google/Booking 降为不稳定备选                                                                                                                            | data-sources.md §Hotels                                                                                                     | 原链接模板保留                                                                                           |
| 假日查询             | Nager.Date 唯一                     | 中国大陆目的地：**timor.tech 节假日 API** + 国务院公告人工核对；国际：Nager.Date（不稳定标注）+ timeanddate.com 兜底                                                                                     | data-sources.md §PublicHolidays、phase-1-brief.md                                                                            | —                                                                                                 |
| 页内地图嵌入           | Google Maps iframe（keyless）       | **高德静态地图方案**（第四阶段后更新）：渲染时 `day_embed_url` 用 AMAP_KEY 调 `restapi.amap.com/v3/staticmap` 把每日途经点画成 PNG（GCJ-02 已换算、编号标记+连线），base64 烙进 HTML——访客零网络、key 不出现在成品页、无 key 时回退隐藏折叠块；逐跳 amap/baidu 深链保留 | theme_common.py（`_wgs84_to_gcj02`、`_amap_static_key`、`day_embed_url`）、7 渲染器（`.map-embed`/`.m-embed` 内嵌 `<img>` + `data-done`/`data-on` 守卫键）、themes.md | 页面体积每图 +60~90 KB（base64）；渲染期需联网取图，离线渲染时地图折叠自动隐藏 |
| 生图供应链            | OpenRouter gpt-image-2（唯一 key 路径） | 三 provider：**dashscope**（阿里百炼 wanx2.1-t2i-turbo，异步任务轮询）、**siliconflow**（Kolors，同步）、openrouter（保留）；auto 按 env key 自动检测                                                   | themes/gen.py（`--provider`/`--api-key`、`call_dashscope`、`call_siliconflow`）、ART-SCHEMA.md、themes/README.md、SKILL.md Phase 0 | 原 OpenRouter 路径与 `.auth_header` 不变；manifest 记录实际 model，国内 provider cost 记 n/a                     |
| 生视频（portal）      | OpenRouter /videos                | **dashscope wan2.2**（t2v-plus / i2v-flash 首帧图生视频，异步轮询）+ openrouter 保留；另注明可灵/即梦网页端产出可直接放入 outdir                                                                         | themes/genvideo.py（`call_dashscope_video`、`--provider`）                                                                     | 原 /videos 流程不变                                                                                    |
| 汇率               | frankfurter 优先                    | **open.er-api.com 优先**（先判键）→ frankfurter 交叉回退 + 中国银行牌价（购汇口径）                                                                                                            | data-sources.md §FX、SKILL.md 硬规则 5                                                                                          | —                                                                                                 |
| 旅行预警             | US/UK/AU 为主                       | **中国领事服务网 cs.mfa.gov.cn 为主源**（含 12308、移民局 NIA）；US/UK 降为不稳定第二来源；等级映射不变（红/橙=Level 4/3）                                                                                    | data-sources.md §Travel advisory                                                                                            | —                                                                                                 |
| 健康来源             | CDC/TravelHealthPro/WHO           | 海关总署/ITHC（中文主源，原有）+ 中国疾控；CDC 等降为不稳定第二意见                                                                                                                                 | data-sources.md §Travel health                                                                                              | —                                                                                                 |
| 灾害源              | GDACS/USGS/NOAA                   | **中国地震台网 ceic.ac.cn、中央气象台 nmc.cn、台风路径 slt.zj.gov.cn、12379 预警**（境内）为主；GDACS/USGS/NOAA 降为不稳定国际源                                                                           | data-sources.md §Hazard feeds                                                                                               | —                                                                                                 |
| 演示站字体            | Google Fonts @import              | 移除 @import，用本地系统字体栈（--serif 已有本地回退）                                                                                                                                     | scripts/build_site.py                                                                                                       | 视觉近似（Fraunces 缺失时回退衬线）                                                                            |
| 演示站链接            | skywain.github.io                 | 文档内改为指向 `examples/` 本地已渲染页面                                                                                                                                             | phase-0-intake.md、output-template.md                                                                                        | —                                                                                                 |
| pip 安装           | 默认 PyPI                           | 文档注明可用清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`                                                                                                                | ADAPTATION.md §实施步骤                                                                                                         | —                                                                                                 |
| Windows tzdata   | （原版隐含依赖）                          | 文档注明 Windows 下 `sun`/时区解析需 `pip install tzdata`，否则回退经度近似 tz 且拒绝写 sun                                                                                                    | ADAPTATION.md                                                                                                               | —                                                                                                 |
| 示例数据中的 Google 深链 | 原版生成                              | 保留原样（静态演示数据）；提供重生成命令：`route_tools links --write --provider amap`                                                                                                        | examples/（未改）、ADAPTATION.md                                                                                                 | 可选执行                                                                                              |

**刻意保留、未替换的项**（避免过度工程）：Open-Meteo（境内可用，保留默认）；12go.asia / Klook（境内可用）；高德 URI scheme（原版已内置支持，本次只翻转默认值）；`xprobe.sh`/`xt.sh`（本机 Chrome 导出探针，与网络无关）；GitHub Actions 部署（上游功能，不涉及 skill 使用）。

---

## 三、实施步骤（历史记录——第一阶段方案，其中 google/apple/Nominatim/`--api`/openrouter 等"保留"项已被 §七 第三阶段境内-only 改造取代，复现时以 §七 为准）

1. **复制项目**：`mkdir trip-planner-cn && cp -r`（README×2、SKILL.md、LICENSE、NOTICES、assets、references、scripts、themes、docs、examples、.github、.gitignore）→ 原 skill 零改动。
2. **route_tools.py**：加 `import os`；`PROVIDERS=(amap,baidu,apple,google)` + `DEFAULT_PROVIDER`（env `TRIP_MAP_PROVIDER`，默认 amap）；新增 `wgs84_to_gcj02` / `gcj02_to_wgs84`；`dir_url` 增加 baidu 分支并对 amap 坐标纠偏；新增 `_geocode_amap`，`cmd_geocode` 改为高德优先；`cmd_sun` 重构为本地 NOAA 计算（`--api` 保留原路径）；`main()` 参数与 docstring 同步。
3. **flight_scan.py**：新增 `cn_links()` 与 `--cn-links`；ImportError 分支输出国内深链；docstring 顶部加 CN 说明。
4. **themes/gen.py**：`--provider auto|dashscope|siliconflow|openrouter` + `--api-key`；新增 `call_dashscope`（异步任务提交/轮询/下载）与 `call_siliconflow`；`register()` 记录真实 model；dry-run 支持。
5. **themes/genvideo.py**：`--provider` + `call_dashscope_video`（wan2.2 t2v/i2v 首帧，异步轮询下载）；openrouter 原路径保留。
6. **themes/theme_common.py**：`day_embed_url` 默认返回空（env 开关可恢复）；加 `import os`。
7. **scripts/plan_lint.py**：`SUN_OK` 正则接受 `本地天文计算 | NOAA local solar model | sunrise-sunset.org` 三种尾标。
8. **scripts/build_site.py**：移除 Google Fonts `<link>`，注释说明字体回退。
9. **文档**：data-sources.md（顶部适配说明 + Flights/Hotels/Transit/Geocode/Holidays/Weather-sun/FX/Advisory/Health/Hazards/keys 十一节改造）、navigation.md（链接配方与 provider 决策表重写）、scheduling.md（sun 本地化）、phase-1/3（来源阶梯）、phase-0/output-template（demo 链接）、themes.md、ART-SCHEMA.md（生成器选择）、themes/README.md、README×2（适配声明）、SKILL.md（frontmatter name/description、-CN 一段总述、硬规则 3/5、Phase 0 图片能力检查、Phase 3 门、§When things fail、Bundled resources）。
10. **验证**（全部通过）：`py_compile` 5 个脚本；`route_tools sun`（kyoto 样例：05:54/17:35 vs 原 API 05:53/17:37，±2 分钟，0 请求）；`links --provider amap/baidu`（china 样例：GCJ02 纠偏后坐标正确）；`flight_scan --cn-links`（PVG→NRT 网格输出正常）；`gen.py --dry-run`（三个 provider 检测/报错路径）；`render_clay2.py` 全量渲染 china 示例 838KB + `qc.py` PASS exit 0。

## 四、使用前配置（用户侧）

| 配置               | 命令/操作                                                                            | 必要性                                                      |
| ---------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 高德 key（推荐）       | lbs.amap.com 注册 → "Web 服务" key → `setx AMAP_KEY <key>`                           | 强烈推荐：地理编码快且稳，CJK 地名命中高；免费                                |
| 生图（可选）           | 阿里百炼开通 → `setx DASHSCOPE_API_KEY <key>`；或硅基流动 → `setx SILICONFLOW_API_KEY <key>` | 可选：7 主题中 5 个需要生成图；无 key 时 stock kit 兜底（illustrated/clay） |
| 时区数据（Windows）    | ~~`pip install tzdata`~~ **已无需安装**（`resolve_tz` 内置中国时区 UTC+8 兜底）                 | 境内版 Windows 开箱即用                                         |
| 可选依赖             | `pip install Pillow`（资产流水线）；fast-flights **已随境外路径移除**                            | 按需                                                       |
| 地图 provider 覆盖   | env `TRIP_MAP_PROVIDER=baidu`（仅 amap|baidu 两个境内源）                                | 默认 amap，一般不用改                                            |
| ~~恢复 Google 嵌入~~ | **已用高德静态地图替代**（第四阶段后）：`day_embed_url` 现经 `restapi.amap.com/v3/staticmap` 产出内嵌 PNG，仍无任何境外恢复入口；无 AMAP_KEY 时折叠块隐藏（原行为） | theme_common.py `day_embed_url`、cn-domestic.md §5 |

## 五、已知边界与后续建议

- **国内无免钥机票票价 API**：`--cn-links` 只能给深链，价格必须人工点开核对——这是刻意设计（原 skill 硬规则 2：绝不猜价格）。若未来接入携程开放平台/Amadeus CN，可在 `flight_scan.py` 增加 `--api` 级别。
- **dashscope/siliconflow 生图参数差异**：两者不支持透明背景与 quality 档位，cut-out 槽位依赖 `cutout.py` 后处理；首次使用建议 `--dry-run` + 单张试跑核对风格锚点。
- **examples/ 中的 Google 深链未改**（静态演示数据）；需要全境内可用示例时执行：  
  `python3 scripts/route_tools.py links examples/china-2026/china.geo.json --write --provider amap`（其余行程同理）。
- **portal 视频**：dashscope wan2.2 只支持首帧条件（无 last-frame 链接镜头）；完整 dive→link 链仍建议本地 GPU（ComfyUI）或可灵/即梦网页端产出后放入 outdir。
- **验证盲区**：高德/百炼/timor.tech 的实测依赖真实 key（本次仅做 dry-run 与逻辑验证）；首次使用按 data-sources.md 各节 ⚡ 标注先人工核验一次。

---

## 六、境内游深度适配建议（面向"国内旅游计划制作"的第二阶段改造）

> 前五章解决的是"境外资源在大陆**能不能用**"；本章解决的是"计划国内游时好不好用"。  
> 原 skill 的六阶段剧本是为**出境游**设计的（签证/汇率/国际机票/入境卡是默认 gate），  
> 国内游场景下这些环节要么空转、要么缺位。建议按 P0→P2 分三批实施。

### 6.0 总体思路：引入"境内模式"开关，而不是另写一套 skill

在计划 JSON 的 `meta` 增加 `mode: "cn-domestic"`（`route_tools geocode` 探测到全部  
坐标落在中国大陆时可自动建议设置）。一个开关驱动三处分流：

| 分流点                | 出境模式（现状）               | 境内模式                                             |
| ------------------ | ---------------------- | ------------------------------------------------ |
| `plan_lint.py` 门禁  | 查护照/签证/as-of、FX 行、国际预警 | **跳过**签证/FX/国际预警 gate，改查：景区预约行、12306 开售日、高原/限流提示 |
| `phase-1-brief.md` | 签证+假日+汇率+预警+健康         | 假日调休+天气预警+景区预约窗口+（高原线）高反提示                       |
| 预算表                | 外币+汇率折算行               | 直接人民币；行项改为停车费/摆渡车/景区交通/押金                        |

实现成本极低：`plan_lint` 加一个 `if plan.meta.mode == "cn-domestic"` 分支；phase 文档各加一节即可。

### 6.1 P0 建议（低成本、高价值，1 次会话可完成）

1. **高德多途经点"day chain"补齐**（当前适配版的最大缺口——amap 每跳链接可点，但整日链视图缺失）。  
   高德 web 版 `uri.amap.com/navigation` 支持 `via=lon,lat;lon,lat` 途经参数 ⚡需实测一次；  
   若可用，在 `route_tools.py dir_url` 的 amap 分支把 `waypoints` 拼成 `via=`，DAY CHAIN  
   即可恢复，与 google/apple 对齐。实测不可用则退而求其次：给每天输出一条"高德地图网页版  
   搜索串"（`uri.amap.com/search` 或 marker 链接组）作为 day_map 降级。
2. **12306 深链配方**（data-sources.md §Transit 现在只有一句话说明）：  
   `https://kyfw.12306.cn/otn/leftTicketQuery?leftTicketDTO.train_date=YYYY-MM-DD&leftTicketDTO.from_station=XXN&leftTicketDTO.to_station=...`  
   需要维护一张**电报码表**（北京=BJP、上海=SHH…，可内置于 `scripts/` 一个 json）；  
   同时写清国内火车票规则：15 天预售、各站放票时刻不同、候补优先于捡漏、  
   开售即抢节假日票（行程确认日期后当天开售时提醒用户）。
3. **新建 `references/cn-domestic.md`——景区预约与实名制速查**（国内游第一雷区）：
   - 预约制清单：故宫（提前 7 天 20:00 放票）、国家博物馆、莫高窟（A 票提前 30 天）、  
     军事博物馆、热门省级博物馆——各写明放票时刻与预约渠道（官方公众号/小程序，非 OTA）。
   - 实名制：一人一证一票，入园刷身份证；证件号要提前收。
   - 门票与优惠：美团/大众点评/携程门票深链模板；学生/老人半价规则差异大，标注"现场核验证件"。
   - 把 SKILL.md Phase 4 的"official venue site first"在国内场景下指向本文件。
4. **假日与调休的"拼假逻辑"**（timor.tech API 已接入，但只用了"查假日"）：  
   增加两条排程规则进 `scheduling.md`：① 调休补班日（周六上班）不是休息日，  
   周边游高峰反而低——是错峰好日子；② 黄金周首日与末日是高速/高铁最堵点，  
   骨架选日期时避开，或注明"早 7 点前出发"。Phase 1 简报在国内模式下输出"本次行程  
   是否撞上调休拼假窗口"。
5. **天气预警本地化**：Open-Meteo 保留，但国内游加一行"查中央气象台预警信号  
   （暴雨橙色/台风红色直接触发改期建议）"，和风天气 dev key（免费）列为可选升级——  
   分钟级降水对"当天要不要按计划去户外"是决定性的。
6. **紧急号码与保险**（替换出境的 12308/使馆内容）：110/120/119 之外，旅游服务 12301、  
   高速救援 12122、12395 海上搜救；国内旅行险（平安/人保/支付宝"出行保"）给 1-2 个  
   深链，高原线（川西/西藏/青海）强制附高反提示与药品清单。

### 6.2 P1 建议（中成本，建议下一批）

1. **用高德路径规划 API 拿"真实时距"**：现有 `route_tools check` 只做距离聚类合理性；  
   有了 `AMAP_KEY`（使用前配置里已要求申请），调驾车/公交路径规划 API 可把每跳的  
   估时换成**实时路况时距**，并在计划页标注"高德实时路况 as-of"。这是国内游排程  
   精度的最大单项提升（原 skill 的停留时长数据库对国内景点覆盖弱，通勤时长估计误差大）。
2. **POI 补全走高德 place API**：`fill-a-spare-block`（"我在 X 附近有 2 小时空档"）  
   场景，用高德周边搜索（types=风景名胜;餐饮服务）替代原方案的浏览器搜索；  
   餐厅推荐以大众点评/美团评分为来源并标注（原 skill 用 Google place card）。
3. **攻略来源适配**：马蜂窝/小红书作为灵感来源进 data-sources.md，但标注硬规则  
   不变——小红书"绝美机位"类内容时效与真实性差，只作灵感、不作事实来源，  
   开放时间/票价仍回到景区官网与美团实价。
4. **境内样例行程**：examples/ 增加 1 个纯境内示例（如"云南 7 日"或"川西小环线"，  
   含 12306 段、景区预约行、高原提示），跑通全链路并出 8 主题页。**这是新用户  
   理解"境内模式长什么样"的最快途径**，也顺手验证 P0 全部改动。
5. **住宿深链模板**：携程/飞猪/美团标准搜索深链 + 连锁酒店官网（华住/亚朵/锦江）  
   会员价提示；民宿用途家。删掉出境场景的 Agoda 优先级。
6. **新疆/西藏时差提示**：官方统一北京时间，但喀什日落比上海晚约 2.5 小时——  
   本地太阳模型（改造后已内置）算出的日照是对的，需在 scheduling.md 加一句  
   "西部线路的'天亮'时间不是排程错了"，避免 agent 自我纠错改掉正确数据。

### 6.3 P2 建议（长期/可选）

1. **国内视频工作流**：portal 主题的可灵/即梦网页端出片→放 outdir 的半自动流程  
   写成脚本（`genvideo.py --from-local`），绕开 API 限制（见 §五 已知边界）。
2. **腾讯地图 provider**：qq.com map URI 作为第三 provider（微信生态用户点开体验好），  
   `dir_url` 加一个分支即可，约 20 行。
3. **离线包从 KML 转向"高德收藏夹"**：国内用户几乎不用 KML；保留 KML 不删，  
   但 cn-domestic.md 加一节"把 KML 坐标批量转高德收藏点"的操作说明（或小脚本生成  
   可分享的 marker 链接列表）。
4. **Phase 6 交付物国内化**：`gates.ics`（登机口检查清单）在国内游降权，新增  
   "出发前 24h 检查"——身份证/学生证、景区预约截图、充电宝（共享充电宝节假日常缺）、  
   加油/充电桩规划（自驾线用高德充电地图）。

### 6.4 建议实施顺序

```
第一批（P0）: 6.1-1 高德via实测 → 6.1-2 12306深链+电报码 → 6.1-3 cn-domestic.md
              → 6.1-4 拼假规则 → 6.1-5/6 文档两处小节
第二批（P1）: 6.2-7 高德路径API时距 → 6.2-8 POI周边搜索 → 6.2-10 境内样例行程
              → 6.2-9/11/12 文档
第三批（P2）: 按需
每批结束都跑: render_clay2.py + qc.py + plan_lint --strict 回归（同 §三.10）。
```

> 优先级判断依据：P0 全部是"文档 + 少量代码分支"，不引入新依赖、不动渲染层，  
> 但每一项都堵住国内游会真实翻车的坑（约不上票、抢不到票、调休误判）；P1 依赖  
> 真实 key 的联调；P2 属于锦上添花。

### 6.5 实施状态核查（第三阶段境内-only 改造后复核）

| 建议项                                    | 状态        | 说明                                                                                                                        |
| -------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| 6.0 境内模式开关 `meta.mode`                 | **被取代**   | 第三阶段直接境内-only（lint 门禁/简报/预算全部境内化，无出境分支），开关不再需要                                                                            |
| 6.1-1 高德 via 多途经 day chain             | **完成**    | `route_tools links` amap 分支输出 via= 驾车概览链（每链 ≤3 途经点、按 4 站一段切链、>SUSPICIOUS_KM 抑制），写入 `day_map`；⚡首用建议浏览器实测一次                 |
| 6.1-2 12306 深链 + 电报码表                  | **完成**    | `STATION_TELECODE` 内置约 70 个主要站电报码，`flight_scan --rail` 直接输出 12306 官网 leftTicket 直查深链（未收录车站退携程兜底）；预售/候补规则在 data-sources.md |
| 6.1-3 `references/cn-domestic.md` 预约速查 | **完成**    | 独立文件已建并注册进 SKILL.md Bundled resources：预约制清单（故宫/国博/莫高窟/陕历博等放票规则+官方渠道）、实名制、门票复核阶梯、KML→高德收藏点                                 |
| 6.1-4 调休拼假排程规则                         | **完成**    | scheduling.md Day types 首条新增：补班周六错峰组合 + 黄金周首末日规避（早 7 点前出发、首日不排预约场馆）；phase-1-brief.md 拼假三问已有                               |
| 6.1-5 天气预警境内化                          | **完成**    | 中央气象台预警（橙红=停）已入 phase-1-brief.md 与 data-sources.md                                                                        |
| 6.1-6 紧急号码/保险/高反                       | **完成**    | 110/120/119/122/12122/12301/12345 八行应急卡 + 高反提示（4 处）已入 phase-1-brief.md；示例 checklist 含保险行                                  |
| 6.2 高德路径 API 实时时距                      | **待 key** | 依赖真实 AMAP_KEY 联调；免费申请指引已写入 cn-domestic.md §5，用户拿到 key 后即接入                                                                |
| 6.2 高德 POI 周边搜索                        | **待 key** | 同上，与路径 API 一并接入                                                                                                           |
| 6.2 马蜂窝/小红书攻略来源                        | **完成**    | data-sources.md 新增「灵感与攻略来源（境内）」节：只作灵感、不作事实来源，硬规则 2 不变                                                                     |
| 6.2 境内样例行程                             | **完成**    | `examples/china-2026/`（上海→北京→西安纯境内游，plan_lint --strict 0 FAIL 0 WARN，7 主题页可渲染）                                            |
| 6.2 住宿深链境内化                            | **完成**    | data-sources.md §Hotels 改携程/飞猪/美团，出境 OTA 已删                                                                               |
| 6.2 新疆/西部时差提示                          | **完成**    | scheduling.md 已加"乌鲁木齐日落比上海晚约两小时"提示（经度差，非排程错误）                                                                             |
| 6.3-1 国内视频工作流                          | **已取消**   | 第三阶段彻底移除视频能力，genvideo/portal 不复存在                                                                                         |
| 6.3-2 腾讯地图第三 provider                  | **不加**    | 2026-10-01 用户决定：amap+baidu 已覆盖，避免 provider 表复杂化                                                                           |
| 6.3-3 高德收藏夹转换说明                        | **完成**    | cn-domestic.md §4：逐点链接收藏法 / Organic Maps·奥维 KML 图层 / 计划页深链兜底                                                              |
| 6.3-4 出发前 24h 检查                       | **完成**    | phase-6-assemble.md 交付 checklist 新增：身份证原件/预约截图/值机确认/充电宝/充电桩规划/离线地图包/天气预警复查                                                |

**结论（2026-10-01 复核后更新）**：§一~§五（资源替换）+ §七（境内-only/图文-only）

- §六 P0 全部及 P1/P2 文档类项已全部完成并回归通过（compile / lint --strict 0 FAIL 0    
  WARN / check / links --write / flight_scan / render+qc 全绿）。仍在等待的仅两项依赖真实    
  AMAP_KEY 的 API 联调（高德路径实时时距、高德 POI 周边搜索——免费申请指引已写入    
  cn-domestic.md §5，接入提示已入 SKILL.md/route_tools/data-sources）；腾讯地图    
  provider 经用户决定不加。均为增量优化，不影响"仅境内 + 纯图文"核心目标。

**附：复核中顺带修复的遗漏**——① 7 个主题渲染器 footer 残留 sunrise-sunset.org  
（全部改"本地天文计算"）；② qc.py 外链白名单清空；③ scheduling.md 境外例子  
（梵蒂冈安检/西班牙午休/日本宅急便/卡帕多奇亚等）全部境内化，并新增境内独有  
Trap（周一闭馆、县城午休歇业、周末集市）；④ data-sources/phase-4/cover-titles  
共 5 处 Morocco/Tromsø/Japan/Mexico 残留改写。
