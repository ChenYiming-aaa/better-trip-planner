[English](README.md) | [简体中文](README.zh-CN.md)

> **境内-only 适配版** — 本目录是 trip-planner-skill 的**仅支持境内旅游**分支：
> 目的地必须在中国大陆（港澳台同样停止）；地图链接只有高德/百度、地理编码走高德
> API（`AMAP_KEY`）+ 百度回退（`BAIDU_MAP_AK`）、机票/火车走携程/12306 深链
> （`flight_scan.py`）、日照本地天文计算（零网络）、预算一律人民币（无汇率）、
> 生图走阿里云百炼/硅基流动（OpenRouter 原路径已移除）。**全部视频能力（portal
> 穿越主题、genvideo、视频嵌入）已彻底移除**，攻略内容仅以图文呈现。适配记录见
> [`ADAPTATION.md`](ADAPTATION.md)。

# Trip Planner Skill（境内版）

**一句话进，一份核实过的、逐小时的、可以直接照着订的境内行程计划出 —— 交付形态就是一个
设计版页面，七种视觉主题里挑一种。** 一个开放格式的 Agent Skill(`SKILL.md`)，跑在你现在
用的那个 coding agent 里 —— Claude Code、Codex、Gemini CLI、Cursor、GitHub Copilot、
OpenCode、Qwen Code、Goose、Kiro、Roo Code，以及任何能加载 Agent Skills 的宿主：营业
时间、价格和节假日都用工具查，不靠猜；每一项预订都递给你一条链接；从不替你预订、也不替
你付款。

![Agent Skills: open format](https://img.shields.io/badge/Agent%20Skills-open%20format-0A7B83.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![境内-only](https://img.shields.io/badge/scope-境内行程-CE0000.svg)

## 示例

[`examples/china-2026/`](examples/) 收着一趟完整示例：上海 → 北京 → 西安 → 北京 →
上海，8 天，境内游客视角（身份证入园、12306 实名、景区预约），附两种主题的成品页面：

- **clay 黏土** —— 一整片连续的黏土定格地景，一条路串起沿途的里程碑石头。
  渲染：`python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html`
- **splash 闪屏** —— 一张被拉长成长卷的游戏启动画面：浮空的日子岛屿悬在成链的天空下。

两页都是自包含 HTML，双击即开、零网络请求；`examples/china-2026/` 里还有行程的
`gates.ics`（T-14/T-7/T-3/T-1 行前阶梯）和 `trip.kml`（40 个编号图钉，导入 Organic
Maps 离线用）。

朴素的、未上主题的打印页是可额外要的东西（`scripts/render_plan.py`），从来不是默认交付
物；`themes/render_picker.py` 会生成一个风格选择页，按 `<prefix>-<theme>.html` 链接到
某趟旅行所有已渲染的版本。

## 你会得到什么

说一句 *「云南，10 月去 8 天，中等预算，自然风光 + 古城。」* 这个 skill 会给你：

- **一条跨城路线** —— 先给 2–3 套骨架让你挑，再给机票/高铁深链（`flight_scan.py`：
  携程/Trip.com/去哪儿机票 + 携程火车票；国内无免钥票价 API，价格由点开链接核对），
  以及每一段城际的高铁 vs 飞机结论。
- **每一天的逐小时安排** —— 营业时间和闭馆日都用工具查过，预约政策（故宫/陕历博/
  莫高窟等实名分时预约）写进清单，每一跳都有可点开的高德/百度地图链接。
- **交付物是一个设计版页面，不是一堵文字墙** —— 计划会经**七种主题渲染器**里的一种
  （默认 **illustrated 插画版**）渲染成一个自包含、手机友好的文件：`trip-<theme>.html`。
  七种主题全部是图文形态，自带离线分享图按钮（*存这一天* / *存附录* / *存一张长图*；
  noir 和 glass 只导出单日模块）。
- **`plan.geo.json`，唯一真源** —— 主题页面、地图链接，以及一份给 Organic Maps 用的
  离线 KML，全都从这一个文件出。
- **按片区给出的酒店候选清单**(带日期的深链，不编造房价)、一份**人民币**预算汇总，
  和一份**按截止日排序的预订清单**（预约/门票秒杀/车票起售排最前）。
- **行前简报** —— 应急号码（110/120/119/122/12301）、中央气象台预警行、高反提示、
  假日调休、支付分层、离线地图准备，全部境内来源。
- **图片按你的 agent 能做到什么来** —— 三级台阶，在提到页面风格之前就静默判完：
  agent 的**原生**生图 → 环境变量里的**境内生图 key**（阿里云百炼 dashscope /
  硅基流动 siliconflow）→ 内置的**素材库(stock kit)**。走到最后一级依然交付主题页面，
  并且把这件事明说出来。

中文用户直接用中文提就行：说「旅行规划」「帮我排个行程」「机票比价」都能触发，整趟跑完，
交付的页面也是中文的。

它不会做的事：预订、付款、占位、填写个人信息。链接由你自己点。

## 快速开始

**1. 安装** —— 支持 Agent Skills 的 agent 按目录发现 skill，直接把本目录放进你的
skills 目录（Claude Code 是 `~/.claude/skills/trip-planner`；其他宿主见各自身份说明）。
可选依赖只有 Pillow（素材流水线）；其余全部只用 Python 3.9+ 标准库。

**30 秒试一下** —— 不需要 key，也不需要 agent，在本目录执行：

```bash
python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html \
  && python3 themes/qc.py china-clay.html    # 主题页面 + 它的 QC(退出码 0)
```

**2. 规划一趟旅行** —— 在你的 agent 里，一句话。遇到旅行/行程类请求这个 skill 会自己
触发，也可以显式调用：

```
/trip-planner 云南 8 天，10 月出发，中等预算，自然风光和古城，日期前后可挪 2 天
```

计划页面的界面语言跟着你提问用的语言走（计划里的 `"lang": "zh"|"en"`；每个渲染器都可以用
`--lang` 覆盖）。会根据你的问法在四种模式里挑一种：

| 模式 | 触发 | 会跑什么 |
|---|---|---|
| **整趟旅行** | 「帮我规划云南 8 天」 | 全部阶段:意图收集 → 行前简报 → 路线骨架 → 交通 → 每日计划 → 酒店 → 汇总 + 自检 |
| **单日** | 「我们在杭州有一天」 | 节假日/节庆检查 + 这一天 + 自检;跳过交通和酒店 |
| **空档填充** | 「我在 X 附近,有 2 小时空」 | 15 分钟半径内给 2–3 个选项,各带步行时间、地图链接、必须往回走的时刻 |
| **临场重排** | 「高铁没赶上 / 下暴雨了」 | 只根据降级标签重建受影响的那一天 |

**3. 设计版页面** —— 这就是这个 skill 交到你手上的东西，用你挑的那个主题（默认
**illustrated 插画版** = `render_theme2.py`），绝不会退化成一个朴素文字页面：

```bash
python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html   # theme2 clay2 noir2 glass2 journal zine splash
python3 themes/qc.py trip-<theme>.html                                # 退出码 0 = 干净;退出码即 FAIL 条数
```

美术契约见 [`themes/ART-SCHEMA.md`](themes/ART-SCHEMA.md)；每个字段都是可选的，一份空的
art 文件也必须能渲染出来。图片按 `--assets` → art 目录 → plan 目录 →
`themes/assets/` 的顺序解析。

**4. 图片：三级台阶，从好到次（图文-only，无任何视频环节）。**

1. **原生生成** —— agent 自己就能生图，那就用它自己的能力：为这趟旅行现画，**不用配
   任何 key**（下游 `split_sheet.py` → `cutout.py` → `towebp.py` → 行程 manifest 步骤
   一样；契约见 `themes/ART-SCHEMA.md`）。
2. **一把境内 key** —— 没有原生生成能力：设环境变量 `DASHSCOPE_API_KEY`（阿里云百炼
   通义万相）或 `SILICONFLOW_API_KEY`（硅基流动 Kolors），`themes/gen.py
   --provider auto` 自动检测。两家都国内直连、支付宝开通。

   ```bash
   python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json   # 先 --dry-run
   ```

3. **素材库(stock kit)** —— 以上两级都没有：图片取自随仓库附带的这套素材，页面依然是
   主题页面：

   ```bash
   python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
   python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
           --assets themes/assets/stock -o trip-illustrated.html   # 这里的 --assets 是必需的
   ```

   `stock_art.py` 按目的地和每天的关键词挑图，文字（封面标题、每天的标题、图注）仍然交给
   agent 写，并把「图片来自内置素材库」声明写进页面小字。覆盖度：**illustrated** 完整，
   **clay** 可用；其余五种主题仍需要生成的图片。细节见
   [`themes/assets/stock/README.md`](themes/assets/stock/README.md)。

凡目的地专属的图（封面、主视觉、标题贴纸、地形色带）必须为这趟旅行现画；通用件（胶带、
印章、车票、云朵等道具）可复用。

## 工作原理

**流水线。** `SKILL.md` 是 agent 照着走的剧本：Phase 0 意图收集(只问缺的,一条消息问完)
→ Phase 1 行前简报(应急号码、中央气象台预警、假日调休 API、天气、支付分层)
→ Phase 2 路线骨架 → 检查点 → Phase 3 交通与城际(`scripts/flight_scan.py`：
机票/高铁深链) → Phase 4 各城市的每日计划(并行的城市 subagent,搜索预算写死)
→ Phase 5 酒店 → Phase 6 汇总、对抗式自检、交付。与用户之间最多三次交互,通常只有两次:
只有当核心事实缺失且推不出来时才发的开场消息、从 2-3 套路线骨架里挑一套、以及最后交付。

**一个文件，一个真源。** `plan.geo.json` 只写一次，所有东西都读它：
`scripts/route_tools.py`（`geocode` · `check` · `links --write` · `kml` · `sun`）从它的
`stops` 生成地图链接和 KML；`scripts/render_plan.py` 生成朴素 HTML；每个主题渲染器读的
都是同一份文件加它的 `art.json`。Schema 模板：
[`assets/plan.example.json`](assets/plan.example.json) —— 复制一份，把 `PLACEHOLDER`
填掉，再渲染。

**硬规则**(提炼自 [`SKILL.md`](SKILL.md) 和 `references/`):

1. 从不代订、付款、占位或填写个人信息 —— 只给链接和清单。
2. 价格和营业时间来自工具,绝不来自记忆;查不到的价格写成「—,点链接查」。
3. 先便宜后贵:先用自带脚本和免密钥路径,浏览器排第二;绝不 curl OTA 或航司网站。
4. 搜索预算是显式的,写进每一个 subagent 的 prompt。
5. 估算就明说是估算:交通时长以 `(est.)` 区间交付,除非核实过。
6. 超过约 3 个月之外,没人会公布那一天的营业时间 —— 核实季节性规律,盖上「截至 {date}」,
   并在清单上加一条二次确认任务。
7. 计划必须先过自检才能交付:闭馆扫描、链条算术、最晚入场时间、步行总量。
8. **目的地必须在中国大陆**；境外行程不在本 skill 范围内。

**数据来源** —— 境内直连、免密钥为主；价格是用来横向比较的，计划里的深链才是真源
([`references/data-sources.md`](references/data-sources.md)):

| 数据源 | 用途 | 备注 |
|---|---|---|
| 高德 restapi（`AMAP_KEY`） | 景点坐标（geocode 首选） | GCJ02 自动回算 WGS84；免费 key |
| 百度 geocoding v3（`BAIDU_MAP_AK`） | geocode 回退 | 同上，脚本自动回退 |
| 高德/百度网页深链 | 每一跳的导航链接 | 默认 amap，H5 拉起 App |
| 12306 / 携程 / 去哪儿 / Trip.com | 机票与火车票深链 | `flight_scan.py` 生成;票价点开核对 |
| timor.tech + 国务院放假安排 | 法定节假日与调休 | API 是社区维护,以官方公告为准 |
| Open-Meteo | 对应日期的天气与气候 | 首次调用可能要约 10 秒 |
| 中央气象台 nmc.cn / 12379 | 预警与灾害季 | 橙红色预警 = 行程停止线 |
| 本地 NOAA 天文模型 | 日出日落/民用晨光 | 零网络,境内版唯一日照路径 |

## 兼容性

- **是一种格式，不是某个产品的集成。** 这是一个 Agent Skill —— 开放格式：一份
  `SKILL.md` 剧本，加上 `references/`、`scripts/` 和 `themes/`。任何能加载 Agent
  Skills 的宿主都能加载它；脚本只用 Python 3.9+ 标准库。
- **宿主需要具备什么。** 一个能跑 Python 3.9+ 的 shell，以及网页搜索/抓取工具（简报、
  每日计划和酒店阶段都要在线核实）。锦上添花：subagent（Phase 4 并行）、浏览器工具、
  原生生图能力（没有就用境内 key，再没有就用附带的素材库 —— 无论哪种，页面都还是主题
  页面）。
- **任何模型。** 这个 skill 是说明加脚本；真正执行它的是你宿主里跑的那个模型。

## 仓库结构

```
README.md  README.zh-CN.md    本页,英文版与中文版
THIRD-PARTY-NOTICES.md        随仓库再分发的字体与图标的许可证全文(Caveat OFL、Lucide ISC)
SKILL.md                      剧本:各阶段、硬规则、快捷模式（境内-only 门禁在 Phase 0）
ADAPTATION.md                 境内适配记录:受限清单、替换对照、境内-only 改造日志
references/
  data-sources.md             境内数据源 + URL 配方,含回落链
  scheduling.md               停留时长、缓冲、日子类型、常见坑、核验清单
  navigation.md               高德/百度链接、跳转行格式、核实 vs 估算的策略
  output-template.md          城市块交接格式 + 最终交付物结构
  phase-0-intake.md           Phase 0:核心/可选事实、目的地门禁、意图收集消息、prefs、生图能力检查
  phase-1-brief.md            Phase 1:应急卡、预警行、健康行、假日调休、灾害季、退出判据
  phase-3-legs.md             Phase 3:机票/高铁/自驾段的价源与字段、退出判据
  phase-4-days.md             Phase 4:城市子 agent 契约、每城六步、route_tools 顺序、退出判据
  phase-6-assemble.md         Phase 6:组装、对抗自检、交付、主题渲染流程、退出判据
  cover-titles.md             中英双语诗意封面标题库 + 陈词滥调黑名单
  themes.md                   主题渲染手册:七种主题、如何加一种、缺陷检查清单
scripts/
  flight_scan.py              机票/火车票深链生成器(免密钥零网络;携程/Trip.com/去哪儿 + 携程火车票)
  route_tools.py              geocode → 距离检查 → 高德/百度链接 → KML → 闸门 .ics → 日出日落(本地天文)
  plan_lint.py                渲染前的内容门禁(--strict 下退出码 = FAIL 数)
  render_plan.py              plan JSON → 自包含可打印 HTML
themes/
  README.md                   这里有什么、三条命令、图片从哪来
  render_theme2.py …          七个渲染器:theme2(illustrated)· clay2 · noir2 · glass2 · journal · zine · splash
  render_picker.py            风格选择页(链接 <prefix>-<theme>.html)
  theme_common.py             共享工具函数、i18n、离线分享图引擎
  qc.py  xprobe.sh  xt.sh     静态 QC · 无头导出探针
  gen.py                      境内生图备胎(dashscope 通义万相 / siliconflow Kolors)
  stock_art.py                没有生图能力也没有 key 时:用素材库拼出 art.json 的图片部分
  towebp.py cutout.py split_sheet.py build_manifest.py
                              素材流水线(png→webp、抠图、拼版切分、manifest)
  ART-SCHEMA.md               art.json 契约(唯一副本)
  assets/                     图库:webp 素材、Caveat 字体、manifest.json
    stock/                    素材库:大区封面画 + 通用/地标抠图、index.json、README.md
assets/plan.example.json      schema 模板(境内示例数据) —— 复制一份,填掉 PLACEHOLDER 再渲染
examples/
  README.md                   china-2026 示例:两种主题、渲染命令、KML/ICS
  china-2026/                 <plan>.geo.json + <plan>.art.json + 两个主题页面 + gates.ics + trip.kml
```

## 核验方式

- **静态 QC** —— `themes/qc.py page.html` 检查离线契约(无网络、无外部请求)、无 JS 时
  能否存活、打印、焦点顺序和链接卫生；退出码就是 FAIL 条数。
- **逐字节回归** —— 示例页能用 [`examples/README.md`](examples/README.md) 里的命令重新
  渲染出逐字节一致的结果。
- **导出探针** —— `themes/xprobe.sh` / `xt.sh` 驱动无头 Chrome 去点页面上真正的分享
  按钮，把导出图片写下来——缺陷是被看见的，不是被假设的。
- **内容门禁** —— `scripts/plan_lint.py --strict`：简报卡齐全且按序、无占位文案、自检
  行、每天有 stop 和 `sun --write` 串，退出码 = FAIL 数。

## 状态与限制

**运行要求。** Python 3.9+；只用标准库，除了可选的 Pillow（素材流水线）。渲染任意主题
用附带图库或素材库时，一个 key 都不需要。

**限制与非目标。**

- **仅支持境内行程。** 目的地门禁在 Phase 0：港澳台同样停止；境外数据源与入口已整体移除。
- **仅图文交付。** 不含任何视频生成、嵌入或展示能力。
- **不是实时的。** 它做规划；它不追踪延误，也不改签。
- **价格会变。** 每个数字都带一个「截至」日期，正是为此。

## 致谢

- [Caveat](https://fonts.google.com/specimen/Caveat)(SIL 开放字体许可 1.1)—— journal
  主题里内嵌的手写体 webfont(`themes/assets/caveat-vf.woff2`)。
- [Lucide](https://lucide.dev/)(ISC)—— `themes/lucide-icons.json` 里的图标雪碧图。
  两者的许可证全文:[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。
- 高德开放平台 / 百度地图开放平台 —— 地理编码与导航深链（key 由用户自备，免费申请）。
- Open-Meteo、timor.tech —— 天气与节假日数据。
- 生成图片：阿里云百炼通义万相 / 硅基流动 Kolors（境内直连）。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
