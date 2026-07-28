import pytest

from owde_addon.core import ShapeType, TileParameters


def test_default_parameters_are_valid() -> None:
    parameters = TileParameters()
    parameters.validate()


def test_shape_must_fit_on_tile() -> None:
    parameters = TileParameters(
        tile_width_mm=50.0,
        tile_depth_mm=50.0,
        shape_width_mm=60.0,
    )

    with pytest.raises(ValueError, match="fit within"):
        parameters.validate()


def test_circle_requires_minimum_resolution() -> None:
    parameters = TileParameters(
        shape=ShapeType.CIRCLE,
        circle_segments=12,
    )

    with pytest.raises(ValueError, match="at least 24"):
        parameters.validate()
