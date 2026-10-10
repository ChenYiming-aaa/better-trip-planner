/**
 * Optional install-level check. Requires a profile that already has the
 * harness registry installed and this plugin linked into its node_modules
 * (for example after `dsh plugin --profile <p> add ...`). It mirrors what the
 * harness does at boot: resolve the plugin by bare package name, mount the
 * skill registry, mount the plugin row, then read and load the skill.
 *
 *   node tests/install.check.mjs <profileDir>
 *
 * The default `npm test` stays dependency-free; this file is the deeper check
 * you run once a harness is available.
 */
import { existsSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const PROFILE = process.argv[2];
if (!PROFILE) {
	console.error("usage: node tests/install.check.mjs <profileDir>");
	process.exit(2);
}
const require = createRequire(join(PROFILE, "package.json"));
let failures = 0;

/** Print one check result and record failures. */
function check(label, ok, detail = "") {
	console.log(`${ok ? "ok  " : "FAIL"}  ${label}${detail ? ` — ${detail}` : ""}`);
	if (!ok) failures += 1;
}

// 1. Bare-name resolution: what the bundle's cordis.patch.yml depends on.
let pluginEntry;
try {
	pluginEntry = require.resolve("dsh-trip-planner-cn");
	check("plugin resolves by package name from the profile", pluginEntry.startsWith(PROFILE), pluginEntry.replace(PROFILE, "<profile>"));
} catch (error) {
	check("plugin resolves by package name from the profile", false, String(error.code));
	console.log(`\nFAIL — ${failures} check(s) failed`);
	process.exit(1);
}

// 2. One coherent cordis + skill registry, as the harness loads them.
const { Context } = await import(pathToFileURL(require.resolve("@deepseek-ai/cordis")).href);
const skillModule = await import(pathToFileURL(require.resolve("@deepseek-ai/dsh-skill")).href);
const SkillRegistry = skillModule.default ?? skillModule.SkillRegistry;

const ctx = new Context();
const base = ctx.plugin(SkillRegistry, {});
if (typeof base?.await === "function") await base.await();

const row = ctx.plugin(await import(pathToFileURL(pluginEntry).href), {});
if (typeof row?.await === "function") await row.await();

// 3. The skill is in the catalog, with a usable policy and resource base.
const pick = (v) => (Array.isArray(v) ? v : (v?.skills ?? v?.candidates ?? []));
const catalog = pick(await ctx.skills.list({ cwd: PROFILE }));
check("catalog exposes exactly one skill", catalog.length === 1, `${catalog.length} entries`);
const entry = catalog[0] ?? {};
check("catalog name is trip-planner-cn", entry.name === "trip-planner-cn", String(entry.name));
check("model and user invocable", entry.invocation?.modelInvocable === true && entry.invocation?.userInvocable === true, JSON.stringify(entry.invocation));
check("carries a description", typeof entry.description === "string" && entry.description.length > 0, `${String(entry.description ?? "").length} chars`);

// 4. Loading returns the body without frontmatter.
const loaded = await ctx.skills.get("trip-planner-cn", { cwd: PROFILE });
const body = loaded?.content ?? "";
check("load returns the full body", body.length > 10000, `${body.length} bytes`);
check("body has no frontmatter leak", !body.startsWith("---"));

// 5. Resources resolve against the installed copy, not the source checkout.
const resourceDir = entry.resourceBase?.path ?? "";
for (const rel of ["SKILL.md", "references/data-sources.md", "scripts/route_tools.py", "themes/render_clay2.py"]) {
	check(`resource present in installed copy: ${rel}`, existsSync(join(resourceDir, rel)));
}

// 6. Disposal removes the provider again (list before tearing down the registry).
await row?.dispose?.();
const after = pick(await ctx.skills.list({ cwd: PROFILE }));
check("disposal empties the catalog again", after.length === 0, `${after.length} entries`);
if (typeof base?.dispose === "function") await base.dispose();

console.log(failures === 0 ? "\nPASS — install-level check clean" : `\nFAIL — ${failures} check(s) failed`);
process.exit(failures === 0 ? 0 : 1);
