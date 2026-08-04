import pytest

from owde_addon.core import (
    ShapeType,
    TileParameters,
    build_tile_mesh,
    shape_outline,
)


RAISED_SHAPES = (
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.SQUARE,
    ShapeType.HEXAGON,
)

COMPLEX_PRIMITIVES = (
    ShapeType.SLOT,
    ShapeType.HINGE,
    ShapeType.FOLD,
    ShapeType.APERTURE,
    ShapeType.LENS,
    ShapeType.MIRROR,
)

ALL_IMPLEMENTED_PRIMITIVES = (
    *RAISED_SHAPES,
    *COMPLEX_PRIMITIVES,
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

    assert (
        len(shape_outline(parameters))
        == expected_points
    )


def test_circle_outline_uses_requested_resolution() -> None:
    parameters = TileParameters(
        shape=ShapeType.CIRCLE,
        circle_segments=64,
    )

    assert len(shape_outline(parameters)) == 64


@pytest.mark.parametrize(
    "shape",
    ALL_IMPLEMENTED_PRIMITIVES,
)
def test_each_primitive_builds_a_valid_mesh(
    shape: ShapeType,
) -> None:
    mesh = build_tile_mesh(
        TileParameters(shape=shape)
    )

    mesh.validate()

    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0


@pytest.mark.parametrize(
    "shape",
    (
        ShapeType.CIRCLE,
        ShapeType.TRIANGLE,
        ShapeType.SQUARE,
        ShapeType.HEXAGON,
        ShapeType.HINGE,
        ShapeType.FOLD,
        ShapeType.LENS,
        ShapeType.MIRROR,
    ),
)
def test_solid_primitives_reach_above_tile(
    shape: ShapeType,
) -> None:
    parameters = TileParameters(
        shape=shape,
        tile_height_mm=8.0,
        shape_height_mm=5.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    assert maximum_z > parameters.tile_height_mm


def test_aperture_does_not_add_geometry_above_tile() -> None:
    parameters = TileParameters(
        shape=ShapeType.APERTURE,
        tile_height_mm=8.0,
        shape_width_mm=40.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    assert maximum_z == pytest.approx(8.0)


def test_aperture_contains_inner_circular_wall() -> None:
    parameters = TileParameters(
        shape=ShapeType.APERTURE,
        shape_width_mm=40.0,
        circle_segments=64,
    )

    mesh = build_tile_mesh(parameters)
    expected_radius = 20.0

    circular_vertices = [
        vertex
        for vertex in mesh.vertices
        if (
            vertex[0] ** 2
            + vertex[1] ** 2
        ) ** 0.5
        == pytest.approx(expected_radius)
    ]

    assert len(circular_vertices) == 128


def test_hexagon_has_horizontal_top_and_bottom_edges() -> None:
    parameters = TileParameters(
        shape=ShapeType.HEXAGON,
        shape_width_mm=60.0,
    )

    points = shape_outline(parameters)

    highest_y = max(y for _, y in points)
    lowest_y = min(y for _, y in points)

    top_points = [
        point
        for point in points
        if point[1] == pytest.approx(highest_y)
    ]

    bottom_points = [
        point
        for point in points
        if point[1] == pytest.approx(lowest_y)
    ]

    assert len(top_points) == 2
    assert len(bottom_points) == 2

    assert top_points[0][1] == pytest.approx(
        top_points[1][1]
    )

    assert bottom_points[0][1] == pytest.approx(
        bottom_points[1][1]
    )


def test_fold_creates_elevated_plane() -> None:
    parameters = TileParameters(
        shape=ShapeType.FOLD,
        tile_height_mm=8.0,
        shape_width_mm=55.0,
        shape_height_mm=4.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    assert maximum_z > 30.0




def test_slot_creates_rim_above_tile() -> None:
    parameters = TileParameters(
        shape=ShapeType.SLOT,
        tile_height_mm=8.0,
        shape_width_mm=55.0,
        shape_height_mm=5.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    assert maximum_z > parameters.tile_height_mm

def test_lens_has_center_apex() -> None:
    parameters = TileParameters(
        shape=ShapeType.LENS,
        tile_height_mm=8.0,
        shape_width_mm=50.0,
        shape_height_mm=8.0,
    )

    mesh = build_tile_mesh(parameters)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    apex_vertices = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(maximum_z)
    ]

    assert any(
        vertex[0] == pytest.approx(0.0)
        and vertex[1] == pytest.approx(0.0)
        for vertex in apex_vertices
    )


def test_feature_must_fit_inside_tile() -> None:
    parameters = TileParameters(
        shape=ShapeType.MIRROR,
        tile_width_mm=100.0,
        tile_depth_mm=100.0,
        shape_width_mm=100.0,
    )

    with pytest.raises(
        ValueError,
        match="must be smaller than the tile",
    ):
        build_tile_mesh(parameters)
