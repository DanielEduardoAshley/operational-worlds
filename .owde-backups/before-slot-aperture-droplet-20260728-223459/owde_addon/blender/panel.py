from __future__ import annotations

import bpy


CIRCULAR_PRIMITIVES = {
    "CIRCLE",
    "HINGE",
    "APERTURE",
    "LENS",
}


def draw_dimension(
    layout,
    label: str,
    value,
    unit: str = "mm",
) -> None:
    if value is None:
        layout.label(text=f"{label}: -")
    else:
        layout.label(
            text=f"{label}: {value:g} {unit}"
        )


class OWDE_PT_tile_builder(bpy.types.Panel):
    bl_label = "Operational Tile Builder"
    bl_idname = "OWDE_PT_tile_builder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"

    def draw(
        self,
        context: bpy.types.Context,
    ) -> None:
        layout = self.layout
        settings = context.scene.owde_settings

        single_box = layout.box()
        single_box.label(
            text="Single Primitive",
            icon="MESH_CIRCLE",
        )
        single_box.prop(settings, "shape")

        tile_box = layout.box()
        tile_box.label(text="Tile Dimensions")
        tile_box.prop(settings, "tile_width_mm")
        tile_box.prop(settings, "tile_depth_mm")
        tile_box.prop(settings, "tile_height_mm")

        feature_box = layout.box()
        feature_box.label(
            text="Operational Feature"
        )
        feature_box.prop(
            settings,
            "shape_width_mm",
        )
        feature_box.prop(
            settings,
            "shape_height_mm",
        )

        if settings.shape in CIRCULAR_PRIMITIVES:
            feature_box.prop(
                settings,
                "circle_segments",
            )

        finish_box = layout.box()
        finish_box.label(text="Finish")
        finish_box.prop(settings, "bevel_mm")

        layout.operator(
            "owde.create_tile",
            text="Create Selected Primitive",
            icon="MESH_CUBE",
        )

        layout.separator()

        gallery_box = layout.box()
        gallery_box.label(
            text="Primitive Gallery",
            icon="OUTLINER_COLLECTION",
        )

        gallery_box.label(
            text="OW01-OW04 and OW06-OW10"
        )

        gallery_box.prop(
            settings,
            "gallery_gap_mm",
        )

        gallery_box.prop(
            settings,
            "gallery_clear_existing",
        )

        gallery_box.operator(
            "owde.create_primitive_gallery",
            text="Create Primitive Gallery",
            icon="GROUP",
        )

        gallery_box.operator(
            "owde.frame_primitive_gallery",
            text="Frame Gallery in View",
            icon="VIEWZOOM",
        )


class OWDE_PT_primitive_inspector(
    bpy.types.Panel
):
    bl_label = "Primitive Inspector"
    bl_idname = "OWDE_PT_primitive_inspector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(
        cls,
        context: bpy.types.Context,
    ) -> bool:
        return context.active_object is not None

    def draw(
        self,
        context: bpy.types.Context,
    ) -> None:
        layout = self.layout
        object_ = context.active_object

        if object_ is None:
            layout.label(text="No active object.")
            return

        if not object_.get("owde_object", False):
            info_box = layout.box()
            info_box.label(
                text=(
                    "Selected object is not "
                    "an OWDE primitive."
                ),
                icon="INFO",
            )
            info_box.label(
                text="Select a generated primitive."
            )
            return

        identity_box = layout.box()
        identity_box.label(
            text=object_.get(
                "owde_primitive_id",
                "Uncatalogued Primitive",
            ),
            icon="BOOKMARKS",
        )

        identity_box.label(
            text=object_.get(
                "owde_primitive_name",
                object_.name,
            )
        )

        shape_name = object_.get(
            "owde_shape",
            "unknown",
        )

        identity_box.label(
            text=(
                "Geometry Type: "
                f"{shape_name.replace('_', ' ').title()}"
            )
        )

        description = object_.get(
            "owde_description",
            "",
        )

        if description:
            description_box = layout.box()
            description_box.label(
                text="Description"
            )
            description_box.label(
                text=description
            )

        capability_box = layout.box()
        capability_box.label(
            text="Capabilities",
            icon="OUTLINER_OB_LIGHT",
        )

        capabilities = object_.get(
            "owde_capabilities",
            "",
        )

        capability_items = [
            item.strip()
            for item in capabilities.split("|")
            if item.strip()
        ]

        if capability_items:
            for capability in capability_items:
                row = capability_box.row()
                row.label(
                    text=capability,
                    icon="DOT",
                )
        else:
            capability_box.label(
                text="No capabilities recorded."
            )

        geometry_box = layout.box()
        geometry_box.label(
            text="Geometry",
            icon="MESH_DATA",
        )

        draw_dimension(
            geometry_box,
            "Tile Width",
            object_.get("owde_tile_width_mm"),
        )
        draw_dimension(
            geometry_box,
            "Tile Depth",
            object_.get("owde_tile_depth_mm"),
        )
        draw_dimension(
            geometry_box,
            "Tile Height",
            object_.get("owde_tile_height_mm"),
        )
        draw_dimension(
            geometry_box,
            "Feature Width",
            object_.get("owde_shape_width_mm"),
        )
        draw_dimension(
            geometry_box,
            "Feature Height",
            object_.get("owde_shape_height_mm"),
        )
        draw_dimension(
            geometry_box,
            "Bevel",
            object_.get("owde_bevel_mm"),
        )

        if shape_name in CIRCULAR_PRIMITIVES:
            segments = object_.get(
                "owde_circle_segments"
            )
            geometry_box.label(
                text=f"Radial Segments: {segments}"
            )

        research_box = layout.box()
        research_box.label(
            text="Research Record",
            icon="FILE_TEXT",
        )

        version = object_.get(
            "owde_version",
            "Unknown",
        )
        research_box.label(
            text=f"OWDE Version: {version}"
        )

        gallery_index = object_.get(
            "owde_gallery_index"
        )

        if gallery_index is not None:
            research_box.label(
                text=(
                    "Gallery Position: "
                    f"{gallery_index}"
                )
            )

        object_box = layout.box()
        object_box.label(
            text="Blender Object",
            icon="OBJECT_DATA",
        )
        object_box.label(
            text=f"Name: {object_.name}"
        )

        if object_.type == "MESH":
            mesh = object_.data
            object_box.label(
                text=f"Vertices: {len(mesh.vertices)}"
            )
            object_box.label(
                text=f"Edges: {len(mesh.edges)}"
            )
            object_box.label(
                text=f"Faces: {len(mesh.polygons)}"
            )
