from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SHOWCASE_PATH = (
    ROOT
    / "owde_addon"
    / "blender"
    / "showcase.py"
)


def test_showcase_has_canonical_shading_function() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "def apply_canonical_shading(" in source


def test_shading_classifies_feature_by_tile_height() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "tile_height_m" in source
    assert "belongs_to_feature" in source


def test_base_is_not_smoothed_unconditionally() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "for polygon in object_.data.polygons:\n"
        "                    polygon.use_smooth = True"
        not in source
    )


def test_weight_is_not_in_curved_feature_shapes() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    function = source.split(
        "def apply_canonical_shading(",
        1,
    )[1].split(
        "\ndef ",
        1,
    )[0]

    assert "ShapeType.WEIGHT" not in function
