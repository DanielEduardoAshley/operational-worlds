from __future__ import annotations

import math
from collections.abc import Sequence

from .mesh import MeshData
from .models import ShapeType, TileParameters


Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


RAISED_SHAPES = {
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.SQUARE,
    ShapeType.HEXAGON,
}


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
            radius * math.cos(
                rotation + index * 2.0 * math.pi / sides
            ),
            radius * math.sin(
                rotation + index * 2.0 * math.pi / sides
            ),
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


def shape_outline(
    parameters: TileParameters,
) -> tuple[Point2D, ...]:
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

    raise ValueError(
        f"{parameters.shape.value} does not use a flat shape outline."
    )


def extrude_polygon(
    outline: Sequence[Point2D],
    bottom_z_mm: float,
    top_z_mm: float,
) -> MeshData:
    if len(outline) < 3:
        raise ValueError("Outline requires at least three points.")

    if top_z_mm <= bottom_z_mm:
        raise ValueError(
            "top_z_mm must be greater than bottom_z_mm."
        )

    count = len(outline)

    bottom = tuple(
        (x, y, bottom_z_mm)
        for x, y in outline
    )
    top = tuple(
        (x, y, top_z_mm)
        for x, y in outline
    )

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
    vertices: list[Point3D] = []
    faces: list[tuple[int, ...]] = []
    offset = 0

    for mesh in meshes:
        mesh.validate()
        vertices.extend(mesh.vertices)

        for face in mesh.faces:
            faces.append(
                tuple(index + offset for index in face)
            )

        offset += len(mesh.vertices)

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )
    result.validate()
    return result


def transform_mesh(
    mesh: MeshData,
    *,
    translate_x_mm: float = 0.0,
    translate_y_mm: float = 0.0,
    translate_z_mm: float = 0.0,
    rotate_x_degrees: float = 0.0,
    rotate_y_degrees: float = 0.0,
    rotate_z_degrees: float = 0.0,
) -> MeshData:
    x_angle = math.radians(rotate_x_degrees)
    y_angle = math.radians(rotate_y_degrees)
    z_angle = math.radians(rotate_z_degrees)

    cos_x = math.cos(x_angle)
    sin_x = math.sin(x_angle)
    cos_y = math.cos(y_angle)
    sin_y = math.sin(y_angle)
    cos_z = math.cos(z_angle)
    sin_z = math.sin(z_angle)

    transformed: list[Point3D] = []

    for x, y, z in mesh.vertices:
        y, z = (
            y * cos_x - z * sin_x,
            y * sin_x + z * cos_x,
        )

        x, z = (
            x * cos_y + z * sin_y,
            -x * sin_y + z * cos_y,
        )

        x, y = (
            x * cos_z - y * sin_z,
            x * sin_z + y * cos_z,
        )

        transformed.append(
            (
                x + translate_x_mm,
                y + translate_y_mm,
                z + translate_z_mm,
            )
        )

    result = MeshData(
        vertices=tuple(transformed),
        faces=mesh.faces,
    )
    result.validate()
    return result


def rectangular_prism(
    width_mm: float,
    depth_mm: float,
    height_mm: float,
    *,
    bottom_z_mm: float = 0.0,
) -> MeshData:
    half_width = width_mm / 2.0
    half_depth = depth_mm / 2.0

    outline = (
        (-half_width, -half_depth),
        (half_width, -half_depth),
        (half_width, half_depth),
        (-half_width, half_depth),
    )

    return extrude_polygon(
        outline=outline,
        bottom_z_mm=bottom_z_mm,
        top_z_mm=bottom_z_mm + height_mm,
    )


def cylinder_mesh(
    radius_mm: float,
    length_mm: float,
    segments: int,
    *,
    axis: str = "Z",
) -> MeshData:
    if radius_mm <= 0:
        raise ValueError("radius_mm must be greater than zero.")

    if length_mm <= 0:
        raise ValueError("length_mm must be greater than zero.")

    if segments < 12:
        raise ValueError("Cylinder requires at least 12 segments.")

    circle = circle_points(
        diameter_mm=radius_mm * 2.0,
        segments=segments,
    )

    if axis == "Z":
        return extrude_polygon(
            outline=circle,
            bottom_z_mm=0.0,
            top_z_mm=length_mm,
        )

    z_axis_mesh = extrude_polygon(
        outline=circle,
        bottom_z_mm=-length_mm / 2.0,
        top_z_mm=length_mm / 2.0,
    )

    if axis == "X":
        return transform_mesh(
            z_axis_mesh,
            rotate_y_degrees=90.0,
        )

    if axis == "Y":
        return transform_mesh(
            z_axis_mesh,
            rotate_x_degrees=90.0,
        )

    raise ValueError(f"Unsupported cylinder axis: {axis}")


def square_tile_base(
    parameters: TileParameters,
) -> MeshData:
    return rectangular_prism(
        width_mm=parameters.tile_width_mm,
        depth_mm=parameters.tile_depth_mm,
        height_mm=parameters.tile_height_mm,
    )


def build_raised_tile_mesh(
    parameters: TileParameters,
) -> MeshData:
    base = square_tile_base(parameters)

    raised_shape = extrude_polygon(
        outline=shape_outline(parameters),
        bottom_z_mm=parameters.tile_height_mm,
        top_z_mm=(
            parameters.tile_height_mm
            + parameters.shape_height_mm
        ),
    )

    return combine_meshes(base, raised_shape)



def build_slot_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build a recessed capsule-shaped slot on a square tile.

    The core mesh creates the tile and a shallow raised rim. Blender adds
    a separate dark inset object so the recessed channel reads clearly.
    """

    base = square_tile_base(parameters)

    slot_length = parameters.shape_width_mm
    slot_width = max(
        8.0,
        min(
            parameters.shape_height_mm * 2.4,
            slot_length * 0.30,
        ),
    )

    rim_width = max(
        1.8,
        slot_width * 0.18,
    )

    rim_height = max(
        0.8,
        parameters.shape_height_mm * 0.22,
    )

    straight_length = max(
        1.0,
        slot_length - slot_width,
    )

    rail_length = straight_length
    rail_depth = rim_width

    top_rail = transform_mesh(
        rectangular_prism(
            width_mm=rail_length,
            depth_mm=rail_depth,
            height_mm=rim_height,
        ),
        translate_y_mm=(
            slot_width / 2.0
            + rim_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    bottom_rail = transform_mesh(
        rectangular_prism(
            width_mm=rail_length,
            depth_mm=rail_depth,
            height_mm=rim_height,
        ),
        translate_y_mm=-(
            slot_width / 2.0
            + rim_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    end_radius = (
        slot_width / 2.0
        + rim_width
    )

    left_end = transform_mesh(
        cylinder_mesh(
            radius_mm=end_radius,
            length_mm=rim_height,
            segments=parameters.circle_segments,
            axis="Z",
        ),
        translate_x_mm=-straight_length / 2.0,
        translate_z_mm=parameters.tile_height_mm,
    )

    right_end = transform_mesh(
        cylinder_mesh(
            radius_mm=end_radius,
            length_mm=rim_height,
            segments=parameters.circle_segments,
            axis="Z",
        ),
        translate_x_mm=straight_length / 2.0,
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        top_rail,
        bottom_rail,
        left_end,
        right_end,
    )

def build_hinge_mesh(
    parameters: TileParameters,
) -> MeshData:
    base = square_tile_base(parameters)

    barrel_length = parameters.shape_width_mm
    barrel_radius = max(
        2.0,
        parameters.shape_height_mm / 2.0,
    )
    barrel_center_z = (
        parameters.tile_height_mm
        + barrel_radius
    )

    segments = max(24, parameters.circle_segments)

    barrel = transform_mesh(
        cylinder_mesh(
            radius_mm=barrel_radius,
            length_mm=barrel_length,
            segments=segments,
            axis="Y",
        ),
        translate_z_mm=barrel_center_z,
    )

    knuckle_length = barrel_length * 0.18
    knuckle_radius = barrel_radius * 1.15

    knuckles: list[MeshData] = []

    for y_offset in (
        -barrel_length * 0.32,
        0.0,
        barrel_length * 0.32,
    ):
        knuckles.append(
            transform_mesh(
                cylinder_mesh(
                    radius_mm=knuckle_radius,
                    length_mm=knuckle_length,
                    segments=segments,
                    axis="Y",
                ),
                translate_y_mm=y_offset,
                translate_z_mm=barrel_center_z,
            )
        )

    pin = transform_mesh(
        cylinder_mesh(
            radius_mm=barrel_radius * 0.32,
            length_mm=barrel_length * 1.08,
            segments=segments,
            axis="Y",
        ),
        translate_z_mm=barrel_center_z,
    )

    leaf_width = barrel_radius * 2.2
    leaf_depth = barrel_length * 0.76
    leaf_height = max(1.0, parameters.shape_height_mm * 0.22)

    left_leaf = transform_mesh(
        rectangular_prism(
            width_mm=leaf_width,
            depth_mm=leaf_depth,
            height_mm=leaf_height,
        ),
        translate_x_mm=-(barrel_radius + leaf_width / 2.0),
        translate_z_mm=parameters.tile_height_mm,
    )

    right_leaf = transform_mesh(
        rectangular_prism(
            width_mm=leaf_width,
            depth_mm=leaf_depth,
            height_mm=leaf_height,
        ),
        translate_x_mm=barrel_radius + leaf_width / 2.0,
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        left_leaf,
        right_leaf,
        barrel,
        *knuckles,
        pin,
    )


def build_fold_mesh(
    parameters: TileParameters,
) -> MeshData:
    base = square_tile_base(parameters)

    panel_width = parameters.shape_width_mm
    panel_height = min(
        parameters.tile_depth_mm * 0.58,
        parameters.shape_width_mm,
    )
    panel_thickness = max(
        1.5,
        parameters.shape_height_mm,
    )
    fold_angle_degrees = 58.0

    panel = rectangular_prism(
        width_mm=panel_width,
        depth_mm=panel_thickness,
        height_mm=panel_height,
    )

    angle = math.radians(fold_angle_degrees)

    panel = transform_mesh(
        panel,
        rotate_x_degrees=fold_angle_degrees,
        translate_y_mm=(
            math.sin(angle) * panel_height * 0.05
        ),
        translate_z_mm=(
            parameters.tile_height_mm
            + math.sin(angle) * panel_thickness / 2.0
        ),
    )

    foot = transform_mesh(
        rectangular_prism(
            width_mm=panel_width * 1.08,
            depth_mm=panel_thickness * 2.4,
            height_mm=max(1.5, panel_thickness * 0.55),
        ),
        translate_y_mm=-(panel_thickness * 0.45),
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        foot,
        panel,
    )


def square_circle_ring_mesh(
    *,
    tile_width_mm: float,
    tile_depth_mm: float,
    hole_radius_mm: float,
    height_mm: float,
    segments: int,
) -> MeshData:
    if segments < 24:
        raise ValueError(
            "Aperture requires at least 24 segments."
        )

    half_width = tile_width_mm / 2.0
    half_depth = tile_depth_mm / 2.0

    inner_bottom: list[Point3D] = []
    outer_bottom: list[Point3D] = []
    inner_top: list[Point3D] = []
    outer_top: list[Point3D] = []

    for index in range(segments):
        angle = index * 2.0 * math.pi / segments
        cosine = math.cos(angle)
        sine = math.sin(angle)

        inner_x = hole_radius_mm * cosine
        inner_y = hole_radius_mm * sine

        square_scale = min(
            half_width / max(abs(cosine), 1e-9),
            half_depth / max(abs(sine), 1e-9),
        )

        outer_x = cosine * square_scale
        outer_y = sine * square_scale

        inner_bottom.append((inner_x, inner_y, 0.0))
        outer_bottom.append((outer_x, outer_y, 0.0))
        inner_top.append((inner_x, inner_y, height_mm))
        outer_top.append((outer_x, outer_y, height_mm))

    vertices = tuple(
        inner_bottom
        + outer_bottom
        + inner_top
        + outer_top
    )

    inner_bottom_offset = 0
    outer_bottom_offset = segments
    inner_top_offset = segments * 2
    outer_top_offset = segments * 3

    faces: list[tuple[int, ...]] = []

    for index in range(segments):
        next_index = (index + 1) % segments

        ib = inner_bottom_offset + index
        ibn = inner_bottom_offset + next_index
        ob = outer_bottom_offset + index
        obn = outer_bottom_offset + next_index

        it = inner_top_offset + index
        itn = inner_top_offset + next_index
        ot = outer_top_offset + index
        otn = outer_top_offset + next_index

        faces.append((ob, obn, ibn, ib))
        faces.append((it, itn, otn, ot))
        faces.append((ob, ot, otn, obn))
        faces.append((ibn, itn, it, ib))

    result = MeshData(
        vertices=vertices,
        faces=tuple(faces),
    )
    result.validate()
    return result


def build_aperture_mesh(
    parameters: TileParameters,
) -> MeshData:
    hole_radius = parameters.shape_width_mm / 2.0

    minimum_border = min(
        parameters.tile_width_mm,
        parameters.tile_depth_mm,
    ) * 0.08

    maximum_radius = (
        min(
            parameters.tile_width_mm,
            parameters.tile_depth_mm,
        )
        / 2.0
        - minimum_border
    )

    if hole_radius > maximum_radius:
        raise ValueError(
            "The aperture leaves too little material around the tile."
        )

    return square_circle_ring_mesh(
        tile_width_mm=parameters.tile_width_mm,
        tile_depth_mm=parameters.tile_depth_mm,
        hole_radius_mm=hole_radius,
        height_mm=parameters.tile_height_mm,
        segments=parameters.circle_segments,
    )


def droplet_surface_mesh(
    *,
    diameter_mm: float,
    rise_mm: float,
    base_z_mm: float,
    radial_segments: int,
    ring_segments: int = 14,
) -> MeshData:
    """Create a domed teardrop resembling water resting on a surface."""

    if diameter_mm <= 0:
        raise ValueError(
            "Droplet diameter must be greater than zero."
        )

    if rise_mm <= 0:
        raise ValueError(
            "Droplet rise must be greater than zero."
        )

    if radial_segments < 24:
        raise ValueError(
            "Droplet requires at least 24 radial segments."
        )

    radius = diameter_mm / 2.0

    vertices: list[Point3D] = []
    faces: list[tuple[int, ...]] = []

    # Build nested teardrop rings. The outer ring sits on the tile.
    for ring_index in range(ring_segments):
        fraction = 1.0 - ring_index / ring_segments

        # Rounded water profile: low at the perimeter and high at center.
        z = (
            base_z_mm
            + rise_mm
            * (1.0 - fraction * fraction)
        )

        for radial_index in range(radial_segments):
            angle = (
                radial_index
                * 2.0
                * math.pi
                / radial_segments
            )

            # A softened cardioid creates a rounded rear body and a
            # tapered forward point without collapsing vertices.
            boundary_radius = radius * (
                0.08
                + 0.92
                * (1.0 - math.sin(angle))
                / 2.0
            )

            local_radius = boundary_radius * fraction

            x = local_radius * math.cos(angle)
            y = local_radius * math.sin(angle)

            # Move the body slightly backward so the pointed end reads
            # as a droplet rather than a heart.
            y -= radius * 0.16 * fraction

            vertices.append((x, y, z))

    apex_index = len(vertices)
    vertices.append(
        (
            0.0,
            0.0,
            base_z_mm + rise_mm,
        )
    )

    for ring_index in range(ring_segments - 1):
        current_offset = (
            ring_index * radial_segments
        )
        next_offset = (
            (ring_index + 1) * radial_segments
        )

        for radial_index in range(radial_segments):
            next_radial = (
                radial_index + 1
            ) % radial_segments

            faces.append(
                (
                    current_offset + radial_index,
                    current_offset + next_radial,
                    next_offset + next_radial,
                    next_offset + radial_index,
                )
            )

    final_ring_offset = (
        ring_segments - 1
    ) * radial_segments

    for radial_index in range(radial_segments):
        next_radial = (
            radial_index + 1
        ) % radial_segments

        faces.append(
            (
                final_ring_offset + radial_index,
                final_ring_offset + next_radial,
                apex_index,
            )
        )

    faces.append(
        tuple(
            reversed(range(radial_segments))
        )
    )

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )
    result.validate()
    return result


def build_lens_mesh(
    parameters: TileParameters,
) -> MeshData:
    base = square_tile_base(parameters)

    lens_rise = min(
        parameters.shape_height_mm,
        parameters.shape_width_mm * 0.30,
    )

    mount_height = max(
        0.6,
        lens_rise * 0.10,
    )

    mount = transform_mesh(
        cylinder_mesh(
            radius_mm=parameters.shape_width_mm * 0.37,
            length_mm=mount_height,
            segments=parameters.circle_segments,
            axis="Z",
        ),
        translate_y_mm=-parameters.shape_width_mm * 0.07,
        translate_z_mm=parameters.tile_height_mm,
    )

    droplet = droplet_surface_mesh(
        diameter_mm=parameters.shape_width_mm,
        rise_mm=lens_rise,
        base_z_mm=(
            parameters.tile_height_mm
            + mount_height
        ),
        radial_segments=parameters.circle_segments,
    )

    return combine_meshes(
        base,
        mount,
        droplet,
    )


def build_mirror_mesh(

    parameters: TileParameters,
) -> MeshData:
    base = square_tile_base(parameters)

    mirror_width = parameters.shape_width_mm
    mirror_depth = mirror_width
    mirror_thickness = max(
        0.8,
        parameters.shape_height_mm * 0.28,
    )

    frame_width = max(
        2.0,
        mirror_width * 0.07,
    )
    frame_height = max(
        1.5,
        parameters.shape_height_mm * 0.55,
    )

    mirror = transform_mesh(
        rectangular_prism(
            width_mm=mirror_width,
            depth_mm=mirror_depth,
            height_mm=mirror_thickness,
        ),
        translate_z_mm=(
            parameters.tile_height_mm
            + frame_height
        ),
    )

    outer_width = mirror_width + frame_width * 2.0
    outer_depth = mirror_depth + frame_width * 2.0

    top_frame = transform_mesh(
        rectangular_prism(
            width_mm=outer_width,
            depth_mm=frame_width,
            height_mm=frame_height,
        ),
        translate_y_mm=(
            mirror_depth / 2.0
            + frame_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    bottom_frame = transform_mesh(
        rectangular_prism(
            width_mm=outer_width,
            depth_mm=frame_width,
            height_mm=frame_height,
        ),
        translate_y_mm=-(
            mirror_depth / 2.0
            + frame_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    left_frame = transform_mesh(
        rectangular_prism(
            width_mm=frame_width,
            depth_mm=mirror_depth,
            height_mm=frame_height,
        ),
        translate_x_mm=-(
            mirror_width / 2.0
            + frame_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    right_frame = transform_mesh(
        rectangular_prism(
            width_mm=frame_width,
            depth_mm=mirror_depth,
            height_mm=frame_height,
        ),
        translate_x_mm=(
            mirror_width / 2.0
            + frame_width / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        mirror,
        top_frame,
        bottom_frame,
        left_frame,
        right_frame,
    )


def build_tile_mesh(
    parameters: TileParameters,
) -> MeshData:
    parameters.validate()

    if parameters.shape in RAISED_SHAPES:
        return build_raised_tile_mesh(parameters)

    if parameters.shape is ShapeType.SLOT:
        return build_slot_mesh(parameters)

    if parameters.shape is ShapeType.HINGE:
        return build_hinge_mesh(parameters)

    if parameters.shape is ShapeType.FOLD:
        return build_fold_mesh(parameters)

    if parameters.shape is ShapeType.APERTURE:
        return build_aperture_mesh(parameters)

    if parameters.shape is ShapeType.LENS:
        return build_lens_mesh(parameters)

    if parameters.shape is ShapeType.MIRROR:
        return build_mirror_mesh(parameters)

    raise ValueError(
        f"Unsupported operational primitive: {parameters.shape}"
    )
