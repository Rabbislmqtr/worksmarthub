#!/usr/bin/env python3
"""Generate social share cards and inject Open Graph / Twitter meta tags.

Run from the repository root:

    python scripts/generate-social-meta.py

For every HTML page it:
  1. renders a 1200x630 PNG card into og/ using the Studio token palette
     (cream paper, dark ink band, serif display headline, green accent)
  2. rewrites the page's Open Graph + Twitter Card tags between the
     <!-- social:start --> / <!-- social:end --> markers

The script is idempotent: re-running it regenerates the images and replaces the
managed block. Any loose og:*/twitter:* tags outside the markers are removed
first, so a page can never end up with duplicate conflicting tags.

Add a page, re-run the script, done.
"""

from __future__ import annotations

import html
import math
import pathlib
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: python -m pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OG_DIR = ROOT / "og"

ORIGIN = "https://worksmarthub.rabbilslmqtr.workers.dev"
SITE_NAME = "WorkSmart Hub"
SITE_TAGLINE = "Practical tools for small business"

CARD_W, CARD_H = 1200, 630
MARGIN = 76
BAND_TOP = 520
BRAND_BASELINE_Y = 64
BRAND_MARK = 52
RULE_Y = 168
# The headline is bottom-anchored so the card never opens a dead gap above the band.
BLOCK_TOP = 236
BLOCK_BOTTOM = BAND_TOP - 52

START, END = "<!-- social:start -->", "<!-- social:end -->"


# ---------------------------------------------------------------- colour ----

def oklch(lightness: float, chroma: float, hue_deg: float) -> tuple[int, int, int]:
    """Convert an OKLCH triple (L 0-1, C, H degrees) to an sRGB 8-bit tuple."""
    hue = math.radians(hue_deg)
    a, b = chroma * math.cos(hue), chroma * math.sin(hue)

    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3

    channels = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

    out = []
    for c in channels:
        c = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        out.append(max(0, min(255, round(c * 255))))
    return tuple(out)  # type: ignore[return-value]


PAPER = oklch(0.96, 0.018, 92)
PAPER_DEEP = oklch(0.91, 0.026, 92)
INK = oklch(0.23, 0.035, 242)
INK_FAINT = oklch(0.57, 0.028, 242)
ACCENT = oklch(0.61, 0.145, 159)
ACCENT_DEEP = oklch(0.43, 0.11, 158)
ACCENT_LIGHT = oklch(0.75, 0.13, 158)
RULE = oklch(0.80, 0.025, 92)
WHITE = oklch(0.99, 0.006, 92)


# ----------------------------------------------------------------- fonts ----

FONT_CANDIDATES = {
    "display_bold": [
        "C:/Windows/Fonts/georgiab.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    ],
    "display": [
        "C:/Windows/Fonts/georgia.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "body": [
        "C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "body_bold": [
        "C:/Windows/Fonts/segoeuib.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mono": [
        "C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
}


def load_font(role: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES[role]:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit(f"No usable font found for role '{role}'. Tried: {FONT_CANDIDATES[role]}")


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Greedy word wrap; a single oversized word is hard-broken."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            trial = f"{current} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


# ----------------------------------------------------------------- cards ----

LABELS = {
    "index": "Free small business tools",
    "tools": "Tool library",
    "guides": "Guide library",
    "templates": "Templates",
    "ai-assistant": "Tool finder",
    "about": "About",
    "contact": "Contact",
    "editorial-standards": "Editorial standards",
    "privacy-policy": "Policy · privacy",
    "terms": "Policy · terms",
    "cookie-policy": "Policy · cookies",
    "disclaimer": "Policy · disclaimer",
}

EYEBROW_RE = re.compile(r'<span class="eyebrow">(.*?)</span>', re.S)


def card_label(page: pathlib.Path, source: str) -> str:
    segments = page.relative_to(ROOT).as_posix().split("/")
    if len(segments) == 1:
        return LABELS["index"]
    if len(segments) == 2:  # a section index, e.g. tools/index.html
        return LABELS.get(segments[0], SITE_TAGLINE)
    if segments[0] == "tools":
        return "Free calculator"
    if segments[0] == "guides":
        found = EYEBROW_RE.search(source)  # e.g. "Marketing · 6 min read"
        return re.sub(r"\s+", " ", found.group(1)).strip() if found else "Guide"
    return LABELS.get(segments[0], SITE_TAGLINE)


def render_card(headline: str, label: str) -> Image.Image:
    img = Image.new("RGB", (CARD_W, CARD_H), PAPER)
    draw = ImageDraw.Draw(img)

    available = CARD_W - 2 * MARGIN

    # Brand row ---------------------------------------------------------
    draw.rounded_rectangle(
        (MARGIN, BRAND_BASELINE_Y, MARGIN + BRAND_MARK, BRAND_BASELINE_Y + BRAND_MARK),
        radius=13, fill=ACCENT,
    )
    mark_font = load_font("display_bold", 30)
    draw.text(
        (MARGIN + BRAND_MARK / 2, BRAND_BASELINE_Y + BRAND_MARK / 2),
        "W", font=mark_font, fill=WHITE, anchor="mm",  # anchor="mm" is the ink centre
    )

    name_font = load_font("display_bold", 34)
    draw.text(
        (MARGIN + BRAND_MARK + 20, BRAND_BASELINE_Y + BRAND_MARK / 2),
        SITE_NAME, font=name_font, fill=INK, anchor="lm",
    )

    label_font = load_font("mono", 21)
    draw.text(
        (CARD_W - MARGIN, BRAND_BASELINE_Y + BRAND_MARK / 2),
        label.upper(), font=label_font, fill=ACCENT_DEEP, anchor="rm",
    )

    draw.line((MARGIN, RULE_Y, CARD_W - MARGIN, RULE_Y), fill=RULE, width=2)

    # Headline ----------------------------------------------------------
    # Largest display size whose wrapped block still fits the available band.
    size = 112
    while size > 40:
        font = load_font("display_bold", size)
        lines = wrap(draw, headline, font, available)
        line_h = round(size * 1.16)
        if len(lines) * line_h <= (BLOCK_BOTTOM - BLOCK_TOP) and all(
            draw.textlength(line, font=font) <= available for line in lines
        ):
            break
        size -= 2
    line_h = round(size * 1.16)

    y = BLOCK_BOTTOM - len(lines) * line_h
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=INK)
        y += line_h

    # Footer band -------------------------------------------------------
    draw.rectangle((0, BAND_TOP, CARD_W, CARD_H), fill=INK)

    tagline_font = load_font("body", 25)
    draw.text(
        (MARGIN, BAND_TOP + 55), SITE_TAGLINE, font=tagline_font, fill=PAPER, anchor="lm",
    )
    domain_font = load_font("mono", 23)
    draw.text(
        (CARD_W - MARGIN, BAND_TOP + 55),
        ORIGIN.replace("https://", ""), font=domain_font, fill=ACCENT_LIGHT, anchor="rm",
    )
    draw.line((MARGIN, BAND_TOP + 26, CARD_W - MARGIN, BAND_TOP + 26), fill=PAPER_DEEP, width=1)

    return img


# ------------------------------------------------------------------ meta ----

TAG_RE = re.compile(r'[ \t]*<meta (?:property="og:[^"]*"|name="twitter:[^"]*")[^>]*>\s*')
TITLE_SUFFIX = re.compile(r"\s*\|\s*" + re.escape(SITE_NAME) + r"\s*$")


def build_block(title, description, og_type, url, image_url, alt) -> str:
    esc = lambda v: html.escape(v, quote=True)
    lines = [
        START,
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:type" content="{esc(og_type)}">',
        f'<meta property="og:url" content="{esc(url)}">',
        f'<meta property="og:image" content="{esc(image_url)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(alt)}">',
        '<meta property="og:site_name" content="WorkSmart Hub">',
        '<meta property="og:locale" content="en_US">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
        f'<meta name="twitter:image" content="{esc(image_url)}">',
        f'<meta name="twitter:image:alt" content="{esc(alt)}">',
        END,
    ]
    return "".join(lines)


def main() -> int:
    OG_DIR.mkdir(exist_ok=True)
    pages = sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in {".git", ".freebuff", "og", "scripts"} for part in p.parts)
    )

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        source = page.read_text(encoding="utf-8")

        title_match = re.search(r"<title>(.*?)</title>", source, re.S)
        if not title_match:
            print(f"  skip  {rel}  (no <title>)")
            continue
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()

        desc_match = re.search(r'<meta name="description" content="(.*?)"', source, re.S)
        if not desc_match:
            print(f"  skip  {rel}  (no meta description)")
            continue
        description = html.unescape(re.sub(r"\s+", " ", desc_match.group(1)).strip())

        if rel == "index.html":
            # The homepage keeps its own punchier share description.
            description = "Calculate, plan, price and make better business decisions with practical free tools."

        canon_match = re.search(r'<link rel="canonical" href="(.*?)"', source)
        url = canon_match.group(1) if canon_match else f"{ORIGIN}/{'' if rel == 'index.html' else rel.replace('index.html', '')}"

        slug = "home" if rel == "index.html" else rel.replace("/index.html", "").replace("/", "-").replace(".html", "")
        image_path = OG_DIR / f"{slug}.png"
        image_url = f"{ORIGIN}/og/{slug}.png"

        headline = TITLE_SUFFIX.sub("", title)
        render_card(headline, card_label(page, source)).save(image_path, "PNG", optimize=True)

        og_type = "article" if rel.startswith("guides/") and rel != "guides/index.html" else "website"
        block = build_block(title, description, og_type, url, image_url, headline)

        stripped = TAG_RE.sub("", source)
        region = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)

        if region.search(stripped):
            updated = region.sub(block, stripped, count=1)
        elif canon_match and '<link rel="canonical"' in stripped:
            updated = stripped.replace(
                f'<link rel="canonical" href="{canon_match.group(1)}">',
                f'<link rel="canonical" href="{canon_match.group(1)}">{block}',
                1,
            )
        else:
            print(f"  skip  {rel}  (no canonical anchor)")
            continue

        if updated != source:
            page.write_text(updated, encoding="utf-8")
        print(f"  ok    {rel:52} og/{slug}.png  [{og_type}]")

    print(f"\n{len(pages)} pages processed · cards written to og/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
