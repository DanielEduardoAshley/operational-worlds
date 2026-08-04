from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
ADDON_DIRECTORY = ROOT / "owde_addon"
OUTPUT_DIRECTORY = ROOT / "dist"
OUTPUT_FILE = OUTPUT_DIRECTORY / "owde-0.2.0-alpha.1.zip"


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    with ZipFile(
        OUTPUT_FILE,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for path in ADDON_DIRECTORY.rglob("*"):
            if not path.is_file():
                continue

            if "__pycache__" in path.parts:
                continue

            archive_name = Path("owde_addon") / path.relative_to(
                ADDON_DIRECTORY
            )

            archive.write(path, archive_name)

    print(f"Built {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
