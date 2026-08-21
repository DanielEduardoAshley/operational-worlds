from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "export_fabrication_batch_02.py"
)


def source() -> str:
    return SCRIPT.read_text(
        encoding="utf-8"
    )


def test_exporter_reimports_stl() -> None:
    text = source()

    assert "validate_exported_stl" in text
    assert "import_stl" in text


def test_exporter_checks_connected_components() -> None:
    text = source()

    assert "component_count" in text
    assert "connected components" in text


def test_exporter_checks_non_manifold_edges() -> None:
    text = source()

    assert "non_manifold_edges" in text
    assert "is_manifold" in text


def test_exporter_checks_footprint() -> None:
    text = source()

    assert "expected_width_mm" in text
    assert "expected_depth_mm" in text
    assert "FOOTPRINT_TOLERANCE_MM" in text


def test_zip_is_blocked_on_failure() -> None:
    text = source()

    assert "No printer ZIP was created." in text
    assert "if failures:" in text


def test_base_height_is_explicitly_configurable() -> None:
    text = source()

    assert "--base-height-mm" in text
