#!/usr/bin/env bash
set -euo pipefail

# OWDE 0.7.0-alpha.1
# Adds substrate-free COMP-0001 Actor, COMP-0002 Gate, COMP-0003 Net.
# Run from the OWDE repository root.

if [[ ! -f "owde_addon/__init__.py" ]]; then
  echo "ERROR: Run this script from the OWDE repository root."
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR=".owde-backups/before-competition-primitives-${STAMP}"

mkdir -p "$BACKUP_DIR/owde_addon"
cp owde_addon/__init__.py "$BACKUP_DIR/owde_addon/__init__.py"

if [[ -f "owde_addon/blender/operators.py" ]]; then
  mkdir -p "$BACKUP_DIR/owde_addon/blender"
  cp owde_addon/blender/operators.py "$BACKUP_DIR/owde_addon/blender/operators.py"
fi

mkdir -p owde_addon/core owde_addon/blender scripts tests

cat > owde_addon/core/competition_builders.py <<'PYFILE'
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

# Canonical v0.1 defaults, proportioned for a 20 x 16 inch field.
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
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
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
    """Build COMP-0001 Actor. Supported variants: CIRCLE and SQUARE."""
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
    """Build COMP-0002 Gate as a simple freestanding rectangular portal."""
    if min(length_mm, height_mm, depth_mm, member_mm) <= 0:
        raise ValueError("gate dimensions must be positive")

    if member_mm * 2 >= length_mm or member_mm >= height_mm:
        raise ValueError("gate member is too large for the requested opening")

    left_x = -length_mm / 2.0 + member_mm / 2.0
    right_x = length_mm / 2.0 - member_mm / 2.0

    return _combine((
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
    ))


def build_net_mesh(
    length_mm: float = NET_LENGTH_MM,
    height_mm: float = NET_HEIGHT_MM,
    depth_mm: float = NET_DEPTH_MM,
    frame_mm: float = NET_FRAME_MM,
    grid_member_mm: float = NET_GRID_MEMBER_MM,
    columns: int = 10,
    rows: int = 4,
    woven_depth: bool = True,
) -> MeshData:
    """Build COMP-0003 Net with a real open lattice.

    With woven_depth=True, vertical and horizontal strands sit on slightly
    different Y planes. This preserves mesh texture in both level and strict
    top/plan views.
    """
    if min(length_mm, height_mm, depth_mm, frame_mm, grid_member_mm) <= 0:
        raise ValueError("net dimensions must be positive")

    if columns < 2 or rows < 2:
        raise ValueError("net requires at least 2 columns and 2 rows")

    if 2 * frame_mm >= length_mm or 2 * frame_mm >= height_mm:
        raise ValueError("net frame is too large")

    meshes: list[MeshData] = []

    # Outer frame.
    meshes.extend((
        _box(
            length_mm,
            depth_mm,
            frame_mm,
            (0.0, 0.0, frame_mm / 2.0),
        ),
        _box(
            length_mm,
            depth_mm,
            frame_mm,
            (0.0, 0.0, height_mm - frame_mm / 2.0),
        ),
        _box(
            frame_mm,
            depth_mm,
            height_mm,
            (-length_mm / 2.0 + frame_mm / 2.0, 0.0, height_mm / 2.0),
        ),
        _box(
            frame_mm,
            depth_mm,
            height_mm,
            (length_mm / 2.0 - frame_mm / 2.0, 0.0, height_mm / 2.0),
        ),
    ))

    inner_w = length_mm - 2.0 * frame_mm
    inner_h = height_mm - 2.0 * frame_mm

    # Slightly different Y planes create a shallow woven relief.
    mesh_depth = depth_mm * 0.52
    y_offset = depth_mm * 0.16 if woven_depth else 0.0

    # columns = number of openings across.
    for i in range(1, columns):
        x = -inner_w / 2.0 + inner_w * i / columns
        meshes.append(_box(
            grid_member_mm,
            mesh_depth,
            inner_h,
            (x, -y_offset, height_mm / 2.0),
        ))

    # rows = number of openings high.
    for j in range(1, rows):
        z = frame_mm + inner_h * j / rows
        meshes.append(_box(
            inner_w,
            mesh_depth,
            grid_member_mm,
            (0.0, y_offset, z),
        ))

    return _combine(meshes)


def mesh_bounds(mesh: MeshData) -> tuple[float, float, float]:
    """Return X/Y/Z overall dimensions in millimetres."""
    xs = [v[0] for v in mesh.vertices]
    ys = [v[1] for v in mesh.vertices]
    zs = [v[2] for v in mesh.vertices]

    return (
        max(xs) - min(xs),
        max(ys) - min(ys),
        max(zs) - min(zs),
    )

PYFILE

cat > owde_addon/blender/competition.py <<'PYFILE'
"""Blender UI and operators for OWDE Competition Primitives."""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)
from bpy.types import Operator, Panel, PropertyGroup

from ..core.competition_builders import (
    ACTOR_DIAMETER_MM,
    ACTOR_HEIGHT_MM,
    ACTOR_SQUARE_MM,
    GATE_DEPTH_MM,
    GATE_HEIGHT_MM,
    GATE_LENGTH_MM,
    GATE_MEMBER_MM,
    NET_DEPTH_MM,
    NET_FRAME_MM,
    NET_GRID_MEMBER_MM,
    NET_HEIGHT_MM,
    NET_LENGTH_MM,
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
)

MM_TO_METERS = 0.001
COMPETITION_VERSION = "0.7.0-alpha.1"


def _mesh_to_blender(mesh_data, name: str):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")

    vertices = [
        (x * MM_TO_METERS, y * MM_TO_METERS, z * MM_TO_METERS)
        for x, y, z in mesh_data.vertices
    ]

    mesh.from_pydata(vertices, [], list(mesh_data.faces))
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj


def _set_metadata(obj, primitive_id: str, primitive_name: str, capability: str):
    obj["owde_namespace"] = "COMP"
    obj["owde_primitive_id"] = primitive_id
    obj["owde_primitive_name"] = primitive_name
    obj["owde_capability"] = capability
    obj["owde_version"] = COMPETITION_VERSION
    obj["owde_substrate"] = "NONE"


class OWDE_PG_competition_settings(PropertyGroup):

    primitive: EnumProperty(
        name="Primitive",
        items=(
            ("ACTOR", "Actor", "COMP-0001 — mobile unit / token"),
            ("GATE", "Gate", "COMP-0002 — regulates passage"),
            ("NET", "Net", "COMP-0003 — porous barrier / target / filter"),
        ),
        default="ACTOR",
    )

    actor_variant: EnumProperty(
        name="Actor Shape",
        items=(
            ("CIRCLE", "Circle", "Circular actor/token"),
            ("SQUARE", "Square", "Square actor/token"),
        ),
        default="CIRCLE",
    )

    actor_diameter_mm: FloatProperty(
        name="Diameter",
        default=ACTOR_DIAMETER_MM,
        min=1.0,
    )

    actor_square_mm: FloatProperty(
        name="Width",
        default=ACTOR_SQUARE_MM,
        min=1.0,
    )

    actor_height_mm: FloatProperty(
        name="Height",
        default=ACTOR_HEIGHT_MM,
        min=1.0,
    )

    gate_length_mm: FloatProperty(
        name="Length",
        default=GATE_LENGTH_MM,
        min=1.0,
    )

    gate_height_mm: FloatProperty(
        name="Height",
        default=GATE_HEIGHT_MM,
        min=1.0,
    )

    gate_depth_mm: FloatProperty(
        name="Depth",
        default=GATE_DEPTH_MM,
        min=1.0,
    )

    gate_member_mm: FloatProperty(
        name="Member",
        default=GATE_MEMBER_MM,
        min=0.5,
    )

    net_length_mm: FloatProperty(
        name="Length",
        default=NET_LENGTH_MM,
        min=1.0,
    )

    net_height_mm: FloatProperty(
        name="Height",
        default=NET_HEIGHT_MM,
        min=1.0,
    )

    net_depth_mm: FloatProperty(
        name="Depth",
        default=NET_DEPTH_MM,
        min=1.0,
    )

    net_frame_mm: FloatProperty(
        name="Frame",
        default=NET_FRAME_MM,
        min=0.5,
    )

    net_grid_member_mm: FloatProperty(
        name="Grid Member",
        default=NET_GRID_MEMBER_MM,
        min=0.25,
    )

    net_columns: IntProperty(
        name="Columns",
        description="Number of openings across the net",
        default=10,
        min=2,
        max=40,
    )

    net_rows: IntProperty(
        name="Rows",
        description="Number of openings vertically",
        default=4,
        min=2,
        max=20,
    )

    net_woven_depth: BoolProperty(
        name="Top-view Relief",
        description="Offset crossing grid members slightly in depth so the net remains legible from above",
        default=True,
    )


class OWDE_OT_create_competition_primitive(Operator):
    bl_idname = "owde.create_competition_primitive"
    bl_label = "Create Competition Primitive"
    bl_description = "Create a substrate-free Actor, Gate, or Net"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.owde_competition_settings

        try:
            if settings.primitive == "ACTOR":
                mesh_data = build_actor_mesh(
                    variant=settings.actor_variant,
                    diameter_mm=settings.actor_diameter_mm,
                    square_mm=settings.actor_square_mm,
                    height_mm=settings.actor_height_mm,
                )

                suffix = "Circle" if settings.actor_variant == "CIRCLE" else "Square"
                obj = _mesh_to_blender(mesh_data, f"COMP-0001_Actor_{suffix}")

                _set_metadata(obj, "COMP-0001", "Actor", "Occupy / move")
                obj["owde_variant"] = settings.actor_variant

            elif settings.primitive == "GATE":
                mesh_data = build_gate_mesh(
                    length_mm=settings.gate_length_mm,
                    height_mm=settings.gate_height_mm,
                    depth_mm=settings.gate_depth_mm,
                    member_mm=settings.gate_member_mm,
                )

                obj = _mesh_to_blender(mesh_data, "COMP-0002_Gate")
                _set_metadata(obj, "COMP-0002", "Gate", "Regulate passage")

            else:
                mesh_data = build_net_mesh(
                    length_mm=settings.net_length_mm,
                    height_mm=settings.net_height_mm,
                    depth_mm=settings.net_depth_mm,
                    frame_mm=settings.net_frame_mm,
                    grid_member_mm=settings.net_grid_member_mm,
                    columns=settings.net_columns,
                    rows=settings.net_rows,
                    woven_depth=settings.net_woven_depth,
                )

                obj = _mesh_to_blender(mesh_data, "COMP-0003_Net")
                _set_metadata(
                    obj,
                    "COMP-0003",
                    "Net",
                    "Porous barrier / intercept / filter",
                )

            self.report(
                {"INFO"},
                f"Created {obj.name} — substrate-free competition primitive",
            )
            return {"FINISHED"}

        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}


class OWDE_PT_competition_primitives(Panel):
    bl_label = "Competition Primitives"
    bl_idname = "OWDE_PT_competition_primitives"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.owde_competition_settings

        box = layout.box()
        box.label(text="COMP Library v0.1")
        box.label(text="Substrate-free / movable")

        layout.prop(settings, "primitive")

        if settings.primitive == "ACTOR":
            layout.label(text="COMP-0001 — Actor")
            layout.prop(settings, "actor_variant")

            if settings.actor_variant == "CIRCLE":
                layout.prop(settings, "actor_diameter_mm")
            else:
                layout.prop(settings, "actor_square_mm")

            layout.prop(settings, "actor_height_mm")

        elif settings.primitive == "GATE":
            layout.label(text="COMP-0002 — Gate")
            layout.prop(settings, "gate_length_mm")
            layout.prop(settings, "gate_height_mm")
            layout.prop(settings, "gate_depth_mm")
            layout.prop(settings, "gate_member_mm")

        else:
            layout.label(text="COMP-0003 — Net")
            layout.prop(settings, "net_length_mm")
            layout.prop(settings, "net_height_mm")
            layout.prop(settings, "net_depth_mm")
            layout.prop(settings, "net_frame_mm")
            layout.prop(settings, "net_grid_member_mm")
            layout.prop(settings, "net_columns")
            layout.prop(settings, "net_rows")
            layout.prop(settings, "net_woven_depth")

        layout.separator()
        layout.operator(
            OWDE_OT_create_competition_primitive.bl_idname,
            icon="MESH_CUBE",
        )

        footer = layout.box()
        footer.label(text='Reference field: 20" × 16"')
        footer.label(text='Actor default: 1.25" × 0.375"')
        footer.label(text='Gate + Net length: 6.0"')


_CLASSES = (
    OWDE_PG_competition_settings,
    OWDE_OT_create_competition_primitive,
    OWDE_PT_competition_primitives,
)


def register_competition():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.owde_competition_settings = PointerProperty(
        type=OWDE_PG_competition_settings
    )


def unregister_competition():
    if hasattr(bpy.types.Scene, "owde_competition_settings"):
        del bpy.types.Scene.owde_competition_settings

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)

PYFILE

cat > scripts/create_competition_primitives.py <<'PYFILE'
"""Create the first OWDE competition configuration in Blender.

Run from the repository root, for example:
    blender --python scripts/create_competition_primitives.py

Creates:
- 2 circular actors
- 1 square actor
- 1 gate
- 2 nets
- 20 x 16 inch reference field

All competition primitives are substrate-free.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from owde_addon.core.competition_builders import (  # noqa: E402
    INCH_MM,
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
)

MM_TO_METERS = 0.001


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def mesh_to_object(mesh_data, name: str):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    vertices = [
        (x * MM_TO_METERS, y * MM_TO_METERS, z * MM_TO_METERS)
        for x, y, z in mesh_data.vertices
    ]
    mesh.from_pydata(vertices, [], list(mesh_data.faces))
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_reference_field():
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.0, -0.0005),
    )

    field = bpy.context.object
    field.name = "REFERENCE_FIELD_20x16"
    field.dimensions = (
        20.0 * INCH_MM * MM_TO_METERS,
        16.0 * INCH_MM * MM_TO_METERS,
        0.001,
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    field.display_type = "WIRE"
    field.hide_render = True
    return field


def build():
    clear_scene()
    make_reference_field()

    actor_a = mesh_to_object(
        build_actor_mesh("CIRCLE"),
        "COMP-0001_Actor_Circle_A",
    )
    actor_b = mesh_to_object(
        build_actor_mesh("CIRCLE"),
        "COMP-0001_Actor_Circle_B",
    )
    actor_c = mesh_to_object(
        build_actor_mesh("SQUARE"),
        "COMP-0001_Actor_Square",
    )

    gate = mesh_to_object(
        build_gate_mesh(),
        "COMP-0002_Gate",
    )

    net_left = mesh_to_object(
        build_net_mesh(),
        "COMP-0003_Net_Left",
    )
    net_right = mesh_to_object(
        build_net_mesh(),
        "COMP-0003_Net_Right",
    )

    # Long dimension runs vertically in the top-view field composition.
    net_left.rotation_euler[2] = math.radians(90)
    net_right.rotation_euler[2] = math.radians(90)

    inch = INCH_MM * MM_TO_METERS

    net_left.location.x = -4.25 * inch
    net_right.location.x = 4.25 * inch

    gate.location = (0.0, 0.0, 0.0)

    actor_a.location = (0.0, 0.0, 0.0)
    actor_b.location = (-6.75 * inch, 2.5 * inch, 0.0)
    actor_c.location = (6.75 * inch, 2.5 * inch, 0.0)

    print("OWDE Competition Primitives v0.1 created")
    print("Reference field: 20 x 16 in")
    print("Actors: 2 circle + 1 square")
    print("Gate: 6.0 in long")
    print("Nets: 6.0 in long x 2.5 in high")
    print("All primitives are substrate-free")


if __name__ == "__main__":
    build()

PYFILE

cat > tests/test_competition_primitives.py <<'PYFILE'
import pytest

from owde_addon.core.competition_builders import (
    ACTOR_DIAMETER_MM,
    ACTOR_HEIGHT_MM,
    ACTOR_SQUARE_MM,
    GATE_DEPTH_MM,
    GATE_HEIGHT_MM,
    GATE_LENGTH_MM,
    NET_DEPTH_MM,
    NET_HEIGHT_MM,
    NET_LENGTH_MM,
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
    mesh_bounds,
)


def test_circle_actor_defaults():
    mesh = build_actor_mesh("CIRCLE")
    assert mesh_bounds(mesh) == pytest.approx((
        ACTOR_DIAMETER_MM,
        ACTOR_DIAMETER_MM,
        ACTOR_HEIGHT_MM,
    ))


def test_square_actor_defaults():
    mesh = build_actor_mesh("SQUARE")
    assert mesh_bounds(mesh) == pytest.approx((
        ACTOR_SQUARE_MM,
        ACTOR_SQUARE_MM,
        ACTOR_HEIGHT_MM,
    ))


def test_gate_defaults():
    mesh = build_gate_mesh()
    assert mesh_bounds(mesh) == pytest.approx((
        GATE_LENGTH_MM,
        GATE_DEPTH_MM,
        GATE_HEIGHT_MM,
    ))


def test_net_defaults():
    mesh = build_net_mesh()
    assert mesh_bounds(mesh) == pytest.approx((
        NET_LENGTH_MM,
        NET_DEPTH_MM,
        NET_HEIGHT_MM,
    ))
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0


def test_net_top_view_relief_changes_y_positions():
    mesh = build_net_mesh(woven_depth=True)
    y_values = {round(v[1], 6) for v in mesh.vertices}
    assert len(y_values) > 4


def test_actor_rejects_unknown_variant():
    with pytest.raises(ValueError):
        build_actor_mesh("TRIANGLE")

PYFILE

python3 - <<'PY'
from pathlib import Path
import re

root = Path("owde_addon/__init__.py")
text = root.read_text()

text = re.sub(
    r'("version"\s*:\s*)\([^)]+\)',
    r'\g<1>(0, 7, 0)',
    text,
    count=1,
)

marker = "# --- OWDE COMPETITION PRIMITIVES v0.1 ---"

if marker not in text:
    text += """

# --- OWDE COMPETITION PRIMITIVES v0.1 ---
# Domain-specific, substrate-free primitives introduced in 0.7.0-alpha.1.
# Kept in their own registration layer so the original OW01-OW15 registry
# remains unchanged.
from .blender.competition import (
    register_competition as _owde_register_competition,
    unregister_competition as _owde_unregister_competition,
)

_owde_register_base = register
_owde_unregister_base = unregister


def register():
    _owde_register_base()
    _owde_register_competition()


def unregister():
    _owde_unregister_competition()
    _owde_unregister_base()
"""

root.write_text(text)

operators = Path("owde_addon/blender/operators.py")
if operators.exists():
    op_text = operators.read_text()
    op_text = re.sub(
        r'OWDE_VERSION\s*=\s*["\'][^"\']+["\']',
        'OWDE_VERSION = "0.7.0-alpha.1"',
        op_text,
        count=1,
    )
    operators.write_text(op_text)
PY

echo
echo "Created:"
echo "  owde_addon/core/competition_builders.py"
echo "  owde_addon/blender/competition.py"
echo "  scripts/create_competition_primitives.py"
echo "  tests/test_competition_primitives.py"
echo
echo "Updated:"
echo "  owde_addon/__init__.py -> 0.7.0 + competition registration"
echo "  owde_addon/blender/operators.py -> OWDE_VERSION 0.7.0-alpha.1 (if present)"
echo
echo "Backup:"
echo "  $BACKUP_DIR"
echo
echo "Running release checks..."

python3 -m py_compile \
  owde_addon/__init__.py \
  owde_addon/core/*.py \
  owde_addon/blender/*.py \
  scripts/*.py

python3 -m pytest

echo
echo "Competition primitive patch installed successfully."
echo
echo "Next:"
echo "  python3 scripts/build_addon.py"
echo "  git status"
echo "  git diff --stat"
