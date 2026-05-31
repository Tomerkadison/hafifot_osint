"""
Tiny helper to build paired Exercises / Solutions notebooks from a single
list of (question, solution) items.

Each chapter file defines:
    TITLE      - str
    INTRO_MD   - markdown shown at the top of both notebooks
    ITEMS      - list of dicts: {"md": <question markdown>, "sol": <solution code str>}

We then:
    * build Solutions.ipynb (question markdown + solution code) and EXECUTE it
      with nbclient so the real Polars output is embedded in the file
    * build Exercises.ipynb (question markdown + an empty code cell)

Questions are written bilingual: an English instruction (the format the
students already know from the pandas course) followed by a short Hebrew line,
because their English is limited.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def _kernel_meta() -> dict:
    return {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }


def build(chapter_dir: Path, title: str, intro_md: str, items: list[dict]) -> None:
    chapter_dir = Path(chapter_dir)

    header = f"# {title}\n\n{intro_md}"

    # ---- Solutions notebook (executed) ----
    sol_cells = [new_markdown_cell(header + "\n\n---\n\n> **גרסת פתרונות** — נסו קודם לבד מתוך `Exercises.ipynb`.")]
    for i, item in enumerate(items, start=1):
        sol_cells.append(new_markdown_cell(f"### {i}. {item['md']}"))
        sol_cells.append(new_code_cell(item["sol"]))
    sol_nb = new_notebook(cells=sol_cells, metadata=_kernel_meta())

    client = NotebookClient(
        sol_nb,
        timeout=120,
        resources={"metadata": {"path": str(chapter_dir)}},
    )
    client.execute()
    nbformat.write(sol_nb, chapter_dir / "Solutions.ipynb")

    # ---- Exercises notebook (empty answer cells) ----
    ex_cells = [new_markdown_cell(header)]
    for i, item in enumerate(items, start=1):
        ex_cells.append(new_markdown_cell(f"### {i}. {item['md']}"))
        ex_cells.append(new_code_cell(""))
    ex_nb = new_notebook(cells=ex_cells, metadata=_kernel_meta())
    nbformat.write(ex_nb, chapter_dir / "Exercises.ipynb")

    print(f"  built Exercises.ipynb + Solutions.ipynb in {chapter_dir.name} "
          f"({len(items)} questions)")
