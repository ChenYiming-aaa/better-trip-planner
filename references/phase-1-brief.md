# Phase 1 — 行前简报 (the procedure · domestic-China only)

> 本 skill 仅支持中国大陆境内行程。本阶段产出境内行前简报:节假日调休 · 天气与预警 ·
> 支付 · 保险 · 安全提示 · 紧急电话 · 健康。签证/护照/汇率/外国预警等境外环节不存在。

SKILL.md Phase 1 is only the contract; this file is the procedure. Read it before any
fact about the destination is written, and never answer a Phase 1 fact from memory of
this file — the as-of stamps prove which facts were checked this session.

Inputs: destination(s) and dates (`prefs`, `meta.party`), the route skeleton candidates.
Outputs: the `brief` cards — emergency · safety · health · holidays · weather · money ·
connectivity · insurance (canonical order, output-template.md §Brief templates) — the
Phase 1 checklist rows, and the facts later phases inherit.

## Where the facts come from

The same rule as everywhere: official sources + tools, never memory, every line stamped
source + as-of. 境内各卡片的来源:

- **holidays**: 国务院办公厅当年放假安排(官方公告为唯一权威)+ timor.tech 节假日 API
  交叉核对;调休补班日单独列出——补班日不是休息日,反而是周边游错峰好日子。
- **weather**: Open-Meteo 同期历史气候 + 行前中央气象台 `nmc.cn` 城市预报;出发前
  T-7 复查。
- **safety**: 中央气象台预警信号(暴雨橙色/台风红色等直接触发改期建议)、景区限流/
  临时 closure 公告(官方公众号)、当地 12345/12301 旅游服务热线提示。
- **money**: 境内事实,不需要 API——微信支付/支付宝扫码全覆盖,备少量现金;
  写清"现金场景"(山区/庙会/个别停车场)。
- **connectivity**: 高德/百度地图、12306、滴滴;山区信号弱 → 离线地图包 + trip.kml。
- **health / insurance / emergency**: 见下文专节。

## The fact lines (holidays · weather · money · insurance · safety)

每张卡片的写法约束(output-template.md 有模板):

- 每行 ≤ 2 句,带来源 + as-of;查不到 → "n/a — 见 safety 卡",不猜。
- **holidays** 必答三问:行程撞法定假日吗?撞调休补班日吗?出发/返程日在黄金周
  首末日吗(高铁票/高速最堵点)?——答案直接进排程(错峰规则见 scheduling.md)。
- **weather** 给同期历史区间(如"11 月中旬北京 4-17 °C/夜间 -2 至 +4 °C,降水少")
  与"带什么"一句话;不做逐日预报(那是 T-7 复查的事)。
- **money** 固定三件:扫码全覆盖、现金建议、景区/地铁/打车支付方式。
- **insurance**: 境内旅行险(意外+医疗+延误),支付宝保险频道/保险公司官方渠道,
  8 天 ¥30-60 量级;高原/滑雪等高风险项目确认附加条款——写入 checklist 并给
  购买截止日(出发前,理由:行程取消保障只保购买后发生的事件)。
- **safety**: 见 Advisory line。

## Advisory line — 安全提示 · 来源 · 日期, line 0 of `brief.safety`

`brief.safety` 第一行是**安全提示行**(境内没有"旅行预警级别",但有等价物):

```
安全提示: {目的地} 无当前气象/地质预警(中央气象台, as-of 日期) · 景区正常开放(官方公众号, as-of 日期)
```

- 查到**暴雨橙色/红色、台风、暴雪、地质灾害预警** → 触发改期建议并停下来与用户确认
  (境外 Level 4 的境内等价物);黄色/蓝色预警 → 照常排程但把户外块放进 rain_alt。
- **景区限流/预约告罄公告**(如故宫放票即罄)→ 不算预警,但预约窗口必须写进
  checklist(Phase 4 会用到)。
- 依据来源: 中央气象台 `nmc.cn`、应急管理部门预警发布、景区官方公众号;每条带
  as-of。查不到预警 ≠ 没有风险——写"未查到当前预警",不写"无风险"。

## Emergency card — `brief.emergency`, six lines

固定六行(境内事实,不需要搜索,但号码必须正确):

1. 报警 110 · 急救 120 · 火警 119 · 交通事故 122
2. 高速公路救援 12122(自驾行程必带)
3. 全国旅游服务热线 12301(投诉/咨询)· 政务服务便民热线 12345
4. 就近三甲医院急诊(每个基地写 1 家,含 24 h 急诊说明;北京/西安一类的城市写实际医院名)
5. 药店连锁(国大/同仁堂/老百姓等)多为 24 h 或延时营业——常备药清单在 health 卡
6. 天气/灾害预警查询: 中央气象台 nmc.cn · 国家预警发布 12379

## Health line — `brief.health`

境内无黄热病/接种审计;写四件:

- 目的地当季健康要点(11 月华北干冷保暖、7 月南方防暑防蚊、高原线防高反——川西/
  西藏/青海行程**必须**给高反提示与布洛芬/红景天自备清单,并建议阶梯适应)。
- 就医路径: 三甲医院急诊(见 emergency 卡)、药店自备药清单(感冒/肠胃/创可贴/个人处方药)。
- 饮食: 街头小吃选择人流旺的摊位;肠胃药进清单。
- 无需国际旅行接种;如行程含野外徒步,提示蜱虫/防晒即可(来源: 中国疾控
  `chinacdc.cn` 健康提示, as-of)。

## Hazard line — the season card and the hazard gate

境内灾害季速查(原各国 hazard 表的境内版):

| 区域 | 季节 | 风险 | 动作 |
|---|---|---|---|
| 东南沿海 | 7-9 月 | 台风 | 预警触发改期;行程买退改 |
| 南方全域 | 6-8 月 | 暴雨/洪水 | 山区景区关闭风险;rain_alt 必填 |
| 北方山区 | 12-2 月 | 暴雪封路 | 自驾线改高铁或避开;防滑链 |
| 西北 | 3-5 月 | 沙尘 | 户外块室内备选 |
| 川西/西藏/青海 | 全年 | 高反/塌方 | 阶梯行程+保险含高原 |

- **A hazard-season hit means a gate**: season card 进 brief.safety、hazard gate 进
  checklist 与 `.ics`、保险截止日 NOW、可退改预订优先。
- T-14 / T-7 / T-3 阶梯复查时重读中央气象台与景区公告(不是 Phase 1 一次完事)。

## Exit criteria — tick every line before Phase 2

- [ ] `brief` 八卡齐全、顺序正确(emergency · safety · health · holidays · weather ·
      money · connectivity · insurance),每条带来源 + as-of
- [ ] `brief.safety` 以"安全提示:"行开头;预警/限流状态已核
- [ ] 行程日期与法定假日/调休的三问已回答并进排程
- [ ] 高原线(如适用)高反提示已写;否则写"无高原风险"
- [ ] emergency 卡六行完整,含基地城市三甲医院
- [ ] checklist 已有: 身份证/证件行 · 景区预约窗口行 · 保险行(含截止日) ·
      hazard gate(如命中) · T 阶梯
- [ ] 没有任何境外字段(签证/护照/汇率/外国预警)被写入
