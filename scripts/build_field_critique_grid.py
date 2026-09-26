"""
OWDE Field Architecture critique grid.

Input:
    exports/field_architectures/regular/

Output:
    exports/critique/
        OWDE_Field_Architectures_Seven_Grid.png
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit(
        "Pillow is required. Install with:\n"
        "python3 -m pip install pillow"
    )


ROOT = Path("exports/field_architectures/regular")
OUTPUT_DIR = Path("exports/critique")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_DIR / "OWDE_Field_Architectures_Seven_Grid.png"


FIELDS = [
    (
        "FIELD-0001_Division_REGULAR.png",
        "DIVISION",
    ),
    (
        "FIELD-0002_Intersection_REGULAR.png",
        "INTERSECTION",
    ),
    (
        "FIELD-0003_Bottleneck_REGULAR.png",
        "BOTTLENECK",
    ),
    (
        "FIELD-0004_Divergence_REGULAR.png",
        "DIVERGENCE",
    ),
    (
        "FIELD-0005_Nested_Zones_REGULAR.png",
        "NESTED ZONES",
    ),
    (
        "FIELD-0006_Offset_Zones_REGULAR.png",
        "OFFSET ZONES",
    ),
    (
        "FIELD-0007_Terminal_Target_REGULAR.png",
        "TERMINAL / TARGET",
    ),
]


CANVAS_WIDTH = 3840
CANVAS_HEIGHT = 2160

BACKGROUND = (238, 238, 235)

IMAGE_WIDTH = 680
IMAGE_HEIGHT = 850

COL_GAP = 90
ROW_GAP = 150
LABEL_GAP = 28

TOP_Y = 115
BOTTOM_Y = 115 + IMAGE_HEIGHT + ROW_GAP


def load_font(size):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    for candidate in candidates:
        path = Path(candidate)

        if path.exists():
            try:
                return ImageFont.truetype(
                    str(path),
                    size=size,
                )
            except Exception:
                pass

    return ImageFont.load_default()


font = load_font(32)

canvas = Image.new(
    "RGB",
    (CANVAS_WIDTH, CANVAS_HEIGHT),
    BACKGROUND,
)

draw = ImageDraw.Draw(canvas)


def fit_image(path):
    image = Image.open(path).convert("RGB")

    image.thumbnail(
        (IMAGE_WIDTH, IMAGE_HEIGHT),
        Image.Resampling.LANCZOS,
    )

    return image


def centered_label(text, center_x, top_y):
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font,
    )

    width = bbox[2] - bbox[0]

    draw.text(
        (
            center_x - width / 2,
            top_y,
        ),
        text,
        fill=(30, 30, 28),
        font=font,
    )


def place_row(items, y):
    count = len(items)

    total_width = (
        count * IMAGE_WIDTH
        + (count - 1) * COL_GAP
    )

    start_x = (
        CANVAS_WIDTH - total_width
    ) / 2

    for index, (filename, label) in enumerate(items):
        path = ROOT / filename

        if not path.exists():
            raise SystemExit(
                f"Missing export: {path}"
            )

        image = fit_image(path)

        x = (
            start_x
            + index * (IMAGE_WIDTH + COL_GAP)
        )

        image_x = int(
            x + (IMAGE_WIDTH - image.width) / 2
        )

        image_y = int(
            y + (IMAGE_HEIGHT - image.height) / 2
        )

        canvas.paste(
            image,
            (image_x, image_y),
        )

        centered_label(
            label,
            x + IMAGE_WIDTH / 2,
            y + IMAGE_HEIGHT + LABEL_GAP,
        )


place_row(
    FIELDS[:4],
    TOP_Y,
)

place_row(
    FIELDS[4:],
    BOTTOM_Y,
)

canvas.save(
    OUTPUT,
    format="PNG",
    optimize=True,
)

print()
print("OWDE critique grid created:")
print(f"  {OUTPUT}")
print()
print(
    f"  {CANVAS_WIDTH} x {CANVAS_HEIGHT}"
)
