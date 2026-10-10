/**
 * Self-check for the DSH plugin wrapper. No dependencies, no harness required:
 *
 *   node tests/plugin.test.mjs
 *
 * Verifies the parts a reviewer would check by hand — that the bundle manifest
 * is wired up, that the SKILL.md frontmatter parses into the fields the skill
 * registry validates, and that every resource path the skill body relies on
 * exists next to SKILL.md.
 *
 * Exits non-zero on the first failure.
 */
import { access, readFile } from "node:fs/promises";
import { parseSkillDocument, SKILL_NAME, inject } from "../index.js";

const root = new URL("../", import.meta.url);
let failures = 0;

/**
 * Assert a condition, printing the outcome either way.
 *
 * @param {string} label - What is being checked.
 * @param {boolean} ok - The condition.
 * @param {string} [detail] - Extra context printed after the label.
 */
function check(label, ok, detail = "") {
	const line = `${ok ? "ok  " : "FAIL"}  ${label}${detail.length > 0 ? ` — ${detail}` : ""}`;
	console.log(line);
	if (!ok) failures += 1;
}

// --- 1. bundle manifest -----------------------------------------------------
const manifest = JSON.parse(await readFile(new URL("package.json", root), "utf8"));
check("package.json declares dsh.bundle.patch", manifest.dsh?.bundle?.patch === "./cordis.patch.yml", String(manifest.dsh?.bundle?.patch));
check("bundle patch exists", await exists("cordis.patch.yml"));
check("exports cover locale/*.json", Object.keys(manifest.exports ?? {}).includes("./locale/*.json"));
check("icon declared and inside the package", typeof manifest.icon === "string" && await exists(manifest.icon));
check("files[] ships SKILL.md and references/", (manifest.files ?? []).includes("SKILL.md") && (manifest.files ?? []).includes("references/"));
check("@deepseek-ai/dsh-skill is a peerDependency, not a dependency", Boolean(manifest.peerDependencies?.["@deepseek-ai/dsh-skill"]) && manifest.dependencies === undefined);
check("package name matches the patch row", (await readFile(new URL("cordis.patch.yml", root), "utf8")).includes(manifest.name));

// --- 2. patch wiring --------------------------------------------------------
const patch = await readFile(new URL("cordis.patch.yml", root), "utf8");
check("patch inserts the wrapper row", /-\s*insert:/.test(patch) && patch.includes("name: dsh-trip-planner-cn"));

// --- 3. skill frontmatter ---------------------------------------------------
const raw = await readFile(new URL("SKILL.md", root), "utf8");
const parsed = parseSkillDocument(raw, "SKILL.md");
const NAME_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/; // registry grammar
check("inject asks for the skills registry", Array.isArray(inject) && inject.includes("skills"));
check("frontmatter name is valid kebab-case", NAME_RE.test(parsed.name), parsed.name);
check("frontmatter name matches the exported SKILL_NAME", parsed.name === SKILL_NAME);
check("description is present and non-empty", parsed.description.length > 0, `${parsed.description.length} chars`);
check("description is folded to one line", !parsed.description.includes("\n"));
check("body drops the frontmatter block", !parsed.content.startsWith("---") && parsed.content.length > 1000, `${parsed.content.length} bytes`);

// --- 4. resources the skill body references ---------------------------------
const resources = [
	"references/data-sources.md",
	"references/output-template.md",
	"references/themes.md",
	"scripts/plan_lint.py",
	"scripts/route_tools.py",
	"scripts/render_plan.py",
	"scripts/flight_scan.py",
	"themes/render_clay2.py",
	"themes/render_theme2.py",
	"themes/render_journal.py",
	"themes/render_zine.py",
	"themes/render_splash.py",
	"themes/render_noir2.py",
	"themes/render_glass2.py",
	"themes/qc.py",
	"assets/plan.example.json",
];
for (const rel of resources) {
	check(`resource resolves: ${rel}`, await exists(rel));
}

// --- 5. the resources directory is what resourceBase points at --------------
check("resourceBase directory contains SKILL.md", await exists("SKILL.md"));

console.log(failures === 0 ? "\nPASS — plugin wrapper self-check clean" : `\nFAIL — ${failures} check(s) failed`);
process.exit(failures === 0 ? 0 : 1);

/**
 * Whether a path exists relative to the repository root.
 *
 * @param {string} rel - Repository-relative path.
 * @returns Whether the path exists.
 */
async function exists(rel) {
	try {
		await access(new URL(rel, root));
		return true;
	} catch {
		return false;
	}
}
