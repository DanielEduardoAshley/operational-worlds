bl_info = {
    "name": "Operational Worlds Design Engine",
    "author": "Operational Worlds Research Program",
    "version": (0, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Operational Worlds",
    "description": "Create parametric Operational Worlds tiles",
    "category": "Add Mesh",
}


def register() -> None:
    import bpy

    from .blender import (
        OWDE_OT_create_tile,
        OWDE_PG_settings,
        OWDE_PT_tile_builder,
    )

    classes = (
        OWDE_PG_settings,
        OWDE_OT_create_tile,
        OWDE_PT_tile_builder,
    )

    for class_ in classes:
        bpy.utils.register_class(class_)

    bpy.types.Scene.owde_settings = bpy.props.PointerProperty(
        type=OWDE_PG_settings
    )


def unregister() -> None:
    import bpy

    from .blender import (
        OWDE_OT_create_tile,
        OWDE_PG_settings,
        OWDE_PT_tile_builder,
    )

    if hasattr(bpy.types.Scene, "owde_settings"):
        del bpy.types.Scene.owde_settings

    classes = (
        OWDE_PG_settings,
        OWDE_OT_create_tile,
        OWDE_PT_tile_builder,
    )

    for class_ in reversed(classes):
        bpy.utils.unregister_class(class_)


if __name__ == "__main__":
    register()
