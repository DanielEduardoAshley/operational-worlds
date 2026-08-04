from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "export_manufacturing_package.py"
)


def test_manufacturing_export_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_manufacturing_export_covers_all_primitive_ids() -> None:
    source = SCRIPT_PATH.read_text(
        encoding="utf-8"
    )

    for index in range(1, 16):
        primitive_id = f"PRIM-{index:04d}"
        assert primitive_id in source


def test_manufacturing_export_declares_millimeters() -> None:
    source = SCRIPT_PATH.read_text(
        encoding="utf-8"
    )

    assert "millimeters" in source
    assert "STL does not encode units" in source


def test_manufacturing_export_includes_separate_components() -> None:
    source = SCRIPT_PATH.read_text(
        encoding="utf-8"
    )

    expected_components = (
        "dark_slot_insert",
        "dark_aperture_insert",
        "reflective_insert_template",
        "translucent_light_insert",
        "dark_sensor_insert",
    )

    for component in expected_components:
        assert component in source
