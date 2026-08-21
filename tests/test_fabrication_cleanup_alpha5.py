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


def test_cleanup_function_exists() -> None:
    text = source()

    assert "def cleanup_fabrication_mesh(" in text


def test_cleanup_merges_duplicate_vertices() -> None:
    text = source()

    assert "remove_doubles" in text


def test_cleanup_dissolves_degenerate_geometry() -> None:
    text = source()

    assert "dissolve_degenerate" in text


def test_cleanup_recalculates_normals() -> None:
    text = source()

    assert "recalc_face_normals" in text


def test_cleanup_removes_loose_geometry() -> None:
    text = source()

    assert "loose_edges" in text
    assert "loose_vertices" in text


def test_aperture_does_not_receive_union_overlap() -> None:
    text = source()

    block = text.split(
        "if primitive.shape not in {",
        1,
    )[1].split(
        "}:",
        1,
    )[0]

    assert "ShapeType.APERTURE" in block


def test_degenerate_faces_are_validated() -> None:
    text = source()

    assert "degenerate_face_count" in text
    assert "degenerate faces" in text


def test_cleanup_occurs_before_export() -> None:
    text = source()

    union_index = text.index(
        'apply_boolean(\n            base,\n            feature,\n            "UNION",'
    )

    cleanup_index = text.index(
        "cleanup_fabrication_mesh(",
        union_index,
    )

    export_index = text.index(
        "export_stl(",
        cleanup_index,
    )

    assert union_index < cleanup_index < export_index
