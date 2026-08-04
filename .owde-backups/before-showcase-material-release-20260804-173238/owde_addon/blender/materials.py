from __future__ import annotations

import bpy

from ..core.models import ShapeType


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
    for name in names:
        value = node.inputs.get(name)

        if value is not None:
            return value

    return None


def get_or_create_tile_material() -> bpy.types.Material:
    name = "OWDE Tile"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            0.72,
            0.69,
            0.64,
            1.0,
        )
        principled.inputs["Roughness"].default_value = 0.62

    return material


def get_or_create_clear_lens_material() -> bpy.types.Material:
    name = "OWDE Clear Lens"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            0.92,
            0.97,
            1.0,
            1.0,
        )
        principled.inputs["Roughness"].default_value = 0.08

        metallic = _input(
            principled,
            "Metallic",
        )

        if metallic is not None:
            metallic.default_value = 0.0

        transmission = _input(
            principled,
            "Transmission Weight",
            "Transmission",
        )

        if transmission is not None:
            transmission.default_value = 0.92

        ior = _input(
            principled,
            "IOR",
        )

        if ior is not None:
            ior.default_value = 1.45

    return material


def get_or_create_frosted_light_material() -> bpy.types.Material:
    name = "OWDE Frosted Light"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            1.0,
            0.82,
            0.52,
            1.0,
        )
        principled.inputs["Roughness"].default_value = 0.34

        emission = _input(
            principled,
            "Emission Color",
            "Emission",
        )

        if emission is not None:
            emission.default_value = (
                1.0,
                0.38,
                0.06,
                1.0,
            )

        strength = _input(
            principled,
            "Emission Strength",
        )

        if strength is not None:
            strength.default_value = 3.0

        transmission = _input(
            principled,
            "Transmission Weight",
            "Transmission",
        )

        if transmission is not None:
            transmission.default_value = 0.18

    return material


def get_or_create_brushed_steel_material() -> bpy.types.Material:
    name = "OWDE Brushed Steel"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            0.23,
            0.25,
            0.27,
            1.0,
        )
        principled.inputs["Metallic"].default_value = 0.92
        principled.inputs["Roughness"].default_value = 0.28

        anisotropic = _input(
            principled,
            "Anisotropic IOR Level",
            "Anisotropic",
        )

        if anisotropic is not None:
            anisotropic.default_value = 0.38

    return material


def get_or_create_sensor_material() -> bpy.types.Material:
    name = "OWDE Piano Black Sensor"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            0.004,
            0.005,
            0.007,
            1.0,
        )
        principled.inputs["Metallic"].default_value = 0.08
        principled.inputs["Roughness"].default_value = 0.06

        coat = _input(
            principled,
            "Coat Weight",
            "Clearcoat",
        )

        if coat is not None:
            coat.default_value = 0.65

    return material


def get_or_create_mirror_material() -> bpy.types.Material:
    name = "OWDE Mirror Chrome"

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True

        principled = _principled(material)

        principled.inputs["Base Color"].default_value = (
            0.82,
            0.84,
            0.87,
            1.0,
        )
        principled.inputs["Metallic"].default_value = 1.0
        principled.inputs["Roughness"].default_value = 0.035

    return material


def material_for_shape(
    shape: ShapeType,
) -> bpy.types.Material:
    if shape is ShapeType.LENS:
        return get_or_create_clear_lens_material()

    if shape is ShapeType.LIGHT_SOURCE:
        return get_or_create_frosted_light_material()

    if shape is ShapeType.WEIGHT:
        return get_or_create_brushed_steel_material()

    if shape is ShapeType.SENSOR:
        return get_or_create_sensor_material()

    if shape is ShapeType.MIRROR:
        return get_or_create_mirror_material()

    return get_or_create_tile_material()


def assign_shape_material(
    object_: bpy.types.Object,
    shape: ShapeType,
) -> None:
    material = material_for_shape(shape)

    object_.data.materials.clear()
    object_.data.materials.append(material)
