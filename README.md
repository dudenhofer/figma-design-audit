# figma-design-audit

A Claude Code skill that audits a Figma frame or node against a fixed set of
design-quality standards and reports findings inline in chat. It's read-only with
respect to Figma — it never edits, generates, or writes anything back to the file.

## Prerequisites

- Claude Code with the **claude.ai Figma connector** (MCP) connected. This is an
  account-level connection (Settings → Connectors on claude.ai, or wherever your org
  manages this) — installing the skill itself doesn't set this up, and the skill
  won't work without it.

## Usage

```
/figma-design-audit <figma-url>
```

The URL must include a `node-id` (e.g.
`https://www.figma.com/design/<file-key>/<file-name>?node-id=<node-id>`) — the audit
is scoped to that specific frame/node, not the whole file. If you paste a URL without
a `node-id`, the skill will ask which frame/node to scope the audit to instead of
silently auditing everything.

Output is an inline chat report only, grouped by category — nothing is written to
disk or back to the Figma file.

## The checklist

Every audit checks four things. Full detail — exact regex patterns, WCAG thresholds,
and how each check is performed — lives in [`references/checklist.md`](references/checklist.md);
this skill reads that file directly, so editing it changes what the skill checks
without needing to touch `SKILL.md`.

1. **Tokens / Variables** — flags fills, strokes, corner radii, and text styles that
   are raw/hardcoded values instead of bound Figma variables or shared styles. This is
   checked for *internal consistency* within the file, not against one pinned design
   system — a value is flagged if it's raw where a bound variable exists for the same
   value elsewhere, or raw with no matching variable at all.

2. **Component / Instance Hygiene** — flags detached instances (components that have
   lost their link to the original) and hand-built elements that appear to duplicate
   an existing library component rather than reusing it.

3. **Naming & Structure Hygiene** — flags leftover default Figma names (`Rectangle 4`,
   `Frame 23`, `Group 12`, bare `Text`, etc.) and frames with multiple children that
   use manual absolute positioning instead of auto layout.

4. **Accessibility (Contrast)** — checks every text/background color pair against
   **both** WCAG 2.1 AA and AAA (not just a single pass/fail), using the bundled
   `scripts/contrast_ratio.py` for exact math. When a pair fails a threshold, the
   report includes the smallest color adjustment that would clear it.

The report skips any category with no findings rather than padding the output with
"no issues found" noise, and ends with a one-line count per category.

## Installation

### For yourself

Drop the `figma-design-audit/` directory into your personal skills folder:

```
~/.claude/skills/figma-design-audit/
```

Restart Claude Code (or run `/reload-plugins`) and confirm `figma-design-audit`
appears in your skills listing.

### Sharing with colleagues

Following the same clone-and-symlink pattern used for other internal skills:

```bash
git clone <this-repo-url>
ln -s "$(pwd)/<repo-name>/figma-design-audit" ~/.claude/skills/figma-design-audit
```

Then restart Claude Code or run `/reload-plugins`. Because it's a symlink rather than
a copy, a `git pull` in the cloned repo keeps everyone's copy current. Each person who
installs it still needs their own Figma connector enabled (see Prerequisites above) —
that's per-account and isn't something the clone/symlink step provides.

## Structure

```
figma-design-audit/
├── SKILL.md                    # Workflow: which Figma MCP tools to call, in what order,
│                                # and how to format the report. Read this for the "how".
├── references/
│   └── checklist.md            # The actual standards being checked. Edit this file to
│                                # tune thresholds, naming rules, etc. — not SKILL.md.
└── scripts/
    └── contrast_ratio.py       # WCAG contrast ratio calculator + minimal-fix suggester.
                                 # Used so contrast math is computed exactly, never eyeballed.
```
