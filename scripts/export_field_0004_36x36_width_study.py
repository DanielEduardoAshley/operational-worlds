#!/usr/bin/env python3
"""FIELD-0004 Divergence — 36x36 final width study.

Controlled comparison:

    1.000 in / 25.40 mm
    1.250 in / 31.75 mm

Everything else is held constant.

Uses the resolved continuous-miter geometry from
FIELD-0004 Fabrication v0.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from pathlib import Path


# ============================================================
# CONSTANTS
# ============================================================

INCH_MM = 25.4

ROOT = Path(__file__).resolve().parents[1]

EXPORT_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_36x36_FinalWidthStudy"
)


# ============================================================
# FIELD
# ============================================================

FIELD_WIDTH_MM = 36.0 * INCH_MM
FIELD_HEIGHT_MM = 36.0 * INCH_MM


# ============================================================
# FIELD-0004 PARAMETERS — LOCKED
# ============================================================

STEM_WIDTH_MM = 2.500 * INCH_MM
BRANCH_ANGLE_DEG = 32.0
SPLIT_Y_MM = 0.0


# ============================================================
# PROPOSED RELIEF HEIGHT — LOCKED
# ============================================================

ARCHITECTURE_HEIGHT_MM = 0.750 * INCH_MM


# ============================================================
# PREVIEW COLORS
# ============================================================

FIELD_COLOR = "#062D20"
ARCHITECTURE_COLOR = "#F2EBDD"


# ============================================================
# WIDTH VARIANTS
# ============================================================

@dataclass(frozen=True)
class Variant:
    slug: str
    width_in: float

    @property
    def width_mm(self) -> float:
        return self.width_in * INCH_MM


VARIANTS = (

    Variant(
        slug="100in",
        width_in=1.000,
    ),

    Variant(
        slug="125in",
        width_in=1.250,
    ),
)


# ============================================================
# HELPERS
# ============================================================

def fmt(value: float) -> str:
    return (
        f"{value:.4f}"
        .rstrip("0")
        .rstrip(".")
    )


def svg_point(x, y):

    return (
        x + FIELD_WIDTH_MM / 2.0,
        FIELD_HEIGHT_MM / 2.0 - y,
    )


def polygon_string(points):

    result = []

    for x, y in points:

        sx, sy = svg_point(x, y)

        result.append(
            f"{fmt(sx)},{fmt(sy)}"
        )

    return " ".join(result)


# ============================================================
# LINE INTERSECTION
# ============================================================

def line_intersection(
    p1,
    d1,
    p2,
    d2,
):

    x1, y1 = p1
    dx1, dy1 = d1

    x2, y2 = p2
    dx2, dy2 = d2

    cross = (
        dx1 * dy2
        - dy1 * dx2
    )

    if abs(cross) < 1e-9:
        raise ValueError(
            "cannot intersect parallel lines"
        )

    rx = x2 - x1
    ry = y2 - y1

    t = (
        rx * dy2
        - ry * dx2
    ) / cross

    return (
        x1 + t * dx1,
        y1 + t * dy1,
    )


# ============================================================
# CONTINUOUS MITERED MEMBER
# ============================================================

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


    # Vertical stem.

    stem_dir = (
        0.0,
        1.0,
    )

    stem_normal = (
        -1.0,
        0.0,
    )


    # Diagonal branch.

    branch_dx = (
        branch_top_x
        - stem_x
    )

    branch_dy = (
        branch_top_y
        - split_y
    )

    branch_length = (
        branch_dx * branch_dx
        + branch_dy * branch_dy
    ) ** 0.5

    if branch_length <= 0:
        raise ValueError(
            "branch must have positive length"
        )

    branch_dir = (
        branch_dx / branch_length,
        branch_dy / branch_length,
    )

    branch_normal = (
        -branch_dir[1],
        branch_dir[0],
    )


    # Stem boundaries.

    stem_left_bottom = (
        stem_x
        + stem_normal[0] * half,
        bottom_y,
    )

    stem_right_bottom = (
        stem_x
        - stem_normal[0] * half,
        bottom_y,
    )

    stem_left_split = (
        stem_x
        + stem_normal[0] * half,
        split_y,
    )

    stem_right_split = (
        stem_x
        - stem_normal[0] * half,
        split_y,
    )


    # Branch boundaries.

    branch_left_split = (
        stem_x
        + branch_normal[0] * half,
        split_y
        + branch_normal[1] * half,
    )

    branch_right_split = (
        stem_x
        - branch_normal[0] * half,
        split_y
        - branch_normal[1] * half,
    )

    branch_left_top = (
        branch_top_x
        + branch_normal[0] * half,
        branch_top_y
        + branch_normal[1] * half,
    )

    branch_right_top = (
        branch_top_x
        - branch_normal[0] * half,
        branch_top_y
        - branch_normal[1] * half,
    )


    # True miter intersections.

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


# ============================================================
# DIVERGENCE GEOMETRY
# ============================================================

def build_geometry(
    architecture_width_mm,
):

    bottom_y = (
        -FIELD_HEIGHT_MM / 2.0
    )

    top_y = (
        FIELD_HEIGHT_MM / 2.0
    )

    half_stem = (
        STEM_WIDTH_MM / 2.0
    )

    left_stem_x = -half_stem
    right_stem_x = half_stem

    angle = radians(
        BRANCH_ANGLE_DEG
    )


    # Extend beyond field so SVG clipping
    # creates a flush top termination.

    overshoot_y = (
        architecture_width_mm
        * 3.0
    )

    branch_top_y = (
        top_y
        + overshoot_y
    )

    vertical_run = (
        branch_top_y
        - SPLIT_Y_MM
    )

    horizontal_run = (
        sin(angle)
        / cos(angle)
        * vertical_run
    )


    left_branch_top_x = (
        left_stem_x
        - horizontal_run
    )

    right_branch_top_x = (
        right_stem_x
        + horizontal_run
    )


    left = build_side_polygon(
        stem_x=left_stem_x,
        split_y=SPLIT_Y_MM,
        branch_top_x=left_branch_top_x,
        branch_top_y=branch_top_y,
        bottom_y=bottom_y,
        width_mm=architecture_width_mm,
    )


    right = build_side_polygon(
        stem_x=right_stem_x,
        split_y=SPLIT_Y_MM,
        branch_top_x=right_branch_top_x,
        branch_top_y=branch_top_y,
        bottom_y=bottom_y,
        width_mm=architecture_width_mm,
    )


    return left, right


# ============================================================
# SVG
# ============================================================

def make_svg(variant):

    left, right = build_geometry(
        variant.width_mm
    )

    left_points = polygon_string(
        left
    )

    right_points = polygon_string(
        right
    )


    return f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{fmt(FIELD_WIDTH_MM)}mm"
    height="{fmt(FIELD_HEIGHT_MM)}mm"
    viewBox="0 0 {fmt(FIELD_WIDTH_MM)} {fmt(FIELD_HEIGHT_MM)}"
>

<title>
FIELD-0004 Divergence
36 x 36 in
Architecture width {variant.width_in:.3f} in
</title>


<defs>

    <clipPath id="fieldClip">

        <rect
            x="0"
            y="0"
            width="{fmt(FIELD_WIDTH_MM)}"
            height="{fmt(FIELD_HEIGHT_MM)}"
        />

    </clipPath>

</defs>


<!-- FIELD -->

<rect
    x="0"
    y="0"
    width="{fmt(FIELD_WIDTH_MM)}"
    height="{fmt(FIELD_HEIGHT_MM)}"
    fill="{FIELD_COLOR}"
/>


<!-- CONTINUOUS MITERED ARCHITECTURE -->

<g clip-path="url(#fieldClip)">

    <polygon
        points="{left_points}"
        fill="{ARCHITECTURE_COLOR}"
    />

    <polygon
        points="{right_points}"
        fill="{ARCHITECTURE_COLOR}"
    />

</g>


</svg>
'''


# ============================================================
# REPORT
# ============================================================

def make_report(variant):

    percentage = (
        variant.width_mm
        / FIELD_WIDTH_MM
        * 100.0
    )

    return f"""OPERATIONAL WORLDS
FIELD-0004 DIVERGENCE

36 x 36 FINAL WIDTH STUDY


FIELD
-----
36 x 36 in

{FIELD_WIDTH_MM:.3f} x
{FIELD_HEIGHT_MM:.3f} mm


ARCHITECTURE WIDTH
------------------
{variant.width_in:.3f} in

{variant.width_mm:.3f} mm


PROPOSED RELIEF HEIGHT
----------------------
0.750 in

{ARCHITECTURE_HEIGHT_MM:.3f} mm


WIDTH / FIELD WIDTH
-------------------
{percentage:.3f}%


LOCKED PARAMETERS
-----------------
Stem centerline separation:

2.500 in
63.500 mm


Branch angle:

32 degrees


Split Y:

0 mm


GEOMETRY
--------
Continuous mitered architecture.

No overlap at junction.

No gap at junction.


PURPOSE
-------
Final width calibration for 36 x 36 field.

Only member width changes between the
two variants.
"""


# ============================================================
# EXPORT
# ============================================================

def main():

    EXPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print(
        "FIELD-0004 — 36x36"
    )

    print(
        "FINAL WIDTH STUDY"
    )

    print()

    for variant in VARIANTS:

        prefix = (
            "FIELD-0004_Divergence_"
            "36x36_"
            f"WIDTH-{variant.slug}"
        )

        svg_path = (
            EXPORT_ROOT
            / f"{prefix}.svg"
        )

        report_path = (
            EXPORT_ROOT
            / f"{prefix}_PARAMS.txt"
        )

        svg_path.write_text(
            make_svg(variant),
            encoding="utf-8",
        )

        report_path.write_text(
            make_report(variant),
            encoding="utf-8",
        )

        percentage = (
            variant.width_mm
            / FIELD_WIDTH_MM
            * 100
        )

        print(
            f"{variant.width_in:.3f} in"
            f" / {variant.width_mm:.2f} mm"
            f" / {percentage:.2f}% field width"
        )

        print(
            f"  {svg_path.relative_to(ROOT)}"
        )

        print()


if __name__ == "__main__":
    main()
