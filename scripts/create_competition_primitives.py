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

