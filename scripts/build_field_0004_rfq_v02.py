#!/usr/bin/env python3

"""FIELD-0004 Divergence — RFQ Production Documents v0.2.

IMPORTANT
---------
This script DOES NOT regenerate FIELD-0004 geometry.

It consumes the approved RFQ v0.1 SVG files and derives:

    1. True ASCII DXF closed polylines
    2. Dimensioned fabrication PDFs
    3. Master RFQ PDF
    4. RFQ v0.2 ZIP

This preserves the approved SVGs as the single geometric
source of truth.
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_vendor = ROOT / ".vendor" / "reportlab"
if _vendor.is_dir():
    sys.path.insert(0, str(_vendor))

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

SOURCE_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_Fabrication_RFQ_v01"
)

OUTPUT_ROOT = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_Fabrication_RFQ_v02"
)

ZIP_PATH = (
    ROOT
    / "exports"
    / "fabrication"
    / "FIELD-0004_Divergence_Fabrication_RFQ_v02.zip"
)

INCH_MM = 25.4

RELIEF_HEIGHT_IN = 0.750
RELIEF_HEIGHT_MM = RELIEF_HEIGHT_IN * INCH_MM

STEM_SPACING_IN = 2.500
STEM_SPACING_MM = STEM_SPACING_IN * INCH_MM

BRANCH_ANGLE_DEG = 32.0


@dataclass(frozen=True)
class Panel:
    slug: str
    width_in: float
    height_in: float
    member_width_in: float

    @property
    def width_mm(self):
        return self.width_in * INCH_MM

    @property
    def height_mm(self):
        return self.height_in * INCH_MM

    @property
    def member_width_mm(self):
        return self.member_width_in * INCH_MM


PANELS = (
    Panel("16x20", 16.0, 20.0, 0.750),
    Panel("18x24", 18.0, 24.0, 0.750),
    Panel("36x36", 36.0, 36.0, 1.250),
    Panel("40x40", 40.0, 40.0, 1.250),
)


def parse_number(text: str) -> float:
    match = re.match(r"\s*([-+]?[0-9]*\.?[0-9]+)", text)
    if not match:
        raise ValueError(f"Cannot parse number from {text!r}")
    return float(match.group(1))


def parse_polygon_points(text: str):
    points = []
    for token in text.strip().split():
        x_text, y_text = token.split(",")
        points.append((float(x_text), float(y_text)))
    if len(points) < 3:
        raise ValueError("Polygon has fewer than three vertices.")
    return points


def load_svg(svg_path: Path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    width_mm = parse_number(root.attrib["width"])
    height_mm = parse_number(root.attrib["height"])

    polygons = []
    for element in root.iter():
        if element.tag.endswith("polygon"):
            points = parse_polygon_points(element.attrib["points"])
            polygons.append(points)

    if len(polygons) != 2:
        raise ValueError(
            f"{svg_path.name}: expected exactly 2 architecture polygons; "
            f"found {len(polygons)}"
        )

    return width_mm, height_mm, polygons


def dxf_pair(code, value):
    return f"{code}\n{value}\n"


def write_dxf(
    path: Path,
    *,
    width_mm: float,
    height_mm: float,
    polygons,
):
    """Write simple AutoCAD R12-compatible ASCII DXF (millimetres)."""

    chunks = []

    chunks.append(dxf_pair(0, "SECTION"))
    chunks.append(dxf_pair(2, "HEADER"))
    chunks.append(dxf_pair(9, "$INSUNITS"))
    chunks.append(dxf_pair(70, 4))
    chunks.append(dxf_pair(0, "ENDSEC"))
    chunks.append(dxf_pair(0, "SECTION"))
    chunks.append(dxf_pair(2, "ENTITIES"))

    def add_polyline(layer, points):
        chunks.append(dxf_pair(0, "POLYLINE"))
        chunks.append(dxf_pair(8, layer))
        chunks.append(dxf_pair(66, 1))
        chunks.append(dxf_pair(70, 1))

        for x, y in points:
            dxf_y = height_mm - y
            chunks.append(dxf_pair(0, "VERTEX"))
            chunks.append(dxf_pair(8, layer))
            chunks.append(dxf_pair(10, f"{x:.6f}"))
            chunks.append(dxf_pair(20, f"{dxf_y:.6f}"))
            chunks.append(dxf_pair(30, "0.0"))

        chunks.append(dxf_pair(0, "SEQEND"))

    add_polyline(
        "PANEL_OUTLINE",
        [
            (0.0, height_mm),
            (width_mm, height_mm),
            (width_mm, 0.0),
            (0.0, 0.0),
        ],
    )

    for polygon in polygons:
        add_polyline("ARCHITECTURE", polygon)

    chunks.append(dxf_pair(0, "ENDSEC"))
    chunks.append(dxf_pair(0, "EOF"))

    path.write_text("".join(chunks), encoding="ascii")


def draw_arrow(c, x1, y1, x2, y2):
    c.line(x1, y1, x2, y2)
    size = 5

    if abs(x2 - x1) > abs(y2 - y1):
        c.line(x1, y1, x1 + size, y1 + 2)
        c.line(x1, y1, x1 + size, y1 - 2)
        c.line(x2, y2, x2 - size, y2 + 2)
        c.line(x2, y2, x2 - size, y2 - 2)
    else:
        c.line(x1, y1, x1 + 2, y1 + size)
        c.line(x1, y1, x1 - 2, y1 + size)
        c.line(x2, y2, x2 + 2, y2 - size)
        c.line(x2, y2, x2 - 2, y2 - size)


def centered_text(c, x, y, text, size=8):
    c.setFont("Helvetica", size)
    c.drawCentredString(x, y, text)


def make_fabrication_pdf(path: Path, panel: Panel, polygons):
    page_w, page_h = landscape(letter)

    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))
    c.setTitle(
        f"FIELD-0004 Divergence {panel.slug} Fabrication Drawing"
    )

    c.setFont("Helvetica-Bold", 15)
    c.drawString(40, page_h - 42, "OPERATIONAL WORLDS")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, page_h - 60, "FIELD-0004 — DIVERGENCE")
    c.setFont("Helvetica", 8)
    c.drawRightString(page_w - 40, page_h - 42, "FABRICATION RFQ v0.2")
    c.drawRightString(page_w - 40, page_h - 55, "DO NOT SCALE DRAWING")
    c.drawRightString(page_w - 40, page_h - 68, "USE DIMENSIONS / VECTOR FILE")

    drawing_x = 70
    drawing_y = 100
    max_w = 330
    max_h = 390

    scale = min(max_w / panel.width_mm, max_h / panel.height_mm)
    pw = panel.width_mm * scale
    ph = panel.height_mm * scale

    c.setLineWidth(1)
    c.rect(drawing_x, drawing_y, pw, ph, stroke=1, fill=0)

    for polygon in polygons:
        p = c.beginPath()
        for i, (svg_x, svg_y) in enumerate(polygon):
            x = drawing_x + svg_x * scale
            y = drawing_y + (panel.height_mm - svg_y) * scale
            if i == 0:
                p.moveTo(x, y)
            else:
                p.lineTo(x, y)
        p.close()
        c.drawPath(p, stroke=1, fill=0)

    centered_text(
        c, drawing_x + pw / 2, drawing_y + ph + 16, "FRONT ELEVATION", 8
    )

    dim_y = drawing_y - 28
    c.line(drawing_x, drawing_y, drawing_x, dim_y + 4)
    c.line(drawing_x + pw, drawing_y, drawing_x + pw, dim_y + 4)
    draw_arrow(c, drawing_x, dim_y, drawing_x + pw, dim_y)
    centered_text(
        c,
        drawing_x + pw / 2,
        dim_y - 13,
        f"{panel.width_in:g} in ({panel.width_mm:.1f} mm)",
        8,
    )

    dim_x = drawing_x - 28
    c.line(drawing_x, drawing_y, dim_x + 4, drawing_y)
    c.line(drawing_x, drawing_y + ph, dim_x + 4, drawing_y + ph)
    draw_arrow(c, dim_x, drawing_y, dim_x, drawing_y + ph)
    c.saveState()
    c.translate(dim_x - 12, drawing_y + ph / 2)
    c.rotate(90)
    centered_text(
        c,
        0,
        0,
        f"{panel.height_in:g} in ({panel.height_mm:.1f} mm)",
        8,
    )
    c.restoreState()

    tx = 455
    ty = page_h - 105
    c.setFont("Helvetica-Bold", 11)
    c.drawString(tx, ty, "FABRICATION DIMENSIONS")
    ty -= 24

    lines = [
        ("Overall panel", f"{panel.width_in:g} × {panel.height_in:g} in"),
        (
            "Overall metric",
            f"{panel.width_mm:.1f} × {panel.height_mm:.1f} mm",
        ),
        (
            "Member width",
            f"{panel.member_width_in:.3f} in / {panel.member_width_mm:.2f} mm",
        ),
        ("Proposed relief", "0.750 in / 19.05 mm"),
        ("Stem C/L spacing", "2.500 in / 63.50 mm"),
        ("Branch angle", "32°"),
        ("Split position", "Centered vertically"),
    ]

    for label, value in lines:
        c.setFont("Helvetica-Bold", 8)
        c.drawString(tx, ty, label)
        c.setFont("Helvetica", 8)
        c.drawString(tx + 112, ty, value)
        ty -= 17

    ty -= 12
    c.setFont("Helvetica-Bold", 11)
    c.drawString(tx, ty, "RELIEF PROFILE")
    ty -= 25

    base_x = tx
    base_y = ty - 60
    panel_visual_depth = 10
    relief_visual = 45

    c.rect(base_x, base_y, 165, panel_visual_depth, stroke=1, fill=0)
    c.rect(
        base_x + 55,
        base_y + panel_visual_depth,
        55,
        relief_visual,
        stroke=1,
        fill=0,
    )
    c.line(
        base_x + 130,
        base_y + panel_visual_depth,
        base_x + 150,
        base_y + panel_visual_depth,
    )
    c.line(
        base_x + 110,
        base_y + panel_visual_depth + relief_visual,
        base_x + 150,
        base_y + panel_visual_depth + relief_visual,
    )
    draw_arrow(
        c,
        base_x + 145,
        base_y + panel_visual_depth,
        base_x + 145,
        base_y + panel_visual_depth + relief_visual,
    )
    c.setFont("Helvetica", 8)
    c.drawString(base_x + 155, base_y + 30, '0.750"')
    c.drawString(base_x, base_y - 14, "Panel/substrate construction:")
    c.drawString(base_x, base_y - 26, "fabricator recommendation requested")

    note_y = 170
    c.setFont("Helvetica-Bold", 10)
    c.drawString(tx, note_y, "FINISH / FABRICATION INTENT")
    note_y -= 17

    notes = [
        "• Field: deep dark green, smooth matte sprayed finish.",
        "• Architecture: warm/off-white, smooth matte sprayed finish.",
        "• Green field finish continues around visible exterior sides.",
        "• No exposed raw substrate on visible surfaces.",
        "• No visible fasteners or adhesive from normal frontal viewing.",
        "• Raised members to read as continuous architectural relief.",
        "• Central stem/branch transitions: no visible gap or overlap.",
        "• Concealed wall mounting preferred.",
        "• Material/construction method: fabricator recommendation requested.",
    ]
    c.setFont("Helvetica", 7.5)
    for note in notes:
        c.drawString(tx, note_y, note)
        note_y -= 12

    c.setFont("Helvetica", 6.5)
    c.drawString(
        40,
        28,
        "FIELD-0004 geometry and member width locked for RFQ. Relief height provisional.",
    )
    c.drawRightString(
        page_w - 40, 28, "All production vector dimensions in millimetres."
    )
    c.save()


def make_master_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    page_w, page_h = letter

    c.setTitle("Operational Worlds FIELD-0004 Fabrication RFQ")
    y = page_h - 55

    c.setFont("Helvetica-Bold", 17)
    c.drawString(50, y, "OPERATIONAL WORLDS")
    y -= 23
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "FIELD-0004 — DIVERGENCE")
    y -= 17
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "FABRICATION REQUEST FOR QUOTE — v0.2")
    y -= 35

    def heading(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, text)
        y -= 17

    def body(text):
        nonlocal y
        c.setFont("Helvetica", 8.5)
        for line in text.splitlines():
            c.drawString(50, y, line)
            y -= 12
        y -= 7

    heading("PROJECT")
    body(
        "Wall-mounted architectural relief consisting of a "
        "dark-green field and two raised warm-white members.\n"
        "Production vector files define the approved front-view geometry."
    )

    heading("SIZES REQUESTED")
    for panel in PANELS:
        c.setFont("Helvetica", 8.5)
        c.drawString(65, y, f"{panel.width_in:g} × {panel.height_in:g} in")
        c.drawString(180, y, f"member width {panel.member_width_in:.3f} in")
        c.drawString(340, y, "proposed relief 0.750 in")
        y -= 14
    y -= 10

    heading("PLEASE QUOTE")
    body(
        "A. Fabrication only / unfinished.\n"
        "B. Complete fabrication with professional "
        "sprayed gallery-ready finish."
    )

    heading("CONSTRUCTION")
    body(
        "Please recommend a stable construction method appropriate "
        "to each scale. Material is intentionally not locked.\n"
        "Priorities: dimensional stability, crisp geometry, clean "
        "miter transitions, reasonable weight, durability and "
        "gallery-quality presentation."
    )

    heading("FINISH")
    body(
        "Field: deep dark green, smooth matte sprayed finish.\n"
        "Architecture: warm/off-white, smooth matte sprayed finish.\n"
        "Green field finish continues around all visible exterior sides.\n"
        "No exposed raw substrate, visible fasteners or adhesive "
        "from normal viewing position."
    )

    heading("PLEASE INCLUDE")
    body(
        "• Unfinished fabrication cost for each size\n"
        "• Fully finished fabrication cost for each size\n"
        "• Proposed material and construction method\n"
        "• Estimated finished weight\n"
        "• Lead time\n"
        "• Concealed mounting recommendation\n"
        "• Shipping/delivery cost if applicable"
    )

    heading("DESIGN STATUS")
    body(
        "Front-view geometry: LOCKED FOR RFQ\n"
        "Member widths: LOCKED FOR RFQ\n"
        "Relief height: PROVISIONAL at 0.750 in / 19.05 mm\n"
        "Material/construction: FABRICATOR RECOMMENDATION REQUESTED"
    )

    c.setFont("Helvetica-Bold", 8)
    c.drawString(
        50,
        35,
        "DO NOT SCALE DRAWINGS — USE DIMENSIONS / PRODUCTION VECTOR FILES",
    )
    c.save()


def find_source_svg(panel):
    folder = SOURCE_ROOT / panel.slug
    matches = list(folder.glob("*.svg"))
    if len(matches) != 1:
        raise RuntimeError(
            f"{panel.slug}: expected exactly one source SVG, found {len(matches)}"
        )
    return matches[0]


def validate_dimensions(panel, svg_width, svg_height):
    tolerance = 0.01
    if abs(svg_width - panel.width_mm) > tolerance:
        raise ValueError(f"{panel.slug}: SVG width mismatch.")
    if abs(svg_height - panel.height_mm) > tolerance:
        raise ValueError(f"{panel.slug}: SVG height mismatch.")


def main():
    if not SOURCE_ROOT.exists():
        raise SystemExit(
            "\nRFQ v0.1 package not found:\n"
            f"{SOURCE_ROOT}\n\n"
            "Run export_field_0004_rfq_v01.py first."
        )

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    shutil.copytree(SOURCE_ROOT, OUTPUT_ROOT)

    master_pdf = OUTPUT_ROOT / "00_MASTER_RFQ.pdf"
    make_master_pdf(master_pdf)

    for panel in PANELS:
        source_svg = find_source_svg(panel)
        width_mm, height_mm, polygons = load_svg(source_svg)
        validate_dimensions(panel, width_mm, height_mm)

        output_folder = OUTPUT_ROOT / panel.slug
        prefix = f"FIELD-0004_Divergence_{panel.slug}_RFQ_v02"

        svg_out = output_folder / f"{prefix}.svg"
        shutil.copy2(source_svg, svg_out)

        dxf_out = output_folder / f"{prefix}.dxf"
        write_dxf(
            dxf_out,
            width_mm=width_mm,
            height_mm=height_mm,
            polygons=polygons,
        )

        pdf_out = output_folder / f"{prefix}_FABRICATION_DRAWING.pdf"
        make_fabrication_pdf(pdf_out, panel, polygons)

        print()
        print(panel.slug)
        print(f"  SVG source dimensions: {width_mm:.3f} x {height_mm:.3f} mm")
        print(f"  DXF: {dxf_out.relative_to(ROOT)}")
        print(f"  PDF: {pdf_out.relative_to(ROOT)}")

    readme = OUTPUT_ROOT / "README_v02.txt"
    readme.write_text(
        """OPERATIONAL WORLDS
FIELD-0004 DIVERGENCE
FABRICATION RFQ v0.2


START HERE
==========

00_MASTER_RFQ.pdf


FOR EACH SIZE
=============

SVG
Approved source geometry.

DXF
True closed production polylines.
Units: millimetres.

FABRICATION_DRAWING.pdf
Human-readable dimensional and finish drawing.

SPEC.txt
Detailed written fabrication specification.


IMPORTANT
=========

DO NOT SCALE DRAWINGS.

Use explicit dimensions and production
vector geometry.

DXF architecture geometry is derived
directly from the approved v0.1 SVG
polygons.

No independent reconstruction of the
Divergence geometry was performed.


STATUS
======

Geometry:
LOCKED FOR RFQ

Member widths:
LOCKED FOR RFQ

Relief:
PROVISIONAL 0.750 in / 19.05 mm

Material / construction:
FABRICATOR RECOMMENDATION REQUESTED
""",
        encoding="utf-8",
    )

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(
        ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for file in sorted(OUTPUT_ROOT.rglob("*")):
            if not file.is_file():
                continue
            zf.write(file, file.relative_to(OUTPUT_ROOT.parent))

    print()
    print("============================================")
    print("RFQ v0.2 COMPLETE")
    print("============================================")
    print()
    print(OUTPUT_ROOT.relative_to(ROOT))
    print()
    print(ZIP_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
