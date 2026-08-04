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


def rotate_mesh_z(
    mesh: MeshData,
    angle_degrees: float,
) -> MeshData:
    """Rotate a mesh around the vertical Z axis."""

    angle = math.radians(angle_degrees)
    cosine = math.cos(angle)
    sine = math.sin(angle)

    result = MeshData(
        vertices=tuple(
            (
                vertex[0] * cosine - vertex[1] * sine,
                vertex[0] * sine + vertex[1] * cosine,
                vertex[2],
            )
            for vertex in mesh.vertices
        ),
        faces=mesh.faces,
    )

    result.validate()
    return result


def rotational_profile_mesh(
    *,
    profile: tuple[tuple[float, float], ...],
    segments: int,
) -> MeshData:
    """Revolve a radius/Z profile around the vertical axis.

    The profile must begin and end on the rotation axis or include an
    explicit bottom radius suitable for closing the mesh.
    """

    if len(profile) < 3:
        raise ValueError(
            "A rotational profile requires at least three points."
        )

    if segments < 24:
        raise ValueError(
            "A rotational profile requires at least 24 segments."
        )

    vertices: list[Point3D] = []
    faces: list[tuple[int, ...]] = []

    ring_indices: list[list[int]] = []

    for radius_mm, z_mm in profile:
        if radius_mm < 0:
            raise ValueError(
                "Profile radius cannot be negative."
            )

        if math.isclose(radius_mm, 0.0, abs_tol=1e-9):
            index = len(vertices)
            vertices.append((0.0, 0.0, z_mm))
            ring_indices.append([index])
            continue

        ring: list[int] = []

        for segment_index in range(segments):
            angle = (
                2.0
                * math.pi
                * segment_index
                / segments
            )

            ring.append(len(vertices))
            vertices.append(
                (
                    radius_mm * math.cos(angle),
                    radius_mm * math.sin(angle),
                    z_mm,
                )
            )

        ring_indices.append(ring)

    for first_ring, second_ring in zip(
        ring_indices,
        ring_indices[1:],
    ):
        first_is_point = len(first_ring) == 1
        second_is_point = len(second_ring) == 1

        if first_is_point and second_is_point:
            continue

        if first_is_point:
            point = first_ring[0]

            for index in range(segments):
                next_index = (index + 1) % segments
                faces.append(
                    (
                        point,
                        second_ring[index],
                        second_ring[next_index],
                    )
                )

            continue

        if second_is_point:
            point = second_ring[0]

            for index in range(segments):
                next_index = (index + 1) % segments
                faces.append(
                    (
                        first_ring[index],
                        point,
                        first_ring[next_index],
                    )
                )

            continue

        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append(
                (
                    first_ring[index],
                    second_ring[index],
                    second_ring[next_index],
                    first_ring[next_index],
                )
            )

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )
    result.validate()
    return result


def build_water_droplet_mesh(
    *,
    diameter_mm: float,
    rise_mm: float,
    base_z_mm: float,
    radial_segments: int,
    profile_segments: int = 18,
) -> MeshData:
    """Build a circular, rotationally symmetric surface-tension droplet.

    The footprint is circular from above. The surface blends directly
    into the supporting plane and reaches its maximum height at center.
    """

    if diameter_mm <= 0:
        raise ValueError(
            "Droplet diameter must be greater than zero."
        )

    if rise_mm <= 0:
        raise ValueError(
            "Droplet rise must be greater than zero."
        )

    radius = diameter_mm / 2.0

    profile: list[tuple[float, float]] = [
        (0.0, base_z_mm),
        (radius, base_z_mm),
    ]

    # Travel from the perimeter toward the center. A smoothstep-style
    # curve produces a gentle meniscus and a rounded central crown.
    for index in range(1, profile_segments):
        fraction = index / profile_segments
        local_radius = radius * (1.0 - fraction)

        smooth = (
            fraction
            * fraction
            * (3.0 - 2.0 * fraction)
        )

        crown = smooth ** 0.82

        profile.append(
            (
                local_radius,
                base_z_mm + rise_mm * crown,
            )
        )

    profile.append(
        (
            0.0,
            base_z_mm + rise_mm,
        )
    )

    return rotational_profile_mesh(
        profile=tuple(profile),
        segments=radial_segments,
    )


def build_light_bulb_mesh(
    *,
    bulb_radius_mm: float,
    bulb_height_mm: float,
    neck_radius_mm: float,
    neck_height_mm: float,
    base_z_mm: float,
    radial_segments: int,
) -> MeshData:
    """Build a squat bulb with a short neck and rounded crown."""

    if bulb_radius_mm <= 0:
        raise ValueError(
            "Bulb radius must be greater than zero."
        )

    if bulb_height_mm <= 0:
        raise ValueError(
            "Bulb height must be greater than zero."
        )

    if neck_radius_mm <= 0:
        raise ValueError(
            "Neck radius must be greater than zero."
        )

    neck_top = base_z_mm + neck_height_mm
    crown_top = neck_top + bulb_height_mm

    profile = (
        (0.0, base_z_mm),
        (neck_radius_mm, base_z_mm),
        (neck_radius_mm, neck_top),
        (bulb_radius_mm * 0.74, neck_top + bulb_height_mm * 0.08),
        (bulb_radius_mm * 0.94, neck_top + bulb_height_mm * 0.30),
        (bulb_radius_mm, neck_top + bulb_height_mm * 0.48),
        (bulb_radius_mm * 0.92, neck_top + bulb_height_mm * 0.70),
        (bulb_radius_mm * 0.66, neck_top + bulb_height_mm * 0.90),
        (0.0, crown_top),
    )

    return rotational_profile_mesh(
        profile=profile,
        segments=radial_segments,
    )


def build_sensor_dome_mesh(
    *,
    sphere_radius_mm: float,
    exposed_height_mm: float,
    base_z_mm: float,
    radial_segments: int,
    profile_segments: int = 12,
) -> MeshData:
    """Build the exposed upper portion of a sphere."""

    if sphere_radius_mm <= 0:
        raise ValueError(
            "Sensor radius must be greater than zero."
        )

    exposed_height_mm = min(
        exposed_height_mm,
        sphere_radius_mm,
    )

    profile: list[tuple[float, float]] = [
        (0.0, base_z_mm),
    ]

    for index in range(profile_segments + 1):
        fraction = index / profile_segments

        z_from_center = (
            sphere_radius_mm
            - exposed_height_mm
            + exposed_height_mm * fraction
        )

        ring_radius = math.sqrt(
            max(
                0.0,
                sphere_radius_mm ** 2
                - z_from_center ** 2,
            )
        )

        profile.append(
            (
                ring_radius,
                base_z_mm
                + exposed_height_mm * fraction,
            )
        )

    profile.append(
        (
            0.0,
            base_z_mm + exposed_height_mm,
        )
    )

    return rotational_profile_mesh(
        profile=tuple(profile),
        segments=radial_segments,
    )


def build_lens_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build OW09 as a uniform surface-tension lens.

    From above, the lens is perfectly circular. Its convex surface rises
    directly from the tile without a separate pedestal.
    """

    base = square_tile_base(parameters)

    diameter_mm = parameters.shape_width_mm * 0.78

    rise_mm = min(
        parameters.shape_height_mm * 1.55,
        diameter_mm * 0.28,
    )

    droplet = build_water_droplet_mesh(
        diameter_mm=diameter_mm,
        rise_mm=rise_mm,
        base_z_mm=parameters.tile_height_mm,
        radial_segments=max(
            48,
            parameters.circle_segments,
        ),
    )

    return combine_meshes(
        base,
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




def build_light_source_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build OW11 as a low, squat bulb with a short neck."""

    base = square_tile_base(parameters)

    bulb_radius_mm = parameters.shape_width_mm * 0.31

    bulb_height_mm = min(
        parameters.shape_height_mm * 2.15,
        bulb_radius_mm * 1.30,
    )

    neck_radius_mm = bulb_radius_mm * 0.48

    neck_height_mm = max(
        2.0,
        parameters.shape_height_mm * 0.38,
    )

    mounting_ring = transform_mesh(
        cylinder_mesh(
            radius_mm=bulb_radius_mm * 0.72,
            length_mm=max(
                1.0,
                parameters.shape_height_mm * 0.18,
            ),
            segments=max(
                48,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    bulb = build_light_bulb_mesh(
        bulb_radius_mm=bulb_radius_mm,
        bulb_height_mm=bulb_height_mm,
        neck_radius_mm=neck_radius_mm,
        neck_height_mm=neck_height_mm,
        base_z_mm=(
            parameters.tile_height_mm
            + max(
                1.0,
                parameters.shape_height_mm * 0.18,
            )
        ),
        radial_segments=max(
            48,
            parameters.circle_segments,
        ),
    )

    return combine_meshes(
        base,
        mounting_ring,
        bulb,
    )


def build_weight_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build OW12 as a cubic mass rotated 45 degrees on the tile."""

    base = square_tile_base(parameters)

    cube_size_mm = min(
        parameters.shape_width_mm * 0.58,
        parameters.tile_width_mm * 0.42,
        parameters.tile_depth_mm * 0.42,
    )

    cube = rectangular_prism(
        width_mm=cube_size_mm,
        depth_mm=cube_size_mm,
        height_mm=cube_size_mm,
    )

    cube = rotate_mesh_z(
        cube,
        angle_degrees=45.0,
    )

    cube = transform_mesh(
        cube,
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        cube,
    )

def build_threshold_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build a raised boundary extending across the tile."""

    base = square_tile_base(parameters)

    threshold_length = min(
        parameters.shape_width_mm,
        parameters.tile_width_mm * 0.86,
    )

    threshold_depth = max(
        5.0,
        min(
            parameters.shape_height_mm * 2.0,
            parameters.tile_depth_mm * 0.22,
        ),
    )

    threshold_height = max(
        2.0,
        parameters.shape_height_mm,
    )

    threshold = transform_mesh(
        rectangular_prism(
            width_mm=threshold_length,
            depth_mm=threshold_depth,
            height_mm=threshold_height,
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    approach_depth = threshold_depth * 0.42
    approach_height = max(
        0.8,
        threshold_height * 0.22,
    )

    front_approach = transform_mesh(
        rectangular_prism(
            width_mm=threshold_length,
            depth_mm=approach_depth,
            height_mm=approach_height,
        ),
        translate_y_mm=-(
            threshold_depth / 2.0
            + approach_depth / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    rear_approach = transform_mesh(
        rectangular_prism(
            width_mm=threshold_length,
            depth_mm=approach_depth,
            height_mm=approach_height,
        ),
        translate_y_mm=(
            threshold_depth / 2.0
            + approach_depth / 2.0
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        front_approach,
        threshold,
        rear_approach,
    )



def build_sensor_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build OW14 as a small spherical detector seated in a recess."""

    base = square_tile_base(parameters)

    recess_radius_mm = parameters.shape_width_mm * 0.27

    recess_depth_mm = max(
        0.8,
        parameters.shape_height_mm * 0.16,
    )

    outer_ring = transform_mesh(
        cylinder_mesh(
            radius_mm=recess_radius_mm,
            length_mm=recess_depth_mm,
            segments=max(
                48,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_z_mm=parameters.tile_height_mm,
    )

    detector_radius_mm = parameters.shape_width_mm * 0.15

    exposed_height_mm = detector_radius_mm * 0.58

    detector = build_sensor_dome_mesh(
        sphere_radius_mm=detector_radius_mm,
        exposed_height_mm=exposed_height_mm,
        base_z_mm=(
            parameters.tile_height_mm
            + recess_depth_mm * 0.42
        ),
        radial_segments=max(
            48,
            parameters.circle_segments,
        ),
    )

    return combine_meshes(
        base,
        outer_ring,
        detector,
    )

def build_handle_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build an elevated bridge handle supported at both ends."""

    base = square_tile_base(parameters)

    handle_span = parameters.shape_width_mm

    post_width = max(
        4.0,
        min(
            parameters.shape_height_mm,
            handle_span * 0.14,
        ),
    )

    post_depth = max(
        5.0,
        post_width * 1.25,
    )

    post_height = max(
        12.0,
        parameters.shape_height_mm * 3.0,
    )

    support_offset = (
        handle_span / 2.0
        - post_width / 2.0
    )

    left_post = transform_mesh(
        rectangular_prism(
            width_mm=post_width,
            depth_mm=post_depth,
            height_mm=post_height,
        ),
        translate_x_mm=-support_offset,
        translate_z_mm=parameters.tile_height_mm,
    )

    right_post = transform_mesh(
        rectangular_prism(
            width_mm=post_width,
            depth_mm=post_depth,
            height_mm=post_height,
        ),
        translate_x_mm=support_offset,
        translate_z_mm=parameters.tile_height_mm,
    )

    grip_width = handle_span
    grip_depth = post_depth
    grip_height = max(
        4.0,
        post_width,
    )

    grip = transform_mesh(
        rectangular_prism(
            width_mm=grip_width,
            depth_mm=grip_depth,
            height_mm=grip_height,
        ),
        translate_z_mm=(
            parameters.tile_height_mm
            + post_height
        ),
    )

    left_foot = transform_mesh(
        cylinder_mesh(
            radius_mm=post_depth * 0.72,
            length_mm=max(1.5, post_width * 0.34),
            segments=parameters.circle_segments,
            axis="Z",
        ),
        translate_x_mm=-support_offset,
        translate_z_mm=parameters.tile_height_mm,
    )

    right_foot = transform_mesh(
        cylinder_mesh(
            radius_mm=post_depth * 0.72,
            length_mm=max(1.5, post_width * 0.34),
            segments=parameters.circle_segments,
            axis="Z",
        ),
        translate_x_mm=support_offset,
        translate_z_mm=parameters.tile_height_mm,
    )

    return combine_meshes(
        base,
        left_foot,
        right_foot,
        left_post,
        right_post,
        grip,
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

    if parameters.shape is ShapeType.LIGHT_SOURCE:
        return build_light_source_mesh(parameters)

    if parameters.shape is ShapeType.WEIGHT:
        return build_weight_mesh(parameters)

    if parameters.shape is ShapeType.THRESHOLD:
        return build_threshold_mesh(parameters)

    if parameters.shape is ShapeType.SENSOR:
        return build_sensor_mesh(parameters)

    if parameters.shape is ShapeType.HANDLE:
        return build_handle_mesh(parameters)

    raise ValueError(
        f"Unsupported operational primitive: {parameters.shape}"
    )
