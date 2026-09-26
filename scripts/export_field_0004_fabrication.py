#!/usr/bin/env python3
"""Export FIELD-0004 Divergence fabrication quote drawings.

These drawings are derived directly from the canonical
owde_addon.core.field_builders.build_divergence_field specification.

Fabrication v0.1:

- canonical clean FIELD-0004 geometry
- 12.7 mm architecture width
- 63.5 mm stem width
- 32 degree branch angle
- centered split
- 19.05 mm proposed relief height
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from owde_addon.core.field_builders import (
    INCH_MM,
    build_divergence_field,
)

EXPORT_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_v01"
)

LINE_WIDTH_MM = 0.50 * INCH_MM
STEM_WIDTH_MM = 2.50 * INCH_MM
BRANCH_ANGLE_DEG = 32.0
SPLIT_Y_MM = 0.0
ARCHITECTURE_HEIGHT_MM = 0.75 * INCH_MM


@dataclass(frozen=True)
class FabricationSize:
    slug: str
    width_in: float
    height_in: float

    @property
    def width_mm(self) -> float:
        return self.width_in * INCH_MM

    @property
    def height_mm(self) -> float:
        return self.height_in * INCH_MM


SIZES = (
    FabricationSize("16x20", 16.0, 20.0),
    FabricationSize("18x24", 18.0, 24.0),
    FabricationSize("36x36", 36.0, 36.0),
    FabricationSize("40x40", 40.0, 40.0),
)


def fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def svg_for(size: FabricationSize) -> str:
    spec = build_divergence_field(
        width_mm=size.width_mm,
        height_mm=size.height_mm,
        line_width_mm=LINE_WIDTH_MM,
        split_y_mm=SPLIT_Y_MM,
        stem_width_mm=STEM_WIDTH_MM,
        branch_angle_deg=BRANCH_ANGLE_DEG,
    )

    width = spec.width_mm
    height = spec.height_mm

    def sx(x: float) -> float:
        return x + width / 2.0

    def sy(y: float) -> float:
        return height / 2.0 - y

    clip_id = f"field-clip-{size.slug}"

    line_markup = "\n".join(
        (
            f'  <line x1="{fmt(sx(line.x1))}" '
            f'y1="{fmt(sy(line.y1))}" '
            f'x2="{fmt(sx(line.x2))}" '
            f'y2="{fmt(sy(line.y2))}" '
            f'stroke="#F2EBDD" '
            f'stroke-width="{fmt(line.width_mm)}" '
            f'stroke-linecap="butt" '
            f'stroke-linejoin="miter" />'
        )
        for line in spec.lines
    )

    title = escape(
        f"FIELD-0004 Divergence — {size.width_in:g} × "
        f"{size.height_in:g} in"
    )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{fmt(width)}mm" '
        f'height="{fmt(height)}mm" '
        f'viewBox="0 0 {fmt(width)} {fmt(height)}">\n'
        f"  <title>{title}</title>\n"
        f"\n"
        f"  <defs>\n"
        f'    <clipPath id="{clip_id}">\n'
        f'      <rect x="0" y="0" width="{fmt(width)}" '
        f'height="{fmt(height)}" />\n'
        f"    </clipPath>\n"
        f"  </defs>\n"
        f"\n"
        f'  <rect x="0" y="0" width="{fmt(width)}" '
        f'height="{fmt(height)}" fill="#062D20" />\n'
        f"\n"
        f'  <g clip-path="url(#{clip_id})">\n'
        f"{line_markup}\n"
        f"  </g>\n"
        f"</svg>\n"
    )


def spec_text(size: FabricationSize) -> str:
    spec = build_divergence_field(
        width_mm=size.width_mm,
        height_mm=size.height_mm,
        line_width_mm=LINE_WIDTH_MM,
        split_y_mm=SPLIT_Y_MM,
        stem_width_mm=STEM_WIDTH_MM,
        branch_angle_deg=BRANCH_ANGLE_DEG,
    )

    line_rows = []
    for i, line in enumerate(spec.lines, start=1):
        line_rows.append(
            f"  {i}: "
            f"({line.x1:.3f}, {line.y1:.3f}) -> "
            f"({line.x2:.3f}, {line.y2:.3f}), "
            f"width={line.width_mm:.3f} mm"
        )

    return f"""FIELD-0004 DIVERGENCE
FABRICATION QUOTE SPECIFICATION v0.1

FIELD
-----
Overall size:
  {size.width_in:g} × {size.height_in:g} in
  {size.width_mm:.3f} × {size.height_mm:.3f} mm

Architecture:
  FIELD-0004 Divergence
  Edge character: CLEAN

CANONICAL OPERATIONAL PARAMETERS
--------------------------------
Architecture width:
  {LINE_WIDTH_MM:.3f} mm
  {LINE_WIDTH_MM / INCH_MM:.3f} in

Stem width:
  {STEM_WIDTH_MM:.3f} mm
  {STEM_WIDTH_MM / INCH_MM:.3f} in

Split Y:
  {SPLIT_Y_MM:.3f} mm

Branch angle:
  {BRANCH_ANGLE_DEG:.3f} degrees

PROPOSED FABRICATION PARAMETER
------------------------------
Raised architecture height:
  {ARCHITECTURE_HEIGHT_MM:.3f} mm
  {ARCHITECTURE_HEIGHT_MM / INCH_MM:.3f} in

FINISH
------
Field:
  Dark green, smooth matte sprayed finish.
  Finish continues across top field and all four exterior sides.

Raised architecture:
  Warm white, smooth matte sprayed finish.

Back:
  May remain unfinished unless required for dimensional stability.
  Keep flat and suitable for mounting.

Visible surfaces:
  No exposed raw substrate, visible fasteners,
  adhesive squeeze-out, or unfinished seams
  when viewed from front or sides.

USE
---
Surface should tolerate repeated placement and manipulation
of Operational Worlds physical primitives.

CONSTRUCTION QUOTE
------------------
Please quote separately:

A. Raw / unfinished fabrication.
B. Fabrication plus professional sprayed finish.

Please also identify recommended substrate/material and
construction method for:

1. economical prototype construction.
2. durable gallery-quality construction.

CANONICAL CENTERLINE GEOMETRY
-----------------------------
Coordinates are millimetres relative to field center.
+X = right
+Y = top

{chr(10).join(line_rows)}

NOTE
----
Geometry is generated directly from the canonical
Operational Worlds FIELD-0004 builder.

The architecture is clipped at the physical field boundary.
The branch centerlines intentionally overshoot the field so
the thick diagonal architecture terminates flush after clipping.

The 36 × 36 and 40 × 40 versions are NOT stretch versions
of the 16 × 20 field. They instantiate the same operational
parameters within different field boundaries.
"""


def main() -> None:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)

    for size in SIZES:
        folder = EXPORT_ROOT / size.slug
        folder.mkdir(parents=True, exist_ok=True)

        prefix = (
            f"FIELD-0004_Divergence_"
            f"{size.slug}_FAB_v01"
        )

        svg_path = folder / f"{prefix}.svg"
        txt_path = folder / f"{prefix}_SPEC.txt"

        svg_path.write_text(svg_for(size), encoding="utf-8")
        txt_path.write_text(spec_text(size), encoding="utf-8")

        print(f"wrote {svg_path.relative_to(ROOT)}")
        print(f"wrote {txt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
