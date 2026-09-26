#!/usr/bin/env python3
"""FIELD-0005 Nested Zones fabrication line-width study.

Generates 16 x 20 SVG comparisons at:
    0.500 in
    0.625 in
    0.750 in

Uses the canonical FIELD-0005 builder and changes only line width.
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from owde_addon.core.field_builders import (
    INCH_MM,
    build_nested_zones_field,
)

EXPORT_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0005_LineWidthStudy"
)

FIELD_WIDTH_MM = 16.0 * INCH_MM
FIELD_HEIGHT_MM = 20.0 * INCH_MM

WIDTHS = (
    ("050in", 0.500),
    ("0625in", 0.625),
    ("075in", 0.750),
)


def fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def make_svg(width_in: float) -> str:
    line_width_mm = width_in * INCH_MM

    spec = build_nested_zones_field(
        width_mm=FIELD_WIDTH_MM,
        height_mm=FIELD_HEIGHT_MM,
        line_width_mm=line_width_mm,
    )

    width = spec.width_mm
    height = spec.height_mm

    def sx(x: float) -> float:
        return x + width / 2.0

    def sy(y: float) -> float:
        return height / 2.0 - y

    lines = []

    for line in spec.lines:
        lines.append(
            f'''    <line
        x1="{fmt(sx(line.x1))}"
        y1="{fmt(sy(line.y1))}"
        x2="{fmt(sx(line.x2))}"
        y2="{fmt(sy(line.y2))}"
        stroke="#F2EBDD"
        stroke-width="{fmt(line.width_mm)}"
        stroke-linecap="square"
        stroke-linejoin="miter"
    />'''
        )

    title = escape(
        f"FIELD-0005 Nested Zones — "
        f"16 × 20 in — {width_in:g} in architecture"
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{fmt(width)}mm"
     height="{fmt(height)}mm"
     viewBox="0 0 {fmt(width)} {fmt(height)}">

  <title>{title}</title>

  <defs>
    <clipPath id="field-clip">
      <rect
        x="0"
        y="0"
        width="{fmt(width)}"
        height="{fmt(height)}"
      />
    </clipPath>
  </defs>

  <rect
    x="0"
    y="0"
    width="{fmt(width)}"
    height="{fmt(height)}"
    fill="#062D20"
  />

  <g clip-path="url(#field-clip)">
{chr(10).join(lines)}
  </g>

</svg>
'''


def main() -> None:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)

    for slug, width_in in WIDTHS:
        width_mm = width_in * INCH_MM

        path = EXPORT_ROOT / (
            f"FIELD-0005_NestedZones_16x20_"
            f"WIDTH-{slug}.svg"
        )

        path.write_text(
            make_svg(width_in),
            encoding="utf-8",
        )

        print(
            f"{width_in:.3f} in / "
            f"{width_mm:.3f} mm -> "
            f"{path.relative_to(ROOT)}"
        )


if __name__ == "__main__":
    main()
