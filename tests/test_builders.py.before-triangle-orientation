import pytest

from owde_addon.core import (
    ShapeType,
    TileParameters,
    build_tile_mesh,
    shape_outline,
)


@pytest.mark.parametrize(
    ("shape", "expected_points"),
    (
        (ShapeType.TRIANGLE, 3),
        (ShapeType.SQUARE, 4),
        (ShapeType.HEXAGON, 6),
    ),
)
def test_polygon_outline_point_counts(
    shape: ShapeType,
    expected_points: int,
) -> None:
    parameters = TileParameters(shape=shape)
    assert len(shape_outline(parameters)) == expected_points


def test_circle_outline_uses_requested_resolution() -> None:
    parameters = TileParameters(
        shape=ShapeType.CIRCLE,
        circle_segments=64,
    )

    assert len(shape_outline(parameters)) == 64


@pytest.mark.parametrize(
    "shape",
    (
        ShapeType.CIRCLE,
        ShapeType.TRIANGLE,
        ShapeType.SQUARE,
        ShapeType.HEXAGON,
    ),
)
def test_each_shape_builds_a_valid_mesh(shape: ShapeType) -> None:
    mesh = build_tile_mesh(TileParameters(shape=shape))

    mesh.validate()

    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0


def test_mesh_reaches_expected_total_height() -> None:
    parameters = TileParameters(
        tile_height_mm=8.0,
        shape_height_mm=5.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(vertex[2] for vertex in mesh.vertices)

    assert maximum_z == pytest.approx(13.0)
