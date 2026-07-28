import bpy


class OWDE_PG_settings(bpy.types.PropertyGroup):
    shape: bpy.props.EnumProperty(
        name="Shape",
        description="Raised operational shape",
        items=(
            ("CIRCLE", "Circle", "Raised circular primitive"),
            ("TRIANGLE", "Triangle", "Raised triangular primitive"),
            ("SQUARE", "Square", "Raised square primitive"),
            ("HEXAGON", "Hexagon", "Raised hexagonal primitive"),
        ),
        default="CIRCLE",
    )

    tile_width_mm: bpy.props.FloatProperty(
        name="Tile Width",
        default=100.0,
        min=10.0,
        unit="LENGTH",
    )

    tile_depth_mm: bpy.props.FloatProperty(
        name="Tile Depth",
        default=100.0,
        min=10.0,
        unit="LENGTH",
    )

    tile_height_mm: bpy.props.FloatProperty(
        name="Tile Height",
        default=8.0,
        min=1.0,
        unit="LENGTH",
    )

    shape_width_mm: bpy.props.FloatProperty(
        name="Shape Width",
        default=55.0,
        min=1.0,
        unit="LENGTH",
    )

    shape_height_mm: bpy.props.FloatProperty(
        name="Shape Height",
        default=5.0,
        min=0.5,
        unit="LENGTH",
    )

    bevel_mm: bpy.props.FloatProperty(
        name="Bevel",
        default=1.0,
        min=0.0,
        unit="LENGTH",
    )

    circle_segments: bpy.props.IntProperty(
        name="Circle Resolution",
        default=64,
        min=24,
        max=256,
    )
