from __future__ import annotations

import math
from collections.abc import Sequence

from .mesh import MeshData
from .models import ShapeType, TileParameters


Point2D = tuple[float, float]


def regular_polygon_points(
    sides: int,
    diameter_mm: float,
    rotation_degrees: float = 90.0,
) -> tuple[Point2D, ...]:
    if sides < 3:
        raise ValueError("A polygon requires at least three sides.")

    if diameter_mm <= 0:
        raise ValueError("diameter_mm must be greater than zero.")

    radius = diameter_mm / 2.0
    rotation = math.radians(rotation_degrees)

    return tuple(
        (
            radius * math.cos(rotation + index * 2.0 * math.pi / sides),
            radius * math.sin(rotation + index * 2.0 * math.pi / sides),
        )
        for index in range(sides)
    )


def circle_points(
    diameter_mm: float,
    segments: int,
) -> tuple[Point2D, ...]:
    if segments < 24:
        raise ValueError("Circle requires at least 24 segments.")

    return regular_polygon_points(
        sides=segments,
        diameter_mm=diameter_mm,
        rotation_degrees=0.0,
    )


def shape_outline(parameters: TileParameters) -> tuple[Point2D, ...]:
    if parameters.shape is ShapeType.CIRCLE:
        return circle_points(
            diameter_mm=parameters.shape_width_mm,
            segments=parameters.circle_segments,
        )

    if parameters.shape is ShapeType.TRIANGLE:
        return regular_polygon_points(
            sides=3,
            diameter_mm=parameters.shape_width_mm,
            rotation_degrees=90.0,
        )

    if parameters.shape is ShapeType.SQUARE:
        return regular_polygon_points(
            sides=4,
            diameter_mm=parameters.shape_width_mm,
            rotation_degrees=45.0,
        )

    if parameters.shape is ShapeType.HEXAGON:
        return regular_polygon_points(
            sides=6,
            diameter_mm=parameters.shape_width_mm,
            rotation_degrees=0.0,
        )

    raise ValueError(f"Unsupported shape: {parameters.shape}")


def extrude_polygon(
    outline: Sequence[Point2D],
    bottom_z_mm: float,
    top_z_mm: float,
) -> MeshData:
    if len(outline) < 3:
        raise ValueError("Outline requires at least three points.")

    if top_z_mm <= bottom_z_mm:
        raise ValueError("top_z_mm must be greater than bottom_z_mm.")

    count = len(outline)

    bottom = tuple((x, y, bottom_z_mm) for x, y in outline)
    top = tuple((x, y, top_z_mm) for x, y in outline)

    vertices = bottom + top

    faces: list[tuple[int, ...]] = []

    faces.append(tuple(reversed(range(count))))
    faces.append(tuple(range(count, count * 2)))

    for index in range(count):
        next_index = (index + 1) % count
        faces.append(
            (
                index,
                next_index,
                count + next_index,
                count + index,
            )
        )

    result = MeshData(
        vertices=vertices,
        faces=tuple(faces),
    )
    result.validate()
    return result


def combine_meshes(*meshes: MeshData) -> MeshData:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    offset = 0

    for mesh in meshes:
        mesh.validate()
        vertices.extend(mesh.vertices)

        for face in mesh.faces:
            faces.append(tuple(index + offset for index in face))

        offset += len(mesh.vertices)

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )
    result.validate()
    return result


def build_tile_mesh(parameters: TileParameters) -> MeshData:
    parameters.validate()

    half_width = parameters.tile_width_mm / 2.0
    half_depth = parameters.tile_depth_mm / 2.0

    base_outline = (
        (-half_width, -half_depth),
        (half_width, -half_depth),
        (half_width, half_depth),
        (-half_width, half_depth),
    )

    base = extrude_polygon(
        outline=base_outline,
        bottom_z_mm=0.0,
        top_z_mm=parameters.tile_height_mm,
    )

    raised_shape = extrude_polygon(
        outline=shape_outline(parameters),
        bottom_z_mm=parameters.tile_height_mm,
        top_z_mm=parameters.tile_height_mm + parameters.shape_height_mm,
    )

    return combine_meshes(base, raised_shape)
