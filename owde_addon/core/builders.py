from __future__ import annotations

import math
from collections.abc import Sequence

from .mesh import MeshData
from .models import ShapeType, TileParameters


Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


RAISED_OUTLINE_SHAPES = {
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.SQUARE,
    ShapeType.HEXAGON,
}


# =====================================================================
# General polygon and mesh utilities
# =====================================================================

def regular_polygon_points(
    sides: int,
    diameter_mm: float,
    rotation_degrees: float = 90.0,
) -> tuple[Point2D, ...]:
    if sides < 3:
        raise ValueError(
            "A polygon requires at least three sides."
        )

    if diameter_mm <= 0:
        raise ValueError(
            "diameter_mm must be greater than zero."
        )

    radius = diameter_mm / 2.0
    rotation = math.radians(rotation_degrees)

    return tuple(
        (
            radius
            * math.cos(
                rotation
                + index
                * 2.0
                * math.pi
                / sides
            ),
            radius
            * math.sin(
                rotation
                + index
                * 2.0
                * math.pi
                / sides
            ),
        )
        for index in range(sides)
    )


def circle_points(
    diameter_mm: float,
    segments: int,
) -> tuple[Point2D, ...]:
    if segments < 24:
        raise ValueError(
            "Circle requires at least 24 segments."
        )

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
        # Flat-top canonical orientation:
        # top and bottom sides parallel to tile edges.
        return regular_polygon_points(
            sides=6,
            diameter_mm=parameters.shape_width_mm,
            rotation_degrees=0.0,
        )

    raise ValueError(
        f"{parameters.shape.value} does not use a polygon outline."
    )


def extrude_polygon(
    outline: Sequence[Point2D],
    bottom_z_mm: float,
    top_z_mm: float,
) -> MeshData:
    if len(outline) < 3:
        raise ValueError(
            "Outline requires at least three points."
        )

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

    faces.append(
        tuple(reversed(range(count)))
    )

    faces.append(
        tuple(range(count, count * 2))
    )

    for index in range(count):
        next_index = (
            index + 1
        ) % count

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


def combine_meshes(
    *meshes: MeshData,
) -> MeshData:
    vertices: list[Point3D] = []
    faces: list[tuple[int, ...]] = []

    offset = 0

    for mesh in meshes:
        mesh.validate()
        vertices.extend(mesh.vertices)

        for face in mesh.faces:
            faces.append(
                tuple(
                    index + offset
                    for index in face
                )
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
    x_angle = math.radians(
        rotate_x_degrees
    )

    y_angle = math.radians(
        rotate_y_degrees
    )

    z_angle = math.radians(
        rotate_z_degrees
    )

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
        raise ValueError(
            "radius_mm must be greater than zero."
        )

    if length_mm <= 0:
        raise ValueError(
            "length_mm must be greater than zero."
        )

    if segments < 12:
        raise ValueError(
            "Cylinder requires at least 12 segments."
        )

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

    z_mesh = extrude_polygon(
        outline=circle,
        bottom_z_mm=-length_mm / 2.0,
        top_z_mm=length_mm / 2.0,
    )

    if axis == "X":
        return transform_mesh(
            z_mesh,
            rotate_y_degrees=90.0,
        )

    if axis == "Y":
        return transform_mesh(
            z_mesh,
            rotate_x_degrees=90.0,
        )

    raise ValueError(
        f"Unsupported cylinder axis: {axis}"
    )


def rotational_profile_mesh(
    *,
    profile: tuple[tuple[float, float], ...],
    segments: int,
) -> MeshData:
    if len(profile) < 3:
        raise ValueError(
            "A rotational profile requires at least three points."
        )

    if segments < 24:
        raise ValueError(
            "A rotational profile requires at least 24 segments."
        )

    vertices: list[Point3D] = []
    rings: list[list[int]] = []
    faces: list[tuple[int, ...]] = []

    for radius_mm, z_mm in profile:
        if math.isclose(
            radius_mm,
            0.0,
            abs_tol=1e-9,
        ):
            index = len(vertices)
            vertices.append(
                (0.0, 0.0, z_mm)
            )
            rings.append([index])
            continue

        ring: list[int] = []

        for segment in range(segments):
            angle = (
                segment
                * 2.0
                * math.pi
                / segments
            )

            ring.append(
                len(vertices)
            )

            vertices.append(
                (
                    radius_mm
                    * math.cos(angle),
                    radius_mm
                    * math.sin(angle),
                    z_mm,
                )
            )

        rings.append(ring)

    for lower, upper in zip(
        rings,
        rings[1:],
    ):
        lower_point = len(lower) == 1
        upper_point = len(upper) == 1

        if lower_point and upper_point:
            continue

        if lower_point:
            point = lower[0]

            for index in range(segments):
                next_index = (
                    index + 1
                ) % segments

                faces.append(
                    (
                        point,
                        upper[index],
                        upper[next_index],
                    )
                )

            continue

        if upper_point:
            point = upper[0]

            for index in range(segments):
                next_index = (
                    index + 1
                ) % segments

                faces.append(
                    (
                        lower[index],
                        point,
                        lower[next_index],
                    )
                )

            continue

        for index in range(segments):
            next_index = (
                index + 1
            ) % segments

            faces.append(
                (
                    lower[index],
                    upper[index],
                    upper[next_index],
                    lower[next_index],
                )
            )

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )

    result.validate()
    return result


def chamfered_box_mesh(
    *,
    width_mm: float,
    depth_mm: float,
    height_mm: float,
    chamfer_mm: float,
    bottom_z_mm: float,
) -> MeshData:
    """Create a box with clipped vertical corners.
    The eight-point outline gives the Weight a manufactured, machined
    character while remaining simple and watertight.
    """
    if width_mm <= 0:
        raise ValueError(
            "width_mm must be greater than zero."
        )
    if depth_mm <= 0:
        raise ValueError(
            "depth_mm must be greater than zero."
        )
    if height_mm <= 0:
        raise ValueError(
            "height_mm must be greater than zero."
        )
    maximum_chamfer = min(
        width_mm,
        depth_mm,
    ) / 4.0
    chamfer = min(
        max(chamfer_mm, 0.0),
        maximum_chamfer,
    )
    half_width = width_mm / 2.0
    half_depth = depth_mm / 2.0
    outline = (
        (-half_width + chamfer, -half_depth),
        (half_width - chamfer, -half_depth),
        (half_width, -half_depth + chamfer),
        (half_width, half_depth - chamfer),
        (half_width - chamfer, half_depth),
        (-half_width + chamfer, half_depth),
        (-half_width, half_depth - chamfer),
        (-half_width, -half_depth + chamfer),
    )
    return extrude_polygon(
        outline=outline,
        bottom_z_mm=bottom_z_mm,
        top_z_mm=bottom_z_mm + height_mm,
    )


def scale_outline(
    outline: Sequence[Point2D],
    scale: float,
) -> tuple[Point2D, ...]:
    """Scale a centered 2D polygon around the origin."""

    if scale <= 0:
        raise ValueError(
            "Outline scale must be greater than zero."
        )

    return tuple(
        (
            x * scale,
            y * scale,
        )
        for x, y in outline
    )


def chamfered_extruded_polygon(
    *,
    outline: Sequence[Point2D],
    bottom_z_mm: float,
    height_mm: float,
    chamfer_mm: float,
) -> MeshData:
    """Extrude a polygon with a small canonical top-edge chamfer."""

    if height_mm <= 0:
        raise ValueError(
            "height_mm must be greater than zero."
        )

    if len(outline) < 3:
        raise ValueError(
            "Outline requires at least three points."
        )

    chamfer = min(
        max(chamfer_mm, 0.0),
        height_mm * 0.45,
    )

    maximum_radius = max(
        math.hypot(x, y)
        for x, y in outline
    )

    if maximum_radius <= 0:
        raise ValueError(
            "Outline must have non-zero radius."
        )

    inset_scale = max(
        0.70,
        1.0 - chamfer / maximum_radius,
    )

    middle_z = (
        bottom_z_mm
        + height_mm
        - chamfer
    )

    top_z = (
        bottom_z_mm
        + height_mm
    )

    lower = tuple(outline)
    middle = tuple(outline)
    upper = scale_outline(
        outline,
        inset_scale,
    )

    count = len(lower)

    vertices = (
        tuple(
            (x, y, bottom_z_mm)
            for x, y in lower
        )
        + tuple(
            (x, y, middle_z)
            for x, y in middle
        )
        + tuple(
            (x, y, top_z)
            for x, y in upper
        )
    )

    faces: list[tuple[int, ...]] = []

    faces.append(
        tuple(
            reversed(
                range(count)
          )
        )
    )

    for index in range(count):
        next_index = (
            index + 1
        ) % count

        faces.append(
            (
                index,
                next_index,
                count + next_index,
                count + index,
            )
        )

    for index in range(count):
        next_index = (
            index + 1
        ) % count

        faces.append(
            (
                count + index,
                count + next_index,
                count * 2 + next_index,
                count * 2 + index,
            )
        )

    faces.append(
        tuple(
            range(
                count * 2,
                count * 3,
            )
        )
    )

    result = MeshData(
        vertices=vertices,
        faces=tuple(faces),
    )

    result.validate()
    return result


def capsule_outline(
    *,
    length_mm: float,
    width_mm: float,
    segments_per_end: int = 24,
) -> tuple[Point2D, ...]:
    """Create a horizontal capsule outline."""

    if length_mm <= width_mm:
        raise ValueError(
            "Capsule length must exceed width."
        )

    if width_mm <= 0:
        raise ValueError(
            "Capsule width must be greater than zero."
        )

    radius = width_mm / 2.0
    half_straight = (
        length_mm - width_mm
    ) / 2.0

    points: list[Point2D] = []

    for index in range(
        segments_per_end + 1
    ):
        angle = (
            -math.pi / 2.0
            + index
            * math.pi
            / segments_per_end
        )

        points.append(
            (
                half_straight
                + radius * math.cos(angle),
                radius * math.sin(angle),
            )
        )

    for index in range(
        segments_per_end + 1
    ):
        angle = (
            math.pi / 2.0
            + index
            * math.pi
            / segments_per_end
        )

        points.append(
            (
                -half_straight
                + radius * math.cos(angle),
            radius * math.sin(angle),
            )
        )

    return tuple(points)


def annular_cylinder_mesh(
    *,
    outer_radius_mm: float,
    inner_radius_mm: float,
    height_mm: float,
    bottom_z_mm: float,
    segments: int,
) -> MeshData:
    """Create a watertight annular bezel."""

    if outer_radius_mm <= inner_radius_mm:
        raise ValueError(
            "Outer radius must exceed inner radius."
        )

    if inner_radius_mm <= 0:
        raise ValueError(
            "Inner radius must be greater than zero."
        )

    vertices: list[Point3D] = []

    for z in (
        bottom_z_mm,
        bottom_z_mm + height_mm,
    ):
        for radius in (
            outer_radius_mm,
            inner_radius_mm,
        ):
            for index in range(segments):
                angle = (
                    2.0
                    * math.pi
                    * index
                    / segments
                )

                vertices.append(
                    (
                        radius * math.cos(angle),
                        radius * math.sin(angle),
                        z,
                    )
                )

    outer_bottom = 0
    inner_bottom = segments
    outer_top = segments * 2
    inner_top = segments * 3

    faces: list[tuple[int, ...]] = []

    for index in range(segments):
        next_index = (
            index + 1
        ) % segments

        # Outer wall.
        faces.append(
            (
                outer_bottom + index,
                outer_bottom + next_index,
                outer_top + next_index,
                outer_top + index,
            )
        )

        # Inner wall.
        faces.append(
            (
                inner_bottom + next_index,
                inner_bottom + index,
                inner_top + index,
                inner_top + next_index,
            )
        )

        # Top annulus.
        faces.append(
            (
                outer_top + index,
                outer_top + next_index,
                inner_top + next_index,
                inner_top + index,
            )
        )

        # Bottom annulus.
        faces.append(
            (
                outer_bottom + next_index,
                outer_bottom + index,
                inner_bottom + index,
                inner_bottom + next_index,
            )
        )

    result = MeshData(
        vertices=tuple(vertices),
        faces=tuple(faces),
    )

    result.validate()
    return result


# =====================================================================
# Canonical invariant substrate
# =====================================================================

def build_base_tile_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build the invariant Operational Worlds substrate.

    Every primitive receives this exact rectangular base. Primitive
    identity is introduced only through feature geometry placed above
    the canonical top surface.

    The base is:

    - rectangular;
    - centered at the world origin;
    - aligned to X and Y;
    - flat on Z=0;
    - identical for all fifteen primitives.
    """

    return rectangular_prism(
        width_mm=parameters.tile_width_mm,
        depth_mm=parameters.tile_depth_mm,
        height_mm=parameters.tile_height_mm,
        bottom_z_mm=0.0,
    )


# Backward-compatible name used by earlier OWDE code.
def square_tile_base(
    parameters: TileParameters,
) -> MeshData:
    return build_base_tile_mesh(parameters)


# =====================================================================
# Primitive feature generators
# =====================================================================


def build_raised_outline_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW01-OW04 raised geometric bosses.

    All four use the same height and top-edge treatment. Primitive
    identity comes only from plan geometry.
    """

    outline = shape_outline(parameters)

    feature_height_mm = (
        parameters.shape_height_mm
    )

    chamfer_mm = max(
        0.6,
        min(
            feature_height_mm * 0.22,
            parameters.shape_width_mm * 0.025,
        ),
    )

    return chamfered_extruded_polygon(
        outline=outline,
        bottom_z_mm=parameters.tile_height_mm,
        height_mm=feature_height_mm,
        chamfer_mm=chamfer_mm,
    )


def build_slot_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW05 as a restrained capsule-shaped slot surround.

    The dark inset remains a separately finished component. The
    canonical structural feature is a shallow capsule lip.
    """

    slot_length_mm = (
        parameters.shape_width_mm
    )

    slot_width_mm = max(
        8.0,
        min(
            parameters.shape_width_mm * 0.22,
            parameters.shape_height_mm * 2.6,
        ),
    )

    lip_extra_mm = max(
        1.8,
        slot_width_mm * 0.15,
    )

    outer_outline = capsule_outline(
        length_mm=(
            slot_length_mm
            + lip_extra_mm * 2.0
        ),
        width_mm=(
            slot_width_mm
            + lip_extra_mm * 2.0
        ),
        segments_per_end=max(
            18,
            parameters.circle_segments // 4,
        ),
    )

    lip_height_mm = max(
        0.9,
        parameters.shape_height_mm * 0.20,
    )

    return chamfered_extruded_polygon(
        outline=outer_outline,
        bottom_z_mm=parameters.tile_height_mm,
        height_mm=lip_height_mm,
        chamfer_mm=min(
            0.45,
            lip_height_mm * 0.35,
        ),
    )



def extrude_yz_profile_along_x(
    *,
    profile_yz: Sequence[tuple[float, float]],
    width_mm: float,
) -> MeshData:
    """Extrude a closed Y/Z profile across X.

    Used for canonical bent-sheet and ramp-like geometry where the
    operational section is easier to define in side elevation.
    """

    if len(profile_yz) < 3:
        raise ValueError(
            "Profile requires at least three points."
        )

    if width_mm <= 0:
        raise ValueError(
            "width_mm must be greater than zero."
        )

    half_width = width_mm / 2.0
    count = len(profile_yz)

    left = tuple(
        (
            -half_width,
            y,
            z,
        )
        for y, z in profile_yz
    )

    right = tuple(
        (
            half_width,
            y,
            z,
        )
        for y, z in profile_yz
    )

    vertices = left + right
    faces: list[tuple[int, ...]] = []

    faces.append(
        tuple(
            reversed(
                range(count)
            )
        )
    )

    faces.append(
        tuple(
            range(
                count,
                count * 2,
            )
        )
    )

    for index in range(count):
        next_index = (
            index + 1
        ) % count

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


def build_hinge_feature(
    parameters: TileParameters,
) -> MeshData:
    """Canonical OW06 fixed hinge.

    The canonical prototype communicates hinge/rotation through a
    continuous barrel, paired leaves, and three raised knuckle bands.

    It intentionally does not model a free-moving pin. That distinction
    belongs to a later functional-mechanism revision.
    """

    hinge_length_mm = (
        parameters.shape_width_mm
    )

    barrel_radius_mm = max(
        3.4,
        parameters.shape_height_mm * 0.72,
    )

    leaf_thickness_mm = max(
        1.5,
        parameters.shape_height_mm * 0.27,
    )

    leaf_width_mm = max(
        11.0,
        parameters.shape_width_mm * 0.23,
    )

    # Sink the hinge very slightly into the substrate. This makes the
    # physical relationship unambiguously intersecting for fabrication.
    embed_mm = max(
        0.35,
        parameters.shape_height_mm * 0.07,
    )

    base_z_mm = (
        parameters.tile_height_mm
        - embed_mm
    )

    barrel_center_z_mm = (
        parameters.tile_height_mm
        + barrel_radius_mm * 0.82
    )

    barrel = transform_mesh(
        cylinder_mesh(
            radius_mm=barrel_radius_mm,
            length_mm=hinge_length_mm,
            segments=max(
                72,
                parameters.circle_segments,
            ),
            axis="Y",
        ),
        translate_z_mm=barrel_center_z_mm,
    )

    leaf_depth_mm = hinge_length_mm * 0.82

    left_leaf = transform_mesh(
        rectangular_prism(
            width_mm=leaf_width_mm,
            depth_mm=leaf_depth_mm,
            height_mm=leaf_thickness_mm,
        ),
        translate_x_mm=-(
            barrel_radius_mm * 0.55
            + leaf_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )

    right_leaf = transform_mesh(
        rectangular_prism(
            width_mm=leaf_width_mm,
            depth_mm=leaf_depth_mm,
            height_mm=leaf_thickness_mm,
        ),
        translate_x_mm=(
            barrel_radius_mm * 0.55
            + leaf_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )

    band_radius_mm = (
        barrel_radius_mm * 1.12
    )

    band_length_mm = (
        hinge_length_mm * 0.16
    )

    bands: list[MeshData] = []

    for y_mm in (
        -hinge_length_mm * 0.31,
        0.0,
        hinge_length_mm * 0.31,
    ):
        bands.append(
            transform_mesh(
                cylinder_mesh(
                    radius_mm=band_radius_mm,
                    length_mm=band_length_mm,
                    segments=max(
                        72,
                        parameters.circle_segments,
                    ),
                    axis="Y",
                ),
                translate_y_mm=y_mm,
                translate_z_mm=barrel_center_z_mm,
            )
        )

    return combine_meshes(
        left_leaf,
        right_leaf,
        barrel,
        *bands,
    )


def build_fold_feature(
    parameters: TileParameters,
) -> MeshData:
    """Canonical OW07 continuous bent-sheet solid.

    The geometry is constructed from one closed side profile and
    extruded across X, eliminating disconnected/coplanar components.
    """

    width_mm = parameters.shape_width_mm

    anchor_depth_mm = max(
        10.0,
        parameters.shape_width_mm * 0.19,
    )

    rising_length_mm = min(
        parameters.shape_width_mm * 0.67,
        parameters.tile_depth_mm * 0.55,
    )

    sheet_thickness_mm = max(
        1.6,
        parameters.shape_height_mm * 0.29,
    )

    fold_angle_degrees = 54.0
    angle = math.radians(
        fold_angle_degrees
    )

    horizontal_run_mm = (
        rising_length_mm
        * math.cos(angle)
    )

    vertical_rise_mm = (
        rising_length_mm
        * math.sin(angle)
    )

    # Offset normal to the rising plane to create physical sheet
    # thickness while retaining a single watertight profile.
    normal_y_mm = (
        -sheet_thickness_mm
        * math.sin(angle)
    )

    normal_z_mm = (
        sheet_thickness_mm
        * math.cos(angle)
    )

    embed_mm = max(
        0.35,
        sheet_thickness_mm * 0.20,
    )

    base_z_mm = (
        parameters.tile_height_mm
        - embed_mm
    )

    profile = (
        (
            -anchor_depth_mm,
            base_z_mm,
        ),
        (
            0.0,
            base_z_mm,
        ),
        (
            horizontal_run_mm,
            base_z_mm
            + vertical_rise_mm),
        (
            horizontal_run_mm
            + normal_y_mm,
            base_z_mm
            + vertical_rise_mm
            + normal_z_mm,
        ),
        (
            normal_y_mm,
            base_z_mm
            + sheet_thickness_mm,
        ),
        (
            -anchor_depth_mm,
            base_z_mm
            + sheet_thickness_mm,
        ),
    )

    return extrude_yz_profile_along_x(
        profile_yz=profile,
        width_mm=width_mm,
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




def build_aperture_feature(
    parameters: TileParameters,
) -> MeshData:
    """Canonical OW08: a circular through-hole in the substrate."""

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

def build_water_droplet_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build the canonical OW09 circular surface-tension lens.
    The feature is rotationally symmetric and perfectly circular from
    above. It begins at the canonical tile surface without a pedestal.
    """
    diameter_mm = parameters.shape_width_mm * 0.76
    radius_mm = diameter_mm / 2.0
    rise_mm = min(
        parameters.shape_height_mm * 1.45,
        diameter_mm * 0.24,
    )
    base_z_mm = parameters.tile_height_mm
    profile_segments = 24
    profile: list[tuple[float, float]] = [
        (0.0, base_z_mm),
        (radius_mm, base_z_mm),
    ]
    for index in range(1, profile_segments):
        fraction = index / profile_segments
        local_radius = (
            radius_mm
            * (1.0 - fraction)
        )
        smoothstep = (
            fraction
            * fraction
            * (3.0 - 2.0 * fraction)
        )
        height_fraction = smoothstep ** 0.88
        profile.append(
            (
                local_radius,
                base_z_mm
                + rise_mm * height_fraction,
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
        segments=max(
            72,
            parameters.circle_segments,
        ),
    )


def build_mirror_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW10 as a recessed square mirror and thin bezel."""
    mirror_width_mm = parameters.shape_width_mm * 0.82
    mirror_depth_mm = mirror_width_mm
    bezel_width_mm = max(
        2.0,
        mirror_width_mm * 0.055,
    )
    bezel_height_mm = max(
        1.2,
        parameters.shape_height_mm * 0.24,
    )
    mirror_thickness_mm = max(
        0.7,
        parameters.shape_height_mm * 0.14,
    )
    outer_width_mm = (
        mirror_width_mm
        + bezel_width_mm * 2.0
    )
    outer_depth_mm = (
        mirror_depth_mm
        + bezel_width_mm * 2.0
    )
    base_z_mm = parameters.tile_height_mm
    top_bar = transform_mesh(
        rectangular_prism(
            width_mm=outer_width_mm,
            depth_mm=bezel_width_mm,
            height_mm=bezel_height_mm,
        ),
        translate_y_mm=(
            mirror_depth_mm / 2.0
            + bezel_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )
    bottom_bar = transform_mesh(
        rectangular_prism(
            width_mm=outer_width_mm,
            depth_mm=bezel_width_mm,
            height_mm=bezel_height_mm,
        ),
        translate_y_mm=-(
            mirror_depth_mm / 2.0
            + bezel_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )
    left_bar = transform_mesh(
        rectangular_prism(
            width_mm=bezel_width_mm,
            depth_mm=mirror_depth_mm,
            height_mm=bezel_height_mm,
        ),
        translate_x_mm=-(
            mirror_width_mm / 2.0
            + bezel_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )
    right_bar = transform_mesh(
        rectangular_prism(
            width_mm=bezel_width_mm,
            depth_mm=mirror_depth_mm,
            height_mm=bezel_height_mm,
        ),
        translate_x_mm=(
            mirror_width_mm / 2.0
            + bezel_width_mm / 2.0
        ),
        translate_z_mm=base_z_mm,
    )
    mirror_surface = transform_mesh(
        rectangular_prism(
            width_mm=mirror_width_mm,
            depth_mm=mirror_depth_mm,
            height_mm=mirror_thickness_mm,
        ),
        translate_z_mm=(
            base_z_mm
            + bezel_height_mm
        ),
    )
    return combine_meshes(
        top_bar,
        bottom_bar,
        left_bar,
        right_bar,
        mirror_surface,
    )


def build_light_source_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW11 as a low frosted bulb with a short neck."""
    bulb_radius_mm = parameters.shape_width_mm * 0.285
    neck_radius_mm = bulb_radius_mm * 0.43
    neck_height_mm = max(
        1.7,
        parameters.shape_height_mm * 0.32,
    )
    bulb_height_mm = min(
        parameters.shape_height_mm * 1.65,
        bulb_radius_mm * 1.02,
    )
    base_z_mm = parameters.tile_height_mm
    neck_top_mm = base_z_mm + neck_height_mm
    crown_top_mm = neck_top_mm + bulb_height_mm
    profile = (
        (0.0, base_z_mm),
        (neck_radius_mm, base_z_mm),
        (neck_radius_mm, neck_top_mm),
        (
            bulb_radius_mm * 0.70,
            neck_top_mm + bulb_height_mm * 0.08,
        ),
        (
            bulb_radius_mm * 0.91,
            neck_top_mm + bulb_height_mm * 0.27,
        ),
        (
            bulb_radius_mm,
            neck_top_mm + bulb_height_mm * 0.48,
        ),
        (
            bulb_radius_mm * 0.92,
            neck_top_mm + bulb_height_mm * 0.69,
        ),
        (
            bulb_radius_mm * 0.69,
            neck_top_mm + bulb_height_mm * 0.88,
        ),
        (
            bulb_radius_mm * 0.34,
            neck_top_mm + bulb_height_mm * 0.98,
        ),
        (0.0, crown_top_mm),
    )
    return rotational_profile_mesh(
        profile=profile,
        segments=max(
            72,
            parameters.circle_segments,
        ),
    )


def build_weight_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW12 as a rotated chamfered metal cube."""
    cube_size_mm = min(
        parameters.shape_width_mm * 0.60,
        parameters.tile_width_mm * 0.44,
        parameters.tile_depth_mm * 0.44,
    )
    chamfer_mm = max(
        1.2,
        cube_size_mm * 0.045,
    )
    cube = chamfered_box_mesh(
        width_mm=cube_size_mm,
        depth_mm=cube_size_mm,
        height_mm=cube_size_mm,
        chamfer_mm=chamfer_mm,
        bottom_z_mm=0.0,
    )
    return transform_mesh(
        cube,
        rotate_z_degrees=45.0,
        translate_z_mm=parameters.tile_height_mm,
    )



def build_threshold_feature(
    parameters: TileParameters,
) -> MeshData:
    """Canonical OW13: a low boundary spanning most of the field."""

    length_mm = min(
        parameters.tile_width_mm * 0.76,
        parameters.shape_width_mm * 1.18,
    )

    depth_mm = max(
        8.0,
        parameters.shape_width_mm * 0.16,
    )

    height_mm = max(
        2.8,
        parameters.shape_height_mm * 0.70,
    )

    outline = (
        (-length_mm / 2.0, -depth_mm / 2.0),
        (length_mm / 2.0, -depth_mm / 2.0),
        (length_mm / 2.0, depth_mm / 2.0),
        (-length_mm / 2.0, depth_mm / 2.0),
    )

    return chamfered_extruded_polygon(
        outline=outline,
        bottom_z_mm=parameters.tile_height_mm,
        height_mm=height_mm,
        chamfer_mm=min(
            1.2,
            height_mm * 0.28,
        ),
    )

def build_sensor_feature(
    parameters: TileParameters,
) -> MeshData:
    """Build canonical OW14 as a small black dome in a shallow recess."""
    recess_radius_mm = parameters.shape_width_mm * 0.235
    recess_height_mm = max(
        0.9,
        parameters.shape_height_mm * 0.18,
    )
    base_z_mm = parameters.tile_height_mm
    recess = transform_mesh(
        cylinder_mesh(
            radius_mm=recess_radius_mm,
            length_mm=recess_height_mm,
            segments=max(
                72,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_z_mm=base_z_mm,
    )
    sphere_radius_mm = parameters.shape_width_mm * 0.135
    exposed_height_mm = (
        sphere_radius_mm * 0.62
    )
    dome_base_z_mm = (
        base_z_mm
        + recess_height_mm
    )
    profile_segments = 18
    profile: list[tuple[float, float]] = [
        (0.0, dome_base_z_mm),
    ]
    for index in range(profile_segments + 1):
        fraction = index / profile_segments
        z_from_center = (
            -sphere_radius_mm
            + exposed_height_mm
            + exposed_height_mm * fraction
        )
        ring_radius_mm = math.sqrt(
            max(
                0.0,
                sphere_radius_mm ** 2
                - z_from_center ** 2,
            )
        )
        profile.append(
            (
                ring_radius_mm,
                dome_base_z_mm
                + exposed_height_mm * fraction,
            )
        )
    profile.append(
        (
            0.0,
            dome_base_z_mm + exposed_height_mm,
        )
    )
    dome = rotational_profile_mesh(
        profile=tuple(profile),
        segments=max(
            72,
            parameters.circle_segments,
        ),
    )
    return combine_meshes(
        recess,
        dome,
    )



def build_handle_feature(
    parameters: TileParameters,
) -> MeshData:
    """Canonical OW15: a graspable bridge with real negative space."""

    total_width_mm = parameters.shape_width_mm

    post_radius_mm = max(
        2.8,
        parameters.shape_height_mm * 0.56,
    )

    grip_clearance_mm = max(
        13.0,
        parameters.shape_height_mm * 2.8,
    )

    support_offset_mm = (
        total_width_mm / 2.0
        - post_radius_mm * 1.6
    )

    post_height_mm = (
        grip_clearance_mm
        + post_radius_mm
    )

    foot_radius_mm = (
        post_radius_mm * 1.45
    )

    foot_height_mm = max(
        1.4,
        post_radius_mm * 0.48,
    )

    left_foot = transform_mesh(
        cylinder_mesh(
            radius_mm=foot_radius_mm,
            length_mm=foot_height_mm,
            segments=max(
                56,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_x_mm=-support_offset_mm,
        translate_z_mm=parameters.tile_height_mm,
    )

    right_foot = transform_mesh(
        cylinder_mesh(
            radius_mm=foot_radius_mm,
            length_mm=foot_height_mm,
            segments=max(
                56,
                parameters.circle_segments,
            ),
          axis="Z",
        ),
        translate_x_mm=support_offset_mm,
        translate_z_mm=parameters.tile_height_mm,
    )

    left_post = transform_mesh(
        cylinder_mesh(
            radius_mm=post_radius_mm,
            length_mm=post_height_mm,
            segments=max(
                56,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_x_mm=-support_offset_mm,
        translate_z_mm=parameters.tile_height_mm,
    )

    right_post = transform_mesh(
        cylinder_mesh(
            radius_mm=post_radius_mm,
            length_mm=post_height_mm,
            segments=max(
                56,
                parameters.circle_segments,
            ),
            axis="Z",
        ),
        translate_x_mm=support_offset_mm,
        translate_z_mm=parameters.tile_height_mm,
    )

    grip = transform_mesh(
        cylinder_mesh(
            radius_mm=post_radius_mm,
            length_mm=support_offset_mm * 2.0,
            segments=max(
                56,
                parameters.circle_segments,
            ),
            axis="X",
        ),
        translate_z_mm=(
            parameters.tile_height_mm
            + post_height_mm
        ),
    )

    return combine_meshes(
        left_foot,
        right_foot,
        left_post,
        right_post,
        grip,
    )

def build_feature_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Build only the operational feature, never the substrate."""

    if parameters.shape in RAISED_OUTLINE_SHAPES:
        return build_raised_outline_feature(
            parameters
        )

    if parameters.shape is ShapeType.SLOT:
        return build_slot_feature(parameters)

    if parameters.shape is ShapeType.HINGE:
        return build_hinge_feature(parameters)

    if parameters.shape is ShapeType.FOLD:
        return build_fold_feature(parameters)

    if parameters.shape is ShapeType.APERTURE:
        return build_aperture_feature(parameters)

    if parameters.shape is ShapeType.LENS:
        return build_water_droplet_feature(
            parameters
        )

    if parameters.shape is ShapeType.MIRROR:
        return build_mirror_feature(parameters)

    if parameters.shape is ShapeType.LIGHT_SOURCE:
        return build_light_source_feature(
            parameters
        )

    if parameters.shape is ShapeType.WEIGHT:
        return build_weight_feature(parameters)

    if parameters.shape is ShapeType.THRESHOLD:
        return build_threshold_feature(
            parameters
        )

    if parameters.shape is ShapeType.SENSOR:
        return build_sensor_feature(parameters)

    if parameters.shape is ShapeType.HANDLE:
        return build_handle_feature(parameters)

    raise ValueError(
        f"Unsupported operational primitive: {parameters.shape}"
    )


# =====================================================================
# Public build function
# =====================================================================

def build_tile_mesh(
    parameters: TileParameters,
) -> MeshData:
    """Compose one canonical substrate with one operational feature."""

    parameters.validate()

    base = build_base_tile_mesh(
        parameters
    )

    feature = build_feature_mesh(
        parameters
    )

    return combine_meshes(
        base,
        feature,
    )


# =====================================================================
# Compatibility wrappers
# =====================================================================

def build_raised_tile_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_raised_outline_feature(parameters),
    )


def build_hinge_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_hinge_feature(parameters),
    )


def build_fold_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_fold_feature(parameters),
    )


def build_aperture_mesh(
    parameters: TileParameters,
) -> MeshData:
    return build_aperture_feature(parameters)


def build_lens_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_water_droplet_feature(parameters),
    )


def build_mirror_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_mirror_feature(parameters),
    )


def build_light_source_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_light_source_feature(parameters),
    )


def build_weight_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_weight_feature(parameters),
    )


def build_threshold_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_threshold_feature(parameters),
    )


def build_sensor_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_sensor_feature(parameters),
    )


def build_handle_mesh(
    parameters: TileParameters,
) -> MeshData:
    return combine_meshes(
        build_base_tile_mesh(parameters),
        build_handle_feature(parameters),
    )
