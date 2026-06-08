"""
Master build for the Spark course.

    1. (re)generate the data            -> python generate_data.py
    2. build + execute every chapter    -> chNN_content.build_all()
    3. zip each chapter for download     -> <chapter>/download.zip

Run with the Spark venv python and JAVA_HOME set, e.g.:

    export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
    .venv-spark/bin/python build_all.py
"""

from __future__ import annotations

import importlib
import zipfile
from pathlib import Path

import generate_data

COURSE_ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = [f"ch{n:02d}_content" for n in range(1, 10)]


def build_zip(chapter_dir: Path) -> None:
    """Bundle Exercises + Solutions + data/ into chapter<NN>.zip.

    Named by chapter number (not download.zip) so the browser saves it with a
    meaningful filename straight from the URL, regardless of the download
    attribute or Content-Disposition quirks.
    """
    num = chapter_dir.name.split("_", 1)[0]   # "03_Spark_SQL" -> "03"
    zip_path = chapter_dir / f"chapter{num}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("Exercises.ipynb", "Solutions.ipynb"):
            f = chapter_dir / name
            if f.exists():
                z.write(f, f.name)
        data_dir = chapter_dir / "data"
        if data_dir.exists():
            for f in sorted(data_dir.rglob("*")):
                if f.is_file():
                    z.write(f, str(f.relative_to(chapter_dir)))
    print(f"  zipped {zip_path.relative_to(COURSE_ROOT)}")


def main() -> None:
    print("== 1. generating data ==")
    generate_data.main()

    print("\n== 2. building chapters ==")
    for mod_name in CHAPTERS:
        mod = importlib.import_module(mod_name)
        mod.build_all()

    print("\n== 3. zipping chapters ==")
    for mod_name in CHAPTERS:
        mod = importlib.import_module(mod_name)
        build_zip(mod.CHAPTER_DIR)

    print("\ndone.")


if __name__ == "__main__":
    main()
