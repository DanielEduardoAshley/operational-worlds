from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SHOWCASE_PATH = (
    ROOT
    / "owde_addon"
    / "blender"
    / "showcase.py"
)

MATERIALS_PATH = (
    ROOT
    / "owde_addon"
    / "blender"
    / "materials.py"
)


def test_showcase_avoids_bpy_path_abspath() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "bpy.path.abspath" not in source


def test_showcase_has_home_directory_fallback() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "Path.home()" in source
    assert "OWDE_Showcase_Exports" in source


def test_showcase_renders_individual_primitives() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "render_individuals" in source
    assert '"individual"' in source


def test_showcase_saves_blend_copy() -> None:
    source = SHOWCASE_PATH.read_text(
        encoding="utf-8"
    )

    assert "OWDE_Showcase.blend" in source
    assert "save_as_mainfile" in source


def test_material_assignment_separates_tile_and_feature() -> None:
    source = MATERIALS_PATH.read_text(
        encoding="utf-8"
    )

    assert "assign_canonical_materials" in source
    assert "polygon.material_index" in source


def test_required_canonical_materials_exist() -> None:
    source = MATERIALS_PATH.read_text(
        encoding="utf-8"
    )

    expected_names = (
        "OWDE Tile",
        "OWDE Clear Lens",
        "OWDE Frosted Light",
        "OWDE Brushed Steel",
        "OWDE Piano Black Sensor",
        "OWDE Mirror Chrome",
        "OWDE Dark Insert",
    )

    for name in expected_names:
        assert name in source
