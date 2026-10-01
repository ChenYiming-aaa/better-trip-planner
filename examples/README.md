# Examples

One finished trip — `china-2026` — plus the plain-page sample artefacts. The folder holds
only the source files and the pages they produce — `china.geo.json` (the facts),
`china.art.json` (what the trip looks and sounds like) and `china-<theme>.html`
(self-contained: every picture is an inlined webp, so the page opens by double-click with
no network). Re-running the render command below rewrites the shipped pages **byte for
byte**, which is what makes this example a regression test as well as a showcase.

（境内版说明：本 skill 仅支持境内行程，原日本/土耳其/北欧/摩洛哥/墨西哥/越南六国
示例与 portal 视频主题已整体移除；`scripts/build_site.py` 演示站链路一并删除，
示例页面本地双击打开即可。）

## What is on disk

| File | What |
|---|---|
| `china-2026/china.geo.json` | the plan — 8 days, 上海→北京→西安→北京→上海, domestic traveller's view |
| `china-2026/china.art.json` | the art file driving both shipped themes |
| `china-2026/china-clay.html` | clay 黏土 theme — one continuous clay landscape with a road |
| `china-2026/china-splash.html` | splash 闪屏 theme — game-splash islands, chained sky gradients |
| `china-2026/gates.ics` | the date-locked checklist gates（T-14/T-7/T-3/T-1 阶梯） |
| `china-2026/trip.kml` | 40 numbered pins + day route lines, importable into Organic Maps |
| `gates-sample.ics` | the same gates file kept beside this README as the .ics worked sample |

## Render them

Run from the repo root; every line rewrites the shipped page exactly.

```
python3 themes/render_clay2.py   examples/china-2026/china.geo.json -o china-clay.html
python3 themes/render_splash.py  examples/china-2026/china.geo.json -o china-splash.html
```

`cmp china-clay.html examples/china-2026/china-clay.html` exits 0, and so does the splash
page — that is the regression gate. Three conventions keep the commands that short:

- **`--art` is implicit.** A renderer picks up `<plan>.art.json` sitting beside the plan.
  Running from somewhere else, or with an art file kept elsewhere, pass
  `--art examples/china-2026/china.art.json` — the art file's own folder joins the asset
  search path, so its pictures come along.
- **Pictures resolve from `themes/assets/`.** Every trip's stems are prefixed with the
  trip name (`china-…`), so `--assets` is never needed here and a library
  size-variant can't shadow a trip's own picture.
- **The page language follows the plan** (`lang` / `meta.lang`); `--lang zh|en` on any
  renderer overrides the chrome, while art copy renders in whatever language it was
  written in.

## Two themes per art file

`china.art.json` carries the shipped splash block **and a second theme's block** (clay),
so one extra command gets a completely different page out of the same trip — the cheapest
way to see how far apart the themes really are. Both shipped pages come from these exact
commands; the remaining five themes each render from their own art blocks the same way
（`references/themes.md` §2 有每种主题的范式说明）.

## Maps and the KML

The offline pin set is generated, not stored — one command:

```
python3 scripts/route_tools.py kml examples/china-2026/china.geo.json -o trip.kml
```

The output imports into Organic Maps（奥维互动地图等支持 KML 的应用均可）. The plan's
traveller advice tells the user to "import the trip KML into Organic Maps" — that is
exactly the file the command above writes, and a real delivery ships it next to the page;
only the repo keeps it out, because it is one command away.

## The .ics gates file

```
python3 scripts/route_tools.py ics examples/china-2026/china.geo.json -o gates.ics
```

Reads the checklist's ISO dates and `T-N` markers and writes one VEVENT per date-locked
gate, full action list in DESCRIPTION, two VALARMs each (`-P1D`, `-PT30M`) — the worked
example is `gates-sample.ics` here. Rules: output-template.md §Booking-artifact
conventions.

## The plain page and the style picker

The plain `scripts/render_plan.py` page (printable, checkbox checklist, offline route
sketch per day) is the extra deliverable, not the default:

```
python3 scripts/render_plan.py examples/china-2026/china.geo.json -o china-plain.html
```

The style picker builds a one-page chooser of all seven themes; it links the shipped
editions by name and marks the ones not on disk with `—` in the size column:

```
python3 themes/render_picker.py examples/china-2026/china.geo.json \
    --prefix china --products examples/china-2026 -o picker.html
```

Full manual for the theme system: [`../references/themes.md`](../references/themes.md);
the art.json field contract: [`../themes/ART-SCHEMA.md`](../themes/ART-SCHEMA.md).
