# Phase 0 — Intake (the procedure)

Read this at the start of Phase 0, before you decide whether to ask the user anything.
SKILL.md Phase 0 is the contract — inputs, outputs, and the gates that decide pass/fail;
this file is the whole procedure it points at: what counts as a core fact, how origin
is inferred, the intake message format and its rules, what goes into `prefs`, the
picture-strategy check (素材库优先), the style line and the plan language.

Inputs: the user's request (and anything said earlier in the conversation). Outputs:
the plan's top-level `prefs` block and `lang`, the picture mode (`prefs.pictures`), the
assumptions block for checkpoint (a) — and at most one intake message.

## Read the request first — one message, or none

**Read the request before deciding whether to ask anything.** Most requests already carry
what matters — "帮我安排今年 10.1 到 10.7 的德国之旅" has the destination and the dates,
and gets **zero questions**: infer the rest, list the assumptions in one block at the top
of checkpoint (a), and move. Ask only when a *core* fact is missing **and** cannot be
inferred — and then ask for everything in ONE message in the **intake format** below,
under four rules: (1) core first, optional after; (2) **only the items the user has not
already answered** — anything stated in the request (destination, dates, party, "自驾",
a style name, a budget) is settled and must not reappear as a question; (3) **each
optional line carries its default**; (4) **one "all defaults" escape hatch** (the 💡 line).

## Core and optional facts

**Core** — must be known or defensibly assumed:
- **Origin** (city/station). Missing → infer from the conversation language, the
  user's locale/timezone or anything said earlier — 境内出发默认按**出发城市**（不是机场，
  高铁常常比飞更快）：语言或 locale 只能锁定大区域，取该区域最大枢纽城市 unless a city
  was mentioned（zh 请求默认上海，and say so），state it as an assumption; it costs one
  line to fix at checkpoint (a) and a whole round trip to ask. Genuinely unguessable →
  it is the one core question.
  A city named anywhere in the request ("我住在成都", "from 西安") overrides the language
  inference. 常见出发枢纽（机场/高铁站都要考虑）:上海 PVG/SHA + 虹桥站 ·
  北京 PEK/PKX + 北京西/南站 · 广州 CAN + 广州南 · 深圳 SZX + 深圳北 ·
  成都 CTU/TFU + 成都东 · 杭州 HGH + 杭州东 · 西安 XIY + 西安北 · 武汉 WUH + 武汉站 ·
  重庆 CKG + 重庆北 · 南京 NKG + 南京南。A city not on this line: look its
  airport/station up; never guess it from the province.
- **Destination** (省/市/景区 shortlist). Missing → ask; nothing to plan without it.
  **目的地必须在中国大陆（港澳台同样停止）**——境外请求直接说明范围外并停止。
- **When / how long** (dates, or a duration + rough month + flexibility). Missing → ask.
- **Page style** — one of the seven themes (Phase 6). Default: **illustrated 插画版**.
  Before you mention styles at all, run the **picture-strategy check** below — its
  result decides how pictures are produced, **not what you say**（用户永远看不到
  图片来源说明）.

**Optional** — ask them in the same message only when you are already asking; never
send a message just for these. Unanswered → default, and the assumptions block says so:
- travel style: self-drive · group tour · public transport + walking (default: public
  transport, or self-drive where the destination is car-first — Phase 3 §Driving legs)
- lodging habit: hotel · hostel · B&B / guesthouse · apartment · 度假酒店/古镇客栈,
  and the band (default: mid-range hotel, refundable)
- scenery taste: scenery/nature · city · beach · forest · lake · mountain (default: read
  from the destination + interests)
- party size & mobility (default: 2 adults, no kids) · budget style or number (mid) ·
  interests ranked (food/history/nature/anime/hiking/shopping/photography/nightlife) ·
  pace 2/3/4 anchors per day (3) · ±day flexibility (±2) · 全员身份证随身（部分
  边境区域需边防证——见 phase-1-brief.md，目的地命中才问）· locked must-sees.

## The intake message

**Intake format** (user's language; markdown; full zh/en samples in
references/output-template.md §Intake message). Keep it to one screen:

```
**先确认几件事 —— 一条消息回我,写序号+答案;没写的按默认**

**必答**
1. 出发城市 —— 我猜是上海(你用中文问的),对吗?
2. 玩多久、大概什么时候 —— 例:10.1–10.7,或「7 天 · 10 月 · 前后可挪 2 天」

**选答(不答走默认)**
3. 页面风格:插画(默认)· 黏土 · 夜航 · 玻璃 · 手账 · Zine · 闪屏 —— 样子见 examples/ 各行程的已渲染页面
4. 出行方式:公共交通+步行(默认)· 自驾 · 跟团
5. 住宿:中档酒店(默认)· 青旅 · 民宿 · 公寓 · 度假酒店/古镇客栈
6. 偏好:城市 · 自然风光 · 海滩 · 森林 · 湖泊 · 山 —— 默认按目的地定
7. 人数 / 预算 / 节奏:默认 2 成人 · 中档 · 每天 3 个主要点

💡 回「默认」= 全部按默认,直接开工。
```

Rules for the block: numbering runs continuously over whatever is left; a heading with
nothing under it is dropped; the 💡 line only when at least one optional item is shown; a guessed core
value is asked as a confirmation ("我猜是 X,对吗?"), not as an open question; never
more than one message, never a follow-up "just one more thing". English sample:
output-template.md. The same facts, answered or defaulted, go into `prefs` next.
**图片策略是内部决策：intake 消息里不出现任何图片来源或生图能力的说明**（不发
"本次没有生图能力/会用素材库"之类的 ℹ️ 行——用户只关心行程，配图是我们的事）。

## `prefs` and the assumptions block

Write what you learned or assumed into the plan's top-level `prefs` block
(`assets/plan.example.json`: `theme`, `pictures`, `travel_style`, `lodging`, `scenery`,
`pace`, `budget`, and `notes` — the inferred values in one line, e.g. "assumed origin
PVG (zh request, no origin given)"; the assumptions block at checkpoint (a) is written
from it) so Phases 2-6 read one place and a later replan does not re-ask.

## Picture-strategy check（素材库优先）

**Picture-strategy check** — silent, once, before styles come up:
1. **先查素材库**（`themes/assets/stock/`，含 `stock_art.py` 的 country/day 关键词
   匹配）：**有适合本次行程的图片就直接选用**（`prefs.pictures = "stock"`），
   **不调用生图**。
2. 素材库无合适图片、且你有 **native image-generation tool** → 为本次行程定制生成，
   nothing to configure (`prefs.pictures = "native"`).
3. 素材库无合适图片、且环境变量里已有 `DASHSCOPE_API_KEY` 或 `SILICONFLOW_API_KEY`
   （never read, print or copy the value）→ `gen.py` 走境内生图（dashscope 通义万相 /
   siliconflow Kolors，`"key"`）。
4. 素材库无合适图、又没有生图能力 → 页面仍以主题页交付（illustrated 走 stock 通用图；
   其余五个主题需要生成图，此时不提供，默认 illustrated）。
   **无论落在哪一档，都不向用户解释图片来源或能力**——不发"没有生图能力/会用素材库/
   给个 key 就能生成"之类的话，never ask for a key in the chat, never handle one。
   `prefs.pictures` records how the pictures were **actually** produced, not what the
   check found: a session that ran `stock_art.py` sets it to `stock` before rendering,
   whatever the env said.
5. **Stock mode covers two themes only**: complete for **illustrated** (default), works
   for **clay** (built-in terrain kit); the other five themes need generated pictures —
   a user asking for one of those in stock mode is told so and offered illustrated instead.

## Style line and plan language

Style, when you do ask, is one line: the eight names with the showcase link
(examples/ 内已渲染示例; offline: render
`themes/render_picker.py`), "skip = illustrated". Set the plan's top-level `"lang"` (`zh` | `en`,
output-template.md §Plan language) from the language the user asked in — the rendered
pages' UI follows it; `--lang` overrides. `lang` covers the page chrome only: **every
content string you write into the plan — day titles, notes, tips, checklist rows,
decisions, hotel blurbs — is in the user's language too.** The research sources are
mostly English and will drag your prose toward English if you let them; a zh user
receiving an English page is a shipped bug, not a style choice (self-check row, Phase 6).

## Exit criteria — tick every line before Phase 1

- [ ] At most one intake message was sent, in the intake format, and only for a core
      fact that was missing AND could not be inferred; nothing the user already stated
      was asked again; no follow-up question.
- [ ] Origin, destination, dates / duration and page style are known or defensibly
      assumed, each assumption written for the checkpoint (a) block.
- [ ] `prefs` carries theme · pictures · travel_style · lodging · scenery · pace ·
      budget · notes (the inferred values in one line); `lang` is set from the user's
      language.
- [ ] The picture-strategy check ran silently before styles were mentioned;
      `prefs.pictures` ∈ stock | native | key, 素材库优先已执行, and the user was
      told NOTHING about picture sources or capability; no key was asked for or
      handled in chat; a non-illustrated /
      clay theme requested in stock mode was redirected to illustrated.
