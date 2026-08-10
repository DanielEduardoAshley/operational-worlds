from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "export_canonical_quote_package.py"
)


def source() -> str:
    return SCRIPT.read_text(
        encoding="utf-8"
    )


def test_quote_export_script_exists() -> None:
    assert SCRIPT.exists()


def test_all_five_canonical_primitives_are_included() -> None:
    text = source()

    for primitive_id in (
        "PRIM-0009",
        "PRIM-0010",
        "PRIM-0011",
        "PRIM-0012",
        "PRIM-0014",
    ):
        assert primitive_id in text


def test_both_exact_sizes_are_included() -> None:
    text = source()

    assert "152.4" in text
    assert "304.8" in text


def test_component_exports_are_included() -> None:
    text = source()

    assert "assembled_stl" in text
    assert "base_stl" in text
    assert "feature_stl" in text


def test_quote_documents_are_included() -> None:
    text = source()

    assert "RFQ_EMAIL.txt" in text
    assert "MANUFACTURING_SPECIFICATION.md" in text
    assert "DFM_RESPONSE_CHECKLIST.md" in text


def test_stl_unit_warning_is_included() -> None:
    text = source()

    assert "Import all STL files as millimeters" in text


def test_visual_reference_renders_are_included() -> None:
    text = source()

    assert "_isometric.png" in text
    assert "_top.png" in text
