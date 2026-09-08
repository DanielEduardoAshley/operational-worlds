import pytest

from owde_addon.core.competition_builders import (
    ACTOR_DIAMETER_MM,
    ACTOR_HEIGHT_MM,
    ACTOR_SQUARE_MM,
    GATE_DEPTH_MM,
    GATE_HEIGHT_MM,
    GATE_LENGTH_MM,
    NET_DEPTH_MM,
    NET_HEIGHT_MM,
    NET_LENGTH_MM,
    build_actor_mesh,
    build_gate_mesh,
    build_net_mesh,
    mesh_bounds,
)


def test_circle_actor_defaults():
    mesh = build_actor_mesh("CIRCLE")
    assert mesh_bounds(mesh) == pytest.approx((
        ACTOR_DIAMETER_MM,
        ACTOR_DIAMETER_MM,
        ACTOR_HEIGHT_MM,
    ))


def test_square_actor_defaults():
    mesh = build_actor_mesh("SQUARE")
    assert mesh_bounds(mesh) == pytest.approx((
        ACTOR_SQUARE_MM,
        ACTOR_SQUARE_MM,
        ACTOR_HEIGHT_MM,
    ))


def test_gate_defaults():
    mesh = build_gate_mesh()
    assert mesh_bounds(mesh) == pytest.approx((
        GATE_LENGTH_MM,
        GATE_DEPTH_MM,
        GATE_HEIGHT_MM,
    ))


def test_net_defaults():
    mesh = build_net_mesh()
    assert mesh_bounds(mesh) == pytest.approx((
        NET_LENGTH_MM,
        NET_DEPTH_MM,
        NET_HEIGHT_MM,
    ))
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0


def test_net_top_view_relief_changes_y_positions():
    mesh = build_net_mesh(woven_depth=True)
    y_values = {round(v[1], 6) for v in mesh.vertices}
    assert len(y_values) > 4


def test_actor_rejects_unknown_variant():
    with pytest.raises(ValueError):
        build_actor_mesh("TRIANGLE")
