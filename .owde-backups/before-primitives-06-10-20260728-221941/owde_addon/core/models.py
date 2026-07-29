from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ShapeType(str, Enum):
    CIRCLE = "CIRCLE"
    TRIANGLE = "TRIANGLE"
    SQUARE = "SQUARE"
    HEXAGON = "HEXAGON"


@dataclass(frozen=True, slots=True)
class TileParameters:
    """Tool-independent parameters for one operational tile.

    All dimensions are expressed in millimeters.
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

        if self.shape_width_mm > min(
            self.tile_width_mm,
            self.tile_depth_mm,
        ):
            raise ValueError("The raised shape must fit within the tile.")

        if self.bevel_mm < 0:
            raise ValueError("bevel_mm cannot be negative.")

        if self.circle_segments < 24:
            raise ValueError("circle_segments must be at least 24.")
