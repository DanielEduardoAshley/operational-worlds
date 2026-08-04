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
from .materials import (
    assign_canonical_materials,
    get_or_create_dark_insert_material,
)


MM_TO_METERS = 0.001
SHOWCASE_COLLECTION_NAME = "OWDE Showcase"
SHOWCASE_RELEASE = "0.5.0-alpha.2"


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


PRIMITIVE_NAMES = {
    ShapeType.CIRCLE: "Raised_Circle",
    ShapeType.TRIANGLE: "Raised_Triangle",
    ShapeType.SQUARE: "Raised_Square",
    ShapeType.HEXAGON: "Raised_Hexagon",
    ShapeType.SLOT: "Slot",
    ShapeType.HINGE: "Hinge",
    ShapeType.FOLD: "Fold",
    ShapeType.APERTURE: "Aperture",
    ShapeType.LENS: "Lens",
    ShapeType.MIRROR: "Mirror",
    ShapeType.LIGHT_SOURCE: "Light_Source",
    ShapeType.WEIGHT: "Weight",
    ShapeType.THRESHOLD: "Threshold",
    ShapeType.SENSOR: "Sensor",
    ShapeType.HANDLE: "Handle",
}


def primitive_identifier(
    index: int,
) -> str:
    return f"PRIM-{index + 1:04d}"


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
        SHOWCASE_COLLECTION_NAME
    )

    if collection is None:
        return

    for object_ in list(collection.all_objects):
        bpy.data.objects.remove(
            object_,
            do_unlink=True,
        )

    bpy.data.collections.remove(collection)


def move_to_collection(
    object_: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for current in list(object_.users_collection):
        current.objects.unlink(object_)

    collection.objects.link(object_)


def point_object_at(
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
    *,
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: bpy.types.Object,
    collection: bpy.types.Collection,
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

    point_object_at(
        object_,
        target,
    )

    move_to_collection(
        object_,
        collection,
    )

    return object_


def create_showcase_camera(
    *,
    gallery_width: float,
    gallery_depth: float,
    target: bpy.types.Object,
    collection: bpy.types.Collection,
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

    point_object_at(
        camera,
        target,
    )

    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(
        gallery_width,
        gallery_depth,
    ) * 1.17

    move_to_collection(
        camera,
        collection,
    )

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
            0.006,
            0.007,
            0.009,
            1.0,
        )
        background.inputs["Strength"].default_value = 0.22


def configure_render(
    *,
    width: int,
    height: int,
    output_path: Path,
) -> None:
    scene = bpy.context.scene

    scene.render.engine = "BLENDER_EEVEE_NEXT"

    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"

    scene.render.film_transparent = False
    scene.render.filepath = str(output_path)

    scene.view_settings.look = "AgX - Medium High Contrast"


def resolve_output_directory(
    requested_value: str,
) -> Path:
    """Resolve a user-writable output directory without bpy.path.abspath.

    `bpy.path.abspath()` treats Blender's `//` prefix specially and can
    resolve unsaved-file paths inside Blender.app on macOS. This function
    deliberately uses Path.home() instead.
    """

    requested = requested_value.strip()

    if requested:
        requested = requested.replace(
            "$HOME",
            str(Path.home()),
        )

        if requested.startswith("~/"):
            candidate = (
                Path.home()
                / requested[2:]
            )
        elif requested == "~":
            candidate = Path.home()
        elif requested.startswith("//"):
            # A Blender-relative path is unsafe when the .blend is unsaved.
            candidate = (
                Path.home()
                / "Documents"
                / "OperationalWorlds"
                / requested[2:]
            )
        else:
            candidate = Path(requested).expanduser()

            if not candidate.is_absolute():
                candidate = Path.home() / candidate
    else:
        candidate = (
            Path.home()
            / "Documents"
            / "OperationalWorlds"
            / "exports"
            / "showcase"
        )

    return candidate.resolve()


def ensure_output_directory(
    requested_value: str,
) -> Path:
    primary = resolve_output_directory(
        requested_value
    )

    try:
        primary.mkdir(
            parents=True,
            exist_ok=True,
        )

        test_path = primary / ".owde-write-test"
        test_path.write_text(
            "ok",
            encoding="utf-8",
        )
        test_path.unlink()

        return primary

    except OSError:
        fallback = (
            Path.home()
            / "OWDE_Showcase_Exports"
        )

        fallback.mkdir(
            parents=True,
            exist_ok=True,
        )

        return fallback.resolve()


def create_cylinder_insert(
    *,
    name: str,
    radius_mm: float,
    depth_mm: float,
    parent_object: bpy.types.Object,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=radius_mm * MM_TO_METERS,
        depth=depth_mm * MM_TO_METERS,
        location=(
            parent_object.location.x,
            parent_object.location.y,
            parent_object.location.z
            + depth_mm * MM_TO_METERS / 2.0,
        ),
    )

    insert = bpy.context.active_object
    insert.name = name

    insert.data.materials.append(
        get_or_create_dark_insert_material()
    )

    insert["owde_showcase_detail"] = True

    move_to_collection(
        insert,
        collection,
    )

    return insert


def create_slot_insert(
    *,
    parent_object: bpy.types.Object,
    collection: bpy.types.Collection,
    feature_width_mm: float,
    feature_height_mm: float,
) -> list[bpy.types.Object]:
    slot_length_mm = feature_width_mm

    slot_width_mm = max(
        8.0,
        min(
            feature_height_mm * 2.4,
            slot_length_mm * 0.30,
        ),
    )

    straight_length_mm = max(
        1.0,
        slot_length_mm - slot_width_mm,
    )

    depth_mm = 0.8
    material = get_or_create_dark_insert_material()

    objects: list[bpy.types.Object] = []

    bpy.ops.mesh.primitive_cube_add(
        location=(
            parent_object.location.x,
            parent_object.location.y,
            parent_object.location.z
            + depth_mm * MM_TO_METERS / 2.0,
        )
    )

    center = bpy.context.active_object
    center.name = (
        f"{parent_object.name}_Dark_Slot_Center"
    )

    center.dimensions = (
        straight_length_mm * MM_TO_METERS,
        slot_width_mm * MM_TO_METERS,
        depth_mm * MM_TO_METERS,
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    center.data.materials.append(material)

    move_to_collection(
        center,
        collection,
    )

    objects.append(center)

    for direction, suffix in (
        (-1.0, "Left"),
        (1.0, "Right"),
    ):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=64,
            radius=(
                slot_width_mm
                * MM_TO_METERS
                / 2.0
            ),
            depth=depth_mm * MM_TO_METERS,
            location=(
                parent_object.location.x
                + direction
                * straight_length_mm
                * MM_TO_METERS
                / 2.0,
                parent_object.location.y,
                parent_object.location.z
                + depth_mm
                * MM_TO_METERS
                / 2.0,
            ),
        )

        cap = bpy.context.active_object
        cap.name = (
            f"{parent_object.name}_Dark_Slot_{suffix}"
        )

        cap.data.materials.append(material)

        move_to_collection(
            cap,
            collection,
        )

        objects.append(cap)

    return objects


def create_showcase_details(
    *,
    shape: ShapeType,
    parent_object: bpy.types.Object,
    collection: bpy.types.Collection,
    parameters: TileParameters,
) -> list[bpy.types.Object]:
    details: list[bpy.types.Object] = []

    if shape is ShapeType.SLOT:
        details.extend(
            create_slot_insert(
                parent_object=parent_object,
                collection=collection,
                feature_width_mm=parameters.shape_width_mm,
                feature_height_mm=parameters.shape_height_mm,
            )
        )

    if shape is ShapeType.APERTURE:
        details.append(
            create_cylinder_insert(
                name=(
                    f"{parent_object.name}_"
                    "Dark_Aperture_Insert"
                ),
                radius_mm=(
                    parameters.shape_width_mm
                    * 0.46
                ),
                depth_mm=0.9,
                parent_object=parent_object,
                collection=collection,
            )
        )

    return details


def set_objects_render_visibility(
    objects: list[bpy.types.Object],
    visible: bool,
) -> None:
    for object_ in objects:
        object_.hide_render = not visible


def object_render_group(
    primitive: bpy.types.Object,
    details_by_parent: dict[
        str,
        list[bpy.types.Object],
    ],
) -> list[bpy.types.Object]:
    return [
        primitive,
        *details_by_parent.get(
            primitive.name,
            [],
        ),
    ]


def frame_individual_object(
    *,
    camera: bpy.types.Object,
    target: bpy.types.Object,
    object_: bpy.types.Object,
) -> None:
    center = object_.location.copy()

    target.location = center

    camera.location = (
        center.x + 0.115,
        center.y - 0.155,
        center.z + 0.135,
    )

    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 0.145


def restore_grid_camera(
    *,
    camera: bpy.types.Object,
    target: bpy.types.Object,
    gallery_width: float,
    gallery_depth: float,
) -> None:
    target.location = (0.0, 0.0, 0.0)

    camera.location = (
        gallery_width * 0.68,
        -gallery_depth * 1.08,
        gallery_depth * 1.12,
    )

    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(
        gallery_width,
        gallery_depth,
    ) * 1.17


def save_showcase_blend(
    output_directory: Path,
) -> Path:
    blend_path = (
        output_directory
        / "OWDE_Showcase.blend"
    )

    bpy.ops.wm.save_as_mainfile(
        filepath=str(blend_path),
        copy=True,
    )

    return blend_path


class OWDE_OT_create_showcase(
    bpy.types.Operator
):
    bl_idname = "owde.create_showcase"
    bl_label = "Create Operational Worlds Showcase"
    bl_description = (
        "Create all fifteen primitives with canonical materials, "
        "studio lighting, individual renders, and a contact sheet"
    )
    bl_options = {
        "REGISTER",
        "UNDO",
    }

    render_image: BoolProperty(
        name="Render Images",
        default=True,
    )

    render_individuals: BoolProperty(
        name="Render Individual Primitives",
        default=True,
    )

    save_blend_file: BoolProperty(
        name="Save Showcase Blend",
        default=True,
    )

    image_resolution: IntProperty(
        name="Contact Sheet Width",
        default=4096,
        min=1024,
        max=8192,
    )

    individual_resolution: IntProperty(
        name="Individual Image Size",
        default=2048,
        min=512,
        max=4096,
    )

    output_directory: StringProperty(
        name="Output Directory",
        subtype="DIR_PATH",
        default="",
    )

    def execute(
        self,
        context: bpy.types.Context,
    ):
        try:
            output_directory = ensure_output_directory(
                self.output_directory
            )
        except OSError as error:
            self.report(
                {"ERROR"},
                (
                    "Could not create a writable showcase "
                    f"directory: {error}"
                ),
            )
            return {"CANCELLED"}

        print(
            "OWDE showcase output directory:",
            output_directory,
        )

        clear_showcase()

        collection = bpy.data.collections.new(
            SHOWCASE_COLLECTION_NAME
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

        details_by_parent: dict[
            str,
            list[bpy.types.Object],
        ] = {}

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

            identifier = primitive_identifier(
                index
            )

            object_name = (
                f"{identifier}_"
                f"{PRIMITIVE_NAMES[shape]}"
            )

            object_ = mesh_object_from_data(
                object_name,
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

            object_["owde_object"] = True
            object_["owde_primitive_id"] = identifier
            object_["owde_shape"] = shape.value
            object_["owde_showcase"] = True
            object_["owde_version"] = SHOWCASE_RELEASE

            assign_canonical_materials(
                object_,
                shape,
                parameters.tile_height_mm,
            )

            if shape is ShapeType.WEIGHT:
                bevel = object_.modifiers.new(
                    name="OWDE Weight Edge Chamfer",
                    type="BEVEL",
                )

                bevel.width = 1.2 * MM_TO_METERS
                bevel.segments = 3
                bevel.limit_method = "ANGLE"

            smooth_shapes = {
                ShapeType.CIRCLE,
                ShapeType.HINGE,
                ShapeType.APERTURE,
                ShapeType.LENS,
                ShapeType.MIRROR,
                ShapeType.LIGHT_SOURCE,
                ShapeType.WEIGHT,
                ShapeType.SENSOR,
                ShapeType.HANDLE,
            }

            if shape in smooth_shapes:
                for polygon in object_.data.polygons:
                    polygon.use_smooth = True

            move_to_collection(
                object_,
                collection,
            )

            details = create_showcase_details(
                shape=shape,
                parent_object=object_,
                collection=collection,
                parameters=parameters,
            )

            details_by_parent[
                object_.name
            ] = details

            created_objects.append(object_)

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

        target = bpy.data.objects.new(
            "OWDE Showcase Target",
            None,
        )

        bpy.context.scene.collection.objects.link(
            target
        )

        move_to_collection(
            target,
            collection,
        )

        add_area_light(
            name="OWDE Key Light",
            location=(
                -gallery_width * 0.44,
                -gallery_depth * 0.42,
                gallery_depth * 1.08,
            ),
            energy=1450.0,
            size=2.4,
            target=target,
            collection=collection,
        )

        add_area_light(
            name="OWDE Fill Light",
            location=(
                gallery_width * 0.64,
                -gallery_depth * 0.04,
                gallery_depth * 0.74,
            ),
            energy=820.0,
            size=3.0,
            target=target,
            collection=collection,
        )

        add_area_light(
            name="OWDE Rim Light",
            location=(
                0.0,
                gallery_depth * 0.68,
                gallery_depth * 0.92,
            ),
            energy=1180.0,
            size=2.2,
            target=target,
            collection=collection,
        )

        camera = create_showcase_camera(
            gallery_width=gallery_width,
            gallery_depth=gallery_depth,
            target=target,
            collection=collection,
        )

        context.scene.camera = camera

        contact_sheet_path = (
            output_directory
            / "OWDE_Primitive_Showcase.png"
        )

        if self.render_image:
            all_render_objects = [
                *created_objects,
                *[
                    detail
                    for details in details_by_parent.values()
                    for detail in details
                ],
            ]

            set_objects_render_visibility(
                all_render_objects,
                True,
            )

            restore_grid_camera(
                camera=camera,
                target=target,
                gallery_width=gallery_width,
                gallery_depth=gallery_depth,
            )

            configure_render(
                width=self.image_resolution,
                height=int(
                    self.image_resolution * 0.68
                ),
                output_path=contact_sheet_path,
            )

            bpy.ops.render.render(
                write_still=True
            )

            print(
                "Rendered showcase contact sheet:",
                contact_sheet_path,
            )

            if self.render_individuals:
                individual_directory = (
                    output_directory
                    / "individual"
                )

                individual_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                for index, object_ in enumerate(
                    created_objects
                ):
                    set_objects_render_visibility(
                        all_render_objects,
                        False,
                    )

                    visible_group = object_render_group(
                        object_,
                        details_by_parent,
                    )

                    set_objects_render_visibility(
                        visible_group,
                        True,
                    )

                    frame_individual_object(
                        camera=camera,
                        target=target,
                        object_=object_,
                    )

                    shape = SHOWCASE_SHAPES[index]

                    individual_path = (
                        individual_directory
                        / (
                            f"{primitive_identifier(index)}_"
                            f"{PRIMITIVE_NAMES[shape]}.png"
                        )
                    )

                    configure_render(
                        width=self.individual_resolution,
                        height=self.individual_resolution,
                        output_path=individual_path,
                    )

                    bpy.ops.render.render(
                        write_still=True
                    )

                    print(
                        "Rendered individual primitive:",
                        individual_path,
                    )

                set_objects_render_visibility(
                    all_render_objects,
                    True,
                )

                restore_grid_camera(
                    camera=camera,
                    target=target,
                    gallery_width=gallery_width,
                    gallery_depth=gallery_depth,
                )

        blend_path = None

        if self.save_blend_file:
            try:
                blend_path = save_showcase_blend(
                    output_directory
                )
            except RuntimeError as error:
                self.report(
                    {"WARNING"},
                    (
                        "Showcase rendered, but the .blend "
                        f"copy could not be saved: {error}"
                    ),
                )

        message = (
            "Created OWDE showcase with 15 primitives"
        )

        if self.render_image:
            message += (
                f"; rendered to {output_directory}"
            )

        if blend_path is not None:
            message += (
                f"; saved {blend_path.name}"
            )

        self.report(
            {"INFO"},
            message,
        )

        return {"FINISHED"}


class OWDE_PT_showcase(bpy.types.Panel):
    bl_label = "Documentation Showcase"
    bl_idname = "OWDE_PT_showcase"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(
        self,
        context: bpy.types.Context,
    ) -> None:
        layout = self.layout

        info_box = layout.box()
        info_box.label(
            text="Canonical Primitive Showcase",
            icon="RENDER_STILL",
        )
        info_box.label(
            text="Builds all 15 primitives."
        )
        info_box.label(
            text="Separates tile and feature materials."
        )
        info_box.label(
            text="Adds camera and studio lights."
        )

        create_operator = layout.operator(
            "owde.create_showcase",
            text="Create Showcase Scene",
            icon="SCENE",
        )

        create_operator.render_image = False
        create_operator.render_individuals = False
        create_operator.save_blend_file = False

        render_operator = layout.operator(
            "owde.create_showcase",
            text="Create and Render Full Showcase",
            icon="RENDER_STILL",
        )

        render_operator.render_image = True
        render_operator.render_individuals = True
        render_operator.save_blend_file = True

        layout.label(
            text=(
                "Default output: Documents/"
                "OperationalWorlds/exports/showcase"
            ),
            icon="FILE_FOLDER",
        )
