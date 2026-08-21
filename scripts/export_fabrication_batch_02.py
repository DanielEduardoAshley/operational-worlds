"""OWDE Fabrication Batch 02 exporter.

Creates one unified STL per physical primitive and refuses to create
the printer ZIP unless every exported file passes post-export checks.

Batch:
    OW01 Circle
    OW02 Triangle
    OW04 Hexagon
    OW06 Hinge
    OW07 Fold
    OW08 Aperture
    OW13 Threshold
    OW15 Handle
"""

from __future__ import annotations

import argparse
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import bmesh
import bpy


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from owde_addon.core.builders import (
    build_base_tile_mesh,
    build_feature_mesh,
)
from owde_addon.core.models import (
    ShapeType,
    TileParameters,
)
from owde_addon.core.mesh import MeshData


MM_TO_METERS = 0.001
DEFAULT_FABRICATION_OVERLAP_MM = 0.50
FOOTPRINT_TOLERANCE_MM = 0.15
CLEANUP_MERGE_DISTANCE_MM = 0.001
DEGENERATE_FACE_AREA_EPSILON = 1.0e-12


@dataclass(frozen=True)
class Primitive:
    number: int
    shape: ShapeType
    label: str


PRIMITIVES = (
    Primitive(1, ShapeType.CIRCLE, "Circle"),
    Primitive(2, ShapeType.TRIANGLE, "Triangle"),
    Primitive(4, ShapeType.HEXAGON, "Hexagon"),
    Primitive(6, ShapeType.HINGE, "Hinge"),
    Primitive(7, ShapeType.FOLD, "Fold"),
    Primitive(8, ShapeType.APERTURE, "Aperture"),
    Primitive(13, ShapeType.THRESHOLD, "Threshold"),
    Primitive(15, ShapeType.HANDLE, "Handle"),
)


def parse_args() -> argparse.Namespace:
    values = []

    if "--" in sys.argv:
        values = sys.argv[
            sys.argv.index("--") + 1:
        ]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--size",
        choices=("6", "12"),
        default="6",
    )

    parser.add_argument(
        "--output",
        default="exports/fabrication_batch_02",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
    )

    parser.add_argument(
        "--base-height-mm",
        type=float,
        default=None,
        help=(
            "Override tile/base thickness. "
            "For the current proportional 6in standard use 12.192."
        ),
    )

    parser.add_argument(
        "--union-overlap-mm",
        type=float,
        default=DEFAULT_FABRICATION_OVERLAP_MM,
    )

    return parser.parse_args(values)


def dimensions_for_size(
    size: str,
    base_height_override: float | None,
) -> tuple[
    float,
    float,
    float,
    float,
    float,
]:
    if size == "6":
        scale = 1.524
        width = 152.4
    else:
        scale = 3.048
        width = 304.8

    default_height = (
        8.0 * scale
    )

    tile_height = (
        base_height_override
        if base_height_override is not None
        else default_height
    )

    if tile_height <= 0:
        raise ValueError(
            "Base height must be greater than zero."
        )

    return (
        width,
        width,
        tile_height,
        55.0 * scale,
        5.0 * scale,
    )


def delete_everything() -> None:
    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete(
        use_global=False
    )


def create_object(
    name: str,
    mesh_data: MeshData,
) -> bpy.types.Object:
    mesh_data.validate()

    mesh = bpy.data.meshes.new(
        f"{name}_Mesh"
    )

    mesh.from_pydata(
        [
            (
                x * MM_TO_METERS,
                y * MM_TO_METERS,
                z * MM_TO_METERS,
            )
            for x, y, z in mesh_data.vertices
        ],
        [],
        list(mesh_data.faces),
    )

    mesh.update(
        calc_edges=True
    )

    object_ = bpy.data.objects.new(
        name,
        mesh,
    )

    bpy.context.scene.collection.objects.link(
        object_
    )

    return object_


def split_mesh_components(
    mesh_data: MeshData,
) -> list[MeshData]:
    vertex_to_faces: dict[int, list[int]] = {}

    for face_index, face in enumerate(
        mesh_data.faces
    ):
        for vertex_index in face:
            vertex_to_faces.setdefault(
                vertex_index,
                [],
            ).append(
                face_index
            )

    remaining = set(
        range(
            len(
                mesh_data.faces
            )
        )
    )
    components: list[MeshData] = []

    while remaining:
        seed = remaining.pop()
        stack = [seed]
        face_indexes = {seed}

        while stack:
            face_index = stack.pop()

            for vertex_index in mesh_data.faces[
                face_index
            ]:
                for neighbor in vertex_to_faces[
                    vertex_index
                ]:
                    if neighbor in remaining:
                        remaining.remove(
                            neighbor
                        )
                        face_indexes.add(
                            neighbor
                        )
                        stack.append(
                            neighbor
                        )

        old_to_new: dict[int, int] = {}
        vertices: list[tuple[float, float, float]] = []
        faces: list[tuple[int, ...]] = []

        for face_index in sorted(
            face_indexes
        ):
            new_face: list[int] = []

            for old_index in mesh_data.faces[
                face_index
            ]:
                if old_index not in old_to_new:
                    old_to_new[old_index] = len(
                        vertices
                    )
                    vertices.append(
                        mesh_data.vertices[
                            old_index
                        ]
                    )

                new_face.append(
                    old_to_new[old_index]
                )

            faces.append(
                tuple(
                    new_face
                )
            )

        components.append(
            MeshData(
                vertices=tuple(
                    vertices
                ),
                faces=tuple(
                    faces
                ),
            )
        )

    return components


def select_only(
    object_: bpy.types.Object,
) -> None:
    bpy.ops.object.select_all(
        action="DESELECT"
    )

    object_.hide_set(False)
    object_.hide_render = False
    object_.select_set(True)

    bpy.context.view_layer.objects.active = object_


def apply_boolean(
    target: bpy.types.Object,
    operand: bpy.types.Object,
    operation: str,
) -> None:
    modifier = target.modifiers.new(
        name=f"OWDE_{operation}",
        type="BOOLEAN",
    )

    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = operand

    select_only(target)

    result = bpy.ops.object.modifier_apply(
        modifier=modifier.name
    )

    if "FINISHED" not in result:
        raise RuntimeError(
            f"Boolean {operation} failed."
        )

    bpy.data.objects.remove(
        operand,
        do_unlink=True,
    )


def cleanup_fabrication_mesh(
    object_: bpy.types.Object,
) -> None:
    """Clean Boolean residue before validation and STL export."""

    mesh = object_.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    bmesh.ops.remove_doubles(
        bm,
        verts=list(
            bm.verts
        ),
        dist=(
            CLEANUP_MERGE_DISTANCE_MM
            * MM_TO_METERS
        ),
    )

    bm.edges.ensure_lookup_table()

    bmesh.ops.dissolve_degenerate(
        bm,
        edges=list(
            bm.edges
        ),
        dist=(
            CLEANUP_MERGE_DISTANCE_MM
            * MM_TO_METERS
        ),
    )

    bm.faces.ensure_lookup_table()

    bmesh.ops.triangulate(
        bm,
        faces=list(
            bm.faces
        ),
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )

    degenerate_faces = [
        face
        for face in bm.faces
        if face.calc_area() <= DEGENERATE_FACE_AREA_EPSILON
    ]

    if degenerate_faces:
        bmesh.ops.delete(
            bm,
            geom=degenerate_faces,
            context="FACES",
        )

    bm.edges.ensure_lookup_table()

    loose_edges = [
        edge
        for edge in bm.edges
        if not edge.link_faces
    ]

    if loose_edges:
        bmesh.ops.delete(
            bm,
            geom=loose_edges,
            context="EDGES",
        )

    bm.verts.ensure_lookup_table()

    loose_vertices = [
        vertex
        for vertex in bm.verts
        if not vertex.link_edges
    ]

    if loose_vertices:
        bmesh.ops.delete(
            bm,
            geom=loose_vertices,
            context="VERTS",
        )

    bm.faces.ensure_lookup_table()

    if bm.faces:
        bmesh.ops.recalc_face_normals(
            bm,
            faces=list(
                bm.faces
            ),
        )

    bm.to_mesh(mesh)
    bm.free()

    mesh.update(
        calc_edges=True
    )


def create_aperture_cutter(
    parameters: TileParameters,
) -> bpy.types.Object:
    radius_mm = (
        parameters.shape_width_mm
        * 0.40
    )

    cutter_height_mm = (
        parameters.tile_height_mm
        + parameters.shape_height_mm
        + 8.0
    )

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=max(
            128,
            parameters.circle_segments,
        ),
        radius=(
            radius_mm
            * MM_TO_METERS
        ),
        depth=(
            cutter_height_mm
            * MM_TO_METERS
        ),
        location=(
            0.0,
            0.0,
            (
                parameters.tile_height_mm
                / 2.0
            )
            * MM_TO_METERS,
        ),
    )

    cutter = bpy.context.active_object
    cutter.name = "OWDE_Aperture_Cutter"

    return cutter


def make_unified_object(
    primitive: Primitive,
    parameters: TileParameters,
    overlap_mm: float,
) -> bpy.types.Object:
    base = create_object(
        "OWDE_Base",
        build_base_tile_mesh(
            parameters
        ),
    )

    if primitive.shape is ShapeType.APERTURE:
        cutter = create_aperture_cutter(
            parameters
        )

        apply_boolean(
            base,
            cutter,
            "DIFFERENCE",
        )

    feature_mesh = build_feature_mesh(
        parameters
    )

    for index, component in enumerate(
        split_mesh_components(
            feature_mesh
        ),
        start=1,
    ):
        feature = create_object(
            f"OWDE_Feature_{index:02d}",
            component,
        )

        # Hinge and Fold already intentionally penetrate the substrate.
        # The other raised features get a small fabrication-only overlap.
        if primitive.shape not in {
            ShapeType.HINGE,
            ShapeType.FOLD,
            ShapeType.APERTURE,
        }:
            feature.location.z -= (
                overlap_mm
                * MM_TO_METERS
            )

        apply_boolean(
            base,
            feature,
            "UNION",
        )

    cleanup_fabrication_mesh(
        base
    )

    base.name = (
        f"OWDE_PRIM-{primitive.number:04d}_"
        f"{primitive.label}_Unified"
    )

    select_only(base)

    bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=True,
    )

    return base


def mesh_validation(
    object_: bpy.types.Object,
) -> dict[str, object]:
    mesh = object_.data
    mesh.update(
        calc_edges=True
    )

    vertex_count = len(
        mesh.vertices
    )

    face_count = len(
        mesh.polygons
    )

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    non_manifold_edges = [
        edge
        for edge in bm.edges
        if not edge.is_manifold
    ]

    degenerate_faces = [
        face
        for face in bm.faces
        if face.calc_area() <= DEGENERATE_FACE_AREA_EPSILON
    ]

    remaining = set(
        bm.verts
    )

    component_count = 0

    while remaining:
        component_count += 1

        seed = remaining.pop()
        stack = [seed]

        while stack:
            vertex = stack.pop()

            for edge in vertex.link_edges:
                other = edge.other_vert(
                    vertex
                )

                if other in remaining:
                    remaining.remove(
                        other
                    )
                    stack.append(
                        other
                    )

    bm.free()

    if vertex_count:
        xs = [
            vertex.co.x / MM_TO_METERS
            for vertex in mesh.vertices
        ]

        ys = [
            vertex.co.y / MM_TO_METERS
            for vertex in mesh.vertices
        ]

        zs = [
            vertex.co.z / MM_TO_METERS
            for vertex in mesh.vertices
        ]

        width_mm = (
            max(xs) - min(xs)
        )

        depth_mm = (
            max(ys) - min(ys)
        )

        height_mm = (
            max(zs) - min(zs)
        )

    else:
        width_mm = 0.0
        depth_mm = 0.0
        height_mm = 0.0

    return {
        "vertex_count": vertex_count,
        "face_count": face_count,
        "non_manifold_edges": len(
            non_manifold_edges
        ),
        "degenerate_face_count": len(
            degenerate_faces
        ),
        "component_count": component_count,
        "width_mm": width_mm,
        "depth_mm": depth_mm,
        "height_mm": height_mm,
    }


def validate_manifold(
    object_: bpy.types.Object,
) -> tuple[
    bool,
    int,
]:
    data = mesh_validation(
        object_
    )

    bad_edges = int(
        data["non_manifold_edges"]
    )
    is_manifold = bad_edges == 0

    return (
        is_manifold,
        bad_edges,
    )


def validate_object(
    object_: bpy.types.Object,
    expected_width_mm: float,
    expected_depth_mm: float,
) -> tuple[
    bool,
    list[str],
    dict[str, object],
]:
    data = mesh_validation(
        object_
    )

    problems: list[str] = []

    if data["vertex_count"] == 0:
        problems.append(
            "mesh has zero vertices"
        )

    if data["face_count"] == 0:
        problems.append(
            "mesh has zero faces"
        )

    if data["non_manifold_edges"] != 0:
        problems.append(
            (
                f"{data['non_manifold_edges']} "
                "non-manifold edges"
            )
        )

    if data["degenerate_face_count"] != 0:
        problems.append(
            (
                f"{data['degenerate_face_count']} "
                "degenerate faces"
            )
        )

    if data["component_count"] != 1:
        problems.append(
            (
                f"{data['component_count']} "
                "connected components"
            )
        )

    if not math.isclose(
        float(data["width_mm"]),
        expected_width_mm,
        abs_tol=FOOTPRINT_TOLERANCE_MM,
    ):
        problems.append(
            (
                "width "
                f"{data['width_mm']:.3f} mm "
                f"!= {expected_width_mm:.3f} mm"
            )
        )

    if not math.isclose(
        float(data["depth_mm"]),
        expected_depth_mm,
        abs_tol=FOOTPRINT_TOLERANCE_MM,
    ):
        problems.append(
            (
                "depth "
                f"{data['depth_mm']:.3f} mm "
                f"!= {expected_depth_mm:.3f} mm"
            )
        )

    return (
        not problems,
        problems,
        data,
    )


def export_stl(
    object_: bpy.types.Object,
    filepath: Path,
) -> None:
    filepath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    select_only(object_)

    if hasattr(
        bpy.ops.wm,
        "stl_export",
    ):
        operator = bpy.ops.wm.stl_export

        supported = {
            item.identifier
            for item
            in operator.get_rna_type().properties
        }

        kwargs = {
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
                kwargs[key] = value

        result = operator(
            **kwargs
        )

    elif hasattr(
        bpy.ops.export_mesh,
        "stl",
    ):
        result = bpy.ops.export_mesh.stl(
            filepath=str(filepath),
            use_selection=True,
            global_scale=1000.0,
            use_scene_unit=False,
            ascii=False,
        )

    else:
        raise RuntimeError(
            "No STL exporter is available."
        )

    if "FINISHED" not in result:
        raise RuntimeError(
            f"Failed to export {filepath}"
        )


def import_stl(
    filepath: Path,
) -> bpy.types.Object:
    before = set(
        bpy.data.objects
    )

    if hasattr(
        bpy.ops.wm,
        "stl_import",
    ):
        result = bpy.ops.wm.stl_import(
            filepath=str(filepath)
        )

    elif hasattr(
        bpy.ops.import_mesh,
        "stl",
    ):
        result = bpy.ops.import_mesh.stl(
            filepath=str(filepath)
        )

    else:
        raise RuntimeError(
            "No STL importer is available."
        )

    if "FINISHED" not in result:
        raise RuntimeError(
            f"Failed to re-import {filepath}"
        )

    after = set(
        bpy.data.objects
    )

    created = list(
        after - before
    )

    mesh_objects = [
        object_
        for object_ in created
        if object_.type == "MESH"
    ]

    if len(mesh_objects) != 1:
        raise RuntimeError(
            (
                f"Expected one imported mesh from {filepath.name}, "
                f"received {len(mesh_objects)}"
            )
        )

    return mesh_objects[0]


def validate_exported_stl(
    filepath: Path,
    expected_width_mm: float,
    expected_depth_mm: float,
) -> tuple[
    bool,
    list[str],
    dict[str, object],
]:
    imported = import_stl(
        filepath
    )

    # Modern Blender imports STL numerical coordinates into scene units.
    # Our exporter writes millimeter coordinates; normalize to meters
    # if the imported object is obviously 1000× oversized.
    dimensions = imported.dimensions

    if(
        dimensions.x > 10.0
        or dimensions.y > 10.0
    ):
        imported.scale = (
            MM_TO_METERS,
            MM_TO_METERS,
            MM_TO_METERS,
        )

        select_only(imported)

        bpy.ops.object.transform_apply(
            location=False,
            rotation=False,
            scale=True,
        )

    result = validate_object(
        imported,
        expected_width_mm,
        expected_depth_mm,
    )

    bpy.data.objects.remove(
        imported,
        do_unlink=True,
    )

    return result


def create_zip(
    package_directory: Path,
) -> Path:
    zip_path = (
        package_directory.parent
        / f"{package_directory.name}.zip"
    )

    if zip_path.exists():
        zip_path.unlink()

    with ZipFile(
        zip_path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for filepath in sorted(
            package_directory.rglob("*")
        ):
            if filepath.is_file():
                archive.write(
                    filepath,
                    filepath.relative_to(
                        package_directory.parent
                    ),
                )

    return zip_path


def main() -> None:
    arguments = parse_args()

    (
        tile_width_mm,
        tile_depth_mm,
        tile_height_mm,
        shape_width_mm,
        shape_height_mm,
    ) = dimensions_for_size(
        arguments.size,
        arguments.base_height_mm,
    )

    size_name = (
        "6in"
        if arguments.size == "6"
        else "12in"
    )

    output_root = Path(
        arguments.output
    )

    if not output_root.is_absolute():
        output_root = (
            ROOT / output_root
        )

    package_directory = (
        output_root
        / f"OWDE_Fabrication_Batch_02_{size_name}"
    )

    if package_directory.exists():
        if not arguments.overwrite:
            raise SystemExit(
                f"{package_directory} already exists. "
                "Use --overwrite."
            )

        shutil.rmtree(
            package_directory
        )

    stl_directory = (
        package_directory
        / "stl"
    )

    stl_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    delete_everything()

    report: list[str] = [
        "OWDE FABRICATION BATCH 02",
        "",
        f"Footprint: {tile_width_mm:.3f} × {tile_depth_mm:.3f} mm",
        f"Base thickness: {tile_height_mm:.3f} mm",
        "Material: white PLA",
        "",
        "VALIDATION POLICY",
        "- non-empty mesh",
        "- zero non-manifold edges",
        "- zero degenerate faces",
        "- exactly one connected component",
        "- expected rectangular footprint",
        "- STL re-import validation",
        "",
    ]

    failures: list[str] = []

    for primitive in PRIMITIVES:
        parameters = TileParameters(
            shape=primitive.shape,
            tile_width_mm=tile_width_mm,
            tile_depth_mm=tile_depth_mm,
            tile_height_mm=tile_height_mm,
            shape_width_mm=shape_width_mm,
            shape_height_mm=shape_height_mm,
            circle_segments=96,
        )

        unified = make_unified_object(
            primitive,
            parameters,
            arguments.union_overlap_mm,
        )

        object_ok, object_problems, object_data = (
            validate_object(
                unified,
                tile_width_mm,
                tile_depth_mm,
            )
        )

        filename = (
            f"PRIM-{primitive.number:04d}_"
            f"{primitive.label}_"
            f"{size_name}_unified.stl"
        )

        filepath = (
            stl_directory
            / filename
        )

        if not object_ok:
            message = (
                f"{filename}: PRE-EXPORT FAILED: "
                + "; ".join(
                    object_problems
                )
            )

            print(message)
            report.append(message)
            failures.append(message)

            bpy.data.objects.remove(
                unified,
                do_unlink=True,
            )

            continue

        export_stl(
            unified,
            filepath,
        )

        bpy.data.objects.remove(
            unified,
            do_unlink=True,
        )

        (
            export_ok,
            export_problems,
            export_data,
        ) = validate_exported_stl(
            filepath,
            tile_width_mm,
            tile_depth_mm,
        )

        if export_ok:
            message = (
                f"{filename}: PASS | "
                f"{export_data['vertex_count']} verts | "
                f"{export_data['face_count']} faces | "
                f"1 component | "
                f"{export_data['degenerate_face_count']} degenerate faces | "
                f"{export_data['width_mm']:.3f} × "
                f"{export_data['depth_mm']:.3f} × "
                f"{export_data['height_mm']:.3f} mm"
            )

        else:
            message = (
                f"{filename}: POST-EXPORT FAILED: "
                + "; ".join(
                    export_problems
                )
            )

            failures.append(
                message
            )

        print(
            message
        )

        report.append(
            message
        )

    report_path = (
        package_directory
        / "VALIDATION_REPORT.txt"
    )

    report_path.write_text(
        "\n".join(report)
        + "\n",
        encoding="utf-8",
    )

    if failures:
        print()
        print("=" * 72)
        print("FABRICATION PACKAGE FAILED VALIDATION")
        print("=" * 72)

        for failure in failures:
            print(
                failure
            )

        print()
        print(
            "No printer ZIP was created."
        )

        print(
            f"Validation report: {report_path}"
        )

        raise SystemExit(1)

    readme_path = (
        package_directory
        / "README_FOR_PRINTER.txt"
    )

    readme_path.write_text(
        (
            "Operational Worlds — Fabrication Batch 02\n\n"
            f"Footprint: {tile_width_mm:.3f} × "
            f"{tile_depth_mm:.3f} mm\n"
            f"Base thickness: {tile_height_mm:.3f} mm\n"
            "Material requested: white PLA\n\n"
            "Each STL is one unified, validated physical object.\n"
            "OW08 Aperture contains a true through-opening.\n"
            "All STL coordinates are millimeters.\n"
            "Please do not rescale the files.\n"
        ),
        encoding="utf-8",
    )

    zip_path = create_zip(
        package_directory
    )

    print()
    print("=" * 72)
    print("ALL FABRICATION FILES PASSED")
    print("=" * 72)
    print()
    print(f"Package: {package_directory}")
    print(f"ZIP:     {zip_path}")
    print()
    print(
        "This ZIP passed the OWDE fabrication validation gate."
    )


if __name__ == "__main__":
    main()
