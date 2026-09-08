"""Blender UI and operators for OWDE Competition Primitives."""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)
from bpy.types import Operator, Panel, PropertyGroup

from ..core.competition_builders import (
    ACTOR_DIAMETER_MM,
    ACTOR_HEIGHT_MM,
    ACTOR_SQUARE_MM,
    GATE_DEPTH_MM,
    GATE_HEIGHT_MM,
    GATE_LENGTH_MM,
    GATE_MEMBER_MM,
    NET_DEPTH_MM,
    NET_FRAME_MM,
    NET_GRID_MEMBER_MM,
    NET_HEIGHT_MM,
    NET_LENGTH_MM,
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
)

MM_TO_METERS = 0.001
COMPETITION_VERSION = "0.7.0-alpha.1"


def _mesh_to_blender(mesh_data, name: str):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")

    vertices = [
        (x * MM_TO_METERS, y * MM_TO_METERS, z * MM_TO_METERS)
        for x, y, z in mesh_data.vertices
    ]

    mesh.from_pydata(vertices, [], list(mesh_data.faces))
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj


def _set_metadata(obj, primitive_id: str, primitive_name: str, capability: str):
    obj["owde_namespace"] = "COMP"
    obj["owde_primitive_id"] = primitive_id
    obj["owde_primitive_name"] = primitive_name
    obj["owde_capability"] = capability
    obj["owde_version"] = COMPETITION_VERSION
    obj["owde_substrate"] = "NONE"


class OWDE_PG_competition_settings(PropertyGroup):

    primitive: EnumProperty(
        name="Primitive",
        items=(
            ("ACTOR", "Actor", "COMP-0001 — mobile unit / token"),
            ("GATE", "Gate", "COMP-0002 — regulates passage"),
            ("NET", "Net", "COMP-0003 — porous barrier / target / filter"),
        ),
        default="ACTOR",
    )

    actor_variant: EnumProperty(
        name="Actor Shape",
        items=(
            ("CIRCLE", "Circle", "Circular actor/token"),
            ("SQUARE", "Square", "Square actor/token"),
        ),
        default="CIRCLE",
    )

    actor_diameter_mm: FloatProperty(
        name="Diameter",
        default=ACTOR_DIAMETER_MM,
        min=1.0,
    )

    actor_square_mm: FloatProperty(
        name="Width",
        default=ACTOR_SQUARE_MM,
        min=1.0,
    )

    actor_height_mm: FloatProperty(
        name="Height",
        default=ACTOR_HEIGHT_MM,
        min=1.0,
    )

    gate_length_mm: FloatProperty(
        name="Length",
        default=GATE_LENGTH_MM,
        min=1.0,
    )

    gate_height_mm: FloatProperty(
        name="Height",
        default=GATE_HEIGHT_MM,
        min=1.0,
    )

    gate_depth_mm: FloatProperty(
        name="Depth",
        default=GATE_DEPTH_MM,
        min=1.0,
    )

    gate_member_mm: FloatProperty(
        name="Member",
        default=GATE_MEMBER_MM,
        min=0.5,
    )

    net_length_mm: FloatProperty(
        name="Length",
        default=NET_LENGTH_MM,
        min=1.0,
    )

    net_height_mm: FloatProperty(
        name="Height",
        default=NET_HEIGHT_MM,
        min=1.0,
    )

    net_depth_mm: FloatProperty(
        name="Depth",
        default=NET_DEPTH_MM,
        min=1.0,
    )

    net_frame_mm: FloatProperty(
        name="Frame",
        default=NET_FRAME_MM,
        min=0.5,
    )

    net_grid_member_mm: FloatProperty(
        name="Grid Member",
        default=NET_GRID_MEMBER_MM,
        min=0.25,
    )

    net_columns: IntProperty(
        name="Columns",
        description="Number of openings across the net",
        default=10,
        min=2,
        max=40,
    )

    net_rows: IntProperty(
        name="Rows",
        description="Number of openings vertically",
        default=4,
        min=2,
        max=20,
    )

    net_woven_depth: BoolProperty(
        name="Top-view Relief",
        description="Offset crossing grid members slightly in depth so the net remains legible from above",
        default=True,
    )

    net_top_mesh: BoolProperty(
        name="Top Mesh",
        description="Add a shallow lattice across the top of the net so it reads as mesh from plan view",
        default=True,
    )

    net_top_mesh_thickness_mm: FloatProperty(
        name="Top Mesh Thickness",
        description="Vertical thickness of the plan-view lattice",
        default=0.8,
        min=0.2,
        max=5.0,
    )

    net_top_mesh_member_mm: FloatProperty(
        name="Top Mesh Member",
        description="Width of the top lattice ribs",
        default=0.9,
        min=0.2,
        max=5.0,
    )

    net_top_mesh_openings: IntProperty(
        name="Top Mesh Openings",
        description="Number of repeating openings across the top lattice",
        default=8,
        min=2,
        max=40,
    )


class OWDE_OT_create_competition_primitive(Operator):
    bl_idname = "owde.create_competition_primitive"
    bl_label = "Create Competition Primitive"
    bl_description = "Create a substrate-free Actor, Gate, or Net"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.owde_competition_settings

        try:
            if settings.primitive == "ACTOR":
                mesh_data = build_actor_mesh(
                    variant=settings.actor_variant,
                    diameter_mm=settings.actor_diameter_mm,
                    square_mm=settings.actor_square_mm,
                    height_mm=settings.actor_height_mm,
                )

                suffix = "Circle" if settings.actor_variant == "CIRCLE" else "Square"
                obj = _mesh_to_blender(mesh_data, f"COMP-0001_Actor_{suffix}")

                _set_metadata(obj, "COMP-0001", "Actor", "Occupy / move")
                obj["owde_variant"] = settings.actor_variant

            elif settings.primitive == "GATE":
                mesh_data = build_gate_mesh(
                    length_mm=settings.gate_length_mm,
                    height_mm=settings.gate_height_mm,
                    depth_mm=settings.gate_depth_mm,
                    member_mm=settings.gate_member_mm,
                )

                obj = _mesh_to_blender(mesh_data, "COMP-0002_Gate")
                _set_metadata(obj, "COMP-0002", "Gate", "Regulate passage")

            else:
                mesh_data = build_net_mesh(
                    length_mm=settings.net_length_mm,
                    height_mm=settings.net_height_mm,
                    depth_mm=settings.net_depth_mm,
                    frame_mm=settings.net_frame_mm,
                    grid_member_mm=settings.net_grid_member_mm,
                    columns=settings.net_columns,
                    rows=settings.net_rows,
                    woven_depth=settings.net_woven_depth,
                    top_mesh=settings.net_top_mesh,
                    top_mesh_thickness_mm=settings.net_top_mesh_thickness_mm,
                    top_mesh_member_mm=settings.net_top_mesh_member_mm,
                    top_mesh_openings=settings.net_top_mesh_openings,
                )

                obj = _mesh_to_blender(mesh_data, "COMP-0003_Net")
                _set_metadata(
                    obj,
                    "COMP-0003",
                    "Net",
                    "Porous barrier / intercept / filter",
                )

            self.report(
                {"INFO"},
                f"Created {obj.name} — substrate-free competition primitive",
            )
            return {"FINISHED"}

        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}


class OWDE_PT_competition_primitives(Panel):
    bl_label = "Competition Primitives"
    bl_idname = "OWDE_PT_competition_primitives"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Operational Worlds"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.owde_competition_settings

        box = layout.box()
        box.label(text="COMP Library v0.1")
        box.label(text="Substrate-free / movable")

        layout.prop(settings, "primitive")

        if settings.primitive == "ACTOR":
            layout.label(text="COMP-0001 — Actor")
            layout.prop(settings, "actor_variant")

            if settings.actor_variant == "CIRCLE":
                layout.prop(settings, "actor_diameter_mm")
            else:
                layout.prop(settings, "actor_square_mm")

            layout.prop(settings, "actor_height_mm")

        elif settings.primitive == "GATE":
            layout.label(text="COMP-0002 — Gate")
            layout.prop(settings, "gate_length_mm")
            layout.prop(settings, "gate_height_mm")
            layout.prop(settings, "gate_depth_mm")
            layout.prop(settings, "gate_member_mm")

        else:
            layout.label(text="COMP-0003 — Net")
            layout.prop(settings, "net_length_mm")
            layout.prop(settings, "net_height_mm")
            layout.prop(settings, "net_depth_mm")
            layout.prop(settings, "net_frame_mm")
            layout.prop(settings, "net_grid_member_mm")
            layout.prop(settings, "net_columns")
            layout.prop(settings, "net_rows")
            layout.prop(settings, "net_woven_depth")

            layout.separator()
            top_box = layout.box()
            top_box.label(text="Top / Plan View Mesh")
            top_box.prop(settings, "net_top_mesh")

            if settings.net_top_mesh:
                top_box.prop(settings, "net_top_mesh_thickness_mm")
                top_box.prop(settings, "net_top_mesh_member_mm")
                top_box.prop(settings, "net_top_mesh_openings")

        layout.separator()
        layout.operator(
            OWDE_OT_create_competition_primitive.bl_idname,
            icon="MESH_CUBE",
        )

        footer = layout.box()
        footer.label(text='Reference field: 20" × 16"')
        footer.label(text='Actor default: 1.25" × 0.375"')
        footer.label(text='Gate + Net length: 6.0"')


_CLASSES = (
    OWDE_PG_competition_settings,
    OWDE_OT_create_competition_primitive,
    OWDE_PT_competition_primitives,
)


def register_competition():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.owde_competition_settings = PointerProperty(
        type=OWDE_PG_competition_settings
    )


def unregister_competition():
    if hasattr(bpy.types.Scene, "owde_competition_settings"):
        del bpy.types.Scene.owde_competition_settings

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)

