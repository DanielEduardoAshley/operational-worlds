import math

import pytest

from owde_addon.core.builders import (
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


def test_lens_is_rotationally_symmetric() -> None:
    values = parameters(ShapeType.LENS)
    mesh = build_feature_mesh(values)

    maximum_z = max(
        vertex[2]
        for vertex in mesh.vertices
    )

    apex = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(maximum_z)
    ]

    assert any(
        vertex[0] == pytest.approx(0.0)
        and vertex[1] == pytest.approx(0.0)
        for vertex in apex
    )


def test_lens_starts_directly_on_tile() -> None:
    values = parameters(ShapeType.LENS)
    mesh = build_feature_mesh(values)

    assert min(
        vertex[2]
        for vertex in mesh.vertices
    ) == pytest.approx(
        values.tile_height_mm
    )


def test_mirror_has_multiple_height_levels() -> None:
    values = parameters(ShapeType.MIRROR)
    mesh = build_feature_mesh(values)

    elevations = {
        round(vertex[2], 4)
        for vertex in mesh.vertices
    }

    assert len(elevations) >= 3


def test_light_is_lower_than_full_sphere() -> None:
    values = parameters(
        ShapeType.LIGHT_SOURCE
    )

    mesh = build_feature_mesh(values)

    feature_height = (
        max(vertex[2] for vertex in mesh.vertices)
        - values.tile_height_mm
    )

    implied_full_sphere = (
        values.shape_width_mm
        * 0.285
        * 2.0
    )

    assert feature_height < implied_full_sphere


def test_weight_is_rotated_forty_five_degrees() -> None:
    values = parameters(ShapeType.WEIGHT)
    mesh = build_feature_mesh(values)

    bottom_z = min(
        vertex[2]
        for vertex in mesh.vertices
    )

    bottom_vertices = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(bottom_z)
    ]

    maximum_x = max(
        vertex[0]
        for vertex in bottom_vertices
    )

    max_x_vertices = [
        vertex
        for vertex in bottom_vertices
        if vertex[0] == pytest.approx(maximum_x)
    ]

    assert max_x_vertices
    assert all(
        abs(vertex[1]) < 2.0
        for vertex in max_x_vertices
    )


def test_weight_has_chamfered_outline() -> None:
    values = parameters(ShapeType.WEIGHT)
    mesh = build_feature_mesh(values)

    bottom_z = min(
        vertex[2]
        for vertex in mesh.vertices
    )

    bottom_vertices = [
        vertex
        for vertex in mesh.vertices
        if vertex[2] == pytest.approx(bottom_z)
    ]

    assert len(bottom_vertices) == 8


def test_sensor_has_recess_and_dome() -> None:
    values = parameters(ShapeType.SENSOR)
    mesh = build_feature_mesh(values)

    elevations = sorted(
        {
            round(vertex[2], 4)
            for vertex in mesh.vertices
        }
    )

    assert len(elevations) > 4


def test_sensor_is_smaller_than_lens() -> None:
    lens = build_feature_mesh(
        parameters(ShapeType.LENS)
    )

    sensor = build_feature_mesh(
        parameters(ShapeType.SENSOR)
    )

    lens_radius = max(
        math.hypot(
            vertex[0],
            vertex[1],
        )
        for vertex in lens.vertices
    )

    sensor_radius = max(
        math.hypot(
            vertex[0],
            vertex[1],
        )
        for vertex in sensor.vertices
    )

    assert sensor_radius < lens_radius
