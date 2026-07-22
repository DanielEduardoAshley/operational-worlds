from dataclasses import dataclass
@dataclass
class Tile:
    width: float=6.0
    height: float=6.0
    thickness: float=0.5
    corner_radius: float=0.15
