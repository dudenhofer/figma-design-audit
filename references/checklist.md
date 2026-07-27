# Design Audit Checklist

Edit this file to tune the standards — `SKILL.md` just points here, it doesn't
duplicate the rules, so changes take effect immediately without touching the skill
definition.

## 1. Tokens / Variables

Standard: every fill, stroke, text style, corner radius, and effect should be bound to
a Figma variable or shared style — not a raw/hardcoded value — regardless of which
library that variable belongs to (we're checking internal consistency, not conformance
to one pinned design system).

How to check:
- From `get_design_context`, look at each node's fills/strokes/effects/corner-radius/
  typography properties.
- Cross-reference against `get_variable_defs` to see which values are bound to a
  variable vs. hardcoded.
- Flag any node using a raw hex color, raw px spacing/radius, or raw font size/line-
  height where a bound variable exists for that same value elsewhere in the file (a
  strong sign it should be tokenized) — and separately flag any raw value with no
  matching variable at all, since that may indicate a missing token.

## 2. Component / Instance Hygiene

Standard: repeated UI elements should be instances of a library component, not
detached copies or one-off hand-built duplicates.

How to check:
- From `get_design_context` / `get_metadata`, identify nodes of type `INSTANCE` vs.
  plain `FRAME`/`GROUP` — a node that looks like a component (button, badge, input,
  card) but has no `componentId` is likely detached or hand-built.
- If unsure whether a hand-built node duplicates an existing component, use
  `search_design_system` to check for a close match before flagging it.
- Flag detached instances and suspected duplicate-of-existing-component nodes
  separately, since the fix differs (re-attach vs. swap to the real component).

## 3. Naming & Structure Hygiene

Standard: no leftover default Figma names, and frames with multiple children use auto
layout rather than stray absolute positioning.

Default-name patterns to flag (case-sensitive, exact match unless noted):
- `^Rectangle \d+$`
- `^Frame \d+$`
- `^Group \d+$`
- `^Ellipse \d+$`
- `^Vector \d+$`
- `^Line \d+$`
- `^Component \d+$`
- `^Text( \d+)?$`
- `^Image \d+$`

Structure check: from `get_metadata`, flag any frame with 2+ children where
`layoutMode` is `NONE` (i.e. not auto layout) — this usually means children are
manually positioned and will break on content/size changes.

This is intentionally generic (no project-specific naming scheme is encoded here yet).
If a specific convention should be enforced later, add it as a new subsection here.

## 4. Accessibility (Contrast)

Standard: text should be legible against its background. Check every text node
against **both** WCAG 2.1 AA and AAA, and report both results rather than a single
pass/fail:

- AA: 4.5:1 normal text, 3:1 large text (≥18pt, or ≥14pt bold) and UI components
- AAA: 7:1 normal text, 4.5:1 large text

How to check:
1. From `get_design_context`, resolve each text node's effective fill color and the
   effective background color behind it (parent fill, or the frame's background).
2. Run `scripts/contrast_ratio.py <text_hex> <bg_hex> [--large]` to get the exact
   ratio and pass/fail for both AA and AAA.
3. If a pair fails AA, or passes AA but fails AAA, report both outcomes and include
   the script's suggested minimal color adjustment to clear the next threshold up
   (e.g. "passes AA (4.6:1); would need `#1A1A1A` instead of `#3D3D3D` to also clear
   AAA").
4. Use the screenshot from `get_screenshot` to sanity-check computed colors against
   what's visually rendered (gradients, opacity, overlays can make the "effective"
   background different from the raw fill value).
