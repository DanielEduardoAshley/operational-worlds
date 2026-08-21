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


def test_exporter_exists() -> None:
    assert SCRIPT.exists()


def test_expected_batch_is_present() -> None:
    text = source()

    for value in (
        "ShapeType.CIRCLE",
        "ShapeType.TRIANGLE",
        "ShapeType.HEXAGON",
        "ShapeType.HINGE",
        "ShapeType.FOLD",
        "ShapeType.APERTURE",
        "ShapeType.THRESHOLD",
        "ShapeType.HANDLE",
    ):
        assert value in text


def test_exporter_boolean_unifies_geometry() -> None:
    text = source()

    assert '"UNION"' in text
    assert "FABRICATION_OVERLAP_MM" in text


def test_aperture_is_physically_cut() -> None:
    text = source()

    assert '"DIFFERENCE"' in text
    assert "create_aperture_cutter" in text


def test_manifold_check_exists() -> None:
    text = source()

    assert "validate_manifold" in text
    assert "is_manifold" in text
