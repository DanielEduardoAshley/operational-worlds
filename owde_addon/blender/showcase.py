from __future__ import annotations

from pathlib import Path
import math

import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
)

from ..core.builders import build_tile_mesh
from ..core.models import ShapeType, TileParameters
from .materials import assign_shape_material


MM_TO_METERS = 0.001


SHOWCASE_SHAPES = (
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.SQUARE,
    ShapeType.HEXAGON,
    ShapeType.SLOT,
    ShapeType.HINGE,
    ShapeType.FOLD,
    ShapeType.APERTURE,
    ShapeType.LENS,
    ShapeType.MIRROR,
    ShapeType.LIGHT_SOURCE,
    ShapeType.WEIGHT,
    ShapeType.THRESHOLD,
    ShapeType.SENSOR,
    ShapeType.HANDLE,
)


def mesh_object_from_data(
    name: str,
    mesh_data,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(
        f"{name}_Mesh"
    )

    vertices = [
        (
            vertex[0] * MM_TO_METERS,
            vertex[1] * MM_TO_METERS,
            vertex[2] * MM_TO_METERS,
        )
        for vertex in mesh_data.vertices
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


def clear_showcase() -> None:
    collection = bpy.data.collections.get(
        "OWDE Showcase"
    )

    if collection is None:
        return

    for object_ in list(collection.objects):
        bpy.data.objects.remove(
            object_,
            do_unlink=True,
        )

    bpy.data.collections.remove(
        collection
    )


def move_to_collection(
    object_: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for current in list(object_.users_collection):
        current.objects.unlink(object_)

    collection.objects.link(object_)


def add_area_light(
    *,
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
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

    direction = (
        math.atan2(location[1], location[0]),
        0.0,
        math.atan2(
            math.sqrt(
                location[0] ** 2
                + location[1] ** 2
            ),
            location[2],
        ),
    )

    object_.rotation_euler = (
        direction[2],
        0.0,
        direction[0] + math.pi / 2.0,
    )

    return object_


def create_showcase_camera(
    gallery_width: float,
    gallery_depth: float,
) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(
        "OWDE Showcase Camera"
    )

    camera = bpy.data.objects.new(
        "OWDE Showcase Camera",
        camera_data,
    )

    bpy.context.scene.collection.objects.link(
        camera
    )

    camera.location = (
        gallery_width * 0.68,
        -gallery_depth * 1.08,
        gallery_depth * 1.12,
    )

    target = bpy.data.objects.new(
        "OWDE Showcase Camera Target",
        None,
    )

    bpy.context.scene.collection.objects.link(
        target
    )

    constraint = camera.constraints.new(
        type="TRACK_TO"
    )
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(
        gallery_width,
        gallery_depth,
    ) * 1.18

    return camera


def configure_world() -> None:
    world = bpy.context.scene.world

    if world is None:
        world = bpy.data.worlds.new(
            "OWDE Showcase World"
        )
        bpy.context.scene.world = world

    world.use_nodes = True

    background = world.node_tree.nodes.get(
        "Background"
    )

    if background is not None:
        background.inputs["Color"].default_value = (
            0.012,
            0.014,
            0.018,
            1.0,
        )
        background.inputs["Strength"].default_value = 0.32


def configure_render(
    *,
    resolution: int,
    output_path: Path,
) -> None:
    scene = bpy.context.scene

    scene.render.engine = "BLENDER_EEVEE_NEXT"

    scene.render.resolution_x = resolution
    scene.render.resolution_y = int(
        resolution * 0.68
    )
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    scene.render.film_transparent = False

    scene.render.filepath = str(
        output_path
    )


class OWDE_OT_create_showcase(
    bpy.types.Operator
):
    bl_idname = "owde.create_showcase"
    bl_label = "Create Operational Worlds Showcase"
    bl_description = (
        "Create all fifteen primitives, apply canonical materials, "
        "build studio lighting, and optionally render a contact sheet"
    )
    bl_options = {
        "REGISTER",
        "UNDO",
    }

    render_image: BoolProperty(
        name="Render Contact Sheet",
        default=True,
    )

    image_resolution: IntProperty(
        name="Image Width",
        default=4096,
        min=1024,
        max=8192,
    )

    output_directory: StringProperty(
        name="Output Directory",
        subtype="DIR_PATH",
        default="//exports/showcase/",
    )

    def execute(self, context):
        clear_showcase()

        collection = bpy.data.collections.new(
            "OWDE Showcase"
        )

        context.scene.collection.children.link(
            collection
        )

        tile_width_mm = 100.0
        tile_depth_mm = 100.0
        spacing_mm = 126.0

        column_count = 5
        row_count = 3

        created_objects: list[
            bpy.types.Object
        ] = []

        for index, shape in enumerate(
            SHOWCASE_SHAPES
        ):
            parameters = TileParameters(
                shape=shape,
                tile_width_mm=tile_width_mm,
                tile_depth_mm=tile_depth_mm,
                tile_height_mm=8.0,
                shape_width_mm=55.0,
                shape_height_mm=5.0,
                circle_segments=64,
            )

            mesh_data = build_tile_mesh(
                parameters
            )

            object_ = mesh_object_from_data(
                f"PRIM-{index + 1:04d}_{shape.value}",
                mesh_data,
            )

            row = index // column_count
            column = index % column_count

            x_mm = (
                column
                - (column_count - 1) / 2.0
            ) * spacing_mm

            y_mm = (
                (row_count - 1) / 2.0
                - row
            ) * spacing_mm

            object_.location = (
                x_mm * MM_TO_METERS,
                y_mm * MM_TO_METERS,
                0.0,
            )

            object_["owde_primitive_id"] = (
                f"PRIM-{index + 1:04d}"
            )
            object_["owde_shape"] = shape.value
            object_["owde_showcase"] = True

            assign_shape_material(
                object_,
                shape,
            )

            if shape is ShapeType.WEIGHT:
                bevel = object_.modifiers.new(
                    name="OWDE Weight Edge Chamfer",
                    type="BEVEL",
                )
                bevel.width = 1.4 * MM_TO_METERS
                bevel.segments = 3
                bevel.limit_method = "ANGLE"

            for polygon in object_.data.polygons:
                polygon.use_smooth = shape in {
                    ShapeType.LENS,
                    ShapeType.LIGHT_SOURCE,
                    ShapeType.SENSOR,
                    ShapeType.MIRROR,
                }

            move_to_collection(
                object_,
                collection,
            )

            created_objects.append(
                object_
            )

        gallery_width = (
            (
                column_count - 1
            )
            * spacing_mm
            + tile_width_mm
        ) * MM_TO_METERS

        gallery_depth = (
            (
                row_count - 1
            )
            * spacing_mm
            + tile_depth_mm
        ) * MM_TO_METERS

        configure_world()

        key = add_area_light(
            name="OWDE Key Light",
            location=(
                -gallery_width * 0.54,
                -gallery_depth * 0.46,
                gallery_depth * 0.98,
            ),
            energy=1350.0,
            size=2.8,
        )

        fill = add_area_light(
            name="OWDE Fill Light",
            location=(
                gallery_width * 0.68,
                -gallery_depth * 0.10,
                gallery_depth * 0.62,
            ),
            energy=780.0,
            size=3.2,
        )

        rim = add_area_light(
            name="OWDE Rim Light",
            location=(
                0.0,
                gallery_depth * 0.72,
                gallery_depth * 0.88,
            ),
            energy=1080.0,
            size=2.4,
        )

        for light in (
            key,
            fill,
            rim,
        ):
            move_to_collection(
                light,
                collection,
            )

        camera = create_showcase_camera(
            gallery_width,
            gallery_depth,
        )

        target = bpy.data.objects.get(
            "OWDE Showcase Camera Target"
        )

        move_to_collection(
            camera,
            collection,
        )

        if target is not None:
            move_to_collection(
                target,
                collection,
            )

        context.scene.camera = camera

        output_directory = Path(
            bpy.path.abspath(
                self.output_directory
            )
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_directory
            / "OWDE_Primitive_Showcase.png"
        )

        configure_render(
            resolution=self.image_resolution,
            output_path=output_path,
        )

        if self.render_image:
            bpy.ops.render.render(
                write_still=True
            )

        self.report(
            {"INFO"},
            (
                "Created OWDE showcase with 15 primitives"
                + (
                    f" and rendered {output_path}"
                    if self.render_image
                    else ""
                )
            ),
        )

        return {"FINISHED"}
