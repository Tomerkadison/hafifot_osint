"""
Build paired Exercises / Solutions notebooks for the Spark course from a single
list of items, and EXECUTE the Solutions notebook on a real local Spark so the
genuine Spark output (`df.show()` tables, counts, plans) is embedded in the file.

Each chapter file defines:
    TITLE      - str
    INTRO_MD   - markdown shown at the top of both notebooks
    ITEMS      - list of dicts:
                   {"md": <question markdown>, "sol": <solution code str>}
                 plus an optional flag:
                   "setup": True  -> the code is boilerplate (SparkSession etc.);
                                     it is pre-filled in BOTH notebooks, not left
                                     blank in Exercises.

Execution notes:
    * We run with the "sparkcourse" kernel (a venv that has pyspark + a JDK on
      PATH). After execution we rewrite the kernelspec back to generic "python3"
      so the shipped notebook is not tied to this machine.
    * Spark is extremely chatty on stderr (WARN / progress bars). We strip every
      stderr stream output after execution so the Solutions notebook stays clean;
      real results from show()/print() go to stdout and are kept.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

KERNEL = "sparkcourse"          # venv kernel used only for execution
SHIP_KERNEL = {                 # what we write into the final files
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}


def _clean_outputs(nb) -> None:
    """Drop noisy stderr streams; keep stdout, results, errors."""
    for cell in nb.cells:
        if cell.get("cell_type") != "code":
            continue
        kept = []
        for out in cell.get("outputs", []):
            if out.get("output_type") == "stream" and out.get("name") == "stderr":
                continue
            kept.append(out)
        cell["outputs"] = kept


def build(chapter_dir: Path, title: str, intro_md: str, items: list[dict]) -> None:
    chapter_dir = Path(chapter_dir)
    header = f"# {title}\n\n{intro_md}"

    # ---- Solutions notebook (executed) ----
    sol_cells = [new_markdown_cell(
        header + "\n\n---\n\n> **גרסת פתרונות** — נסו קודם לבד מתוך `Exercises.ipynb`."
    )]
    for i, item in enumerate(items, start=1):
        sol_cells.append(new_markdown_cell(f"### {i}. {item['md']}"))
        sol_cells.append(new_code_cell(item["sol"]))
    sol_nb = new_notebook(cells=sol_cells, metadata={
        "kernelspec": {"display_name": "Python (spark)", "language": "python", "name": KERNEL},
        "language_info": {"name": "python"},
    })

    client = NotebookClient(
        sol_nb,
        timeout=900,
        kernel_name=KERNEL,
        resources={"metadata": {"path": str(chapter_dir)}},
    )
    client.execute()
    _clean_outputs(sol_nb)
    sol_nb["metadata"] = SHIP_KERNEL
    nbformat.write(sol_nb, chapter_dir / "Solutions.ipynb")

    # ---- Exercises notebook (blank answers, except setup cells) ----
    ex_cells = [new_markdown_cell(header)]
    for i, item in enumerate(items, start=1):
        ex_cells.append(new_markdown_cell(f"### {i}. {item['md']}"))
        if item.get("setup"):
            ex_cells.append(new_code_cell(item["sol"]))
        else:
            ex_cells.append(new_code_cell(""))
    ex_nb = new_notebook(cells=ex_cells, metadata=SHIP_KERNEL)
    nbformat.write(ex_nb, chapter_dir / "Exercises.ipynb")

    print(f"  built Exercises.ipynb + Solutions.ipynb in {chapter_dir.name} "
          f"({len(items)} questions)")
