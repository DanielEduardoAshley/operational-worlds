import bpy
from pathlib import Path
from mathutils import Vector

from owde_addon.core.competition_builders import (
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
)

from owde_addon.blender.competition import _mesh_to_blender


# ============================================================
# OWDE — DIVERGENCE CONFIGURATION STUDIES
#
# CONFIG-0001
#   Default Divergence + 2 Actors
#
# CONFIG-0002
#   Default Divergence + 2 Actors + Net
#
# CONFIG-0003
#   Default Divergence + 2 Actors + Net + Gate
#
# All three configurations preserve:
#   - identical Divergence geometry
#   - identical Actor positions
#   - identical Net position in 0002 and 0003
#
# CONFIG-0003 adds only the Gate.
# ============================================================


SOURCE_FIELD = "FIELD-0004_Divergence"

MM_TO_M = 0.001


# ------------------------------------------------------------
# Configuration placement
#
# These are intentionally simple first propositions rather
# than "balanced compositions."
#
# Actor 01 = lower corridor
# Actor 02 = upper/open territory
#
# Net = crosses the architecture around the transition.
# Gate = introduced as the sole new variable in CONFIG-0003.
# ------------------------------------------------------------

ACTOR_01_X_MM = 0.0
ACTOR_01_Y_MM = -145.0
ACTOR_01_ROTATION_DEG = 0.0

ACTOR_02_X_MM = 72.0
ACTOR_02_Y_MM = 135.0
ACTOR_02_ROTATION_DEG = 0.0

NET_X_MM = 0.0
NET_Y_MM = 15.0
NET_ROTATION_DEG = 90.0

GATE_X_MM = -78.0
GATE_Y_MM = 105.0
GATE_ROTATION_DEG = 90.0


CONFIGS = [
    {
        "id": "CONFIG-0001",
        "name": "Divergence_2_Actors",
        "actors": True,
        "net": False,
        "gate": False,
    },
    {
        "id": "CONFIG-0002",
        "name": "Divergence_2_Actors_Net",
        "actors": True,
        "net": True,
        "gate": False,
    },
    {
        "id": "CONFIG-0003",
        "name": "Divergence_2_Actors_Net_Gate",
        "actors": True,
        "net": True,
        "gate": True,
    },
]


# ============================================================
# Helpers
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


def set_xy_mm(
    obj,
    x_mm,
    y_mm,
    surface_z,
    rotation_deg=0.0,
):
    from math import radians

    obj.location.x = x_mm * MM_TO_M
    obj.location.y = y_mm * MM_TO_M
    obj.location.z = surface_z

    obj.rotation_euler[2] = radians(
        rotation_deg
    )


def duplicate_field(
    source,
    collection,
    config_id,
):
    duplicate = source.copy()

    if source.data is not None:
        duplicate.data = source.data.copy()

    duplicate.name = (
        f"{config_id}_FIELD-0004_Divergence"
    )

    collection.objects.link(duplicate)

    # Normalize the field to XY origin so every configuration
    # is spatially identical and independently reproducible.
    center = bbox_center(source)

    duplicate.location.x -= center.x
    duplicate.location.y -= center.y

    duplicate["configuration_id"] = config_id
    duplicate["field_id"] = "FIELD-0004"
    duplicate["field_name"] = "Divergence"

    return duplicate


def make_actor(
    collection,
    name,
    x_mm,
    y_mm,
    surface_z,
    rotation_deg,
    material,
):
    mesh = build_actor_mesh()

    obj = _mesh_to_blender(
        mesh,
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

    set_xy_mm(
        obj,
        x_mm,
        y_mm,
        surface_z,
        rotation_deg,
    )

    obj["primitive_type"] = "ACTOR"

    return obj


def make_net(
    collection,
    name,
    surface_z,
    material,
):
    mesh = build_net_mesh()

    obj = _mesh_to_blender(
        mesh,
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

    set_xy_mm(
        obj,
        NET_X_MM,
        NET_Y_MM,
        surface_z,
        NET_ROTATION_DEG,
    )

    obj["primitive_type"] = "NET"

    return obj


def make_gate(
    collection,
    name,
    surface_z,
    material,
):
    mesh = build_gate_mesh()

    obj = _mesh_to_blender(
        mesh,
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

    set_xy_mm(
        obj,
        GATE_X_MM,
        GATE_Y_MM,
        surface_z,
        GATE_ROTATION_DEG,
    )

    obj["primitive_type"] = "GATE"

    return obj


# ============================================================
# Resolve canonical Divergence field
# ============================================================

source_field = bpy.data.objects.get(
    SOURCE_FIELD
)

if source_field is None:
    raise RuntimeError(
        f"Could not find canonical field object: "
        f"{SOURCE_FIELD}"
    )


field_center = bbox_center(
    source_field
)

source_surface_z = bbox_top_z(
    source_field
)

# After centering the duplicate in XY, its Z remains identical.
surface_z = source_surface_z


print("")
print("=" * 64)
print("OWDE Divergence Configurations")
print("=" * 64)
print("")
print(
    f"Source field: {source_field.name}"
)
print(
    f"Source center: "
    f"{field_center.x:.4f}, "
    f"{field_center.y:.4f}"
)
print(
    f"Field surface Z: {surface_z:.4f}"
)
print("")


white = make_white_material()


# ============================================================
# Build configurations
# ============================================================

for spec in CONFIGS:

    config_id = spec["id"]

    collection_name = (
        f"{config_id}_{spec['name']}"
    )

    collection = get_or_create_collection(
        collection_name
    )

    clear_collection(
        collection
    )

    print(
        f"Building {collection_name}"
    )

    field = duplicate_field(
        source_field,
        collection,
        config_id,
    )

    # Surface height of the duplicated field.
    config_surface_z = bbox_top_z(
        field
    )

    # --------------------------------------------------------
    # ACTORS
    # --------------------------------------------------------

    if spec["actors"]:

        actor_01 = make_actor(
            collection,
            f"{config_id}_Actor_01",
            ACTOR_01_X_MM,
            ACTOR_01_Y_MM,
            config_surface_z,
            ACTOR_01_ROTATION_DEG,
            white,
        )

        actor_02 = make_actor(
            collection,
            f"{config_id}_Actor_02",
            ACTOR_02_X_MM,
            ACTOR_02_Y_MM,
            config_surface_z,
            ACTOR_02_ROTATION_DEG,
            white,
        )

        actor_01["configuration_id"] = config_id
        actor_02["configuration_id"] = config_id

    # --------------------------------------------------------
    # NET
    # --------------------------------------------------------

    if spec["net"]:

        net = make_net(
            collection,
            f"{config_id}_Net",
            config_surface_z,
            white,
        )

        net["configuration_id"] = config_id

    # --------------------------------------------------------
    # GATE
    # --------------------------------------------------------

    if spec["gate"]:

        gate = make_gate(
            collection,
            f"{config_id}_Gate",
            config_surface_z,
            white,
        )

        gate["configuration_id"] = config_id

    collection["configuration_id"] = config_id
    collection["field_id"] = "FIELD-0004"
    collection["field_name"] = "Divergence"

    print(
        f"  ✓ {config_id}"
    )


# ============================================================
# Hide canonical source architecture collection/object only
# from configuration presentation.
#
# We don't delete or mutate the original.
# ============================================================

source_field.hide_render = True


# ============================================================
# Save as a NEW Blender file
# ============================================================

source_blend = Path(
    bpy.data.filepath
)

if source_blend:
    output_path = (
        source_blend.parent
        / "field_divergee_configs_v01.blend"
    )
else:
    output_path = (
        Path.cwd()
        / "field_divergence_configs_v01.blend"
    )

bpy.ops.wm.save_as_mainfile(
    filepath=str(output_path)
)


print("")
print("=" * 64)
print("Configuration build complete")
print("=" * 64)
print("")
print("Created:")
print(
    "  CONFIG-0001 — Divergence + 2 Actors"
)
print(
    "  CONFIG-0002 — Divergence + 2 Actors + Net"
)
print(
    "  CONFIG-0003 — Divergence + 2 Actors + Net + Gate"
)
print("")
print(
    f"Saved: {output_path}"
)
print("")
