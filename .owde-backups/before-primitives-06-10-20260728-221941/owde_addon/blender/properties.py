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
        description="Width of the tile in millimeters",
        default=100.0,
        min=10.0,
    )
    tile_depth_mm: bpy.props.FloatProperty(
        name="Tile Depth",
        description="Depth of the tile in millimeters",
        default=100.0,
        min=10.0,
    )
    tile_height_mm: bpy.props.FloatProperty(
        name="Tile Height",
        description="Height of the tile base in millimeters",
        default=8.0,
        min=1.0,
    )
    shape_width_mm: bpy.props.FloatProperty(
        name="Shape Width",
        description="Maximum width of the raised shape in millimeters",
        default=55.0,
        min=1.0,
    )
    shape_height_mm: bpy.props.FloatProperty(
        name="Shape Height",
        description="Height of the raised shape in millimeters",
        default=5.0,
        min=0.5,
    )
    bevel_mm: bpy.props.FloatProperty(
        name="Bevel",
        description="Reserved bevel dimension in millimeters",
        default=1.0,
        min=0.0,
    )
    circle_segments: bpy.props.IntProperty(
        name="Circle Resolution",
        description="Number of segments used to construct the circle",
        default=64,
        min=24,
        max=256,
    )
    gallery_gap_mm: bpy.props.FloatProperty(
        name="Gap Between Tiles",
        description="Empty space between adjacent gallery tiles",
        default=20.0,
        min=0.0,
    )
    gallery_clear_existing: bpy.props.BoolProperty(
        name="Replace Existing Gallery",
        description="Delete the previous generated gallery before creating a new one",
        default=True,
    )
