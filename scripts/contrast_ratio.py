#!/usr/bin/env python3
"""WCAG 2.1 contrast ratio calculator and minimal-fix suggester.

Usage:
    python3 contrast_ratio.py <text_hex> <bg_hex> [--large]

Prints a JSON object with the ratio, AA/AAA pass/fail, and a suggested
minimal-adjustment hex for the text color if it fails a threshold.
"""
import sys
import json

AA_NORMAL = 4.5
AA_LARGE = 3.0
AAA_NORMAL = 7.0
AAA_LARGE = 4.5


def parse_hex(hex_str):
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_str}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def relative_luminance(rgb):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a, hex_b):
    la = relative_luminance(parse_hex(hex_a))
    lb = relative_luminance(parse_hex(hex_b))
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def rgb_to_hsl(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return h, s, l


def hsl_to_rgb(h, s, l):
    if s == 0:
        v = l * 255
        return (v, v, v)

    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1 / 3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1 / 3)
    return (r * 255, g * 255, b * 255)


def suggest_fix(text_hex, bg_hex, target_ratio, steps=200):
    """Nudge the text color's lightness toward black or white (whichever
    direction increases contrast against bg) until target_ratio is met.
    Returns the adjusted hex, or None if unreachable within [0,1] lightness.
    """
    h, s, l = rgb_to_hsl(parse_hex(text_hex))
    bg_luminance = relative_luminance(parse_hex(bg_hex))
    # Darken toward black if bg is light, lighten toward white if bg is dark —
    # whichever direction increases contrast against the background.
    direction = -1 if bg_luminance > 0.5 else 1
    target_extreme = 1.0 if direction > 0 else 0.0
    for i in range(1, steps + 1):
        new_l = l + (target_extreme - l) * (i / steps)
        candidate_rgb = hsl_to_rgb(h, s, new_l)
        candidate_hex = to_hex(candidate_rgb)
        if contrast_ratio(candidate_hex, bg_hex) >= target_ratio:
            return candidate_hex
    return None


def evaluate(text_hex, bg_hex, is_large_text=False):
    ratio = contrast_ratio(text_hex, bg_hex)
    aa_threshold = AA_LARGE if is_large_text else AA_NORMAL
    aaa_threshold = AAA_LARGE if is_large_text else AAA_NORMAL

    result = {
        "text": text_hex,
        "background": bg_hex,
        "is_large_text": is_large_text,
        "ratio": round(ratio, 2),
        "aa_threshold": aa_threshold,
        "aa_pass": ratio >= aa_threshold,
        "aaa_threshold": aaa_threshold,
        "aaa_pass": ratio >= aaa_threshold,
    }

    if not result["aa_pass"]:
        result["suggested_fix_for_aa"] = suggest_fix(text_hex, bg_hex, aa_threshold)
    if not result["aaa_pass"]:
        result["suggested_fix_for_aaa"] = suggest_fix(text_hex, bg_hex, aaa_threshold)

    return result


def main():
    args = sys.argv[1:]
    is_large = "--large" in args
    args = [a for a in args if a != "--large"]

    if len(args) != 2:
        print(
            "Usage: python3 contrast_ratio.py <text_hex> <bg_hex> [--large]",
            file=sys.stderr,
        )
        sys.exit(1)

    text_hex, bg_hex = args
    print(json.dumps(evaluate(text_hex, bg_hex, is_large), indent=2))


if __name__ == "__main__":
    main()
