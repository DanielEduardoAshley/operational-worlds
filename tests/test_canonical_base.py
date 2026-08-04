import pytest

from owde_addon.core.builders import (
    build_base_tile_mesh,
    build_feature_mesh,
    build_tile_mesh,
)
from owde_addon.core.models import (
    ShapeType,
    TileParameters,
)


ALL_SHAPES = tuple(ShapeType)


@pytest.mark.parametrize(
    "shape",
    ALL_SHAPES,
)
def test_every_primitive_has_identical_base_bounds(
    shape: ShapeType,
) -> None:
    parameters = TileParameters(
        shape=shape,
        tile_width_mm=100.0,
        tile_depth_mm=100.0,
        tile_height_mm=8.0,
        shape_width_mm=55.0,
        shape_height_mm=5.0,
    )

    base = build_base_tile_mesh(parameters)

    minimum_x = min(
        vertex[0]
        for vertex in base.vertices
    )
    maximum_x = max(
        vertex[0]
        for vertex in base.vertices
    )

    minimum_y = min(
        vertex[1]
        for vertex in base.vertices
    )
    maximum_y = max(
        vertex[1]
        for vertex in base.vertices
    )

    minimum_z = min(
        vertex[2]
        for vertex in base.vertices
    )
    maximum_z = max(
        vertex[2]
        for vertex in base.vertices
    )

    assert minimum_x == pytest.approx(-50.0)
    assert maximum_x == pytest.approx(50.0)

    assert minimum_y == pytest.approx(-50.0)
    assert maximum_y == pytest.approx(50.0)

    assert minimum_z == pytest.approx(0.0)
    assert maximum_z == pytest.approx(8.0)


@pytest.mark.parametrize(
    "shape",
    ALL_SHAPES,
)
def test_feature_is_generated_separately(
    shape: ShapeType,
) -> None:
    parameters = TileParameters(
        shape=shape,
    )

    feature = build_feature_mesh(parameters)

    feature.validate()

    assert feature.vertices
    assert feature.faces


@pytest.mark.parametrize(
    "shape",
    ALL_SHAPES,
)
def test_complete_primitive_retains_rectangular_footprint(
    shape: ShapeType,
) -> None:
    parameters = TileParameters(
        shape=shape,
        tile_width_mm=100.0,
        tile_depth_mm=100.0,
    )

    mesh = build_tile_mesh(parameters)

    xs = [
        vertex[0]
        for vertex in mesh.vertices
    ]

    ys = [
        vertex[1]
        for vertex in mesh.vertices
    ]

    assert min(xs) == pytest.approx(-50.0)
    assert max(xs) == pytest.approx(50.0)

    assert min(ys) == pytest.approx(-50.0)
    assert max(ys) == pytest.approx(50.0)


def test_hexagon_remains_flat_top() -> None:
    parameters = TileParameters(
        shape=ShapeType.HEXAGON,
        shape_width_mm=60.0,
    )

    feature = build_feature_mesh(parameters)

    top_z = max(
        vertex[2]
        for vertex in feature.vertices
    )

    top_vertices = [
        vertex
        for vertex in feature.vertices
        if vertex[2] == pytest.approx(top_z)
    ]

    highest_y = max(
        vertex[1]
        for vertex in top_vertices
    )

    points_at_highest_y = [
        vertex
        for vertex in top_vertices
        if vertex[1] == pytest.approx(
            highest_y
        )
    ]

    assert len(points_at_highest_y) == 2


def test_lens_has_no_separate_mounting_platform() -> None:
    parameters = TileParameters(
        shape=ShapeType.LENS,
    )

    feature = build_feature_mesh(parameters)

    minimum_z = min(
        vertex[2]
        for vertex in feature.vertices
    )

    assert minimum_z == pytest.approx(
        parameters.tile_height_mm
    )


def test_weight_is_directly_supported_by_tile() -> None:
    parameters = TileParameters(
        shape=ShapeType.WEIGHT,
    )

    feature = build_feature_mesh(parameters)

    minimum_z = min(
        vertex[2]
        for vertex in feature.vertices
    )

    assert minimum_z == pytest.approx(
        parameters.tile_height_mm
    )


def test_sensor_is_directly_supported_by_tile() -> None:
    parameters = TileParameters(
        shape=ShapeType.SENSOR,
    )

    feature = build_feature_mesh(parameters)

    minimum_z = min(
        vertex[2]
        for vertex in feature.vertices
    )

    assert minimum_z == pytest.approx(
        parameters.tile_height_mm
    )
