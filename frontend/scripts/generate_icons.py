#!/usr/bin/env python3
"""Generate the Anchor PWA icons: a white anchor (⚓) on a deep slate background.

Renders the Unicode ANCHOR glyph (U+2693) in a monochrome system font, white,
centered, supersampled for crisp edges. Falls back to drawing the anchor
geometrically if no font on this machine has a usable monochrome glyph.

Run:  backend/.venv/bin/python frontend/scripts/generate_icons.py
(needs Pillow; fonttools only for the optional cmap probe)
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

BG = (30, 58, 95)        # #1E3A5F — deep slate blue
FG = (255, 255, 255)     # white anchor
ANCHOR = "⚓"
SS = 4                   # supersample factor for antialiasing
OUT = os.path.join(os.path.dirname(__file__), "..", "public")

# Monochrome font candidates that may carry U+2693, best first.
FONT_CANDIDATES = [
    "/System/Library/Fonts/Apple Symbols.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]


def find_font() -> str | None:
    """Return a font path whose U+2693 glyph actually inks (not .notdef/tofu)."""
    for path in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            font = ImageFont.truetype(path, 200)
        except Exception:
            continue
        anchor_bbox = font.getmask(ANCHOR).getbbox()
        # Compare against a guaranteed-absent glyph: if they ink identically the
        # font is falling back to .notdef for both -> no real anchor glyph.
        missing_bbox = font.getmask("").getbbox()
        if anchor_bbox and anchor_bbox != missing_bbox:
            return path
    return None


def _ink_crop(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def glyph_layer(font_path: str, target_px: int) -> Image.Image:
    """A tight, transparent RGBA layer of the white anchor ~target_px tall/wide."""
    # Render big, then scale the tight-cropped glyph to the target.
    font = ImageFont.truetype(font_path, 1000)
    big = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.text((700, 700), ANCHOR, font=font, fill=FG + (255,), anchor="mm")
    glyph = _ink_crop(big)
    scale = target_px / max(glyph.width, glyph.height)
    return glyph.resize(
        (max(1, round(glyph.width * scale)), max(1, round(glyph.height * scale))),
        Image.LANCZOS,
    )


def geometric_layer(target_px: int) -> Image.Image:
    """Fallback: draw a clean geometric anchor, white, ~target_px tall."""
    S = target_px
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = S / 2
    t = max(2, S * 0.07)              # stroke thickness
    top, bot = S * 0.06, S * 0.94
    ring_r = S * 0.11
    # Ring (top eye)
    d.ellipse([cx - ring_r, top, cx + ring_r, top + 2 * ring_r],
              outline=FG, width=int(t))
    # Shank (vertical)
    d.line([(cx, top + 2 * ring_r), (cx, bot)], fill=FG, width=int(t))
    # Stock (crossbar)
    arm = S * 0.20
    sy = top + 2 * ring_r + S * 0.06
    d.line([(cx - arm, sy), (cx + arm, sy)], fill=FG, width=int(t))
    # Arms / flukes (bottom curve) via an arc, plus fluke barbs
    aw = S * 0.34
    d.arc([cx - aw, bot - 2 * aw, cx + aw, bot], start=20, end=160,
          fill=FG, width=int(t))
    for sx in (cx - aw * 0.96, cx + aw * 0.96):
        d.line([(sx, bot - aw * 0.34), (sx + (S * 0.07 if sx < cx else -S * 0.07),
                bot - aw * 0.34 - S * 0.10)], fill=FG, width=int(t))
    return _ink_crop(img)


def make_icon(size: int, symbol_frac: float, font_path: str | None,
              out_name: str, opaque: bool = True) -> None:
    canvas = size * SS
    bg_alpha = 255 if opaque else 255  # icons are opaque slate either way
    base = Image.new("RGBA", (canvas, canvas), BG + (bg_alpha,))
    target = int(canvas * symbol_frac)
    layer = glyph_layer(font_path, target) if font_path else geometric_layer(target)
    x = (canvas - layer.width) // 2
    y = (canvas - layer.height) // 2
    base.alpha_composite(layer, (x, y))
    final = base.resize((size, size), Image.LANCZOS).convert("RGB")
    final.save(os.path.join(OUT, out_name), "PNG")
    print(f"  wrote {out_name} ({size}x{size}, symbol~{int(symbol_frac*100)}%)")


def main() -> int:
    font_path = find_font()
    print(f"glyph source: {font_path or 'GEOMETRIC FALLBACK (no monochrome U+2693 font found)'}")
    # Maskable: symbol ~57% (well inside the 80% safe zone launchers crop to).
    make_icon(192, 0.57, font_path, "icon-192.png")
    make_icon(512, 0.57, font_path, "icon-512.png")
    # Standard ("any"): ~10% padding -> symbol ~80%.
    make_icon(192, 0.80, font_path, "icon-192-any.png")
    make_icon(512, 0.80, font_path, "icon-512-any.png")
    # Apple touch icon: a touch more breathing room (iOS rounds the corners).
    make_icon(180, 0.74, font_path, "apple-touch-icon.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
