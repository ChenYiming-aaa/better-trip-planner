# -*- coding: utf-8 -*-
"""Build per-theme art blocks for the Hangzhou-Qingdao example.

Each theme has its own art vocabulary (ART-SCHEMA.md):
  illustrated/clay : cover.hero, end.hero, days[d].hero        (already present)
  journal          : cover.photo.stem, days[d].photo.stem
  zine             : cover.photo.stem, days[d].poster/photo.stem
  noir / glass     : themes.<t>.plates[] + day_plate
  splash           : kit palettes + fx (no custom cut-outs needed)
"""
import copy
import json
from pathlib import Path

p = Path("plan.art.json")
a = json.loads(p.read_text(encoding="utf-8"))
ill = a["themes"]["illustrated"]
dates = sorted(ill["days"])
day_stem = {d: ill["days"][d]["hero"] for d in dates}
cover_stem = ill["cover"]["hero"]
plates = [cover_stem] + [day_stem[d] for d in dates]
day_plate = {d: i + 1 for i, d in enumerate(dates)}

kick = a["cover"].get("kick", "")

# ---- common: zine photo vocabulary (journal overrides with its own) --------
a["cover"]["photo"] = {"stem": cover_stem, "caption": [kick, ""]}
for d in dates:
    info = a["days"].get(d, {})
    title = info.get("theme", "")
    mark = info.get("mark", "")
    a["days"][d]["photo"] = {"stem": day_stem[d], "caption": [title, mark]}
    a["days"][d]["poster"] = {"stem": day_stem[d], "caption": [title]}

# ---- journal: polaroid vocabulary (days[d].photo is a PLAIN STEM STRING
# here — render_journal.py reads it as a string; themes.journal.* overrides
# the common zine-style dicts) ------------------------------------------------
a["themes"]["journal"] = {
    "cover": {"photo": {"stem": cover_stem, "caption": [kick, "Hangzhou to Qingdao"]}},
    "days": {d: {"photo": day_stem[d]} for d in dates},
}

# ---- noir: night-film reel -------------------------------------------------
a["themes"]["noir"] = {
    "cover": {"zh": "山海红瓦", "en": "QINGDAO"},
    "plates": plates,
    "day_plate": day_plate,
}

# ---- glass: frosted panes reel ---------------------------------------------
a["themes"]["glass"] = {
    "plates": plates,
    "day_plate": day_plate,
}

# ---- splash: floating-island chapters (kit palettes, no custom cut-outs) ---
splash_days = {
    dates[0]: {"palette": "ocean",   "fx": "halo-cyan"},   # 跨海向北
    dates[1]: {"palette": "lilac",   "fx": ""},            # 老城经典
    dates[2]: {"palette": "alpine",  "fx": "beams-cool"},  # 崂山全天
    dates[3]: {"palette": "goldfog", "fx": "sun"},         # 麦香帆影
    dates[4]: {"palette": "sunrise", "fx": "sunrise"},     # 潮起归程
}
a["themes"]["splash"] = {
    "cover": {"zh": "出发！青岛", "sub": "杭州 → 青岛 · 五天四晚"},
    "hero": {"palette": "ocean"},
    "appendix": {"palette": "homebound"},
    "days": splash_days,
}

p.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("art blocks:", sorted(a["themes"]))
print("plates:", plates)
