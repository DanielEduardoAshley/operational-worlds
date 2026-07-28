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
            text="Create Selected Tile",
            icon="MESH_CUBE",
        )
        layout.separator()
        gallery_box = layout.box()
        gallery_box.label(
            text="Primitive Gallery",
            icon="OUTLINER_COLLECTION",
        )
        gallery_box.label(
            text="Circle / Triangle / Square / Hexagon"
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
