from __future__ import annotations

import bpy

from ..core import ShapeType, TileParameters, build_tile_mesh
from .adapter import create_blender_object


class OWDE_OT_create_tile(bpy.types.Operator):
    bl_idname = "owde.create_tile"
    bl_label = "Create Operational Tile"
    bl_description = "Create a parametric Operational Worlds tile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        settings = context.scene.owde_settings

        parameters = TileParameters(
            shape=ShapeType(settings.shape),
            tile_width_mm=settings.tile_width_mm,
            tile_depth_mm=settings.tile_depth_mm,
            tile_height_mm=settings.tile_height_mm,
            shape_width_mm=settings.shape_width_mm,
            shape_height_mm=settings.shape_height_mm,
            bevel_mm=settings.bevel_mm,
            circle_segments=settings.circle_segments,
        )

        try:
            mesh_data = build_tile_mesh(parameters)
        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        object_name = f"OWDE_{parameters.shape.value.title()}_Tile"

        object_ = create_blender_object(
            name=object_name,
            mesh_data=mesh_data,
        )

        object_["owde_shape"] = parameters.shape.value
        object_["owde_version"] = "0.2.0-alpha.1"
        object_["owde_tile_width_mm"] = parameters.tile_width_mm
        object_["owde_tile_depth_mm"] = parameters.tile_depth_mm
        object_["owde_tile_height_mm"] = parameters.tile_height_mm
        object_["owde_shape_width_mm"] = parameters.shape_width_mm
        object_["owde_shape_height_mm"] = parameters.shape_height_mm

        self.report(
            {"INFO"},
            f"Created {parameters.shape.value.title()} tile",
        )

        return {"FINISHED"}
