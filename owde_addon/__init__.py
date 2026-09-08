bl_info = {
    "name": "Operational Worlds Design Engine",
    "author": "Operational Worlds Research Program",
    "version": (0, 7, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Operational Worlds",
    "description": "Create, inspect, render, and export parametric Operational Worlds primitives",
    "category": "Add Mesh",
}


def _base_classes():
    from .blender import (
        OWDE_OT_create_primitive_gallery,
        OWDE_OT_create_showcase,
        OWDE_OT_create_tile,
        OWDE_OT_frame_primitive_gallery,
        OWDE_PG_settings,
        OWDE_PT_primitive_inspector,
        OWDE_PT_showcase,
        OWDE_PT_tile_builder,
    )

    return (
        OWDE_PG_settings,
        OWDE_OT_create_tile,
        OWDE_OT_create_primitive_gallery,
        OWDE_OT_frame_primitive_gallery,
        OWDE_OT_create_showcase,
        OWDE_PT_tile_builder,
        OWDE_PT_primitive_inspector,
        OWDE_PT_showcase,
    )


def register() -> None:
    import bpy

    from .blender.competition import register_competition

    base_classes = _base_classes()

    for class_ in base_classes:
        bpy.utils.register_class(class_)

    bpy.types.Scene.owde_settings = bpy.props.PointerProperty(
        type=base_classes[0],
    )

    register_competition()


def unregister() -> None:
    import bpy

    from .blender.competition import unregister_competition

    unregister_competition()

    if hasattr(bpy.types.Scene, "owde_settings"):
        del bpy.types.Scene.owde_settings

    for class_ in reversed(_base_classes()):
        bpy.utils.unregister_class(class_)


if __name__ == "__main__":
    register()
