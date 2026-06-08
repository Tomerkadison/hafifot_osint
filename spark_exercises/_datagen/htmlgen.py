"""
Shared generator for the Hebrew RTL HTML pages (subject.html / exercise.html)
of the Spark course. Same engine as the Polars course, but a warm "Spark orange"
palette so the two courses are visually distinct.

Slide types (a page is a list of these dicts):

    {"type": "text",      "h2": str, "body": html_str}
    {"type": "compare",   "h2": str, "intro": str|None,
                           "left_title": str, "left": [html...],
                           "right_title": str, "right": [html...], "note": str|None}
    {"type": "functable", "h2": str, "intro": str|None,
                           "rows": [(desc_he, code, doc_url), ...]}
    {"type": "datatable", "h2": str, "intro": str|None,
                           "rows": [(col, dtype, desc_he), ...]}
    {"type": "steps",     "h2": str, "intro": str|None, "items": [html...]}
    {"type": "list",      "h2": str, "intro": str|None, "items": [html...], "ordered": bool}
    {"type": "tip",       "text": str}
    {"type": "warn",      "text": str}
    {"type": "cta",       "h2": str, "body": html_str, "pills": [(label, url), ...]}

IMPORTANT: never mix Hebrew and Latin letters inside a single word. Keep
technical terms (DataFrame, shuffle, join, Window) in clean Latin.
"""

from __future__ import annotations

from pathlib import Path

CSS = """
  :root{
    --bg:#0f0a06; --card:#1c1510; --ink:#fff7ee; --muted:#d3bda6;
    --brand:#e8590c; --brand2:#f59e0b; --accent:#22d3ee; --line:#3a2c1d;
    --code-bg:#120d08; --green:#34d399; --red:#f76b6b;
  }
  *{box-sizing:border-box}
  body{margin:0; background:radial-gradient(1200px 600px at 80% -10%,#3a2410 0,var(--bg) 55%);
    color:var(--ink); font-family:"Heebo",-apple-system,"Segoe UI",Arial,sans-serif;
    line-height:1.75; padding:0 0 80px}
  .wrap{max-width:900px; margin:0 auto; padding:0 22px}
  header.hero{padding:60px 22px 44px; text-align:center; border-bottom:1px solid var(--line)}
  .kicker{font-weight:600; letter-spacing:.06em; font-size:.95rem}
  h1{font-size:2.4rem; font-weight:800; margin:.2em 0 .15em; line-height:1.2}
  .hero p{color:var(--muted); font-size:1.13rem; max-width:660px; margin:.4em auto 0}
  .slide{background:var(--card); border:1px solid var(--line); border-radius:18px;
    padding:28px 32px; margin:24px 0; box-shadow:0 20px 50px -30px #000}
  .slide h2{font-size:1.55rem; margin:0 0 .5em; display:flex; align-items:center; gap:.5em}
  .slide h2 .num{background:linear-gradient(135deg,var(--brand),var(--brand2)); color:#1a0e02;
    width:1.7em; height:1.7em; border-radius:12px; display:grid; place-items:center;
    font-size:.95rem; font-weight:800; flex:0 0 auto}
  .slide h3{color:var(--brand2); font-size:1.1rem; margin:1.3em 0 .3em}
  p,li{color:#f0e6d8}
  .muted{color:var(--muted)}
  ul,ol{margin:.4em 0; padding-inline-start:1.3em}
  li{margin:.35em 0}
  code{background:var(--code-bg); border:1px solid var(--line); padding:.12em .45em;
    border-radius:7px; font-family:"SFMono-Regular",Consolas,monospace; color:#ffce9e;
    direction:ltr; display:inline-block; font-size:.9em}
  .cmp{display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:10px}
  .cmp>div{border:1px solid var(--line); border-radius:12px; padding:14px 16px}
  .cmp .bad{background:rgba(247,107,107,.06)}
  .cmp .good{background:rgba(232,89,12,.10)}
  .cmp h4{margin:0 0 .4em; font-size:1rem}
  table{width:100%; border-collapse:collapse; margin-top:10px; font-size:.95rem}
  th,td{border:1px solid var(--line); padding:10px 12px; text-align:right; vertical-align:top}
  th{background:#2a1f14; color:var(--brand2); font-weight:600}
  td code{font-size:.85em}
  a{color:var(--brand2); text-decoration:none; font-weight:600}
  a:hover{text-decoration:underline}
  .doc-link{display:inline-block; direction:ltr}
  .tag{display:inline-block; font-size:.78rem; padding:.1em .6em; border-radius:999px;
    border:1px solid var(--line); background:#2a1f14; color:var(--muted); direction:ltr}
  .tip{border-right:4px solid var(--green); background:rgba(52,211,153,.07);
    padding:12px 16px; border-radius:0 12px 12px 0; margin:14px 0}
  .warn{border-right:4px solid var(--brand2); background:rgba(245,158,11,.10);
    padding:12px 16px; border-radius:0 12px 12px 0; margin:14px 0}
  .steps{counter-reset:s; list-style:none; padding:0}
  .steps li{counter-increment:s; position:relative; padding-right:2.4em; margin:.5em 0}
  .steps li::before{content:counter(s); position:absolute; right:0; top:.05em;
    width:1.6em; height:1.6em; border-radius:8px; display:grid; place-items:center;
    background:linear-gradient(135deg,var(--brand),var(--brand2)); color:#1a0e02;
    font-weight:800; font-size:.85rem}
  .cta{background:linear-gradient(135deg,rgba(232,89,12,.16),rgba(245,158,11,.10));
    border:1px solid var(--brand); border-radius:18px; padding:26px 30px; margin-top:30px}
  .cta h2{color:var(--brand2)}
  .pill{display:inline-block; background:#2a1f14; border:1px solid var(--line);
    border-radius:999px; padding:.25em .9em; margin:.2em; font-size:.9rem; direction:ltr}
  @media(max-width:640px){.cmp{grid-template-columns:1fr} h1{font-size:1.85rem}}
"""


def _slide(inner: str, cls: str = "slide") -> str:
    return f'  <section class="{cls}">\n{inner}\n  </section>'


def _render_slide(s: dict, idx: int) -> str:
    t = s["type"]
    num = f'<span class="num">{idx}</span>' if t not in ("tip", "warn", "cta") else ""

    if t == "text":
        return _slide(f'    <h2>{num}{s["h2"]}</h2>\n    {s["body"]}')

    if t == "list":
        tag = "ol" if s.get("ordered") else "ul"
        items = "\n".join(f"      <li>{it}</li>" for it in s["items"])
        intro = f'    <p class="muted">{s["intro"]}</p>\n' if s.get("intro") else ""
        return _slide(f'    <h2>{num}{s["h2"]}</h2>\n{intro}    <{tag}>\n{items}\n    </{tag}>')

    if t == "steps":
        items = "\n".join(f"      <li>{it}</li>" for it in s["items"])
        intro = f'    <p class="muted">{s["intro"]}</p>\n' if s.get("intro") else ""
        return _slide(f'    <h2>{num}{s["h2"]}</h2>\n{intro}    <ol class="steps">\n{items}\n    </ol>')

    if t == "compare":
        intro = f'    <p class="muted">{s["intro"]}</p>\n' if s.get("intro") else ""
        left = "\n".join(f"          <li>{x}</li>" for x in s["left"])
        right = "\n".join(f"          <li>{x}</li>" for x in s["right"])
        note = f'    <div class="tip">{s["note"]}</div>\n' if s.get("note") else ""
        body = (
            f'    <h2>{num}{s["h2"]}</h2>\n{intro}'
            f'    <div class="cmp">\n'
            f'      <div class="bad"><h4>{s["left_title"]}</h4>\n        <ul>\n{left}\n        </ul>\n      </div>\n'
            f'      <div class="good"><h4>{s["right_title"]}</h4>\n        <ul>\n{right}\n        </ul>\n      </div>\n'
            f'    </div>\n{note}'
        )
        return _slide(body.rstrip("\n"))

    if t == "functable":
        intro = f'    <p class="muted">{s["intro"]}</p>\n' if s.get("intro") else ""
        rows = "\n".join(
            f'        <tr><td>{d}</td><td><code>{c}</code></td>'
            f'<td><a class="doc-link" href="{u}" target="_blank">{c.split("(")[0].split(".")[-1] or c} ↗</a></td></tr>'
            for d, c, u in s["rows"]
        )
        body = (
            f'    <h2>{num}{s["h2"]}</h2>\n{intro}'
            f'    <table>\n      <thead><tr><th>מה זה עושה</th><th>פונקציה</th><th>תיעוד רשמי</th></tr></thead>\n'
            f'      <tbody>\n{rows}\n      </tbody>\n    </table>'
        )
        return _slide(body)

    if t == "datatable":
        intro = f'    <p class="muted">{s["intro"]}</p>\n' if s.get("intro") else ""
        rows = "\n".join(
            f'        <tr><td><code>{col}</code></td><td><span class="tag">{dt}</span></td><td>{desc}</td></tr>'
            for col, dt, desc in s["rows"]
        )
        body = (
            f'    <h2>{num}{s["h2"]}</h2>\n{intro}'
            f'    <table>\n      <thead><tr><th>עמודה</th><th>טיפוס</th><th>תיאור</th></tr></thead>\n'
            f'      <tbody>\n{rows}\n      </tbody>\n    </table>'
        )
        return _slide(body)

    if t == "tip":
        return f'  <div class="slide" style="border-right:4px solid var(--green)"><p style="margin:0">💡 {s["text"]}</p></div>'

    if t == "warn":
        return f'  <div class="slide" style="border-right:4px solid var(--brand2)"><p style="margin:0">⚠️ {s["text"]}</p></div>'

    if t == "cta":
        pills = "\n".join(
            f'      <span class="pill"><a href="{u}" target="_blank">{l} ↗</a></span>'
            for l, u in s.get("pills", [])
        )
        pills_block = f'    <div>\n{pills}\n    </div>\n' if pills else ""
        return (
            f'  <div class="cta">\n    <h2>{s["h2"]}</h2>\n    {s["body"]}\n{pills_block}  </div>'
        )

    raise ValueError(f"unknown slide type: {t}")


def render(path: Path, *, lang_title: str, kicker: str, kicker_color: str,
           title: str, subtitle: str, hero_grad: str, slides: list[dict]) -> None:
    body = "\n\n".join(_render_slide(s, i + 1) for i, s in enumerate(slides))
    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{lang_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>{CSS}
  .kicker{{color:{kicker_color}}}
  header.hero{{background:{hero_grad}}}
</style>
</head>
<body>

<header class="hero">
  <div class="kicker">{kicker}</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
</header>

<div class="wrap">

{body}

</div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    print(f"  wrote {path.relative_to(path.parents[2])}")


# Convenience colour presets ------------------------------------------------ #
SUBJECT_GRAD = "linear-gradient(135deg,rgba(232,89,12,.20),rgba(245,158,11,.10))"
EXERCISE_GRAD = "linear-gradient(135deg,rgba(52,211,153,.16),rgba(245,158,11,.10))"
BRAND2 = "#f59e0b"
GREEN = "#34d399"

# Common docs landing pages reused across chapters
DOCS_PILLS = [
    ("PySpark DataFrame API", "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html"),
    ("Functions (F.*)", "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html"),
    ("PySpark API Reference", "https://spark.apache.org/docs/latest/api/python/reference/index.html"),
    ("SQL Programming Guide", "https://spark.apache.org/docs/latest/sql-programming-guide.html"),
]
