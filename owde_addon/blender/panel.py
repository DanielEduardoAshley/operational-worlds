from __future__ import annotations

import bpy


class OWDE_PT_tile_builder(bpy.types.Panel):
    bl_label = "Operational Tile Builder"
    bl_idname = "OWDE_PT_tile_builder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        settings = context.scene.owde_settings

        layout.prop(settings, "shape")

        tile_box = layout.box()
        tile_box.label(text="Tile")
        tile_box.prop(settings, "tile_width_mm")
        tile_box.prop(settings, "tile_depth_mm")
        tile_box.prop(settings, "tile_height_mm")

        shape_box = layout.box()
        shape_box.label(text="Raised Shape")
        shape_box.prop(settings, "shape_width_mm")
        shape_box.prop(settings, "shape_height_mm")

        if settings.shape == "CIRCLE":
            shape_box.prop(settings, "circle_segments")

        finish_box = layout.box()
        finish_box.label(text="Finish")
        finish_box.prop(settings, "bevel_mm")

        layout.operator(
            "owde.create_tile",
            text="Create Tile",
            icon="MESH_CUBE",
        )
