from __future__ import annotations

import bpy

from ..core import ShapeType, TileParameters, build_tile_mesh
from .adapter import create_blender_object


MM_TO_METERS = 0.001
GALLERY_COLLECTION_NAME = "OWDE Primitive Gallery"
OWDE_VERSION = "0.2.0-alpha.1"

GALLERY_SHAPES = (
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.SQUARE,
    ShapeType.HEXAGON,
)

PRIMITIVE_DEFINITIONS = {
    ShapeType.CIRCLE: {
        "id": "PRIM-0001",
        "name": "Raised Circle",
        "description": "A raised circular region introducing centrality.",
        "capabilities": (
            "Center",
            "Zone",
            "Radius",
            "Boundary",
            "Reference Point",
        ),
    },
    ShapeType.TRIANGLE: {
        "id": "PRIM-0002",
        "name": "Raised Triangle",
        "description": (
            "A raised triangular region introducing direction, "
            "orientation, and convergence."
        ),
        "capabilities": (
            "Direction",
            "Orientation",
            "Point",
            "Edge",
            "Convergence",
        ),
    },
    ShapeType.SQUARE: {
        "id": "PRIM-0003",
        "name": "Raised Square",
        "description": (
            "A raised orthogonal region introducing enclosure, "
            "alignment, and stable orientation."
        ),
        "capabilities": (
            "Zone",
            "Boundary",
            "Alignment",
            "Corner",
            "Orthogonal Orientation",
        ),
    },
    ShapeType.HEXAGON: {
        "id": "PRIM-0004",
        "name": "Raised Hexagon",
        "description": (
            "A raised six-sided region introducing adjacency, "
            "cell structure, and distributed orientation."
        ),
        "capabilities": (
            "Cell",
            "Adjacency",
            "Zone",
            "Boundary",
            "Distributed Orientation",
        ),
    },
}


def parameters_from_settings(
    settings,
    shape: ShapeType,
) -> TileParameters:
    return TileParameters(
        shape=shape,
        tile_width_mm=settings.tile_width_mm,
        tile_depth_mm=settings.tile_depth_mm,
        tile_height_mm=settings.tile_height_mm,
        shape_width_mm=settings.shape_width_mm,
        shape_height_mm=settings.shape_height_mm,
        bevel_mm=settings.bevel_mm,
        circle_segments=settings.circle_segments,
    )


def attach_metadata(
    object_: bpy.types.Object,
    parameters: TileParameters,
    primitive_index: int | None = None,
) -> None:
    definition = PRIMITIVE_DEFINITIONS[parameters.shape]

    object_["owde_object"] = True
    object_["owde_primitive_id"] = definition["id"]
    object_["owde_primitive_name"] = definition["name"]
    object_["owde_description"] = definition["description"]
    object_["owde_capabilities"] = "|".join(
        definition["capabilities"]
    )

    object_["owde_shape"] = parameters.shape.value
    object_["owde_version"] = OWDE_VERSION

    object_["owde_tile_width_mm"] = parameters.tile_width_mm
    object_["owde_tile_depth_mm"] = parameters.tile_depth_mm
    object_["owde_tile_height_mm"] = parameters.tile_height_mm

    object_["owde_shape_width_mm"] = parameters.shape_width_mm
    object_["owde_shape_height_mm"] = parameters.shape_height_mm
    object_["owde_bevel_mm"] = parameters.bevel_mm
    object_["owde_circle_segments"] = parameters.circle_segments

    if primitive_index is not None:
        object_["owde_gallery_index"] = primitive_index


def get_or_create_gallery_collection(
    context: bpy.types.Context,
) -> bpy.types.Collection:
    collection = bpy.data.collections.get(GALLERY_COLLECTION_NAME)

    if collection is None:
        collection = bpy.data.collections.new(
            GALLERY_COLLECTION_NAME
        )
        context.scene.collection.children.link(collection)

    return collection


def clear_gallery_collection(
    collection: bpy.types.Collection,
) -> None:
    for object_ in list(collection.objects):
        bpy.data.objects.remove(object_, do_unlink=True)


def move_object_to_collection(
    object_: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for current_collection in list(object_.users_collection):
        current_collection.objects.unlink(object_)

    collection.objects.link(object_)


def deselect_all_objects() -> None:
    for object_ in bpy.context.selected_objects:
        object_.select_set(False)


class OWDE_OT_create_tile(bpy.types.Operator):
    bl_idname = "owde.create_tile"
    bl_label = "Create Operational Tile"
    bl_description = "Create one parametric Operational Worlds tile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        settings = context.scene.owde_settings
        parameters = parameters_from_settings(
            settings,
            ShapeType(settings.shape),
        )

        try:
            mesh_data = build_tile_mesh(parameters)
        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        deselect_all_objects()

        definition = PRIMITIVE_DEFINITIONS[parameters.shape]

        object_ = create_blender_object(
            name=(
                f"{definition['id']}_"
                f"{definition['name'].replace(' ', '_')}"
            ),
            mesh_data=mesh_data,
        )

        attach_metadata(object_, parameters)

        object_.select_set(True)
        context.view_layer.objects.active = object_

        self.report(
            {"INFO"},
            f"Created {definition['name']}",
        )

        return {"FINISHED"}


class OWDE_OT_create_primitive_gallery(bpy.types.Operator):
    bl_idname = "owde.create_primitive_gallery"
    bl_label = "Create Primitive Gallery"
    bl_description = (
        "Create Circle, Triangle, Square, and Hexagon tiles "
        "in an evenly spaced row"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        settings = context.scene.owde_settings

        try:
            parameter_sets = [
                parameters_from_settings(settings, shape)
                for shape in GALLERY_SHAPES
            ]

            meshes = [
                build_tile_mesh(parameters)
                for parameters in parameter_sets
            ]
        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        gallery_collection = get_or_create_gallery_collection(
            context
        )

        if settings.gallery_clear_existing:
            clear_gallery_collection(gallery_collection)

        deselect_all_objects()

        center_distance_mm = (
            settings.tile_width_mm
            + settings.gallery_gap_mm
        )

        gallery_width_mm = (
            center_distance_mm
            * (len(GALLERY_SHAPES) - 1)
        )

        starting_x_mm = -gallery_width_mm / 2.0

        created_objects: list[bpy.types.Object] = []

        for index, (parameters, mesh_data) in enumerate(
            zip(parameter_sets, meshes)
        ):
            definition = PRIMITIVE_DEFINITIONS[
                parameters.shape
            ]

            object_name = (
                f"{definition['id']}_Gallery_"
                f"{definition['name'].replace(' ', '_')}"
            )

            object_ = create_blender_object(
                name=object_name,
                mesh_data=mesh_data,
            )

            move_object_to_collection(
                object_,
                gallery_collection,
            )

            x_mm = (
                starting_x_mm
                + index * center_distance_mm
            )

            object_.location.x = x_mm * MM_TO_METERS
            object_.location.y = 0.0
            object_.location.z = 0.0

            attach_metadata(
                object_,
                parameters,
                primitive_index=index + 1,
            )

            created_objects.append(object_)

        deselect_all_objects()

        for object_ in created_objects:
            object_.select_set(True)

        if created_objects:
            context.view_layer.objects.active = created_objects[0]

        self.report(
            {"INFO"},
            "Created gallery with 4 operational primitives",
        )

        return {"FINISHED"}


class OWDE_OT_frame_primitive_gallery(bpy.types.Operator):
    bl_idname = "owde.frame_primitive_gallery"
    bl_label = "Frame Gallery"
    bl_description = (
        "Select and frame all objects in the primitive gallery"
    )
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context):
        collection = bpy.data.collections.get(
            GALLERY_COLLECTION_NAME
        )

        if collection is None or not collection.objects:
            self.report(
                {"WARNING"},
                "No primitive gallery has been created",
            )
            return {"CANCELLED"}

        deselect_all_objects()

        visible_objects = [
            object_
            for object_ in collection.objects
            if not object_.hide_viewport
        ]

        if not visible_objects:
            self.report(
                {"WARNING"},
                "The primitive gallery contains no visible objects",
            )
            return {"CANCELLED"}

        for object_ in visible_objects:
            object_.select_set(True)

        context.view_layer.objects.active = visible_objects[0]

        try:
            bpy.ops.view3d.view_selected(
                use_all_regions=False
            )
        except RuntimeError:
            self.report(
                {"INFO"},
                "Gallery selected. Press Home to frame it.",
            )

        return {"FINISHED"}
