from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MeshData:
    """Tool-independent indexed polygon mesh."""

    vertices: tuple[tuple[float, float, float], ...]
    faces: tuple[tuple[int, ...], ...]

    def validate(self) -> None:
        if not self.vertices:
            raise ValueError("Mesh must contain vertices.")

        if not self.faces:
            raise ValueError("Mesh must contain faces.")

        vertex_count = len(self.vertices)

        for face in self.faces:
            if len(face) < 3:
                raise ValueError("Every face must contain at least three vertices.")

            for index in face:
                if index < 0 or index >= vertex_count:
                    raise ValueError(f"Invalid vertex index: {index}")
