from __future__ import annotations

import bpy

from ..core.models import ShapeType


SPECIAL_FEATURE_SHAPES = {
    ShapeType.LENS,
    ShapeType.MIRROR,
    ShapeType.LIGHT_SOURCE,
    ShapeType.WEIGHT,
    ShapeType.SENSOR,
}


def _principled(
    material: bpy.types.Material,
):
    if not material.use_nodes:
        material.use_nodes = True

    return material.node_tree.nodes.get(
        "Principled BSDF"
    )


def _input(
    node,
    *names: str,
):
    if node is None:
        return None

    for name in names:
        value = node.inputs.get(name)

        if value is not None:
            return value

    return None


def _set_input(
    node,
    names: tuple[str, ...],
    value,
) -> None:
    input_ = _input(node, *names)

    if input_ is not None:
        input_.default_value = value


def get_or_create_tile_material() -> bpy.types.Material:
    name = "OWDE Tile"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.72, 0.69, 0.64, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.0,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.58,
    )

    return material


def get_or_create_dark_insert_material() -> bpy.types.Material:
    name = "OWDE Dark Insert"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.004, 0.005, 0.007, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.04,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.68,
    )

    return material


def get_or_create_clear_lens_material() -> bpy.types.Material:
    name = "OWDE Clear Lens"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True
    material.diffuse_color = (
        0.88,
        0.96,
        1.0,
        0.38,
    )

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.92, 0.98, 1.0, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.0,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.055,
    )
    _set_input(
        principled,
        ("Transmission Weight", "Transmission"),
        0.96,
    )
    _set_input(
        principled,
        ("IOR",),
        1.45,
    )
    _set_input(
        principled,
        ("Coat Weight", "Clearcoat"),
        0.28,
    )

    return material


def get_or_create_frosted_light_material() -> bpy.types.Material:
    name = "OWDE Frosted Light"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True
    material.diffuse_color = (
        1.0,
        0.76,
        0.42,
        1.0,
    )

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (1.0, 0.83, 0.58, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.0,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.31,
    )
    _set_input(
        principled,
        ("Transmission Weight", "Transmission"),
        0.16,
    )
    _set_input(
        principled,
        ("Emission Color", "Emission"),
        (1.0, 0.34, 0.055, 1.0),
    )
    _set_input(
        principled,
        ("Emission Strength",),
        3.5,
    )

    return material


def get_or_create_brushed_steel_material() -> bpy.types.Material:
    name = "OWDE Brushed Steel"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.26, 0.28, 0.30, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.94,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.24,
    )
    _set_input(
        principled,
        ("Anisotropic IOR Level", "Anisotropic"),
        0.42,
    )
    _set_input(
        principled,
        ("Coat Weight", "Clearcoat"),
        0.12,
    )

    return material


def get_or_create_sensor_material() -> bpy.types.Material:
    name = "OWDE Piano Black Sensor"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.002, 0.003, 0.005, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        0.08,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.045,
    )
    _set_input(
        principled,
        ("Coat Weight", "Clearcoat"),
        0.82,
    )
    _set_input(
        principled,
        ("Coat Roughness", "Clearcoat Roughness"),
        0.025,
    )

    return material


def get_or_create_mirror_material() -> bpy.types.Material:
    name = "OWDE Mirror Chrome"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = _principled(material)

    _set_input(
        principled,
        ("Base Color",),
        (0.86, 0.88, 0.91, 1.0),
    )
    _set_input(
        principled,
        ("Metallic",),
        1.0,
    )
    _set_input(
        principled,
        ("Roughness",),
        0.025,
    )

    return material


def feature_material_for_shape(
    shape: ShapeType,
) -> bpy.types.Material:
    if shape is ShapeType.LENS:
        return get_or_create_clear_lens_material()

    if shape is ShapeType.MIRROR:
        return get_or_create_mirror_material()

    if shape is ShapeType.LIGHT_SOURCE:
        return get_or_create_frosted_light_material()

    if shape is ShapeType.WEIGHT:
        return get_or_create_brushed_steel_material()

    if shape is ShapeType.SENSOR:
        return get_or_create_sensor_material()

    return get_or_create_tile_material()


def assign_canonical_materials(
    object_: bpy.types.Object,
    shape: ShapeType,
    tile_height_mm: float,
) -> None:
    """Assign tile and feature materials within one combined mesh.

    OWDE core geometry combines separate closed shells into one MeshData.
    The base occupies Z=0 through tile_height_mm. A polygon belongs to
    the special feature when it includes at least one vertex above that
    height.

    This leaves the base tile off-white while assigning glass, chrome,
    emissive, metal, or piano-black material only to raised geometry.
    """

    mesh = object_.data
    mesh.materials.clear()

    tile_material = get_or_create_tile_material()
    mesh.materials.append(tile_material)

    if shape not in SPECIAL_FEATURE_SHAPES:
        for polygon in mesh.polygons:
            polygon.material_index = 0

        return

    feature_material = feature_material_for_shape(shape)
    mesh.materials.append(feature_material)

    tile_height_m = tile_height_mm * 0.001
    epsilon = 0.000001

    for polygon in mesh.polygons:
        vertex_heights = [
            mesh.vertices[index].co.z
            for index in polygon.vertices
        ]

        is_feature = any(
            height > tile_height_m + epsilon
            for height in vertex_heights
        )

        polygon.material_index = (
            1 if is_feature else 0
        )


def assign_shape_material(
    object_: bpy.types.Object,
    shape: ShapeType,
) -> None:
    """Compatibility wrapper for older callers.

    Showcase code should use assign_canonical_materials so the base and
    feature receive different materials.
    """

    material = feature_material_for_shape(shape)

    object_.data.materials.clear()
    object_.data.materials.append(material)
