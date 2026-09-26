import bpy
from pathlib import Path
from math import radians
from mathutils import Vector

from owde_addon.core.competition_builders import (
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
)

from owde_addon.blender.competition import _mesh_to_blender


# ============================================================
# OWDE — CONFIG-0004 v2
#
# Tightly concentrated Divergence configuration.
#
# 3 Actors
# 2 Nets
# 2 Gates
#
# All primitives are organized around the default Divergence
# throat rather than spread across the entire field.
# ============================================================

SOURCE_FIELD = "FIELD-0004_Divergence"

CONFIG_ID = "CONFIG-0004"

COLLECTION_NAME = (
    "CONFIG-0004_Divergence_Reference_v2"
)

MM_TO_M = 0.001


# ============================================================
# PLACEMENT
#
# eld dimensions are approximately:
# 406.4 mm x 508 mm
#
# X:
#   negative = left
#   positive = right
#
# Y:
#   negative = lower field
#   positive = upper field
#
# The Divergence junction is approximately near field center.
# ============================================================


# ------------------------------------------------------------
# ACTORS
# ------------------------------------------------------------

# Left / outside actor
ACTOR_01_X_MM = -118.0
ACTOR_01_Y_MM = -40.0

# Central actor inside the concentrated configuration
ACTOR_02_X_MM = 0.0
ACTOR_02_Y_MM = 10.0

# Upper / outside actor
ACTOR_03_X_MM = 92.0
ACTOR_03_Y_MM = 92.0


# ------------------------------------------------------------
# NETS
#
# Vertical barriers flanking the central Actor.
# ------------------------------------------------------------

NET_01_X_MM = -62.0
NET_01_Y_MM = 8.0
NET_01_ROTATION_DEG = 90.0

NET_02_X_MM = 62.0
NET_02_Y_MM = 8.0
NET_02_ROTATION_DEG = 90.0


# ------------------------------------------------------------
# GATES
#
# Short horizontal constraints above and below central Actor.
# ------------------------------------------------------------

GATE_01_X_MM = 0.0
GATE_01_Y_MM = 48.0
GATE_01_ROTATION_DEG = 0.0

GATE_02_X_MM = 0.0
GATE_02_Y_MM = -30.0
GATE_02_ROTATION_DEG = 0.0


# ============================================================
# HELPERS
# ============================================================

def world_bbox(obj):
    return [
        obj.matrix_world @ Vector(corner)
        for corner in obj.bound_box
    ]


def bbox_center(obj):
    pts = world_bbox(obj)

    return Vector((
        (min(p.x for p in pts) + max(p.x for p in pts)) / 2.0,
        (min(p.y for p in pts) + max(p.y for p in pts)) / 2.0,
        (min(p.z for p in pts) + max(p.z for p in pts)) / 2.0,
    ))


def bbox_top_z(obj):
    return max(
        p.z
        for p in world_bbox(obj)
    )


def get_or_create_collection(name):
    collection = bpy.data.collections.get(name)

    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)

    return collection


def clear_collection(collection):
    for obj in list(collection.objects):
        bpy.data.objects.remove(
            obj,
            do_unlink=True,
        )


def move_to_collection(obj, collection):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)

    collection.objects.link(obj)


def make_white_material():
    name = "OWDE_Competition_White"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    bsdf = material.node_tree.nodes.get(
        "Principled BSDF"
    )

    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (
            0.82,
            0.80,
            0.72,
            1.0,
        )

        bsdf.inputs["Roughness"].default_value = 0.62

    return material


def assign_material(obj, material):
    if not hasattr(obj.data, "materials"):
        return

    obj.data.materials.clear()
    obj.data.materials.append(material)


def place(
    obj,
    x_mm,
    y_mm,
    surface_z,
    rotation_deg=0.0,
):
    obj.location.x = x_mm * MM_TO_M
    obj.location.y = y_mm * MM_TO_M
    obj.location.z = surface_z

    obj.rotation_euler[2] = radians(
        rotation_deg
    )


def duplicate_field(
    source,
    collection,
):
    duplicate = source.copy()

    if source.data is not None:
        duplicate.data = source.data.copy()

    duplicate.name = (
        f"{CONFIG_ID}_FIELD-0004_Divergence"
    )

    collection.objects.link(duplicate)

    center = bbox_center(source)

    duplicate.location.x -= center.x
    duplicate.location.y -= center.y

    duplicate["configuration_id"] = CONFIG_ID
    duplicate["field_id"] = "FIELD-0004"
    duplicate["field_name"] = "Divergence"

    return duplicate


def create_actor(
    collection,
    name,
    x_mm,
    y_mm,
    surface_z,
    material,
):
    obj = _mesh_to_blender(
        build_actor_mesh(),
        name,
    )

    move_to_collection(
        obj,
        collection,
    )

    assign_material(
        obj,
        material,
    )

    place(
        obj,
        x_mm,
        y_mm,
        surface_z,
    )

    obj["primitive_type"] = "ACTOR"
    obj["configuration_id"] = CONFIG_ID

    return obj


def create_net(
    collection,
    name,
    x_mm,
    y_mm,
    rotation_deg,
    surface_z,
    material,
):
    obj = _mesh_to_blender(
        build_net_mesh(),
        name,
    )

    move_to_collection(
        obj,
        collection,
    )

    assign_material(
        obj,
        material,
    )

    place(
        obj,
        x_mm,
        y_mm,
        surface_z,
        rotation_deg,
    )

    obj["primitive_type"] = "NET"
    obj["configuration_id"] = CONFIG_ID

    return obj


def create_gate(
    collection,
    name,
    x_mm,
    y_mm,
    rotation_deg,
    surface_z,
    material,
):
    obj = _mesh_to_blender(
        build_gate_mesh(),
        name,
    )

    move_to_collection(
        obj,
        collection,
    )

    assign_material(
        obj,
        material,
    )

    place(
        obj,
        x_mm,
        y_mm,
        surface_z,
        rotation_deg,
    )

    obj["primitive_type"] = "GATE"
    obj["configuration_id"] = CONFIG_ID

    return obj


# ============================================================
# FIND CANONICAL DIVERGENCE
# ============================================================

def available_divergence_fields():
    return sorted(
        obj.name
        for obj in bpy.data.objects
        if "FIELD-0004" in obj.name.upper()
        or "DIVERGENCE" in obj.name.upper()
    )


def resolve_source_field():
    source = bpy.data.objects.get(SOURCE_FIELD)

    if source is not None:
        return source

    for fallback_name in (
        "CONFIG-0003_FIELD-0004_Divergence",
        "FIELD-0004_Divergence.002",
        "FIELD-0004_Divergence.007",
        "FIELD-0004_Divergence.001",
    ):
        source = bpy.data.objects.get(fallback_name)

        if source is not None:
            print(
                f"Using {fallback_name} as source field because "
                f"{SOURCE_FIELD} was not found."
            )
            return source

    available = available_divergence_fields()

    if available:
        fallback_name = available[0]
        print(
            f"Using {fallback_name} as source field because "
            f"{SOURCE_FIELD} was not found."
        )
        return bpy.data.objects.get(fallback_name)

    return None


source_field = resolve_source_field()

if source_field is None:
    raise RuntimeError(
        f"Could not find canonical field: {SOURCE_FIELD}\n"
        f"Available divergence fields: {available_divergence_fields()}"
    )


# ============================================================
# BUILD CONFIGURATION
# ============================================================

collection = get_or_create_collection(
    COLLECTION_NAME
)

clear_collection(
    collection
)

white = make_white_material()

field = duplicate_field(
    source_field,
    collection,
)

surface_z = bbox_top_z(
    field
)


# ------------------------------------------------------------
# ACTORS
# ------------------------------------------------------------

create_actor(
    collection,
    f"{CONFIG_ID}_Actor_01",
    ACTOR_01_X_MM,
    ACTOR_01_Y_MM,
    surface_z,
    white,
)

create_actor(
    collection,
    f"{CONFIG_ID}_Actor_02",
    ACTOR_02_X_MM,
    ACTOR_02_Y_MM,
    surface_z,
    white,
)

create_actor(
    collection,
    f"{CONFIG_ID}_Actor_03",
    ACTOR_03_X_MM,
    ACTOR_03_Y_MM,
    surface_z,
    white,
)


# ------------------------------------------------------------
# NETS
# ------------------------------------------------------------

create_net(
    collection,
    f"{CONFIG_ID}_Net_01",
    NET_01_X_MM,
    NET_01_Y_MM,
    NET_01_ROTATION_DEG,
    surface_z,
    white,
)

create_net(
    collection,
    f"{CONFIG_ID}_Net_02",
    NET_02_X_MM,
    NET_02_Y_MM,
    NET_02_ROTATION_DEG,
    surface_z,
    white,
)


# ------------------------------------------------------------
# GATES
# ------------------------------------------------------------

create_gate(
    collection,
    f"{CONFIG_ID}_Gate_01",
    GATE_01_X_MM,
    GATE_01_Y_MM,
    GATE_01_ROTATION_DEG,
    surface_z,
    white,
)

create_gate(
    collection,
    f"{CONFIG_ID}_Gate_02",
    GATE_02_X_MM,
    GATE_02_Y_MM,
    GATE_02_ROTATION_DEG,
    surface_z,
    white,
)


collection["configuration_id"] = CONFIG_ID
collection["field_id"] = "FIELD-0004"
collection["field_name"] = "Divergence"
collection["configuration_version"] = "v2"


# Hide canonical source from rendering.
source_field.hide_render = True


# ============================================================
# SAVE NEW FILE
# ============================================================

source_blend = Path(
    bpy.data.filepath
)

if source_blend:
    output_path = (
        source_blend.parent
        / "field_divergence_reference_config_v02.blend"
    )
else:
    output_path = (
        Path.cwd()
        / "field_divergence_reference_config_v02.blend"
    )


bpy.ops.wm.save_as_mainfile(
    filepath=str(output_path)
)


print("")
print("=" * 72)
print("OWDE CONFIG-0004 v2 COMPLETE")
print("=" * 72)
print("")
print("Default Divergence")
print("+ Actor 01")
print("+ Actor 02")
print("+ Actor 03")
print("+ Net 01")
print("+ Net 02")
print("+ Gate 01")
print("+ Gate 02")
print("")
print("Configuration concentrated around Divergence throat.")
print("")
print(f"Saved: {output_path}")
print("")
