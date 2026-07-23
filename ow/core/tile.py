from dataclasses import dataclass

@dataclass(slots=True)
class Tile:
    width: float = 6.0
    height: float = 6.0
    thickness: float = 0.5
    corner_radius: float = 0.15

    def validate(self):
        assert self.width>0
        assert self.height>0
        assert self.thickness>0
        assert self.corner_radius>=0

    @property
    def size(self):
        return (self.width,self.height)
