#!/usr/bin/env python3
"""Image generator for trip-planner illustration assets — CN-adapted build.

Three providers (--provider, default auto-detect):

  dashscope    阿里云百炼 通义万相 wanx2.1-t2i-turbo (async task API).
               Key: --api-key or env DASHSCOPE_API_KEY. 国内直连, 支持支付宝开票.
  siliconflow  硅基流动 Kwai-Kolors/Kolors (sync API). Key: --api-key or env
               SILICONFLOW_API_KEY. 国内直连.
Two providers (--provider, default auto-detect) — 境内-only，原 OpenRouter
路径已整体移除：

  dashscope    阿里云百炼 通义万相 wanx2.1-t2i-turbo (async task API).
               Key: --api-key or env DASHSCOPE_API_KEY. 国内直连, 支持支付宝开票.
  siliconflow  硅基流动 Kwai-Kolors/Kolors (sync API). Key: --api-key or env
               SILICONFLOW_API_KEY. 国内直连.

auto picks the first of: --provider flag > DASHSCOPE_API_KEY > SILICONFLOW_API_KEY.
Costs: dashscope/siliconflow are billed on-platform, so cost is printed as n/a
and the manifest records the model instead.

FALLBACK PATH: an agent that can generate images natively should use that
instead (no key to configure) — same specs and prompts, then the same
split_sheet / cutout / towebp / trip-manifest steps (ART-SCHEMA.md "Generator choice").
This script exists for environments without native generation.

Usage: python3 gen.py <jobs.json> [--outdir DIR] [--manifest PATH] [--dry-run]
                      [--provider auto|dashscope|siliconflow] [--api-key KEY]
Each job: {name, prompt, background, aspect_ratio, resolution, quality}
Saves <name>.png into --outdir, upserts each generation into --manifest, prints
per-image status + alpha verification.

  --outdir DIR     where PNGs land (default: themes/assets/, the shared
                   library). A trip keeps its own pictures beside its plan:
                   --outdir trips/kyoto-2027 — data_uri() searches the plan's
                   directory, so nothing has to be copied into themes/assets/.
  --manifest PATH  asset index to upsert into (default: themes/assets/
                   manifest.json). Give a trip its own, e.g.
                   trips/kyoto-2027/manifest.kyoto.json, so it never races
                   the shared index. Created if missing.
  --dry-run        print every payload that WOULD be sent (model, prompt,
                   params) and the exact output paths, then exit. No request,
                   no charge, no files written, manifest untouched.
A job whose <name>.png already exists in --outdir is skipped (so a re-run
after a partial failure only pays for what is missing).
"""
import argparse
import base64
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).parent          # credentials live here, always
ASSETS = HERE / "assets"                      # shared image library + manifest
DASHSCOPE_T2I = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
DASHSCOPE_TASK = "https://dashscope.aliyuncs.com/api/v1/tasks/{}"
DASHSCOPE_MODEL = "wanx2.1-t2i-turbo"
SILICONFLOW_T2I = "https://api.siliconflow.cn/v1/images/generations"
SILICONFLOW_MODEL = "Kwai-Kolors/Kolors"


def _http_json(url, body=None, headers=None, timeout=120):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers or {}, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _download_png(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={
            "User-Agent": "trip-planner-cn/1.0"}), timeout=180) as r:
        return r.read()


_DASHSCOPE_SIZES = {"1:1": "1024*1024", "16:9": "1280*720", "9:16": "720*1280",
                    "4:3": "1024*1024", "3:4": "1024*1024"}
_SILICONFLOW_SIZES = {"1:1": "1024x1024", "16:9": "1280x720", "9:16": "720x1280",
                      "4:3": "1024x1024", "3:4": "1024x1024"}


def call_dashscope(job, key):
    """Async task API: submit -> poll -> download. Transparent background and
    quality tiers are not exposed by wanx2.1-t2i; they are ignored with a note."""
    for note_k in ("background", "quality", "resolution"):
        if job.get(note_k) and job[note_k] not in ("auto", "medium", "1K"):
            print(f"[{job['name']}] note: dashscope ignores {note_k}={job[note_k]!r}")
    size = _DASHSCOPE_SIZES.get(job.get("aspect_ratio", "1:1"), "1024*1024")
    body = {"model": DASHSCOPE_MODEL,
            "input": {"prompt": job["prompt"]},
            "parameters": {"size": size, "n": 1}}
    resp = _http_json(DASHSCOPE_T2I, body, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"})
    task_id = (resp.get("output") or {}).get("task_id")
    if not task_id:
        raise SystemExit(f"FAIL on {job['name']}: no task_id — "
                         f"{json.dumps(resp, ensure_ascii=False)[:300]}")
    for i in range(60):                       # wanx usually finishes in 10-30 s
        time.sleep(3)
        st = _http_json(DASHSCOPE_TASK.format(task_id), headers={
            "Authorization": "Bearer " + key})
        status = (st.get("output") or {}).get("task_status")
        if status == "SUCCEEDED":
            results = (st.get("output") or {}).get("results") or []
            if not results or not results[0].get("url"):
                raise SystemExit(f"FAIL on {job['name']}: SUCCEEDED but no url")
            return _download_png(results[0]["url"]), DASHSCOPE_MODEL + " (dashscope)"
        if status in ("FAILED", "CANCELED", "UNKNOWN"):
            raise SystemExit("FAIL on {}: task {} — {}".format(
                job['name'], status,
                json.dumps(st.get("output"), ensure_ascii=False)[:300]))
    raise SystemExit(f"FAIL on {job['name']}: task {task_id} timed out (3 min)")


def call_siliconflow(job, key):
    size = _SILICONFLOW_SIZES.get(job.get("aspect_ratio", "1:1"), "1024x1024")
    body = {"model": SILICONFLOW_MODEL, "prompt": job["prompt"],
            "image_size": size, "batch_size": 1}
    resp = _http_json(SILICONFLOW_T2I, body, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json"})
    images = resp.get("images") or []
    if not images:
        raise SystemExit("FAIL on {}: no images — {}".format(
            job["name"], json.dumps(resp, ensure_ascii=False)[:300]))
    item = images[0]
    raw = (base64.b64decode(item["b64_json"]) if item.get("b64_json")
           else _download_png(item["url"]))
    return raw, SILICONFLOW_MODEL + " (siliconflow)"


def alpha_report(path):
    from PIL import Image

    im = Image.open(path)
    if im.mode != "RGBA":
        return f"mode={im.mode} NO-ALPHA"
    a = im.getchannel("A")
    lo, hi = a.getextrema()
    transparent_px = sum(1 for v in a.getdata() if v < 16)
    pct = 100.0 * transparent_px / (im.width * im.height)
    return f"mode=RGBA alpha_min={lo} alpha_max={hi} transparent={pct:.1f}%"


def register(job, cost, png, mp, model_str):
    """Upsert this generation into the manifest at `mp` (asset index)."""
    import datetime
    data = json.loads(mp.read_text()) if mp.exists() else {"assets": []}
    assets = [a for a in data.get("assets", []) if a.get("name") != job["name"]]
    assets.append({
        "name": job["name"],
        "kind": ("mockup" if job["name"].startswith("mock-") else
                 "probe" if job["name"].startswith("probe") else "asset"),
        "prompt": job["prompt"],
        "params": {k: job[k] for k in
                   ("background", "aspect_ratio", "resolution", "quality") if k in job},
        "model": model_str,
        "cost_usd": cost,
        "generated_at": datetime.date.today().isoformat(),
        "files": {"png": png.stat().st_size},
        "transparent": False,
    })
    data["assets"] = sorted(assets, key=lambda e: (e.get("kind", ""), e["name"]))
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("jobs", help="jobs.json: list of {name, prompt, ...}")
    ap.add_argument("--outdir", type=pathlib.Path, default=ASSETS,
                    help="where <name>.png lands (default: themes/assets/)")
    ap.add_argument("--manifest", type=pathlib.Path, default=ASSETS / "manifest.json",
                    help="asset index to upsert (default: themes/assets/manifest.json)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the payloads and output paths; send nothing")
    ap.add_argument("--provider", default="auto",
                    choices=["auto", "dashscope", "siliconflow"],
                    help="image backend (default auto: DASHSCOPE_API_KEY > "
                         "SILICONFLOW_API_KEY)")
    ap.add_argument("--api-key", default=None,
                    help="key for --provider dashscope|siliconflow (else the "
                         "matching env var; never printed)")
    args = ap.parse_args()
    provider = args.provider
    if provider == "auto":
        if (args.api_key or os.environ.get("DASHSCOPE_API_KEY")):
            provider = "dashscope"
        else:
            provider = "siliconflow"
    api_key = None
    if provider in ("dashscope", "siliconflow"):
        api_key = args.api_key or os.environ.get(
            "DASHSCOPE_API_KEY" if provider == "dashscope" else "SILICONFLOW_API_KEY")
        if not api_key:
            raise SystemExit("--provider {}: set --api-key or the {} env var"
                             .format(provider,
                                     "DASHSCOPE_API_KEY" if provider == "dashscope"
                                     else "SILICONFLOW_API_KEY"))
    outdir = args.outdir
    jobs = json.loads(pathlib.Path(args.jobs).read_text())
    if args.dry_run:
        print(f"DRY RUN — nothing sent. outdir={outdir}  manifest={args.manifest}  "
              f"provider={provider}")
        for job in jobs:
            png = outdir / f"{job['name']}.png"
            state = "exists → would skip" if png.exists() else "would generate"
            print(f"\n[{job['name']}] {state} → {png}")
            print(json.dumps({"prompt": job["prompt"],
                              "aspect_ratio": job.get("aspect_ratio", "1:1")},
                             ensure_ascii=False, indent=2))
        cred = ("env DASHSCOPE_API_KEY/--api-key" if provider == "dashscope"
                else "env SILICONFLOW_API_KEY/--api-key")
        print(f"\n{len(jobs)} job(s); credentials would be read from {cred}")
        return
    outdir.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for job in jobs:
        png = outdir / f"{job['name']}.png"
        if png.exists():
            print(f"{job['name']}: exists, skipped")
            continue
        t0 = time.time()
        raw, model_str = (call_dashscope(job, api_key) if provider == "dashscope"
                          else call_siliconflow(job, api_key))
        cost = None              # billed on the CN platform; manifest keeps the model
        png.write_bytes(raw)
        total += cost or 0
        register(job, cost, png, args.manifest, model_str)
        print(
            f"{job['name']}: {len(raw)//1024}KB in {time.time()-t0:.0f}s "
            f"cost={'$' + format(cost, 'g') if cost is not None else 'n/a (platform-billed)'} "
            f"model={model_str} | {alpha_report(png)}"
        )
    print(f"TOTAL cost=${total:.4f}")


if __name__ == "__main__":
    main()
