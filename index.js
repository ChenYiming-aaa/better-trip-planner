/**
 * DSH plugin wrapper for the `trip-planner-cn` Agent Skill.
 *
 * The skill itself is host-agnostic: `SKILL.md` plus `references/`, `scripts/`
 * and `themes/` at the repository root. This module is the DeepSeek Harness
 * adapter. It registers the skill bundle on `ctx.skills` so that
 * `dsh plugin add` makes the skill appear in the agent's skill catalog and
 * loadable by name, with every bundled resource resolving against the
 * repository root.
 *
 * Mechanism (mirrors the first-party `@deepseek-ai/dsh-sandbox-windows-acl`
 * bundled skill): a provider registered with `ctx.skills.registerProvider()`
 * publishes one candidate at the bundled rank, carrying a `resourceBase`
 * directory; `list()` reads only frontmatter, and `get()` reads the body on
 * demand.
 *
 * @module dsh-trip-planner-cn
 */

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

/** Skill name registered in the catalog. Kept equal to the `name` frontmatter. */
export const SKILL_NAME = "trip-planner-cn";

/** Fallback used only when `SKILL.md` frontmatter carries no `name`. */
const FRONTMATTER_NAME = SKILL_NAME;

/** Unique provider name on `ctx.skills`; `runtime` is reserved by the registry. */
const PROVIDER = "dsh-trip-planner-cn";

/** Skill-name grammar enforced by the registry (public kebab-case skill names). */
const SKILL_NAME_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

/** Precedence rank for packaged skill providers and local bundled roots. */
const BUNDLED_SKILL_RANK = 600;

/**
 * The skill bundle lives at the repository root: this module is `<root>/index.js`
 * and `SKILL.md`, `references/`, `scripts/`, `themes/` and `assets/` are siblings.
 * Resolved through `import.meta.url` instead of the working directory, so it
 * holds wherever the plugin is installed (the profile's `node_modules`).
 */
const SKILL_ROOT = fileURLToPath(new URL("./", import.meta.url));

/** Locator of the skill's instruction file. */
const SKILL_FILE = `${SKILL_ROOT}SKILL.md`;

/**
 * The registry requires the skill on `ctx.skills`; without it the fiber stays pending.
 */
export const inject = ["skills"];

/**
 * Fold a YAML scalar written as a folded/literal block (`>-`, `|`) or a plain
 * single-line value into one whitespace-normalised line.
 *
 * @param lines - The raw block lines following the key.
 * @returns The folded value, or `undefined` when the block is empty.
 */
function foldBlock(lines) {
	const text = lines
		.map((line) => line.trim())
		.filter((line) => line.length > 0)
		.join(" ")
		.replace(/\s+/gu, " ")
		.trim();
	return text.length > 0 ? text : undefined;
}

/**
 * Strip matching surrounding quotes and unescape the doubled quote.
 *
 * @param value - A raw scalar as written after `key:`.
 * @returns The unquoted scalar.
 */
function unquote(value) {
	const first = value[0];
	const last = value[value.length - 1];
	if ((first === '"' || first === "'") && last === first && value.length >= 2) {
		const inner = value.slice(1, -1);
		return first === "'" ? inner.replaceAll("''", "'") : inner.replaceAll('\\"', '"');
	}
	return value;
}

/**
 * Parse the `SKILL.md` YAML frontmatter for the fields the skill registry
 * validates. Only plain string fields and folded/literal blocks are needed, so
 * this stays dependency-free rather than pulling a YAML parser into the plugin.
 *
 * @param raw - The complete `SKILL.md` contents.
 * @param path - Locator used in diagnostics.
 * @returns The parsed `name`, `description`, `whenToUse` and body.
 * @throws When the file carries no frontmatter block.
 */
export function parseSkillDocument(raw, path) {
	const match = /^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/u.exec(raw);
	if (match?.[1] === undefined) {
		throw new Error(`dsh-trip-planner-cn: ${path} has no YAML frontmatter block`);
	}
	const lines = match[1].split(/\r?\n/u);
	/** @type {Record<string, string>} */
	const fields = {};
	for (let index = 0; index < lines.length; index += 1) {
		const field = /^([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)$/u.exec(lines[index]);
		if (field === null) continue;
		const key = field[1];
		const inline = field[2].trim();
		// A `>-`, `|`, `|-` or `>-` indicator (optionally with a chomping/indent
		// modifier) starts a block the following more-indented lines belong to.
		if (/^[|>][+-]?\d*$/u.test(inline)) {
			const block = [];
			while (index + 1 < lines.length) {
				const next = lines[index + 1];
				if (next.trim().length > 0 && !/^\s/u.test(next)) break;
				block.push(next);
				index += 1;
			}
			const folded = foldBlock(block);
			if (folded !== undefined) fields[key] = folded;
			continue;
		}
		if (inline.length > 0) fields[key] = unquote(inline).replace(/\s+/gu, " ").trim();
	}
	const name = fields.name ?? FRONTMATTER_NAME;
	const description = fields.description;
	if (description === undefined || description.length === 0) {
		throw new Error(`dsh-trip-planner-cn: ${path} has no frontmatter description`);
	}
	if (!SKILL_NAME_RE.test(name)) {
		throw new Error(`dsh-trip-planner-cn: ${path} declares invalid skill name "${name}"`);
	}
	return {
		name,
		description,
		...(fields.whenToUse === undefined ? {} : { whenToUse: fields.whenToUse }),
		content: raw.slice(match[0].length).trim()
	};
}

/**
 * Register the bundled `trip-planner-cn` skill on `ctx.skills`.
 *
 * @param ctx - Context carrying the skill registry.
 */
export function apply(ctx) {
	const candidate = {
		name: SKILL_NAME,
		// Filled in below from frontmatter; placeholder keeps the object shape flat.
		description: "",
		invocation: { modelInvocable: true, userInvocable: true },
		provider: PROVIDER,
		source: "bundled",
		rank: BUNDLED_SKILL_RANK,
		resourceBase: { kind: "directory", path: SKILL_ROOT },
		locator: SKILL_FILE
	};
	const provider = {
		name: PROVIDER,
		list: async () => {
			const raw = await readFile(SKILL_FILE, { encoding: "utf8" });
			const parsed = parseSkillDocument(raw, SKILL_FILE);
			// Frontmatter is the authority for the catalog name, exactly as the
			// filesystem provider treats it; the constant only records the wrapper's
			// identity (and would surface a stray rename in the resources path).
			candidate.name = parsed.name;
			candidate.description = parsed.description;
			if (parsed.whenToUse !== undefined) candidate.whenToUse = parsed.whenToUse;
			else delete candidate.whenToUse;
			return [candidate];
		},
		get: async (entry, options) => {
			const { rank: _rank, locator, ...summary } = entry;
			const raw = await readFile(locator, { encoding: "utf8", signal: options?.signal });
			return { ...summary, content: parseSkillDocument(raw, locator).content };
		}
	};
	return ctx.skills.registerProvider(() => provider);
}
