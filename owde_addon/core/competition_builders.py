"""Parametric geometry for OWDE competition primitives.

All dimensions are millimetres. Competition primitives intentionally have no
substrate tile: they are autonomous objects for painted, projected, or digital
fields.
"""

from __future__ import annotations

from math import cos, pi, sin
from typing import Iterable

from .mesh import MeshData

INCH_MM = 25.4

# Canonical defaults, proportioned for a 20 x 16 inch field.
ACTOR_DIAMETER_MM = 1.25 * INCH_MM
ACTOR_HEIGHT_MM = 0.375 * INCH_MM
ACTOR_SQUARE_MM = 1.25 * INCH_MM

GATE_LENGTH_MM = 6.0 * INCH_MM
GATE_HEIGHT_MM = 1.5 * INCH_MM
GATE_DEPTH_MM = 0.50 * INCH_MM
GATE_MEMBER_MM = 0.30 * INCH_MM

NET_LENGTH_MM = 6.0 * INCH_MM
NET_HEIGHT_MM = 2.5 * INCH_MM
NET_DEPTH_MM = 0.35 * INCH_MM
NET_FRAME_MM = 0.30 * INCH_MM
NET_GRID_MEMBER_MM = 0.10 * INCH_MM


def _combine(meshes: Iterable[MeshData]) -> MeshData:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    offset = 0

    for mesh in meshes:
        vertices.extend(mesh.vertices)
        faces.extend(tuple(i + offset for i in face) for face in mesh.faces)
        offset += len(mesh.vertices)

    return MeshData(vertices=tuple(vertices), faces=tuple(faces))


def _box(
    sx: float,
    sy: float,
    sz: float,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> MeshData:
    cx, cy, cz = center
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0

    vertices = (
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    )

    faces = (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    )

    return MeshData(vertices=vertices, faces=faces)


def _cylinder(radius: float, height: float, segments: int = 64) -> MeshData:
    if segments < 3:
        raise ValueError("segments must be >= 3")

    vertices: list[tuple[float, float, float]] = []

    for z in (0.0, height):
        for i in range(segments):
            a = 2.0 * pi * i / segments
            vertices.append((radius * cos(a), radius * sin(a), z))

    bottom_center = len(vertices)
    vertices.append((0.0, 0.0, 0.0))

    top_center = len(vertices)
    vertices.append((0.0, 0.0, height))

    faces: list[tuple[int, ...]] = []

    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
        faces.append((bottom_center, j, i))
        faces.append((top_center, segments + i, segments + j))

    return MeshData(vertices=tuple(vertices), faces=tuple(faces))


def build_actor_mesh(
    variant: str = "CIRCLE",
    diameter_mm: float = ACTOR_DIAMETER_MM,
    square_mm: float = ACTOR_SQUARE_MM,
    height_mm: float = ACTOR_HEIGHT_MM,
    circle_segments: int = 64,
) -> MeshData:
    variant = variant.upper()

    if height_mm <= 0:
        raise ValueError("height_mm must be positive")

    if variant == "CIRCLE":
        if diameter_mm <= 0:
            raise ValueError("diameter_mm must be positive")
        return _cylinder(diameter_mm / 2.0, height_mm, circle_segments)

    if variant == "SQUARE":
        if square_mm <= 0:
            raise ValueError("square_mm must be positive")
        return _box(
            square_mm,
            square_mm,
            height_mm,
            (0.0, 0.0, height_mm / 2.0),
        )

    raise ValueError(f"Unsupported actor variant: {variant}")


def build_gate_mesh(
    length_mm: float = GATE_LENGTH_MM,
    height_mm: float = GATE_HEIGHT_MM,
    depth_mm: float = GATE_DEPTH_MM,
    member_mm: float = GATE_MEMBER_MM,
) -> MeshData:
    if min(length_mm, height_mm, depth_mm, member_mm) <= 0:
        raise ValueError("gate dimensions must be positive")

    if member_mm * 2 >= length_mm or member_mm >= height_mm:
        raise ValueError("gate member is too large for the requested opening")

    left_x = -length_mm / 2.0 + member_mm / 2.0
    right_x = length_mm / 2.0 - member_mm / 2.0

    return _combine(
        (
            _box(
                member_mm,
                depth_mm,
                height_mm,
                (left_x, 0.0, height_mm / 2.0),
            ),
            _box(
                member_mm,
                depth_mm,
                height_mm,
                (right_x, 0.0, height_mm / 2.0),
            ),
            _box(
                length_mm,
                depth_mm,
                member_mm,
                (0.0, 0.0, height_mm - member_mm / 2.0),
            ),
        )
    )


def build_net_mesh(
    length_mm: float = NET_LENGTH_MM,
    height_mm: float = NET_HEIGHT_MM,
    depth_mm: float = NET_DEPTH_MM,
    frame_mm: float = NET_FRAME_MM,
    grid_member_mm: float = NET_GRID_MEMBER_MM,
    columns: int = 10,
    rows: int = 4,
    woven_depth: bool = True,
    top_mesh: bool = True,
    top_mesh_thickness_mm: float = 0.8,
    top_mesh_member_mm: float = 0.9,
    top_mesh_openings: int = 8,
) -> MeshData:
    """Build COMP-0003 Net.

    The primitive must read as a net from two orthographic conditions:

    LEVEL / FRONT:
        upright framed open lattice

    TOP / PLAN:
        shallow open lattice through the depth of the top member

    When top_mesh=True the normal solid top beam is replaced by an
    open framed grille. Its front and rear rails preserve the appearance
    of a continuous beam from level view, while cross-members create
    visible openings from above.
    """

    if min(
        length_mm,
        height_mm,
        depth_mm,
        frame_mm,
        grid_member_mm,
    ) <= 0:
        raise ValueError("net dimensions must be positive")

    if columns < 2 or rows < 2:
        raise ValueError("net requires at least 2 columns and 2 rows")

    if 2 * frame_mm >= length_mm or 2 * frame_mm >= height_mm:
        raise ValueError("net frame is too large")

    if top_mesh_openings < 2:
        raise ValueError("top_mesh_openings must be at least 2")

    meshes: list[MeshData] = []

    # --------------------------------------------------------
    # LOWER FRAME
    # --------------------------------------------------------

    meshes.append(
        _box(
            length_mm,
            depth_mm,
            frame_mm,
            (0.0, 0.0, frame_mm / 2.0),
        )
    )

    # --------------------------------------------------------
    # SIDE POSTS
    # --------------------------------------------------------

    meshes.append(
        _box(
            frame_mm,
            depth_mm,
            height_mm,
            (
                -length_mm / 2.0 + frame_mm / 2.0,
                0.0,
                height_mm / 2.0,
            ),
        )
    )

    meshes.append(
        _box(
            frame_mm,
            depth_mm,
            height_mm,
            (
                length_mm / 2.0 - frame_mm / 2.0,
                0.0,
                height_mm / 2.0,
            ),
        )
    )

    # --------------------------------------------------------
    # TOP MEMBER
    #
    # Solid when Top Mesh is OFF.
    # Open grille when Top Mesh is ON.
    # --------------------------------------------------------

    if not top_mesh:

        meshes.append(
            _box(
                length_mm,
                depth_mm,
                frame_mm,
                (
                    0.0,
                    0.0,
                    height_mm - frame_mm / 2.0,
                ),
            )
        )

    else:

        # Top grille occupies exactly the same overall envelope as
        # the old solid top rail.
        top_z = height_mm - frame_mm / 2.0

        # Keep a narrow continuous rail at the front and rear edges.
        #
        # These make the object still read as a strong horizontal
        # beam from level view.
        edge_rail_depth = min(
            max(top_mesh_member_mm, 0.8),
            depth_mm * 0.28,
        )

        meshes.append(
            _box(
                length_mm,
                edge_rail_depth,
                frame_mm,
                (
                    0.0,
                    -depth_mm / 2.0 + edge_rail_depth / 2.0,
                    top_z,
                ),
            )
        )

        meshes.append(
            _box(
                length_mm,
                edge_rail_depth,
                frame_mm,
                (
                    0.0,
                    depth_mm / 2.0 - edge_rail_depth / 2.0,
                    top_z,
                ),
            )
        )

        # End caps close the grille at left/right.
        meshes.append(
            _box(
                frame_mm,
                depth_mm,
                frame_mm,
                (
                    -length_mm / 2.0 + frame_mm / 2.0,
                    0.0,
                    top_z,
                ),
            )
        )

        meshes.append(
            _box(
                frame_mm,
                depth_mm,
                frame_mm,
                (
                    length_mm / 2.0 - frame_mm / 2.0,
                    0.0,
                    top_z,
                ),
            )
        )

        # Interior cross ribs.
        #
        # These run front-to-back, so they are clearly visible from
        # strict top orthographic view.
        usable_length = length_mm - 2.0 * frame_mm

        rib_width = min(
            top_mesh_member_mm,
            usable_length / (top_mesh_openings * 2.0),
        )

        for i in range(1, top_mesh_openings):

            x = (
                -usable_length / 2.0
                + usable_length * i / top_mesh_openings
            )

            meshes.append(
                _box(
                    rib_width,
                    depth_mm,
                    frame_mm,
                    (
                        x,
                        0.0,
                        top_z,
                    ),
                )
            )

        # One longitudinal center member adds a second direction to
        # the plan pattern, making the top read unmistakably as mesh.
        center_member_depth = min(
            top_mesh_member_mm,
            depth_mm * 0.22,
        )

        meshes.append(
            _box(
                usable_length,
                center_member_depth,
                frame_mm,
                (
                    0.0,
                    0.0,
                    top_z,
                ),
            )
        )

    # --------------------------------------------------------
    # VERTICAL NET / LEVEL-VIEW LATTICE
    # --------------------------------------------------------

    inner_w = length_mm - 2.0 * frame_mm
    inner_h = height_mm - 2.0 * frame_mm

    mesh_depth = depth_mm * 0.52
    y_offset = depth_mm * 0.16 if woven_depth else 0.0

    # Vertical strands.
    for i in range(1, columns):

        x = (
            -inner_w / 2.0
            + inner_w * i / columns
        )

        meshes.append(
            _box(
                grid_member_mm,
                mesh_depth,
                inner_h,
                (
                    x,
                    -y_offset,
                    height_mm / 2.0,
                ),
            )
        )

    # Horizontal strands.
    for j in range(1, rows):

        z = (
            frame_mm
            + inner_h * j / rows
        )

        meshes.append(
            _box(
                inner_w,
                mesh_depth,
                grid_member_mm,
                (
                    0.0,
                    y_offset,
                    z,
                ),
            )
        )

    return _combine(meshes)


def mesh_bounds(mesh: MeshData) -> tuple[float, float, float]:
    xs = [v[0] for v in mesh.vertices]
    ys = [v[1] for v in mesh.vertices]
    zs = [v[2] for v in mesh.vertices]

    return (
        max(xs) - min(xs),
        max(ys) - min(ys),
        max(zs) - min(zs),
    )
