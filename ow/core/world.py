from dataclasses import dataclass, field
from .primitive import Primitive

@dataclass
class World:
    primitives:list[Primitive]=field(default_factory=list)

    def add(self,primitive:Primitive):
        self.primitives.append(primitive)

    def __len__(self):
        return len(self.primitives)
