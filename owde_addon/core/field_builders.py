"""Parametric field architectures for Operational Worlds.

All dimensions are expressed in millimetres. The core layer intentionally
contains no Blender dependency: it describes a rectangular field and a set of
parameterized line segments that can drive Blender, projections, fabrication
drawings, or archived research records.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

INCH_MM = 25.4

DEFAULT_FIELD_WIDTH_MM = 16.0 * INCH_MM
DEFAULT_FIELD_HEIGHT_MM = 20.0 * INCH_MM
DEFAULT_LINE_WIDTH_MM = 0.50 * INCH_MM


@dataclass(frozen=True)
class FieldLine:
    x1: float
    y1: float
    x2: float
    y2: float
    width_mm: float


@dataclass(frozen=True)
class FieldSpec:
    field_id: str
    name: str
    width_mm: float
    height_mm: float
    lines: tuple[FieldLine, ...]
    parameters: dict[str, float | str]


def _validate_field(
    width_mm: float,
    height_mm: float,
    line_width_mm: float,
) -> None:
    if width_mm <= 0:
        raise ValueError("field width must be positive")

    if height_mm <= 0:
        raise ValueError("field height must be positive")

    if line_width_mm <= 0:
        raise ValueError("line width must be positive")


def build_division_field(
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    orientation: str = "VERTICAL",
    position_mm: float = 0.0,
) -> FieldSpec:
    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    orientation = orientation.upper()

    if orientation == "VERTICAL":
        if abs(position_mm) >= width_mm / 2.0:
            raise ValueError("vertical division position must remain inside field")

        lines = (
            FieldLine(
                position_mm,
                -height_mm / 2.0,
                position_mm,
                height_mm / 2.0,
                line_width_mm,
            ),
        )

    elif orientation == "HORIZONTAL":
        if abs(position_mm) >= height_mm / 2.0:
            raise ValueError("horizontal division position must remain inside field")

        lines = (
            FieldLine(
                -width_mm / 2.0,
                position_mm,
                width_mm / 2.0,
                position_mm,
                line_width_mm,
            ),
        )

    else:
        raise ValueError("orientation must be VERTICAL or HORIZONTAL")

    return FieldSpec(
        field_id="FIELD-0001",
        name="Division",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "orientation": orientation,
            "position_mm": position_mm,
            "line_width_mm": line_width_mm,
        },
    )


def build_intersection_field(
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    vertical_position_mm: float = 0.0,
    horizontal_position_mm: float = 0.0,
) -> FieldSpec:
    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    if abs(vertical_position_mm) >= width_mm / 2.0:
        raise ValueError("vertical line position must remain inside field")

    if abs(horizontal_position_mm) >= height_mm / 2.0:
        raise ValueError("horizontal line position must remain inside field")

    lines = (
        FieldLine(
            vertical_position_mm,
            -height_mm / 2.0,
            vertical_position_mm,
            height_mm / 2.0,
            line_width_mm,
        ),
        FieldLine(
            -width_mm / 2.0,
            horizontal_position_mm,
            width_mm / 2.0,
            horizontal_position_mm,
            line_width_mm,
        ),
    )

    return FieldSpec(
        field_id="FIELD-0002",
        name="Intersection",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "vertical_position_mm": vertical_position_mm,
            "horizontal_position_mm": horizontal_position_mm,
            "line_width_mm": line_width_mm,
        },
    )


def build_bottleneck_field(
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    corridor_width_mm: float = 6.0 * INCH_MM,
    throat_width_mm: float = 2.5 * INCH_MM,
    throat_y_mm: float = 0.0,
    transition_length_mm: float = 2.0 * INCH_MM,
) -> FieldSpec:
    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    if corridor_width_mm <= 0:
        raise ValueError("corridor width must be positive")

    if throat_width_mm <= 0:
        raise ValueError("throat width must be positive")

    if throat_width_mm >= corridor_width_mm:
        raise ValueError("throat width must be narrower than corridor width")

    if corridor_width_mm >= width_mm:
        raise ValueError("corridor width must fit inside field")

    if transition_length_mm <= 0:
        raise ValueError("transition length must be positive")

    half_transition = transition_length_mm / 2.0
    y_lower_transition = throat_y_mm - half_transition
    y_upper_transition = throat_y_mm + half_transition

    if y_lower_transition <= -height_mm / 2.0:
        raise ValueError("lower transition falls outside field")

    if y_upper_transition >= height_mm / 2.0:
        raise ValueError("upper transition falls outside field")

    corridor_half = corridor_width_mm / 2.0
    throat_half = throat_width_mm / 2.0
    bottom = -height_mm / 2.0
    top = height_mm / 2.0

    lines = (
        FieldLine(
            -corridor_half,
            bottom,
            -corridor_half,
            y_lower_transition,
            line_width_mm,
        ),
        FieldLine(
            -corridor_half,
            y_lower_transition,
            -throat_half,
            throat_y_mm,
            line_width_mm,
        ),
        FieldLine(
            -throat_half,
            throat_y_mm,
            -corridor_half,
            y_upper_transition,
            line_width_mm,
        ),
        FieldLine(
            -corridor_half,
            y_upper_transition,
            -corridor_half,
            top,
            line_width_mm,
        ),
        FieldLine(
            corridor_half,
            bottom,
            corridor_half,
            y_lower_transition,
            line_width_mm,
        ),
        FieldLine(
            corridor_half,
            y_lower_transition,
            throat_half,
            throat_y_mm,
            line_width_mm,
        ),
        FieldLine(
            throat_half,
            throat_y_mm,
            corridor_half,
            y_upper_transition,
            line_width_mm,
        ),
        FieldLine(
            corridor_half,
            y_upper_transition,
            corridor_half,
            top,
            line_width_mm,
        ),
    )

    return FieldSpec(
        field_id="FIELD-0003",
        name="Bottleneck",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "corridor_width_mm": corridor_width_mm,
            "throat_width_mm": throat_width_mm,
            "throat_y_mm": throat_y_mm,
            "transition_length_mm": transition_length_mm,
            "line_width_mm": line_width_mm,
        },
    )


def build_divergence_field(
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    split_y_mm: float = 0.0,
    stem_width_mm: float = 2.5 * INCH_MM,
    branch_angle_deg: float = 32.0,
    branch_length_mm: float = 7.0 * INCH_MM,
) -> FieldSpec:
    """Build FIELD-0004 as two parallel lower boundaries that diverge upward."""

    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    if stem_width_mm <= 0:
        raise ValueError("stem width must be positive")

    if stem_width_mm >= width_mm:
        raise ValueError("stem width must fit inside field")

    if not 1.0 <= branch_angle_deg <= 80.0:
        raise ValueError("branch angle must be between 1 and 80 degrees")

    if branch_length_mm <= 0:
        raise ValueError("branch length must be positive")

    bottom_y = -height_mm / 2.0
    top_y = height_mm / 2.0

    if not bottom_y < split_y_mm < top_y:
        raise ValueError("split position must remain inside field")

    angle = radians(branch_angle_deg)
    vertical_run = top_y - split_y_mm
    horizontal_run = sin(angle) / cos(angle) * vertical_run

    half_width = width_mm / 2.0
    half_stem = stem_width_mm / 2.0
    left_split_x = -half_stem
    right_split_x = half_stem
    left_top_x = max(
        -half_width,
        left_split_x - horizontal_run,
    )
    right_top_x = min(
        half_width,
        right_split_x + horizontal_run,
    )

    lines = (
        FieldLine(
            left_split_x,
            bottom_y,
            left_split_x,
            split_y_mm,
            line_width_mm,
        ),
        FieldLine(
            right_split_x,
            bottom_y,
            right_split_x,
            split_y_mm,
            line_width_mm,
        ),
        FieldLine(
            left_split_x,
            split_y_mm,
            left_top_x,
            top_y,
            line_width_mm,
        ),
        FieldLine(
            right_split_x,
            split_y_mm,
            right_top_x,
            top_y,
            line_width_mm,
        ),
    )

    return FieldSpec(
        field_id="FIELD-0004",
        name="Divergence",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "split_y_mm": split_y_mm,
            "stem_width_mm": stem_width_mm,
            "branch_angle_deg": branch_angle_deg,
            "branch_length_mm": branch_length_mm,
            "line_width_mm": line_width_mm,
        },
    )



def build_nested_zones_field(
    *,
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    outer_width_mm: float = 345.0,
    outer_height_mm: float = 435.0,
    middle_width_mm: float = 245.0,
    middle_height_mm: float = 325.0,
    inner_width_mm: float = 115.0,
    inner_height_mm: float = 145.0,
    inner_offset_y_mm: float = -28.0,
) -> FieldSpec:
    """Build FIELD-0005 as three nested containment boundaries."""

    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    def rectangle_lines(
        center_x: float,
        center_y: float,
        rectangle_width_mm: float,
        rectangle_height_mm: float,
    ) -> tuple[FieldLine, ...]:
        half_w = rectangle_width_mm / 2.0
        half_h = rectangle_height_mm / 2.0
        left = center_x - half_w
        right = center_x + half_w
        bottom = center_y - half_h
        top = center_y + half_h

        return (
            FieldLine(left, bottom, right, bottom, line_width_mm),
            FieldLine(right, bottom, right, top, line_width_mm),
            FieldLine(right, top, left, top, line_width_mm),
            FieldLine(left, top, left, bottom, line_width_mm),
        )

    lines = (
        *rectangle_lines(0.0, 0.0, outer_width_mm, outer_height_mm),
        *rectangle_lines(0.0, 0.0, middle_width_mm, middle_height_mm),
        *rectangle_lines(0.0, inner_offset_y_mm, inner_width_mm, inner_height_mm),
    )

    return FieldSpec(
        field_id="FIELD-0005",
        name="Nested Zones",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "line_width_mm": line_width_mm,
            "outer_width_mm": outer_width_mm,
            "outer_height_mm": outer_height_mm,
            "middle_width_mm": middle_width_mm,
            "middle_height_mm": middle_height_mm,
            "inner_width_mm": inner_width_mm,
            "inner_height_mm": inner_height_mm,
            "inner_offset_y_mm": inner_offset_y_mm,
        },
    )


def build_offset_zones_field(
    *,
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    top_left_vertical_x_mm: float = -105.0,
    top_left_horizontal_y_mm: float = 95.0,
    lower_right_outer_x_mm: float = 85.0,
    lower_right_outer_y_mm: float = -65.0,
    lower_right_inner_x_mm: float = 125.0,
    lower_right_inner_y_mm: float = -105.0,
) -> FieldSpec:
    """Build FIELD-0006 as opposed edge-anchored right-angle structures."""

    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    left = -width_mm / 2.0
    right = width_mm / 2.0
    bottom = -height_mm / 2.0
    top = height_mm / 2.0

    lines = (
        FieldLine(
            top_left_vertical_x_mm,
            top,
            top_left_vertical_x_mm,
            top_left_horizontal_y_mm,
            line_width_mm,
        ),
        FieldLine(
            top_left_vertical_x_mm,
            top_left_horizontal_y_mm,
            left,
            top_left_horizontal_y_mm,
            line_width_mm,
        ),
        FieldLine(
            right,
            lower_right_outer_y_mm,
            lower_right_outer_x_mm,
            lower_right_outer_y_mm,
            line_width_mm,
        ),
        FieldLine(
            lower_right_outer_x_mm,
            lower_right_outer_y_mm,
            lower_right_outer_x_mm,
            bottom,
            line_width_mm,
        ),
        FieldLine(
            right,
            lower_right_inner_y_mm,
            lower_right_inner_x_mm,
            lower_right_inner_y_mm,
            line_width_mm,
        ),
        FieldLine(
            lower_right_inner_x_mm,
            lower_right_inner_y_mm,
            lower_right_inner_x_mm,
            bottom,
            line_width_mm,
        ),
    )

    return FieldSpec(
        field_id="FIELD-0006",
        name="Offset Zones",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "line_width_mm": line_width_mm,
            "top_left_vertical_x_mm": top_left_vertical_x_mm,
            "top_left_horizontal_y_mm": top_left_horizontal_y_mm,
            "lower_right_outer_x_mm": lower_right_outer_x_mm,
            "lower_right_outer_y_mm": lower_right_outer_y_mm,
            "lower_right_inner_x_mm": lower_right_inner_x_mm,
            "lower_right_inner_y_mm": lower_right_inner_y_mm,
        },
    )





def build_terminal_target_field(
    *,
    width_mm: float = DEFAULT_FIELD_WIDTH_MM,
    height_mm: float = DEFAULT_FIELD_HEIGHT_MM,
    line_width_mm: float = DEFAULT_LINE_WIDTH_MM,
    outer_margin_x_mm: float = 22.0,
    outer_margin_y_mm: float = 22.0,
    division_y_mm: float = 0.0,
    upper_divider_x_mm: float = 0.0,
    target_width_mm: float = 105.0,
    target_depth_mm: float = 72.0,
) -> FieldSpec:
    """Build FIELD-0007 as a centered terminal target architecture."""

    _validate_field(
        width_mm,
        height_mm,
        line_width_mm,
    )

    field_left = -width_mm / 2.0
    field_right = width_mm / 2.0
    field_bottom = -height_mm / 2.0
    field_top = height_mm / 2.0

    left = field_left + outer_margin_x_mm
    right = field_right - outer_margin_x_mm
    bottom = field_bottom + outer_margin_y_mm
    top = field_top - outer_margin_y_mm

    target_center_x_mm = upper_divider_x_mm
    target_left = target_center_x_mm - target_width_mm / 2.0
    target_right = target_center_x_mm + target_width_mm / 2.0
    target_bottom = division_y_mm - target_depth_mm

    lines = (
        FieldLine(left, bottom, right, bottom, line_width_mm),
        FieldLine(right, bottom, right, top, line_width_mm),
        FieldLine(right, top, left, top, line_width_mm),
        FieldLine(left, top, left, bottom, line_width_mm),
        FieldLine(left, division_y_mm, right, division_y_mm, line_width_mm),
        FieldLine(
            upper_divider_x_mm,
            top,
            upper_divider_x_mm,
            division_y_mm,
            line_width_mm,
        ),
        FieldLine(target_left, division_y_mm, target_left, target_bottom, line_width_mm),
        FieldLine(target_left, target_bottom, target_right, target_bottom, line_width_mm),
        FieldLine(target_right, target_bottom, target_right, division_y_mm, line_width_mm),
    )

    return FieldSpec(
        field_id="FIELD-0007",
        name="Terminal / Target",
        width_mm=width_mm,
        height_mm=height_mm,
        lines=lines,
        parameters={
            "line_width_mm": line_width_mm,
            "outer_margin_x_mm": outer_margin_x_mm,
            "outer_margin_y_mm": outer_margin_y_mm,
            "division_y_mm": division_y_mm,
            "upper_divider_x_mm": upper_divider_x_mm,
            "target_width_mm": target_width_mm,
            "target_depth_mm": target_depth_mm,
        },
    )


FIELD_BUILDERS = {
    "DIVISION": build_division_field,
    "INTERSECTION": build_intersection_field,
    "BOTTLENECK": build_bottleneck_field,
    "DIVERGENCE": build_divergence_field,
    "NESTED_ZONES": build_nested_zones_field,
    "OFFSET_ZONES": build_offset_zones_field,
    "TERMINAL_TARGET": build_terminal_target_field,
}
