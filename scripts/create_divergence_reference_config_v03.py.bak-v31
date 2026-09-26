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
# OWDE — CONFIG-0004 v3
#
# Architecture-dependent Divergence configuration.
#
# 3 Actors
# 2 Nets
# 1 Gate
#
# Default FIELD-0004 Divergence remains unchanged.
# ============================================================

SOURCE_FIELD = "FIELD-0004_Divergence"

CONFIG_ID = "CONFIG-0004"

COLLECTION_NAME = (
    "CONFIG-0004_Divergence_Reference_v3"
)

MM_TO_M = 0.001


# ============================================================
# PLACEMENT PARAMETERS
#
# Approximate field:
#   406.4 x 508 mm
#
# Diveence junction ≈ center of field.
# ============================================================


# ------------------------------------------------------------
# ACTORS
# ------------------------------------------------------------

# Actor occupying lower stem.
ACTOR_01_X_MM = 0.0
ACTOR_01_Y_MM = -155.0

# Actor occupying junction / throat.
ACTOR_02_X_MM = 0.0
ACTOR_02_Y_MM = 18.0

# Actor occupying upper-right territory.
ACTOR_03_X_MM = 100.0
ACTOR_03_Y_MM = 155.0


# ------------------------------------------------------------
# NET 01
#
# Crosses the LEFT diverging branch.
#
# Divergence branch is approximately 32 degrees from vertical,
# so +32 degrees gives us a useful crossing relationship.
# ------------------------------------------------------------

NET_01_X_MM = -82.0
NET_01_Y_MM = 105.0
NET_01_ROTATION_DEG = 32.0


# ------------------------------------------------------------
# NET 02
#
# Crosses the architecture close to the junction.
# This is intentionally not centered high up with Net 01# ------------------------------------------------------------

NET_02_X_MM = 20.0
NET_02_Y_MM = 48.0
NET_02_ROTATION_DEG = 0.0


# ------------------------------------------------------------
# GATE
#
# Crosses the lower stem well below the junction.
#
# This prevents Gate + Nets from becoming a central cage.
# ------------------------------------------------------------

GATE_01_X_MM = 0.0
GATE_01_Y_MM = -92.0
GATE_01_ROTATION_DEG = 0.0


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
        f"{CONFIG_ID}_FIELD-0004_Divergence_v3"
    )

    collection.objects.link(duplicate)

    center = bbox_center(source)

    duplicate.location.x -= center.x
    duplicate.location.y -= center.y

    duplicate["configuration_id"] = CONFIG_ID
    duplicate["configuration_version"] = "v3"
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
    obj["configuration_version"] = "v3"

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
    obj["configuration_version"] = "v3"

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
    obj["configuration_version"] = "v3"

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
        "CONFIG-0004_FIELD-0004_Divergence",
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
# BUILD V3 COLLECTION
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
    f"{CONFIG_ID}_v3_Actor_01",
    ACTOR_01_X_MM,
    ACTOR_01_Y_MM,
    surface_z,
    white,
)

create_actor(
    collection,
    f"{CONFIG_ID}_v3_Actor_02",
    ACTOR_02_X_MM,
    ACTOR_02_Y_MM,
    surface_z,
    white,
)

create_actor(
    collection,
    f"{CONFIG_ID}_v3_Actor_03",
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
    f"{CONFIG_ID}_v3_Net_01",
    NET_01_X_MM,
    NET_01_Y_MM,
    NET_01_ROTATION_DEG,
    surface_z,
    white,
)

create_net(
    collection,
    f"{CONFIG_ID}_v3_Net_02",
    NET_02_X_MM,
    NET_02_Y_MM,
    NET_02_ROTATION_DEG,
    surface_z,
    white,
)


# ------------------------------------------------------------
# GATE
# ------------------------------------------------------------

create_gate(
    collection,
    f"{CONFIG_ID}_v3_Gate_01",
    GATE_01_X_MM,
    GATE_01_Y_MM,
    GATE_01_ROTATION_DEG,
    surface_z,
    white,
)


collection["configuration_id"] = CONFIG_ID
collection["configuration_version"] = "v3"
collection["field_id"] = "FIELD-0004"
collection["field_name"] = "Divergence"


# ============================================================
# PRESENT ONLY V3
#
# Preserve earlier collections but hide them in viewport/render.
# ============================================================

for other_collection in bpy.data.collections:
    if (
        other_collection.name.startswith(
            "CONFIG-0004_Divergence_Reference"
        )
        and other_collection != collection
    ):
        other_collection.hide_viewport = True
        other_collection.hide_render = True

collection.hide_viewport = False
collection.hide_render = False

source_field.hide_render = True


# ============================================================
# SAVE AS NEW VERSION
# ============================================================

source_blend = Path(
    bpy.data.filepath
)

if source_blend:
    output_path = (
        source_blend.parent
        / "field_divergence_reference_config_v03.blend"
    )
else:
    output_path = (
        Path.cwd()
        / "field_divergence_reference_config_v03.blend"
    )


bpy.ops.wm.save_as_mainfile(
    filepath=str(output_path)
)


print("")
print("=" * 72)
print("OWDE CONFIG-0004 v3 COMPLETE")
print("=" * 72)
print("")
print("Default Divergence")
print("+ 3 Actors")
print("+ 2 Nets")
print("+ 1 Gate")
print("")
print("Operational placement:")
print("  Actor 01 -> lower stem")
print("  Gate 01  -> lower passage")
print("  Actor 02 -> junction")
print("  Net 01   -> left branch")
print("  Net 02   -> near junction")
print("  Actor 03 -> upper-right territory")
print("")
print(f"Saved: {output_path}")
print("")
