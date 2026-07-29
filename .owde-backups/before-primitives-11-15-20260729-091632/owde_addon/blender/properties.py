import bpy


class OWDE_PG_settings(bpy.types.PropertyGroup):
    shape: bpy.props.EnumProperty(
        name="Primitive",
        description="Operational primitive to generate",
        items=(
            (
                "CIRCLE",
                "01 Raised Circle",
                "Establishes a distinct central zone",
            ),
            (
                "TRIANGLE",
                "02 Raised Triangle",
                "Introduces directionality",
            ),
            (
                "SQUARE",
                "03 Raised Square",
                "Creates stable territory",
            ),
            (
                "HEXAGON",
                "04 Raised Hexagon",
                "Introduces six-directional adjacency",
            ),
            (
                "SLOT",
                "05 Slot",
                "Creates a linear channel for insertion or guidance",
            ),
            (
                "HINGE",
                "06 Hinge",
                "Enables rotation and connects two states",
            ),
            (
                "FOLD",
                "07 Fold",
                "Changes plane and creates inside and outside",
            ),
            (
                "APERTURE",
                "08 Aperture",
                "Removes material to create visibility or passage",
            ),
            (
                "LENS",
                "09 Lens",
                "Focuses or distorts perception",
            ),
            (
                "MIRROR",
                "10 Mirror",
                "Reflects and creates virtual depth",
            ),
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
        name="Feature Width",
        description=(
            "Primary width or diameter of the operational feature"
        ),
        default=55.0,
        min=1.0,
    )

    shape_height_mm: bpy.props.FloatProperty(
        name="Feature Height",
        description=(
            "Height, thickness, diameter, or rise of the feature"
        ),
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
        name="Radial Resolution",
        description=(
            "Number of segments used for circular geometry"
        ),
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
        description=(
            "Delete the previous generated gallery before "
            "creating a new one"
        ),
        default=True,
    )
