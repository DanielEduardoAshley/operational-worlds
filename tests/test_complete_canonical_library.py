import math

import pytest

from owde_addon.core.builders import (
    build_base_tile_mesh,
    build_feature_mesh,
)
from owde_addon.core.models import (
    ShapeType,
    TileParameters,
)


def parameters(
    shape: ShapeType,
) -> TileParameters:
    return TileParameters(
        shape=shape,
        tile_width_mm=100.0,
        tile_depth_mm=100.0,
        tile_height_mm=8.0,
        shape_width_mm=55.0,
        shape_height_mm=5.0,
        circle_segments=64,
    )


@pytest.mark.parametrize(
    "shape",
    tuple(ShapeType),
)
def test_all_primitives_use_identical_base(
    shape: ShapeType,
) -> None:
    base = build_base_tile_mesh(
        parameters(shape)
    )

    xs = [
        vertex[0]
        for vertex in base.vertices
    ]

    ys = [
        vertex[1]
        for vertex in base.vertices
    ]

    zs = [
        vertex[2]
        for vertex in base.vertices
    ]

    assert min(xs) == pytest.approx(-50.0)
    assert max(xs) == pytest.approx(50.0)

    assert min(ys) == pytest.approx(-50.0)
    assert max(ys) == pytest.approx(50.0)

    assert min(zs) == pytest.approx(0.0)
    assert max(zs) == pytest.approx(8.0)


@pytest.mark.parametrize(
    "shape",
    tuple(ShapeType),
)
def test_every_canonical_feature_builds(
    shape: ShapeType,
) -> None:
    mesh = build_feature_mesh(
        parameters(shape)
    )

    mesh.validate()

    assert mesh.vertices
    assert mesh.faces


@pytest.mark.parametrize(
    "shape",
    (
        ShapeType.CIRCLE,
        ShapeType.TRIANGLE,
        ShapeType.SQUARE,
        ShapeType.HEXAGON,
    ),
)
def test_primary_geometric_primitives_have_top_chamfer(
    shape: ShapeType,
) -> None:
    mesh = build_feature_mesh(
        parameters(shape)
    )

    elevations = {
        round(
            vertex[2],
            5,
        )
        for vertex in mesh.vertices
    }

    assert len(elevations) >= 3


def test_circle_remains_circular() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.CIRCLE
        )
    )

    top_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    top = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(
            top_z
        )
    ]

    radii = [
        math.hypot(
            vertex[0],
            vertex[1],
        )
        for vertex in top
    ]

    assert max(radii) - min(radii) < 1e-6


def test_hexagon_remains_flat_top() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.HEXAGON
        )
    )

    top_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    top = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(
            top_z
        )
    ]

    maximum_y = max(
        vertex[1]
        for vertex in top
    )

    highest = [
        vertex
        for vertex in top
        if vertex[1] == pytest.approx(
            maximum_y
        )
    ]

    assert len(highest) == 2


def test_slot_is_longer_than_wide() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.SLOT
        )
    )

    xs = [
        vertex[0]
        for vertex in mesh.vertices
    ]

    ys = [
        vertex[1]
        for vertex in mesh.vertices
    ]

    assert (
        max(xs) - min(xs)
        >
        max(ys) - min(ys)
    )


def test_hinge_contains_cylindrical_geometry() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.HINGE
        )
    )

    assert len(mesh.vertices) > 100


def test_fold_rises_above_standard_feature_height() -> None:
    values = parameters(
        ShapeType.FOLD
    )

    mesh = build_feature_mesh(
        values
    )

    assert (
        max(
            vertex[2]
            for vertex in mesh.vertices
        )
        >
        values.tile_height_mm
        + values.shape_height_mm
    )


def test_aperture_contains_inner_and_outer_radii() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.APERTURE
        )
    )

    radii = {
        round(
            math.hypot(
                vertex[0],
                vertex[1],
            ),
            4,
        )
        for vertex in mesh.vertices
    }

    assert len(radii) >= 2


def test_threshold_is_wider_than_deep() -> None:
    mesh = build_feature_mesh(
        parameters(
            ShapeType.THRESHOLD
        )
    )

    xs = [
        vertex[0]
        for vertex in mesh.vertices
    ]

    ys = [
        vertex[1]
        for vertex in mesh.vertices
    ]

    assert (
        max(xs) - min(xs)
        >
        max(ys) - min(ys)
    )


def test_handle_has_clearance_above_tile() -> None:
    values = parameters(
        ShapeType.HANDLE
    )

    mesh = build_feature_mesh(
        values
    )

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    assert (
        maximum_z
        >
        values.tile_height_mm
        + 12.0
    )
