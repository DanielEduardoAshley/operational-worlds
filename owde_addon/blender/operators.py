from __future__ import annotations

import bpy

from ..core import ShapeType, TileParameters, build_tile_mesh
from .adapter import create_blender_object


MM_TO_METERS = 0.001
GALLERY_COLLECTION_NAME = "OWDE Primitive Gallery"
OWDE_VERSION = "0.6.0-alpha.2"

GALLERY_SHAPES = (
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

PRIMITIVE_DEFINITIONS = {
    ShapeType.CIRCLE: {
        "id": "PRIM-0001",
        "name": "Raised Circle",
        "description": (
            "A raised circular region introducing centrality."
        ),
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
    ShapeType.SLOT: {
        "id": "PRIM-0005",
        "name": "Slot",
        "description": (
            "A linear recessed channel introducing insertion, "
            "guidance, and constrained movement."
        ),
        "capabilities": (
            "Insertion",
            "Guidance",
            "Channel",
            "Alignment",
            "Constrained Movement",
        ),
    },
    ShapeType.HINGE: {
        "id": "PRIM-0006",
        "name": "Hinge",
        "description": (
            "A rotational joint connecting two spatial states."
        ),
        "capabilities": (
            "Rotation",
            "Connection",
            "Articulation",
            "State Change",
            "Axis",
        ),
    },
    ShapeType.FOLD: {
        "id": "PRIM-0007",
        "name": "Fold",
        "description": (
            "A planar displacement producing an inside, outside, "
            "and directional change."
        ),
        "capabilities": (
            "Plane Change",
            "Inside",
            "Outside",
            "Crease",
            "Orientation",
        ),
    },
    ShapeType.APERTURE: {
        "id": "PRIM-0008",
        "name": "Aperture",
        "description": (
            "An opening created by removing material from a surface."
        ),
        "capabilities": (
            "Opening",
            "Passage",
            "Visibility",
            "Framing",
            "Permeability",
        ),
    },
    ShapeType.LENS: {
        "id": "PRIM-0009",
        "name": "Lens",
        "description": (
            "A convex perceptual surface that focuses or distorts."
        ),
        "capabilities": (
            "Focus",
            "Distortion",
            "Magnification",
            "Perception",
            "Refraction",
        ),
    },
    ShapeType.MIRROR: {
        "id": "PRIM-0010",
        "name": "Mirror",
        "description": (
            "A reflective surface creating a virtual spatial depth."
        ),
        "capabilities": (
            "Reflection",
            "Duplication",
            "Virtual Depth",
            "Reversal",
            "Self-Observation",
        ),
    },
    ShapeType.LIGHT_SOURCE: {
        "id": "PRIM-0011",
        "name": "Light Source",
        "description": (
            "An emitting surface introducing illumination, "
            "visibility, and signaling."
        ),
        "capabilities": (
            "Illuminate",
            "Signal",
            "Reveal",
            "Attract",
            "Orient",
        ),
    },
    ShapeType.WEIGHT: {
        "id": "PRIM-0012",
        "name": "Weight",
        "description": (
            "A concentrated mass introducing resistance, "
            "stability, and downward force."
        ),
        "capabilities": (
            "Weigh",
            "Anchor",
            "Resist",
            "Stabilize",
            "Press",
        ),
    },
    ShapeType.THRESHOLD: {
        "id": "PRIM-0013",
        "name": "Threshold",
        "description": (
            "A raised boundary marking transition between "
            "regions, conditions, or states."
        ),
        "capabilities": (
            "Separate",
            "Transition",
            "Mark",
            "Cross",
            "Regulate",
        ),
    },
    ShapeType.SENSOR: {
        "id": "PRIM-0014",
        "name": "Sensor",
        "description": (
            "A detecting surface that registers presence, "
            "change, proximity, or environmental conditions."
        ),
        "capabilities": (
            "Detect",
            "Measure",
            "Register",
            "Trigger",
            "Respond",
        ),
    },
    ShapeType.HANDLE: {
        "id": "PRIM-0015",
        "name": "Handle",
        "description": (
            "A graspable interface enabling lifting, pulling, "
            "carrying, or direct manipulation."
        ),
        "capabilities": (
            "Grasp",
            "Lift",
            "Pull",
            "Carry",
            "Manipulate",
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
    collection = bpy.data.collections.get(
        GALLERY_COLLECTION_NAME
    )

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
        bpy.data.objects.remove(
            object_,
            do_unlink=True,
        )


def move_object_to_collection(
    object_: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for current_collection in list(
        object_.users_collection
    ):
        current_collection.objects.unlink(object_)

    collection.objects.link(object_)


def deselect_all_objects() -> None:
    for object_ in bpy.context.selected_objects:
        object_.select_set(False)


def get_or_create_dark_insert_material() -> bpy.types.Material:
    material_name = "OWDE Dark Insert"
    material = bpy.data.materials.get(material_name)

    if material is None:
        material = bpy.data.materials.new(
            material_name
        )
        material.diffuse_color = (
            0.008,
            0.008,
            0.012,
            1.0,
        )

        material.use_nodes = True

        principled = material.node_tree.nodes.get(
            "Principled BSDF"
        )

        if principled is not None:
            principled.inputs["Base Color"].default_value = (
                0.005,
                0.005,
                0.008,
                1.0,
            )
            principled.inputs["Roughness"].default_value = 0.72
            principled.inputs["Metallic"].default_value = 0.05

    return material


def create_dark_circular_insert(
    parent_object: bpy.types.Object,
    parameters: TileParameters,
) -> bpy.types.Object:
    radius_m = (
        parameters.shape_width_mm
        * 0.46
        * MM_TO_METERS
    )

    depth_m = max(
        0.4,
        parameters.tile_height_mm * 0.08,
    ) * MM_TO_METERS

    world_location = (
        parent_object.location.x,
        parent_object.location.y,
        parent_object.location.z
        + (
            parameters.tile_height_mm
            * MM_TO_METERS
        )
        + depth_m / 2.0,
    )

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=parameters.circle_segments,
        radius=radius_m,
        depth=depth_m,
        location=world_location,
    )

    insert = bpy.context.active_object
    insert.name = "PRIM-0008_Aperture_Dark_Insert"

    insert.data.materials.append(
        get_or_create_dark_insert_material()
    )

    insert["owde_visual_detail"] = True
    insert["owde_detail_type"] = "dark_aperture_insert"

    insert.parent = parent_object
    insert.matrix_parent_inverse = (
        parent_object.matrix_world.inverted()
    )

    return insert


def create_dark_slot_insert(
    parent_object: bpy.types.Object,
    parameters: TileParameters,
) -> bpy.types.Object:
    slot_length_mm = parameters.shape_width_mm

    slot_width_mm = max(
        8.0,
        min(
            parameters.shape_height_mm * 2.4,
            slot_length_mm * 0.30,
        ),
    )

    straight_length_mm = max(
        1.0,
        slot_length_mm - slot_width_mm,
    )

    depth_m = max(
        0.35,
        parameters.tile_height_mm * 0.07,
    ) * MM_TO_METERS

    material = get_or_create_dark_insert_material()

    collection = bpy.data.collections.new(
        f"{parent_object.name}_Slot_Insert"
    )

    bpy.context.scene.collection.children.link(
        collection
    )

    pieces: list[bpy.types.Object] = []

    bpy.ops.mesh.primitive_cube_add(
        location=(
            parent_object.location.x,
            parent_object.location.y,
            parent_object.location.z
        + (
            parameters.tile_height_mm
            * MM_TO_METERS
        )
        + depth_m / 2.0,
        )
    )

    center = bpy.context.active_object
    center.name = "PRIM-0005_Slot_Dark_Center"
    center.dimensions = (
        straight_length_mm * MM_TO_METERS,
        slot_width_mm * MM_TO_METERS,
        depth_m,
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    pieces.append(center)

    for direction in (-1.0, 1.0):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=parameters.circle_segments,
            radius=(
                slot_width_mm
                / 2.0
                * MM_TO_METERS
            ),
            depth=depth_m,
            location=(
                parent_object.location.x
                + direction
                * straight_length_mm
                / 2.0
                * MM_TO_METERS,
                parent_object.location.y,
                    parent_object.location.z
                + (
                    parameters.tile_height_mm
                    * MM_TO_METERS
                )
                + depth_m / 2.0,
            ),
        )

        cap = bpy.context.active_object
        cap.name = (
            "PRIM-0005_Slot_Dark_End_"
            + ("L" if direction < 0 else "R")
        )
        pieces.append(cap)

    for piece in pieces:
        for current_collection in list(
            piece.users_collection
        ):
            current_collection.objects.unlink(piece)

        collection.objects.link(piece)

        piece.data.materials.append(material)
        piece["owde_visual_detail"] = True
        piece["owde_detail_type"] = "dark_slot_insert"
        piece.parent = parent_object
        piece.matrix_parent_inverse = (
            parent_object.matrix_world.inverted()
        )

    return center


def create_primitive_visual_details(
    object_: bpy.types.Object,
    parameters: TileParameters,
) -> None:
    if parameters.shape is ShapeType.APERTURE:
        create_dark_circular_insert(
            object_,
            parameters,
        )

    if parameters.shape is ShapeType.SLOT:
        create_dark_slot_insert(
            object_,
            parameters,
        )


class OWDE_OT_create_tile(bpy.types.Operator):
    bl_idname = "owde.create_tile"
    bl_label = "Create Operational Tile"
    bl_description = (
        "Create one parametric Operational Worlds primitive"
    )
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

        definition = PRIMITIVE_DEFINITIONS[
            parameters.shape
        ]

        object_ = create_blender_object(
            name=(
                f"{definition['id']}_"
                f"{definition['name'].replace(' ', '_')}"
            ),
            mesh_data=mesh_data,
        )

        attach_metadata(
            object_,
            parameters,
        )

        create_primitive_visual_details(
            object_,
            parameters,
        )

        object_.select_set(True)
        context.view_layer.objects.active = object_

        self.report(
            {"INFO"},
            f"Created {definition['name']}",
        )

        return {"FINISHED"}


class OWDE_OT_create_primitive_gallery(
    bpy.types.Operator
):
    bl_idname = "owde.create_primitive_gallery"
    bl_label = "Create Primitive Gallery"
    bl_description = (
        "Create all currently implemented Operational Worlds "
        "primitives in an evenly spaced gallery"
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

        gallery_collection = (
            get_or_create_gallery_collection(context)
        )

        if settings.gallery_clear_existing:
            clear_gallery_collection(
                gallery_collection
            )

        deselect_all_objects()

        center_distance_mm = (
            settings.tile_width_mm
            + settings.gallery_gap_mm
        )

        column_count = 3
        row_count = (
            len(GALLERY_SHAPES)
            + column_count
            - 1
        ) // column_count

        gallery_width_mm = (
            center_distance_mm
            * (column_count - 1)
        )

        gallery_depth_mm = (
            center_distance_mm
            * (row_count - 1)
        )

        starting_x_mm = -gallery_width_mm / 2.0
        starting_y_mm = gallery_depth_mm / 2.0

        created_objects: list[
            bpy.types.Object
        ] = []

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

            column = index % column_count
            row = index // column_count

            object_.location.x = (
                starting_x_mm
                + column * center_distance_mm
            ) * MM_TO_METERS

            object_.location.y = (
                starting_y_mm
                - row * center_distance_mm
            ) * MM_TO_METERS

            object_.location.z = 0.0

            attach_metadata(
                object_,
                parameters,
                primitive_index=index + 1,
            )

            create_primitive_visual_details(
                object_,
                parameters,
            )

            created_objects.append(object_)

        deselect_all_objects()

        for object_ in created_objects:
            object_.select_set(True)

        if created_objects:
            context.view_layer.objects.active = (
                created_objects[0]
            )

        self.report(
            {"INFO"},
            (
                "Created gallery with "
                f"{len(created_objects)} operational primitives"
            ),
        )

        return {"FINISHED"}


class OWDE_OT_frame_primitive_gallery(
    bpy.types.Operator
):
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
                (
                    "The primitive gallery contains "
                    "no visible objects"
                ),
            )
            return {"CANCELLED"}

        for object_ in visible_objects:
            object_.select_set(True)

        context.view_layer.objects.active = (
            visible_objects[0]
        )

        try:
            bpy.ops.view3d.view_selected(
                use_all_regions=False
            )
        except RuntimeError:
            self.report(
                {"INFO"},
                (
                    "Gallery selected. "
                    "Press Home to frame it."
                ),
            )

        return {"FINISHED"}
