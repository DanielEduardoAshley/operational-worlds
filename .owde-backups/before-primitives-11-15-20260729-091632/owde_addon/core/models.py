from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ShapeType(str, Enum):
    CIRCLE = "CIRCLE"
    TRIANGLE = "TRIANGLE"
    SQUARE = "SQUARE"
    HEXAGON = "HEXAGON"
    SLOT = "SLOT"

    HINGE = "HINGE"
    FOLD = "FOLD"
    APERTURE = "APERTURE"
    LENS = "LENS"
    MIRROR = "MIRROR"


@dataclass(frozen=True, slots=True)
class TileParameters:
    """Tool-independent parameters for one operational tile.

    All dimensions are expressed in millimeters.

    For the original raised primitives:

    - shape_width_mm controls the outline width.
    - shape_height_mm controls the raised extrusion.

    For OW06-OW10 these values become general feature dimensions:

    - Hinge: barrel length and barrel diameter.
    - Fold: panel width and panel thickness.
    - Aperture: opening diameter.
    - Lens: lens diameter and rise.
    - Mirror: reflective surface width and thickness.
    """

    shape: ShapeType = ShapeType.CIRCLE

    tile_width_mm: float = 100.0
    tile_depth_mm: float = 100.0
    tile_height_mm: float = 8.0

    shape_width_mm: float = 55.0
    shape_height_mm: float = 5.0

    bevel_mm: float = 1.0
    circle_segments: int = 64

    def validate(self) -> None:
        positive_values = {
            "tile_width_mm": self.tile_width_mm,
            "tile_depth_mm": self.tile_depth_mm,
            "tile_height_mm": self.tile_height_mm,
            "shape_width_mm": self.shape_width_mm,
            "shape_height_mm": self.shape_height_mm,
        }

        for name, value in positive_values.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")

        maximum_feature_width = min(
            self.tile_width_mm,
            self.tile_depth_mm,
        )

        if self.shape_width_mm >= maximum_feature_width:
            raise ValueError(
                "The operational feature must be smaller than the tile "
                "and fit within the tile."
            )

        if self.bevel_mm < 0:
            raise ValueError("bevel_mm cannot be negative.")

        if self.circle_segments < 24:
            raise ValueError("circle_segments must be at least 24.")
