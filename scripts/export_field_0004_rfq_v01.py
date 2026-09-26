#!/usr/bin/env python3
"""Operational Worlds — FIELD-0004 Divergence RFQ v0.1.

Quote-ready fabrication geometry for four sizes:

    16 x 20 in  — 0.750 in member width
    18 x 24 in  — 0.750 in member width
    36 x 36 in  — 1.250 in member width
    40 x 40 in  — 1.250 in member width

Provisional relief height for all sizes:

    0.750 in / 19.05 mm

Geometry uses the resolved continuous-miter construction.
"""

from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from math import cos, radians, sin
from pathlib import Path


INCH_MM = 25.4

ROOT = Path(__file__).resolve().parents[1]

EXPORT_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_Fabrication_RFQ_v01"
)

ZIP_PATH = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_Fabrication_RFQ_v01.zip"
)


# ------------------------------------------------------------
# CANONICAL / FABRICATION PARAMETERS
# ------------------------------------------------------------

STEM_CENTERLINE_SEPARATION_MM = 2.500 * INCH_MM
BRANCH_ANGLE_DEG = 32.0
SPLIT_Y_MM = 0.0

RELIEF_HEIGHT_MM = 0.750 * INCH_MM

FIELD_COLOR = "#062D20"
ARCHITECTURE_COLOR = "#F2EBDD"


@dataclass(frozen=True)
class Panel:
    slug: str
    width_in: float
    height_in: float
    member_width_in: float

    @property
    def width_mm(self):
        return self.width_in * INCH_MM

    @property
    def height_mm(self):
        return self.height_in * INCH_MM

    @property
    def member_width_mm(self):
        return self.member_width_in * INCH_MM


PANELS = (
    Panel("16x20", 16.0, 20.0, 0.750),
    Panel("18x24", 18.0, 24.0, 0.750),
    Panel("36x36", 36.0, 36.0, 1.250),
    Panel("40x40", 40.0, 40.0, 1.250),
)


# ------------------------------------------------------------
# BASIC HELPERS
# ------------------------------------------------------------

def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def svg_point(x, y, width, height):
    return (
        x + width / 2.0,
        height / 2.0 - y,
    )


def polygon_string(points, width, height):
    out = []

    for x, y in points:
        sx, sy = svg_point(
            x, y, width, height
        )
        out.append(
            f"{fmt(sx)},{fmt(sy)}"
        )

    return " ".join(out)


def line_intersection(p1, d1, p2, d2):
    x1, y1 = p1
    dx1, dy1 = d1

    x2, y2 = p2
    dx2, dy2 = d2

    cross = dx1 * dy2 - dy1 * dx2

    if abs(cross) < 1e-9:
        raise ValueError(
            "Cannot intersect parallel lines."
        )

    rx = x2 - x1
    ry = y2 - y1

    t = (
        rx * dy2 - ry * dx2
    ) / cross

    return (
        x1 + t * dx1,
        y1 + t * dy1,
    )


# ------------------------------------------------------------
# CONTINUOUS MITERED MEMBER
# ------------------------------------------------------------

def build_side_polygon(
    *,
    stem_x,
    split_y,
    branch_top_x,
    branch_top_y,
    bottom_y,
    width_mm,
):
    half = width_mm / 2.0

    stem_dir = (0.0, 1.0)
    stem_normal = (-1.0, 0.0)

    branch_dx = branch_top_x - stem_x
    branch_dy = branch_top_y - split_y

    branch_length = (
        branch_dx ** 2
        + branch_dy ** 2
    ) ** 0.5

    if branch_length <= 0:
        raise ValueError(
            "Branch must have positive length."
        )

    branch_dir = (
        branch_dx / branch_length,
        branch_dy / branch_length,
    )

    branch_normal = (
        -branch_dir[1],
        branch_dir[0],
    )

    stem_left_bottom = (
        stem_x + stem_normal[0] * half,
        bottom_y,
    )

    stem_right_bottom = (
        stem_x - stem_normal[0] * half,
        bottom_y,
    )

    stem_left_split = (
        stem_x + stem_normal[0] * half,
        split_y,
    )

    stem_right_split = (
        stem_x - stem_normal[0] * half,
        split_y,
    )

    branch_left_split = (
        stem_x + branch_normal[0] * half,
        split_y + branch_normal[1] * half,
    )

    branch_right_split = (
        stem_x - branch_normal[0] * half,
        split_y - branch_normal[1] * half,
    )

    branch_left_top = (
        branch_top_x + branch_normal[0] * half,
        branch_top_y + branch_normal[1] * half,
    )

    branch_right_top = (
        branch_top_x - branch_normal[0] * half,
        branch_top_y - branch_normal[1] * half,
    )

    miter_left = line_intersection(
        stem_left_split,
        stem_dir,
        branch_left_split,
        branch_dir,
    )

    miter_right = line_intersection(
        stem_right_split,
        stem_dir,
        branch_right_split,
        branch_dir,
    )

    return (
        stem_left_bottom,
        miter_left,
        branch_left_top,
        branch_right_top,
        miter_right,
        stem_right_bottom,
    )


# ------------------------------------------------------------
# FIELD GEOMETRY
# ------------------------------------------------------------

def build_geometry(panel):
    width = panel.width_mm
    height = panel.height_mm

    bottom_y = -height / 2.0
    top_y = height / 2.0

    half_stem = (
        STEM_CENTERLINE_SEPARATION_MM
        / 2.0
    )

    left_stem_x = -half_stem
    right_stem_x = half_stem

    angle = radians(
        BRANCH_ANGLE_DEG
    )

    overshoot_y = (
        panel.member_width_mm * 3.0
    )

    branch_top_y = (
        top_y + overshoot_y
    )

    vertical_run = (
        branch_top_y - SPLIT_Y_MM
    )

    horizontal_run = (
        sin(angle)
        / cos(angle)
        * vertical_run
    )

    left_top_x = (
        left_stem_x - horizontal_run
    )

    right_top_x = (
        right_stem_x + horizontal_run
    )

    left = build_side_polygon(
        stem_x=left_stem_x,
        split_y=SPLIT_Y_MM,
        branch_top_x=left_top_x,
        branch_top_y=branch_top_y,
        bottom_y=bottom_y,
        width_mm=panel.member_width_mm,
    )

    right = build_side_polygon(
        stem_x=right_stem_x,
        split_y=SPLIT_Y_MM,
        branch_top_x=right_top_x,
        branch_top_y=branch_top_y,
        bottom_y=bottom_y,
        width_mm=panel.member_width_mm,
    )

    return left, right


# ------------------------------------------------------------
# PRODUCTION SVG
# ------------------------------------------------------------

def make_svg(panel):
    left, right = build_geometry(panel)

    left_points = polygon_string(
        left,
        panel.width_mm,
        panel.height_mm,
    )

    right_points = polygon_string(
        right,
        panel.width_mm,
        panel.height_mm,
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
 xmlns="http://www.w3.org/2000/svg"
 width="{fmt(panel.width_mm)}mm"
 height="{fmt(panel.height_mm)}mm"
 viewBox="0 0 {fmt(panel.width_mm)} {fmt(panel.height_mm)}">

<title>
Operational Worlds —
FIELD-0004 Divergence —
{panel.width_in:g} x {panel.height_in:g} in
</title>

<defs>
 <clipPath id="fieldClip">
  <rect
   x="0"
   y="0"
   width="{fmt(panel.width_mm)}"
   height="{fmt(panel.height_mm)}"/>
 </clipPath>
</defs>

<!-- PANEL / FIELD -->
<rect
 x="0"
 y="0"
 width="{fmt(panel.width_mm)}"
 height="{fmt(panel.height_mm)}"
 fill="{FIELD_COLOR}"/>

<!-- RAISED ARCHITECTURE -->
<g clip-path="url(#fieldClip)">
 <polygon
  points="{left_points}"
  fill="{ARCHITECTURE_COLOR}"/>
 <polygon
  points="{right_points}"
  fill="{ARCHITECTURE_COLOR}"/>
</g>

</svg>
'''


# ------------------------------------------------------------
# INDIVIDUAL FABRICATION SPEC
# ------------------------------------------------------------

def make_panel_spec(panel):
    return f"""OPERATIONAL WORLDS
FIELD-0004 — DIVERGENCE

FABRICATION RFQ v0.1
SIZE: {panel.width_in:g} x {panel.height_in:g} IN


OVERALL PANEL
=============

Width:
{panel.width_in:.3f} in
{panel.width_mm:.3f} mm

Height:
{panel.height_in:.3f} in
{panel.height_mm:.3f} mm


RAISED ARCHITECTURE
===================

Member width:
{panel.member_width_in:.3f} in
{panel.member_width_mm:.3f} mm

Provisional relief height:
0.750 in
{RELIEF_HEIGHT_MM:.3f} mm


FIELD-0004 GEOMETRY
===================

Stem centerline separation:
2.500 in
{STEM_CENTERLINE_SEPARATION_MM:.3f} mm

Branch angle:
{BRANCH_ANGLE_DEG:.3f} degrees

Split position:
Centered vertically

Architecture consists of two
continuous mitered members.

Members terminate flush at the
top and bottom field boundaries.


FINISH
======

FIELD:
Dark green, smooth matte sprayed finish.

ARCHITECTURE:
Warm white, smooth matte sprayed finish.

VISIBLE OUTER PANEL SIDES:
Continue dark-green field finish.

BACK:
May remain unfinished unless finishing
is required for dimensional stability.


FABRICATION QUALITY
===================

No exposed raw substrate on visible surfaces.

No visible fasteners from normal frontal viewing.

No visible adhesive squeeze-out.

No visible seams in raised architecture from
normal frontal viewing.

Edges should be clean and suitable for
gallery presentation.


IMPORTANT
=========

The 0.750 in relief height is a proposed
design dimension for quoting.

Fabricator may recommend an alternative
construction/material strategy that achieves
the same visual depth and appearance.
"""


# ------------------------------------------------------------
# MASTER RFQ
# ------------------------------------------------------------

def make_master_rfq():
    rows = []

    for p in PANELS:
        rows.append(
            f"{p.width_in:g} x {p.height_in:g} in"
            f" | member {p.member_width_in:.2f} in"
            f" | relief 0.75 in"
        )

    sizes = "\n".join(rows)

    return f"""OPERATIONAL WORLDS
FIELD-0004 — DIVERGENCE

FABRICATION REQUEST FOR QUOTE
RFQ v0.1


PROJECT
=======

FIELD-0004 Divergence is a wall-mounted
relief surface consisting of a flat field
with two raised architectural members.

The attached vector files define the
front-view geometry.


PLEASE QUOTE THESE FOUR SIZES
=============================

{sizes}


PLEASE PROVIDE TWO QUOTES PER SIZE
==================================

OPTION A
Fabrication only / unfinished.

OPTION B
Complete fabrication with professional
sprayed gallery-ready finish.


CONSTRUCTION
============

Please recommend a stable construction
method appropriate to each scale.

Possible methods may include CNC-cut
sheet material, built-up panel construction,
or another method the fabricator considers
more appropriate.

Material is intentionally not being locked
for this RFQ.

Priorities are:

- dimensional stability
- clean planar field
- crisp raised geometry
- clean miter junctions
- durable gallery-quality construction
- reasonable weight
- clean wall presentation


RELIEF
======

Proposed architecture relief:

0.750 in / 19.05 mm above field.

Please identify if another construction
depth would materially reduce cost,
weight, or fabrication difficulty while
maintaining a similar visual presence.


FINISH
======

Field:
deep dark green.

Architecture:
warm/off white.

Finish:
smooth matte sprayed finish.

The dark-green field color should continue
around the visible exterior sides of the
panel.

Back may remain unfinished unless sealing
is recommended for stability.

No exposed raw substrate should be visible
when installed.


SURFACE CHARACTER
=================

The desired object should read as a
precisely fabricated architectural relief,
not as hand-painted dimensional decoration.

Edges should remain clean.

Raised members should appear continuous.

The central transition between vertical
stem and diagonal branch should have no
visible gap, overlap, or seam.


INSTALLATION
============

Please recommend concealed wall-mounting
hardware appropriate to the finished weight.

Please identify:

- estimated finished weight
- recommended mounting system
- wall clearance, if any


QUOTE REQUEST
=============

For each size please include:

- fabrication cost unfinished
- fabrication + finish cost
- proposed material/construction
- estimated finished weight
- lead time
- mounting recommendation
- shipping/delivery cost if applicable


FILES
=====

Each size folder contains:

- production-scale SVG
- dimensional/specification TXT file

All SVG dimensions are expressed in
millimetres and contain closed architectural
polygons.


DESIGN STATUS
=============

FIELD-0004 geometry:
LOCKED FOR RFQ

Member widths:
LOCKED FOR RFQ

16 x 20:
0.750 in

18 x 24:
0.750 in

36 x 36:
1.250 in

40 x 40:
1.250 in

Relief height:
PROVISIONAL — 0.750 in

Material/construction:
FABRICATOR RECOMMENDATION REQUESTED
"""


# ------------------------------------------------------------
# README
# ------------------------------------------------------------

def make_readme():
    return """OPERATIONAL WORLDS
FIELD-0004 DIVERGENCE
FABRICATION RFQ v0.1

START HERE:

    00_MASTER_RFQ.txt

Folders:

    16x20/
    18x24/
    36x36/
    40x40/

Each folder contains the production-scale
SVG and the corresponding fabrication
specification.

SVG geometry is in millimetres.

Do not scale files when importing.
"""


# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------

def main():
    if EXPORT_ROOT.exists():
        shutil.rmtree(EXPORT_ROOT)

    EXPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    (EXPORT_ROOT / "00_MASTER_RFQ.txt").write_text(
        make_master_rfq(),
        encoding="utf-8",
    )

    (EXPORT_ROOT / "README.txt").write_text(
        make_readme(),
        encoding="utf-8",
    )

    for panel in PANELS:
        folder = EXPORT_ROOT / panel.slug

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        prefix = (
            "FIELD-0004_Divergence_"
            f"{panel.slug}_RFQ_v01"
        )

        svg = folder / f"{prefix}.svg"

        spec = (
            folder
            / f"{prefix}_SPEC.txt"
        )

        svg.write_text(
            make_svg(panel),
            encoding="utf-8",
        )

        spec.write_text(
            make_panel_spec(panel),
            encoding="utf-8",
        )

        print(
            f"{panel.slug}: "
            f"{panel.member_width_in:.2f} in member"
        )

        print(
            f"  {svg.relative_to(ROOT)}"
        )

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(
        ZIP_PATH,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:

        for path in sorted(
            EXPORT_ROOT.rglob("*")
        ):
            if path.is_file():
                zf.write(
                    path,
                    path.relative_to(
                        EXPORT_ROOT.parent
                    ),
                )

    print()
    print("RFQ package:")
    print(
        EXPORT_ROOT.relative_to(ROOT)
    )

    print()
    print("ZIP:")
    print(
        ZIP_PATH.relative_to(ROOT)
    )


if __name__ == "__main__":
    main()
