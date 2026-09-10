import pytest

from owde_addon.core.field_builders import (
    DEFAULT_FIELD_HEIGHT_MM,
    DEFAULT_FIELD_WIDTH_MM,
    build_bottleneck_field,
    build_divergence_field,
    build_division_field,
    build_intersection_field,
    build_nested_zones_field,
    build_offset_zones_field,
    build_terminal_target_field,
)


def test_division_vertical():
    spec = build_division_field()

    assert spec.field_id == "FIELD-0001"
    assert spec.name == "Division"
    assert len(spec.lines) == 1

    line = spec.lines[0]

    assert line.x1 == pytest.approx(0.0)
    assert line.x2 == pytest.approx(0.0)
    assert line.y1 == pytest.approx(-DEFAULT_FIELD_HEIGHT_MM / 2.0)
    assert line.y2 == pytest.approx(DEFAULT_FIELD_HEIGHT_MM / 2.0)


def test_division_horizontal():
    spec = build_division_field(
        orientation="HORIZONTAL",
    )

    assert len(spec.lines) == 1

    line = spec.lines[0]

    assert line.y1 == pytest.approx(0.0)
    assert line.y2 == pytest.approx(0.0)
    assert line.x1 == pytest.approx(-DEFAULT_FIELD_WIDTH_MM / 2.0)
    assert line.x2 == pytest.approx(DEFAULT_FIELD_WIDTH_MM / 2.0)


def test_intersection_contains_two_lines():
    spec = build_intersection_field()

    assert spec.field_id == "FIELD-0002"
    assert len(spec.lines) == 2


def test_bottleneck_has_eight_segments():
    spec = build_bottleneck_field()

    assert spec.field_id == "FIELD-0003"
    assert len(spec.lines) == 8


def test_bottleneck_throat_is_narrower():
    spec = build_bottleneck_field()

    assert spec.parameters["throat_width_mm"] < spec.parameters["corridor_width_mm"]


def test_bottleneck_rejects_invalid_widths():
    with pytest.raises(ValueError):
        build_bottleneck_field(
            corridor_width_mm=50,
            throat_width_mm=80,
        )


def test_divergence_contains_two_stems_and_two_branches():
    spec = build_divergence_field()

    assert spec.field_id == "FIELD-0004"
    assert len(spec.lines) == 4


def test_divergence_is_symmetric():
    spec = build_divergence_field()

    left_stem = spec.lines[0]
    right_stem = spec.lines[1]
    left_branch = spec.lines[2]
    right_branch = spec.lines[3]

    assert left_stem.x1 == pytest.approx(left_stem.x2)
    assert right_stem.x1 == pytest.approx(right_stem.x2)
    assert left_stem.y1 == pytest.approx(-DEFAULT_FIELD_HEIGHT_MM / 2.0)
    assert right_stem.y1 == pytest.approx(-DEFAULT_FIELD_HEIGHT_MM / 2.0)

    assert left_branch.x2 == pytest.approx(-right_branch.x2)
    assert left_branch.y2 == pytest.approx(DEFAULT_FIELD_HEIGHT_MM / 2.0)
    assert right_branch.y2 == pytest.approx(DEFAULT_FIELD_HEIGHT_MM / 2.0)


def test_default_field_is_portrait_20_by_16_inches():
    assert DEFAULT_FIELD_WIDTH_MM == pytest.approx(406.4)
    assert DEFAULT_FIELD_HEIGHT_MM == pytest.approx(508.0)


def test_nested_zones_field():
    spec = build_nested_zones_field()

    assert spec.field_id == "FIELD-0005"
    assert spec.name == "Nested Zones"
    assert len(spec.lines) == 12


def test_offset_zones_field():
    spec = build_offset_zones_field()

    assert spec.field_id == "FIELD-0006"
    assert spec.name == "Offset Zones"
    assert len(spec.lines) == 6


def test_terminal_target_field():
    spec = build_terminal_target_field()

    assert spec.field_id == "FIELD-0007"
    assert spec.name == "Terminal / Target"
    assert len(spec.lines) == 9
