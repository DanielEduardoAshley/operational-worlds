"""
Operational Worlds Design Engine
Field Architecture Standard Exporter

Run inside Blender, for example:

    blender field_architectures.blend \
        --background \
        --python scripts/render_field_architectures.py \
        -- --preset REGULAR

or:

    blender field_architectures.blend \
        --background \
        --python scripts/render_field_architectures.py \
        -- --preset LARGE
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Vector


EXPORT_VERSION = "0.1.0"

FIELD_IDS = (
    ("FIELD-0001", "Division"),
    ("FIELD-0002", "Intersection"),
    ("FIELD-0003", "Bottleneck"),
    ("FIELD-0004", "Divergence"),
    ("FIELD-0005", "Nested_Zones"),
    ("FIELD-0006", "Offset_Zones"),
    ("FIELD-0007", "Terminal_Target"),
)


@dataclass(frozen=True)
class ExportPreset:
    name: str
    width_px: int
    height_px: int
    margin_ratio: float
    samples: int


PRESETS = {
    "REGULAR": ExportPreset(
        name="REGULAR",
        width_px=1600,
        height_px=2000,
        margin_ratio=0.025,
        samples=64,
    ),

    "MEDIUM": ExportPreset(
        name="MEDIUM",
        width_px=2400,
        height_px=3000,
        margin_ratio=0.025,
        samples=96,
    ),

    "LARGE": ExportPreset(
        name="LARGE",
        width_px=3200,
        height_px=4000,
        margin_ratio=0.025,
        samples=128,
    ),
}


def parse_args():
    argv = sys.argv

    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default="REGULAR",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional custom export directory",
    )

    return parser.parse_args(argv)


def find_field_object(field_id: str):
    """Find the primary generated field object by field ID."""

    matches = []

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue

        if field_id.upper() in obj.name.upper():
            matches.append(obj)

    if not matches:
        return None

    # Prefer the largest mesh object in case helper objects remain.
    def approximate_volume(obj):
        dimensions = obj.dimensions
        return dimensions.x * dimensions.y * max(dimensions.z, 0.001)

    return max(
        matches,
        key=approximate_volume,
    )


def world_bbox(obj):
    corners = [
        obj.matrix_world @ Vector(corner)
        for corner in obj.bound_box
    ]

    xs = [p.x for p in corners]
    ys = [p.y for p in corners]
    zs = [p.z for p in corners]

    return (
        min(xs),
        max(xs),
        min(ys),
        max(ys),
        min(zs),
        max(zs),
    )


def ensure_camera():
    camera = bpy.data.objects.get(
        "OWDE_EXPORT_CAMERA"
    )

    if camera is None:
        data = bpy.data.cameras.new(
            "OWDE_EXPORT_CAMERA"
        )

        camera = bpy.data.objects.new(
            "OWDE_EXPORT_CAMERA",
            data,
        )

        bpy.context.scene.collection.objects.link(
            camera
        )

    camera.data.type = "ORTHO"

    bpy.context.scene.camera = camera

    return camera


def configure_camera(camera, obj, preset):
    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = world_bbox(obj)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0

    width = max_x - min_x
    height = max_y - min_y

    margin = preset.margin_ratio

    # Blender orthographic scale represents vertical view span.
    desired_vertical = height * (1.0 + margin * 2.0)

    # Ensure horizontal field also fits the render aspect ratio.
    aspect = preset.width_px / preset.height_px

    vertical_required_for_width = (
        width * (1.0 + margin * 2.0)
    ) / aspect

    camera.data.ortho_scale = max(
        desired_vertical,
        vertical_required_for_width,
    )

    camera.location = (
        center_x,
        center_y,
        max_z + 2.0,
    )

    # Look straight down.
    camera.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )

    camera.rotation_euler[0] = 0.0

    # Blender camera looks down local -Z.
    camera.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )


def set_visibility(target):
    """Render one field at a time."""

    for field_id, _ in FIELD_IDS:
        obj = find_field_object(field_id)

        if obj is None:
            continue

        hidden = obj != target

        obj.hide_render = hidden


# ---------------------------------------------------------------------------
# Canonical export materials
# ---------------------------------------------------------------------------

CANONICAL_FIELD_GREEN = (0.010, 0.045, 0.032, 1.0)
CANONICAL_LINE_WHITE = (0.86, 0.84, 0.76, 1.0)


def canonical_material(name, color):
    """
    Canonical OWDE presentation material.

    Uses Principled shading so the field retains physical depth while
    standardized export lighting keeps color consistent between fields.
    """

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name=name)

    material.use_nodes = True
    material.diffuse_color = color

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.88
    bsdf.inputs["Metallic"].default_value = 0.0

    links.new(
        bsdf.outputs["BSDF"],
        output.inputs["Surface"],
    )

    return material


def normalize_field_materials(obj):
    """
    Replace field material slots with canonical OWDE export materials.

    The generated field objects contain the green substrate and warm-white
    architecture in a single mesh with separate material indices.
    """

    green = canonical_material(
        "OWDE_EXPORT_FIELD_GREEN",
        CANONICAL_FIELD_GREEN,
    )

    white = canonical_material(
        "OWDE_EXPORT_LINE_WHITE",
        CANONICAL_LINE_WHITE,
    )

    if len(obj.data.materials) < 2:
        raise RuntimeError(
            f"{obj.name}: expected at least two material slots "
            "(field + architecture)"
        )

    # Preserve the existing polygon material indices while replacing
    # the materials occupying those slots.
    obj.data.materials[0] = green
    obj.data.materials[1] = white

# ---------------------------------------------------------------------------
# Canonical critique illumination
# ---------------------------------------------------------------------------

def configure_export_lighting():
    """
    Standardized neutral world illumination.

    All scene lights are disabled so every architecture receives exactly
    the same illumination regardless of its position in the Blender scene.
    """

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True

    scene = bpy.context.scene

    world = scene.world

    if world is None:
        world = bpy.data.worlds.new("OWDE_EXPORT_WORLD")
        scene.world = world

    world.use_nodes = True

    background = world.node_tree.nodes.get("Background")

    if background is not None:
        background.inputs["Color"].default_value = (
            0.80,
            0.80,
            0.80,
            1.0,
        )

        background.inputs["Strength"].default_value = 0.35


def configure_render(scene, preset):
    available_engines = {
        item.identifier
        for item in scene.render.bl_rna.properties["engine"].enum_items
    }

    if "BLENDER_EEVEE_NEXT" in available_engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = preset.width_px
    scene.render.resolution_y = preset.height_px
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"

    scene.render.film_transparent = False

    # Consistent color management across Blender versions.
    available_looks = {
        item.identifier
        for item in scene.view_settings.bl_rna.properties["look"].enum_items
    }

    if "AgX - Medium High Contrast" in available_looks:
        scene.view_settings.look = "AgX - Medium High Contrast"
    elif "Medium High Contrast" in available_looks:
        scene.view_settings.look = "Medium High Contrast"

    # Prevent accidental animation/frame differences.
    scene.frame_set(1)


def output_root(preset, custom_output=None):
    if custom_output:
        root = Path(custom_output)
    else:
        root = (
            Path.cwd()
            / "exports"
            / "field_architectures"
            / preset.name.lower()
        )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return root


def render_field(
    *,
    field_id,
    name,
    obj,
    camera,
    preset,
    root,
):
    # Standardize presentation materials before every render.
    normalize_field_materials(obj)

    configure_export_lighting()

    configure_camera(
        camera,
        obj,
        preset,
    )

    set_visibility(obj)

    filename = (
        f"{field_id}_{name}_{preset.name}.png"
    )

    destination = root / filename

    bpy.context.scene.render.filepath = str(
        destination.resolve()
    )

    bpy.ops.render.render(
        write_still=True
    )

    print(
        f"PASS: {destination}"
    )

    return {
        "field_id": field_id,
        "name": name,
        "file": filename,
        "width_px": preset.width_px,
        "height_px": preset.height_px,
    }


def main():
    args = parse_args()

    preset = PRESETS[args.preset]

    scene = bpy.context.scene

    configure_render(
        scene,
        preset,
    )

    camera = ensure_camera()

    root = output_root(
        preset,
        args.output,
    )

    records = []

    missing = []

    print("")
    print("OPERATIONAL WORLDS")
    print("FIELD ARCHITECTURE STANDARD EXPORT")
    print("")
    print(f"Preset: {preset.name}")
    print(
        f"Resolution: "
        f"{preset.width_px} × {preset.height_px}"
    )
    print("")

    for field_id, name in FIELD_IDS:
        obj = find_field_object(
            field_id
        )

        if obj is None:
            missing.append(field_id)

            print(
                f"SKIP: {field_id} "
                f"(object not found)"
            )

            continue

        record = render_field(
            field_id=field_id,
            name=name,
            obj=obj,
            camera=camera,
            preset=preset,
            root=root,
        )

        records.append(record)

    manifest = {
        "system": "Operational Worlds Design Engine",
        "exporter": "Field Architecture Standard Exporter",
        "export_version": EXPORT_VERSION,
        "preset": preset.name,
        "resolution": {
            "width_px": preset.width_px,
            "height_px": preset.height_px,
        },
        "margin_ratio": preset.margin_ratio,
        "fields": records,
        "missing": missing,
    }

    manifest_path = (
        root / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Restore visibility.
    for field_id, _ in FIELD_IDS:
        obj = find_field_object(field_id)

        if obj is not None:
            obj.hide_render = False

    print("")
    print("EXPORT COMPLETE")
    print("")
    print(f"Output: {root}")
    print(
        f"Rendered: {len(records)} / "
        f"{len(FIELD_IDS)}"
    )

    if missing:
        print("")
        print("Missing:")
        for item in missing:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
