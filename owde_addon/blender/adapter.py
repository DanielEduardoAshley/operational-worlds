from __future__ import annotations

import bpy

from ..core.mesh import MeshData


MM_TO_METERS = 0.001


def create_blender_object(
    name: str,
    mesh_data: MeshData,
) -> bpy.types.Object:
    """Convert tool-independent OWDE mesh data into a Blender object."""

    mesh_data.validate()

    vertices = [
        (
            x * MM_TO_METERS,
            y * MM_TO_METERS,
            z * MM_TO_METERS,
        )
        for x, y, z in mesh_data.vertices
    ]

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], list(mesh_data.faces))
    mesh.update()

    object_ = bpy.data.objects.new(name, mesh)

    collection = bpy.context.collection
    collection.objects.link(object_)

    bpy.context.view_layer.objects.active = object_
    object_.select_set(True)

    return object_
