#!/usr/bin/env python3
"""FIELD-0005 Nested Zones — spacing study A vs A2 (0.750 in).

Side-by-side fabrication SVGs at 16 × 20 in and 0.750 in architecture width:

    A  — canonical FIELD-0005 builder defaults
    A2 — refined inner proportions (wider inner box) so middle→inner
         horizontal green clearance matches outer→middle vertical clearance
         at ~36 mm, holding outer/middle geometry unchanged.

Exploratory study only; does not change the canonical builder defaults.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
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
    / "FIELD-0005_SpacingStudy_A_vs_A2"
)

FIELD_WIDTH_MM = 16.0 * INCH_MM
FIELD_HEIGHT_MM = 20.0 * INCH_MM
LINE_WIDTH_IN = 0.750
LINE_WIDTH_MM = LINE_WIDTH_IN * INCH_MM

# Middle-inner horizontal clear green ≈ outer-middle vertical at canonical A.
A2_INNER_WIDTH_MM = 135.0


@dataclass(frozen=True)
class StudyVariant:
    slug: str
    label: str
    build: Callable[[], object]


def fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def make_svg(spec, variant_label: str) -> str:
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
        f"16 × 20 in — {LINE_WIDTH_IN:g} in — {variant_label}"
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


def clearances(params: dict) -> tuple[float, float, float]:
    outer_middle_x = (
        (params["outer_width_mm"] - params["middle_width_mm"]) / 2.0
        - LINE_WIDTH_MM
    )
    outer_middle_y = (
        (params["outer_height_mm"] - params["middle_height_mm"]) / 2.0
        - LINE_WIDTH_MM
    )
    middle_inner_x = (
        (params["middle_width_mm"] - params["inner_width_mm"]) / 2.0
        - LINE_WIDTH_MM
    )
    return outer_middle_x, outer_middle_y, middle_inner_x


def build_a_canonical():
    return build_nested_zones_field(
        width_mm=FIELD_WIDTH_MM,
        height_mm=FIELD_HEIGHT_MM,
        line_width_mm=LINE_WIDTH_MM,
    )


def build_a2_refined():
    return build_nested_zones_field(
        width_mm=FIELD_WIDTH_MM,
        height_mm=FIELD_HEIGHT_MM,
        line_width_mm=LINE_WIDTH_MM,
        inner_width_mm=A2_INNER_WIDTH_MM,
    )


VARIANTS = (
    StudyVariant(
        slug="A_CANONICAL",
        label="A — Canonical spacing",
        build=build_a_canonical,
    ),
    StudyVariant(
        slug="A2_REFINED",
        label="A2 — Refined inner spacing",
        build=build_a2_refined,
    ),
)


def main() -> None:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)

    for variant in VARIANTS:
        spec = variant.build()
        svg_path = EXPORT_ROOT / (
            f"FIELD-0005_NestedZones_16x20_075in_"
            f"{variant.slug}.svg"
        )
        txt_path = EXPORT_ROOT / (
            f"FIELD-0005_NestedZones_16x20_075in_"
            f"{variant.slug}_PARAMS.txt"
        )

        svg_path.write_text(
            make_svg(spec, variant.label),
            encoding="utf-8",
        )

        params = spec.parameters
        ox, oy, mi = clearances(params)

        txt_path.write_text(
            f"""FIELD-0005 SPACING STUDY — A vs A2

Variant:
{variant.label}

Field:
{FIELD_WIDTH_MM:.3f} x {FIELD_HEIGHT_MM:.3f} mm
16 x 20 in

Architecture width:
{LINE_WIDTH_MM:.3f} mm
{LINE_WIDTH_IN:.3f} in

Outer:
{params['outer_width_mm']:.3f} x {params['outer_height_mm']:.3f} mm

Middle:
{params['middle_width_mm']:.3f} x {params['middle_height_mm']:.3f} mm

Inner:
{params['inner_width_mm']:.3f} x {params['inner_height_mm']:.3f} mm

Inner Y offset:
{params['inner_offset_y_mm']:.3f} mm

Approximate clear green spacing:

Outer -> Middle horizontal:
{ox:.3f} mm

Outer -> Middle vertical:
{oy:.3f} mm

Middle -> Inner horizontal:
{mi:.3f} mm

NOTE:
Exploratory fabrication study only.
Canonical FIELD-0005 builder defaults are unchanged.
""",
            encoding="utf-8",
        )

        print()
        print(variant.label)
        print(f"  outer-middle horizontal: {ox:.2f} mm")
        print(f"  outer-middle vertical:   {oy:.2f} mm")
        print(f"  middle-inner horizontal: {mi:.2f} mm")
        print(f"  wrote: {svg_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
