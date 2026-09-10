from __future__ import annotations

import math

import bmesh
import bpy

MM_TO_METERS = 0.001


def _normalize_2d(x: float, y: float) -> tuple[float, float]:
    length = math.hypot(x, y)

    if length <= 1e-12:
        return (0.0, 0.0)

    return (x / length, y / length)


def _smooth_edge_noise(
    x_mm: float,
    y_mm: float,
    scale_mm: float,
    seed: int,
) -> float:
    scale = max(scale_mm, 1.0)
    phase_a = 0.173 * seed + 0.41
    phase_b = 0.317 * seed + 1.23
    phase_c = 0.587 * seed + 2.11

    a = math.sin((x_mm / scale) * 2.10 + phase_a)
    b = math.sin((y_mm / scale) * 1.55 + phase_b)
    c = math.sin(((x_mm + y_mm) / scale) * 1.25 + phase_c)

    return 0.55 * a + 0.30 * b + 0.15 * c


def apply_subtle_hand_edge_character(
    object_: bpy.types.Object,
    *,
    field_top_z_mm: float = 0.0,
    amplitude_mm: float = 0.9,
    scale_mm: float = 42.0,
    seed: int = 11,
) -> None:
    """Apply deterministic, subtle XY variation to raised linework edges."""

    if object_ is None or object_.type != "MESH":
        return

    mesh = object_.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    field_top_z_m = field_top_z_mm * MM_TO_METERS
    tolerance = 1e-6
    architecture_faces = {
        face
        for face in bm.faces
        if any(vertex.co.z > field_top_z_m + tolerance for vertex in face.verts)
    }

    if not architecture_faces:
        bm.free()
        return

    boundary_edges = []

    for edge in bm.edges:
        linked_arch_faces = [
            face
            for face in edge.link_faces
            if face in architecture_faces
        ]

        if len(linked_arch_faces) == 1:
            x0, y0 = edge.verts[0].co.x, edge.verts[0].co.y
            x1, y1 = edge.verts[1].co.x, edge.verts[1].co.y

            if math.hypot(x1 - x0, y1 - y0) > 1e-9:
                boundary_edges.append(edge)

    if not boundary_edges:
        bm.free()
        return

    boundary_vertices = {
        vertex
        for edge in boundary_edges
        for vertex in edge.verts
    }
    cx = sum(vertex.co.x for vertex in boundary_vertices) / len(boundary_vertices)
    cy = sum(vertex.co.y for vertex in boundary_vertices) / len(boundary_vertices)
    edge_map: dict[int, list[bmesh.types.BMEdge]] = {}

    for edge in boundary_edges:
        for vertex in edge.verts:
            edge_map.setdefault(vertex.index, []).append(edge)

    for vertex in boundary_vertices:
        incident_edges = edge_map.get(vertex.index, [])
        outward_x = 0.0
        outward_y = 0.0

        for edge in incident_edges:
            other = edge.verts[0] if edge.verts[1] is vertex else edge.verts[1]
            dx = other.co.x - vertex.co.x
            dy = other.co.y - vertex.co.y
            tx, ty = _normalize_2d(dx, dy)

            if tx == 0.0 and ty == 0.0:
                continue

            n1 = (-ty, tx)
            n2 = (ty, -tx)
            rx = vertex.co.x - cx
            ry = vertex.co.y - cy
            dot1 = rx * n1[0] + ry * n1[1]
            dot2 = rx * n2[0] + ry * n2[1]
            nx, ny = n1 if dot1 >= dot2 else n2

            outward_x += nx
            outward_y += ny

        outward_x, outward_y = _normalize_2d(outward_x, outward_y)

        if outward_x == 0.0 and outward_y == 0.0:
            outward_x, outward_y = _normalize_2d(
                vertex.co.x - cx,
                vertex.co.y - cy,
            )

        if outward_x == 0.0 and outward_y == 0.0:
            continue

        x_mm = vertex.co.x / MM_TO_METERS
        y_mm = vertex.co.y / MM_TO_METERS
        offset_mm = amplitude_mm * _smooth_edge_noise(
            x_mm=x_mm,
            y_mm=y_mm,
            scale_mm=scale_mm,
            seed=seed,
        )

        vertex.co.x += outward_x * offset_mm * MM_TO_METERS
        vertex.co.y += outward_y * offset_mm * MM_TO_METERS

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
