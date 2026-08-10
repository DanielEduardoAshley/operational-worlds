"""Generate a printer-facing OWDE quotation package.

Run with Blender:

    /Applications/Blender.app/Contents/MacOS/Blender \
        --background \
        --python scripts/export_canonical_quote_package.py \
        -- \
        --output exports/OWDE_Canonical_Quote_Package \
        --overwrite

The package contains OW09, OW10, OW11, OW12, and OW14 at:

- 152.4 × 152.4 mm
- 304.8 × 304.8 mm

STL files are exported with numerical coordinates in millimeters.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZIP_DEFLATED, ZipFile

try:
    import bpy
except ImportError as error:
    raise SystemExit(
        "Run this script through Blender, not ordinary Python."
    ) from error


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from owde_addon.core.builders import (
    build_base_tile_mesh,
    build_feature_mesh,
)
from owde_addon.core.mesh import MeshData
from owde_addon.core.models import ShapeType, TileParameters


PACKAGE_VERSION = "0.1.0"
MM_TO_METERS = 0.001


@dataclass(frozen=True)
class SizeDefinition:
    key: str
    label: str
    width_mm: float
    depth_mm: float
    scale_factor: float

    @property
    def tile_height_mm(self) -> float:
        return 8.0 * self.scale_factor

    @property
    def feature_width_mm(self) -> float:
        return 55.0 * self.scale_factor

    @property
    def feature_height_mm(self) -> float:
        return 5.0 * self.scale_factor


@dataclass(frozen=True)
class PrimitiveDefinition:
    primitive_id: str
    shape: ShapeType
    name: str
    filename: str
    base_material: str
    feature_material: str
    finish: str
    functional_status: str
    fabrication_notes: str


SIZES = (
    SizeDefinition(
        key="6in",
        label="6 × 6 inch",
        width_mm=152.4,
        depth_mm=152.4,
        scale_factor=1.524,
    ),
    SizeDefinition(
        key="12in",
        label="12 × 12 inch",
        width_mm=304.8,
        depth_mm=304.8,
        scale_factor=3.048,
    ),
)


PRIMITIVES = (
    PrimitiveDefinition(
        primitive_id="PRIM-0009",
        shape=ShapeType.LENS,
        name="Lens",
        filename="PRIM-0009_Lens",
        base_material="Matte off-white PLA, PETG, resin, or nylon",
        feature_material="Clear or translucent resin/acrylic",
        finish="Matte base; smooth polished or gloss lens",
        functional_status=(
            "Visual lens prototype; no optical focal specification"
        ),
        fabrication_notes=(
            "Quote as one opaque form-test print and as a two-part "
            "assembly with a transparent feature."
        ),
    ),
    PrimitiveDefinition(
        primitive_id="PRIM-0010",
        shape=ShapeType.MIRROR,
        name="Mirror",
        filename="PRIM-0010_Mirror",
        base_material="Matte off-white PLA, PETG, resin, or nylon",
        feature_material=(
            "Mirrored acrylic, reflective film, or polished metal insert"
        ),
        finish="Matte base and bezel; highly reflective central surface",
        functional_status="Reflective visual surface",
        fabrication_notes=(
            "Feature STL is an insert template. Quote mirrored acrylic "
            "and reflective-film options separately."
        ),
    ),
    PrimitiveDefinition(
        primitive_id="PRIM-0011",
        shape=ShapeType.LIGHT_SOURCE,
        name="Light Source",
        filename="PRIM-0011_Light_Source",
        base_material="Matte off-white PLA, PETG, resin, or nylon",
        feature_material="Frosted translucent resin or acrylic",
        finish="Matte base; frosted translucent bulb",
        functional_status=(
            "Diffuser prototype; electronics are not included"
        ),
        fabrication_notes=(
            "Quote the bulb as a separate translucent component. "
            "Optional warm LED integration may be quoted separately."
        ),
    ),
    PrimitiveDefinition(
        primitive_id="PRIM-0012",
        shape=ShapeType.WEIGHT,
        name="Weight",
        filename="PRIM-0012_Weight",
        base_material="Matte off-white PLA, PETG, resin, or nylon",
        feature_material=(
            "Metallic-finish polymer, metal-filled polymer, "
            "or fabricated metal"
        ),
        finish="Matte base; brushed-metal cube",
        functional_status=(
            "Symbolic weight unless physical ballast is separately specified"
        ),
        fabrication_notes=(
            "Quote metallic polymer and actual metal alternatives. "
            "The cube is rotated 45 degrees and has chamfered corners."
        ),
    ),
    PrimitiveDefinition(
        primitive_id="PRIM-0014",
        shape=ShapeType.SENSOR,
        name="Sensor",
        filename="PRIM-0014_Sensor",
        base_material="Matte off-white PLA, PETG, resin, or nylon",
        feature_material="Gloss black resin, acrylic, PLA, or PETG",
        finish="Matte base and recess; polished piano-black dome",
        functional_status=(
            "Symbolic sensor housing; electronics are not included"
        ),
        fabrication_notes=(
            "Quote the detector dome as a separately finished component. "
            "Optional electronic integration may be quoted separately."
        ),
    ),
)


def parse_arguments() -> argparse.Namespace:
    arguments = []

    if "--" in sys.argv:
        arguments = sys.argv[
            sys.argv.index("--") + 1:
        ]

    parser = argparse.ArgumentParser(
        description="Export OWDE canonical-primitives RFQ package."
    )

    parser.add_argument(
        "--output",
        default="exports/OWDE_Canonical_Quote_Package",
    )

    parser.add_argument(
        "--quantity",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
    )

    parser.add_argument(
        "--render-resolution",
        type=int,
        default=1600,
    )

    return parser.parse_args(arguments)


def resolve_output(raw_value: str) -> Path:
    candidate = Path(raw_value).expanduser()

    if not candidate.is_absolute():
        candidate = REPOSITORY_ROOT / candidate

    return candidate.resolve()


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def create_object(
    name: str,
    mesh_data: MeshData,
) -> bpy.types.Object:
    mesh_data.validate()

    mesh = bpy.data.meshes.new(
        f"{name}_Mesh"
    )

    vertices = [
        (
            x * MM_TO_METERS,
            y * MM_TO_METERS,
            z * MM_TO_METERS,
        )
        for x, y, z in mesh_data.vertices
    ]

    mesh.from_pydata(
        vertices,
        [],
        list(mesh_data.faces),
    )

    mesh.update(calc_edges=True)

    object_ = bpy.data.objects.new(
        name,
        mesh,
    )

    bpy.context.scene.collection.objects.link(
        object_
    )

    return object_


def select_only(
    objects: Iterable[bpy.types.Object],
) -> None:
    bpy.ops.object.select_all(action="DESELECT")

    active = None

    for object_ in objects:
        object_.hide_set(False)
        object_.hide_render = False
        object_.select_set(True)
        active = object_

    if active is not None:
        bpy.context.view_layer.objects.active = active


def export_stl(
    filepath: Path,
    objects: Iterable[bpy.types.Object],
) -> None:
    filepath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    select_only(objects)

    if hasattr(bpy.ops.wm, "stl_export"):
        operator = bpy.ops.wm.stl_export

        supported = {
            property_.identifier
            for property_ in operator.get_rna_type().properties
        }

        arguments: dict[str, Any] = {
            "filepath": str(filepath),
        }

        optional = {
            "check_existing": False,
            "export_selected_objects": True,
            "apply_modifiers": True,
            "ascii_format": False,
            "global_scale": 1000.0,
            "apply_unit_scale": False,
        }

        for key, value in optional.items():
            if key in supported:
                arguments[key] = value

        result = operator(**arguments)

    elif hasattr(bpy.ops.export_mesh, "stl"):
        result = bpy.ops.export_mesh.stl(
            filepath=str(filepath),
            use_selection=True,
            use_scene_unit=False,
            global_scale=1000.0,
            ascii=False,
        )

    else:
        raise RuntimeError(
            "No STL export operator is available in this Blender build."
        )

    if "FINISHED" not in result:
        raise RuntimeError(
            f"STL export failed: {filepath}"
        )


def bounds_mm(
    mesh_data: MeshData,
) -> dict[str, float]:
    xs = [value[0] for value in mesh_data.vertices]
    ys = [value[1] for value in mesh_data.vertices]
    zs = [value[2] for value in mesh_data.vertices]

    return {
        "minimum_x_mm": min(xs),
        "maximum_x_mm": max(xs),
        "minimum_y_mm": min(ys),
        "maximum_y_mm": max(ys),
        "minimum_z_mm": min(zs),
        "maximum_z_mm": max(zs),
        "overall_width_mm": max(xs) - min(xs),
        "overall_depth_mm": max(ys) - min(ys),
        "overall_height_mm": max(zs) - min(zs),
    }


def create_material(
    name: str,
    base_color: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.5,
    transmission: float = 0.0,
    emission_color: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = material.node_tree.nodes.get(
        "Principled BSDF"
    )

    if principled is not None:
        inputs = principled.inputs

        if inputs.get("Base Color"):
            inputs["Base Color"].default_value = base_color

        if inputs.get("Metallic"):
            inputs["Metallic"].default_value = metallic

        if inputs.get("Roughness"):
            inputs["Roughness"].default_value = roughness

        transmission_input = (
            inputs.get("Transmission Weight")
            or inputs.get("Transmission")
        )

        if transmission_input is not None:
            transmission_input.default_value = transmission

        emission_input = (
            inputs.get("Emission Color")
            or inputs.get("Emission")
        )

        if (
            emission_input is not None
            and emission_color is not None
        ):
            emission_input.default_value = emission_color

        if inputs.get("Emission Strength"):
            inputs["Emission Strength"].default_value = (
                emission_strength
            )

    return material


def tile_material() -> bpy.types.Material:
    return create_material(
        "OWDE Quote Tile",
        (0.76, 0.73, 0.68, 1.0),
        roughness=0.58,
    )


def feature_material(
    shape: ShapeType,
) -> bpy.types.Material:
    if shape is ShapeType.LENS:
        return create_material(
            "OWDE Quote Clear Lens",
            (0.90, 0.97, 1.0, 1.0),
            roughness=0.055,
            transmission=0.96,
        )

    if shape is ShapeType.MIRROR:
        return create_material(
            "OWDE Quote Mirror",
            (0.86, 0.88, 0.92, 1.0),
            metallic=1.0,
            roughness=0.025,
        )

    if shape is ShapeType.LIGHT_SOURCE:
        return create_material(
            "OWDE Quote Frosted Light",
            (1.0, 0.82, 0.53, 1.0),
            roughness=0.31,
            transmission=0.16,
            emission_color=(1.0, 0.34, 0.05, 1.0),
            emission_strength=3.2,
        )

    if shape is ShapeType.WEIGHT:
        return create_material(
            "OWDE Quote Brushed Steel",
            (0.27, 0.29, 0.31, 1.0),
            metallic=0.94,
            roughness=0.24,
        )

    if shape is ShapeType.SENSOR:
        return create_material(
            "OWDE Quote Piano Black",
            (0.002, 0.003, 0.005, 1.0),
            metallic=0.08,
            roughness=0.045,
        )

    return tile_material()


def assign_material(
    object_: bpy.types.Object,
    material: bpy.types.Material,
) -> None:
    object_.data.materials.clear()
    object_.data.materials.append(material)


def smooth_feature(
    object_: bpy.types.Object,
    shape: ShapeType,
) -> None:
    smooth_shapes = {
        ShapeType.LENS,
        ShapeType.LIGHT_SOURCE,
        ShapeType.SENSOR,
    }

    for polygon in object_.data.polygons:
        polygon.use_smooth = (
            shape in smooth_shapes
        )


def create_camera(
    name: str,
) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name)

    camera = bpy.data.objects.new(
        name,
        camera_data,
    )

    bpy.context.scene.collection.objects.link(
        camera
    )

    camera_data.type = "ORTHO"

    return camera


def point_at(
    object_: bpy.types.Object,
    target: bpy.types.Object,
) -> None:
    constraint = object_.constraints.new(
        type="TRACK_TO"
    )

    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: bpy.types.Object,
) -> bpy.types.Object:
    data = bpy.data.lights.new(
        name=name,
        type="AREA",
    )

    data.energy = energy
    data.shape = "DISK"
    data.size = size

    object_ = bpy.data.objects.new(
        name,
        data,
    )

    bpy.context.scene.collection.objects.link(
        object_
    )

    object_.location = location

    point_at(
        object_,
        target,
    )

    return object_


def available_render_engine() -> str:
    scene = bpy.context.scene

    identifiers = {
        item.identifier
        for item in scene.render.bl_rna.properties[
            "engine"
        ].enum_items
    }

    for candidate in (
        "BLENDER_EEVEE",
        "BLENDER_EEVEE_NEXT",
        "CYCLES",
    ):
        if candidate in identifiers:
            return candidate

    raise RuntimeError(
        f"No supported render engine found: {sorted(identifiers)}"
    )


def configure_render(
    filepath: Path,
    resolution: int,
) -> None:
    scene = bpy.context.scene

    scene.render.engine = available_render_engine()
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(filepath)

    try:
        scene.view_settings.look = (
            "AgX - Medium High Contrast"
        )
    except TypeError:
        pass


def configure_world() -> None:
    scene = bpy.context.scene

    if scene.world is None:
        scene.world = bpy.data.worlds.new(
            "OWDE Quote World"
        )

    scene.world.use_nodes = True

    background = scene.world.node_tree.nodes.get(
        "Background"
    )

    if background is not None:
        background.inputs["Color"].default_value = (
            0.018,
            0.020,
            0.024,
            1.0,
        )
        background.inputs["Strength"].default_value = 0.28


def create_render_rig(
    tile_width_mm: float,
) -> tuple[
    bpy.types.Object,
    bpy.types.Object,
    list[bpy.types.Object],
]:
    scale_m = tile_width_mm * MM_TO_METERS

    target = bpy.data.objects.new(
        "OWDE Quote Target",
        None,
    )

    bpy.context.scene.collection.objects.link(
        target
    )

    target.location = (
        0.0,
        0.0,
        scale_m * 0.05,
    )

    camera = create_camera(
        "OWDE Quote Camera"
    )

    point_at(
        camera,
        target,
    )

    bpy.context.scene.camera = camera

    lights = [
        add_area_light(
            "OWDE Quote Key",
            (
                -scale_m * 1.10,
                -scale_m * 1.25,
                scale_m * 1.65,
            ),
            1000.0,
            scale_m * 2.0,
            target,
        ),
        add_area_light(
            "OWDE Quote Fill",
            (
                scale_m * 1.15,
                -scale_m * 0.20,
                scale_m * 0.90,
            ),
            600.0,
            scale_m * 2.3,
            target,
        ),
        add_area_light(
            "OWDE Quote Rim",
            (
                0.0,
                scale_m * 1.15,
                scale_m * 1.30,
            ),
            850.0,
            scale_m * 1.8,
            target,
        ),
    ]

    return camera, target, lights


def render_views(
    *,
    output_directory: Path,
    stem: str,
    tile_width_mm: float,
    resolution: int,
) -> dict[str, str]:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    camera, target, lights = create_render_rig(
        tile_width_mm
    )

    scale_m = tile_width_mm * MM_TO_METERS

    isometric_path = (
        output_directory
        / f"{stem}_isometric.png"
    )

    camera.location = (
        scale_m * 0.92,
        -scale_m * 1.18,
        scale_m * 1.02,
    )

    camera.data.ortho_scale = (
        scale_m * 1.48
    )

    configure_render(
        isometric_path,
        resolution,
    )

    bpy.ops.render.render(
        write_still=True
    )

    top_path = (
        output_directory
        / f"{stem}_top.png"
    )

    camera.location = (
        0.0,
        0.0,
        scale_m * 2.0,
    )

    camera.data.ortho_scale = (
        scale_m * 1.20
    )

    configure_render(
        top_path,
        resolution,
    )

    bpy.ops.render.render(
        write_still=True
    )

    for object_ in [
        camera,
        target,
        *lights,
    ]:
        bpy.data.objects.remove(
            object_,
            do_unlink=True,
        )

    return {
        "isometric": str(isometric_path),
        "top": str(top_path),
    }


def write_json(
    filepath: Path,
    payload: Any,
) -> None:
    filepath.write_text(
        json.dumps(
            payload,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_csv(
    filepath: Path,
    rows: list[dict[str, Any]],
) -> None:
    fieldnames = (
        "size",
        "primitive_id",
        "primitive_name",
        "base_width_mm",
        "base_depth_mm",
        "base_height_mm",
        "overall_width_mm",
        "overall_depth_mm",
        "overall_height_mm",
        "feature_width_parameter_mm",
        "feature_height_parameter_mm",
        "base_material",
        "feature_material",
        "finish",
        "functional_status",
    )

    with filepath.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    key: row.get(key, "")
                    for key in fieldnames
                }
            )


def rfq_text(
    quantity: int,
) -> str:
    return f"""Subject: Preliminary DFM and quotation request — Operational Worlds

Hello,

I am requesting a preliminary design-for-manufacturing review and
quotation for five sculptural prototype tiles from the Operational
Worlds project.

The package contains each design at two exact base footprints:

- 152.4 × 152.4 mm (nominal 6 × 6 inches)
- 304.8 × 304.8 mm (nominal 12 × 12 inches)

All STL numerical coordinates are in millimeters. Please do not
automatically rescale the files.

Please quote:

- Quantity {quantity} of each primitive and size
- Quantity 5 of each primitive and size
- Quantity 15 of each primitive and size

Please provide separate options for:

1. Economy FDM prototype in PLA
2. Durable FDM prototype in PETG or ASA
3. Exhibition-quality process and surface finish
4. Multi-part fabrication using the separate base and feature files

The complete STL represents the assembled geometry. The components
folder contains separate rectangular-base and operational-feature STLs
for multi-material or separately finished fabrication.

Please advise on:

- recommended process and material;
- wall thickness;
- hollowing, ribbing, and infill;
- base-flatness and warping risk;
- support strategy and orientation;
- mesh repairs or Boolean union;
- insert tolerances;
- finishing;
- setup and engineering charges;
- per-unit and total pricing;
- lead time;
- shipping;
- preferred production file format.

The Lens has no optical focal requirement. The Light Source and Sensor
do not currently include electronics. The Weight is symbolic unless
physical ballast is separately specified.

Thank you,

Daniel Ashley
Operational Worlds Research Program
"""


def specification_text(
    quantity: int,
) -> str:
    return f"""# Operational Worlds Canonical Prototype Specification

## Scope

Five canonical primitives:

- PRIM-0009 Lens
- PRIM-0010 Mirror
- PRIM-0011 Light Source
- PRIM-0012 Weight
- PRIM-0014 Sensor

Two base sizes:

- 152.4 × 152.4 mm
- 304.8 × 304.8 mm

Requested initial quantity: {quantity} per primitive and size.

## Units

All STL coordinates are numerical millimeters.

STL does not carry a reliable unit declaration. Import every STL as
millimeters and do not rescale without written approval.

## File interpretation

Each primitive contains:

- assembled/: rectangular substrate and feature together
- components/base/: invariant rectangular substrate only
- components/feature/: operational feature only
- renders/: isometric and top-view visual references

## Scale

The supplied 6-inch and 12-inch models are proportionally scaled from
the canonical 100 × 100 × 8 mm system.

The manufacturer is also asked to quote lighter alternatives.

### 6-inch

- proportional solid or infilled base
- 8–12 mm practical base with internal ribs or infill

### 12-inch

- proportional base
- 10–15 mm shell or base with internal reinforcement
- hollow or ribbed construction that maintains flatness

Any departure from the supplied outer dimensions should be proposed
before production.

## Appearance

Base substrate:

- matte off-white
- uniform across all five primitives
- flat rectangular lower surface
- crisp, consistent outer geometry

Special features:

- Lens: clear or translucent, smooth, glossy
- Mirror: reflective insert or reflective finish
- Light Source: frosted translucent diffuser
- Weight: brushed-metal appearance
- Sensor: polished piano-black dome

## Prototype processes to quote

- FDM PLA
- FDM PETG or ASA
- SLA, MJF, SLS, or vendor-recommended presentation process
- separately fabricated feature components where useful

## Minimum review requirements

Please check:

- manifold/watertight geometry
- overlapping closed shells
- internal surfaces
- inverted normals
- minimum wall thickness
- support requirements
- base warping
- feature attachment
- assembly clearance
- suitable finish
- suitability for the proposed process

## Production status

This is a preliminary prototype and DFM package, not a release for
unreviewed production.

A complete prototype set must be approved before larger production.
"""


def dfm_checklist() -> str:
    return """# DFM Response Checklist

Please respond for each primitive and size.

## Geometry

- [ ] File opens at the stated millimeter dimensions
- [ ] Geometry is manifold/watertight
- [ ] Intersecting shells are acceptable or repaired
- [ ] Minimum wall thickness is acceptable
- [ ] No unsupported floating components
- [ ] Recommended orientation identified
- [ ] Support-contact areas identified

## Substrate

- [ ] Base-flatness strategy provided
- [ ] Warping risk assessed
- [ ] Infill, shell, or rib strategy provided
- [ ] Expected finished weight supplied

## Materials and finish

- [ ] Base material quoted
- [ ] Feature material quoted
- [ ] Surface finish quoted
- [ ] Color consistency discussed
- [ ] Transparent or reflective finishing limitations disclosed

## Commercial quote

- [ ] Quantity 1 price
- [ ] Quantity 5 price
- [ ] Quantity 15 price
- [ ] Engineering or repair fee
- [ ] Finishing fee
- [ ] Assembly fee
- [ ] Lead time
- [ ] Shipping estimate
- [ ] Quote validity period
"""


def package_readme() -> str:
    return """# OWDE Canonical Quote Package

This ZIP is intended for preliminary DFM review and fabrication
quotation.

## Included primitives

- PRIM-0009 Lens
- PRIM-0010 Mirror
- PRIM-0011 Light Source
- PRIM-0012 Weight
- PRIM-0014 Sensor

## Included sizes

- 6 × 6 inches: 152.4 × 152.4 mm
- 12 × 12 inches: 304.8 × 304.8 mm

## Critical instruction

Import all STL files as millimeters.

## Folder structure

6in/
12in/
specifications/
source/
manifest.json
README.md

Each size folder includes:

assembled/
components/base/
components/feature/
renders/

The assembled STL is useful for general quoting. Separate component
STLs should be used when different materials or finishes are required.
"""


def create_zip(
    package_root: Path,
) -> Path:
    zip_path = package_root.with_suffix(
        ".zip"
    )

    if zip_path.exists():
        zip_path.unlink()

    with ZipFile(
        zip_path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for filepath in sorted(
            package_root.rglob("*")
        ):
            if filepath.is_file():
                archive.write(
                    filepath,
                    filepath.relative_to(
                        package_root.parent
                    ),
                )

    return zip_path


def save_source_blend(
    filepath: Path,
) -> None:
    filepath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    bpy.ops.wm.save_as_mainfile(
        filepath=str(filepath),
        copy=True,
    )


def build_package(
    arguments: argparse.Namespace,
) -> tuple[Path, Path]:
    package_root = resolve_output(
        arguments.output
    )

    if package_root.exists():
        if not arguments.overwrite:
            raise SystemExit(
                f"Output exists: {package_root}\n"
                "Use --overwrite to replace it."
            )

        shutil.rmtree(
            package_root
        )

    package_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    clean_scene()
    configure_world()

    dimension_rows: list[
        dict[str, Any]
    ] = []

    manifest_records: list[
        dict[str, Any]
    ] = []

    for size in SIZES:
        size_root = package_root / size.key

        assembled_directory = (
            size_root / "assembled"
        )

        base_directory = (
            size_root
            / "components"
            / "base"
        )

        feature_directory = (
            size_root
            / "components"
            / "feature"
        )

        render_directory = (
            size_root / "renders"
        )

        for directory in (
            assembled_directory,
            base_directory,
            feature_directory,
            render_directory,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        for primitive in PRIMITIVES:
            parameters = TileParameters(
                shape=primitive.shape,
                tile_width_mm=size.width_mm,
                tile_depth_mm=size.depth_mm,
                tile_height_mm=size.tile_height_mm,
                shape_width_mm=size.feature_width_mm,
                shape_height_mm=size.feature_height_mm,
                circle_segments=96,
            )

            base_mesh = build_base_tile_mesh(
                parameters
            )

            feature_mesh = build_feature_mesh(
                parameters
            )

            base_object = create_object(
                f"{primitive.filename}_{size.key}_Base",
                base_mesh,
            )

            feature_object = create_object(
                f"{primitive.filename}_{size.key}_Feature",
                feature_mesh,
            )

            assign_material(
                base_object,
                tile_material(),
            )

            assign_material(
                feature_object,
                feature_material(
                    primitive.shape
                ),
            )

            smooth_feature(
                feature_object,
                primitive.shape,
            )

            if primitive.shape is ShapeType.WEIGHT:
                modifier = feature_object.modifiers.new(
                    name="Quote Edge Chamfer",
                    type="BEVEL",
                )

                modifier.width = (
                    1.4
                    * size.scale_factor
                    * MM_TO_METERS
                )

                modifier.segments = 3
                modifier.limit_method = "ANGLE"

            stem = (
                f"{primitive.filename}_"
                f"{size.key}"
            )

            assembled_path = (
                assembled_directory
                / f"{stem}_assembled.stl"
            )

            base_path = (
                base_directory
                / f"{stem}_base.stl"
            )

            feature_path = (
                feature_directory
                / f"{stem}_feature.stl"
            )

            export_stl(
                assembled_path,
                (
                    base_object,
                    feature_object,
                ),
            )

            export_stl(
                base_path,
                (base_object,),
            )

            export_stl(
                feature_path,
                (feature_object,),
            )

            render_paths = render_views(
                output_directory=render_directory,
                stem=stem,
                tile_width_mm=size.width_mm,
                resolution=arguments.render_resolution,
            )

            base_bounds = bounds_mm(
                base_mesh
            )

            feature_bounds = bounds_mm(
                feature_mesh
            )

            overall_height = max(
                base_bounds["maximum_z_mm"],
                feature_bounds["maximum_z_mm"],
            )

            row = {
                "size": size.label,
                "primitive_id": primitive.primitive_id,
                "primitive_name": primitive.name,
                "base_width_mm": size.width_mm,
                "base_depth_mm": size.depth_mm,
                "base_height_mm": size.tile_height_mm,
                "overall_width_mm": size.width_mm,
                "overall_depth_mm": size.depth_mm,
                "overall_height_mm": overall_height,
                "feature_width_parameter_mm": (
                    size.feature_width_mm
                ),
                "feature_height_parameter_mm": (
                    size.feature_height_mm
                ),
                "base_material": primitive.base_material,
                "feature_material": primitive.feature_material,
                "finish": primitive.finish,
                "functional_status": primitive.functional_status,
            }

            dimension_rows.append(
                row
            )

            manifest_records.append(
                {
                    "size": asdict(size),
                    "primitive": {
                        **asdict(primitive),
                        "shape": primitive.shape.value,
                    },
                    "parameters": {
                        "tile_width_mm": size.width_mm,
                        "tile_depth_mm": size.depth_mm,
                        "tile_height_mm": size.tile_height_mm,
                        "feature_width_mm": size.feature_width_mm,
                        "feature_height_mm": size.feature_height_mm,
                        "circle_segments": 96,
                    },
                    "files": {
                        "assembled_stl": str(
                            assembled_path.relative_to(
                                package_root
                            )
                        ),
                        "base_stl": str(
                            base_path.relative_to(
                                package_root
                            )
                        ),
                        "feature_stl": str(
                            feature_path.relative_to(
                                package_root
                            )
                        ),
                        "isometric_render": str(
                            Path(
                                render_paths["isometric"]
                            ).relative_to(
                                package_root
                            )
                        ),
                        "top_render": str(
                            Path(
                                render_paths["top"]
                            ).relative_to(
                                package_root
                            )
                        ),
                    },
                    "bounds": {
                        "base": base_bounds,
                        "feature": feature_bounds,
                        "overall_height_mm": overall_height,
                    },
                }
            )

            bpy.data.objects.remove(
                base_object,
                do_unlink=True,
            )

            bpy.data.objects.remove(
                feature_object,
                do_unlink=True,
            )

            print(
                f"Exported {primitive.primitive_id} "
                f"{primitive.name} at {size.label}"
            )

    specifications = (
        package_root
        / "specifications"
    )

    specifications.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        package_root / "README.md"
    ).write_text(
        package_readme(),
        encoding="utf-8",
    )

    (
        specifications
        / "RFQ_EMAIL.txt"
    ).write_text(
        rfq_text(
            arguments.quantity
        ),
        encoding="utf-8",
    )

    (
        specifications
        / "MANUFACTURING_SPECIFICATION.md"
    ).write_text(
        specification_text(
            arguments.quantity
        ),
        encoding="utf-8",
    )

    (
        specifications
        / "DFM_RESPONSE_CHECKLIST.md"
    ).write_text(
        dfm_checklist(),
        encoding="utf-8",
    )

    write_csv(
        specifications
        / "DIMENSION_AND_MATERIAL_SCHEDULE.csv",
        dimension_rows,
    )

    write_json(
        specifications
        / "DIMENSION_AND_MATERIAL_SCHEDULE.json",
        dimension_rows,
    )

    write_json(
        package_root
        / "manifest.json",
        {
            "package_name": (
                "OWDE Canonical Quote Package"
            ),
            "package_version": PACKAGE_VERSION,
            "generated_at_utc": datetime.now(
                UTC
            ).isoformat(),
            "units": "millimeters",
            "stl_unit_warning": (
                "Import all STL files as millimeters."
            ),
            "requested_initial_quantity": (
                arguments.quantity
            ),
            "primitive_count": len(PRIMITIVES),
            "size_count": len(SIZES),
            "records": manifest_records,
        },
    )

    save_source_blend(
        package_root
        / "source"
        / "OWDE_Canonical_Quote_Source.blend"
    )

    zip_path = create_zip(
        package_root
    )

    return package_root, zip_path


def main() -> None:
    arguments = parse_arguments()

    if arguments.quantity < 1:
        raise SystemExit(
            "--quantity must be at least 1."
        )

    package_root, zip_path = build_package(
        arguments
    )

    print()
    print(
        "OWDE canonical quote package complete."
    )
    print(
        f"Folder: {package_root}"
    )
    print(
        f"ZIP:    {zip_path}"
    )
    print()
    print(
        "Send the ZIP as a preliminary DFM "
        "and quotation package."
    )


if __name__ == "__main__":
    main()
