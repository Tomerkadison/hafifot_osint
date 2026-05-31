"""Chapter 07 - Concat, Pivot & Unpivot (medium-long)."""

from pathlib import Path

import htmlgen as H
from nbbuild import build

CH = "07_Concat_Pivot_and_Unpivot"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 07 — Concat, Pivot & Unpivot"

INTRO_MD = (
    "Two everyday reshaping jobs. First, **stacking** files that arrive in pieces — "
    "monthly exports, one file per source system — into one table with `concat()`. "
    "Second, changing a table's **shape**: `pivot()` turns long data into a wide "
    "cross-tab (like an Excel PivotTable), and `unpivot()` does the reverse, turning "
    "wide columns back into tidy long rows.\n\n"
    "*שתי משימות יומיומיות של שינוי צורה. ראשית, **הערמה** של קבצים שמגיעים בחלקים "
    "(export חודשי, קובץ לכל מערכת) לטבלה אחת עם `concat()`. שנית, שינוי **צורת** "
    "הטבלה: `pivot()` הופך מידע ארוך לטבלה רחבה (כמו PivotTable), ו-`unpivot()` "
    "עושה את ההפך.*\n\n"
    "**Data files:** `data/orders_h1.csv`, `data/orders_h2.csv`, `data/orders.csv`"
)

ITEMS = [
    {"md": "Import Polars and the selectors module (`cs`). Read the two half-year "
           "files `orders_h1.csv` and `orders_h2.csv`, and also the full "
           "`orders.csv`.\n\n"
           "*ייבאו את Polars ואת מודול ה-selectors (`cs`). קראו את שני קבצי חצי-השנה "
           "ואת הקובץ המלא.*",
     "sol": 'import polars as pl\nimport polars.selectors as cs\n\n'
            'h1 = pl.read_csv("data/orders_h1.csv")\n'
            'h2 = pl.read_csv("data/orders_h2.csv")\n'
            'orders = pl.read_csv("data/orders.csv")\n'
            'h1.shape, h2.shape, orders.shape'},

    {"md": "**Stack** `h1` on top of `h2` into one table with `pl.concat`.\n\n"
           "*הערימו את `h1` מעל `h2` לטבלה אחת עם `pl.concat`.*",
     "sol": 'combined = pl.concat([h1, h2])\ncombined.shape'},

    {"md": "Confirm the concat was lossless: the combined row count should equal "
           "`h1.height + h2.height`, and equal the full `orders` table.\n\n"
           "*ודאו שה-concat לא איבד מידע: מספר השורות המאוחד צריך להיות שווה ל-"
           "`h1.height + h2.height` ולטבלת `orders` המלאה.*",
     "sol": 'combined = pl.concat([h1, h2])\n'
            'combined.height, h1.height + h2.height, orders.height'},

    {"md": "Diagonal concat: imagine `h2` gained a new column `source` that `h1` "
           "does not have. Add it to `h2`, then concat with `how=\"diagonal\"` so the "
           "missing values become null.\n\n"
           "*concat אלכסוני: דמיינו ש-`h2` קיבל עמודה חדשה `source` שאין ב-`h1`. "
           "הוסיפו אותה ל-`h2`, וחברו עם `how=\"diagonal\"` כך שהערכים החסרים יהפכו ל-null.*",
     "sol": 'h2b = h2.with_columns(source=pl.lit("system_B"))\n'
            'pl.concat([h1, h2b], how="diagonal").select("order_id", "source").head()'},

    {"md": "**Pivot** (cross-tab): total `revenue` per `category` (rows) broken down "
           "by `region` (columns). First add a `revenue` column.\n\n"
           "*pivot: סך ה-`revenue` לכל `category` (שורות) מפוצל לפי `region` (עמודות). "
           "קודם הוסיפו עמודת `revenue`.*",
     "sol": 'o = orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))\n'
            'o.pivot(on="region", index="category", values="revenue", aggregate_function="sum")'},

    {"md": "Pivot the **count of orders** by `region` (rows) × `channel` (columns).\n\n"
           "*pivot של מספר ההזמנות לפי `region` (שורות) × `channel` (עמודות).*",
     "sol": 'orders.pivot(on="channel", index="region", values="order_id",\n'
            '             aggregate_function="len")'},

    {"md": "Pivot the **average `unit_price`** by `category` (rows) × `channel` "
           "(columns), and round the numbers to 2 decimals.\n\n"
           "*pivot של מחיר היחידה הממוצע לפי `category` × `channel`, מעוגל ל-2 ספרות.*",
     "sol": 'orders.pivot(on="channel", index="category", values="unit_price",\n'
            '             aggregate_function="mean").with_columns(\n'
            '    cs.numeric().round(2)\n'
            ')'},

    {"md": "A pivot can leave **null** cells when a combination never occurred. "
           "Take the revenue pivot and fill any nulls with `0`.\n\n"
           "*pivot יכול להשאיר תאים ריקים (null) כשצירוף לא קרה. קחו את pivot ההכנסות "
           "ומלאו כל null ב-0.*",
     "sol": 'o = orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))\n'
            'piv = o.pivot(on="region", index="category", values="revenue",\n'
            '              aggregate_function="sum")\n'
            'piv.with_columns(cs.numeric().fill_null(0))'},

    {"md": "Add a **row total** to the revenue pivot: a `total` column summing all "
           "the region columns (use `pl.sum_horizontal` over the numeric columns).\n\n"
           "*הוסיפו סכום-שורה ל-pivot ההכנסות: עמודת `total` שמסכמת את כל עמודות "
           "האזורים (השתמשו ב-`pl.sum_horizontal`).*",
     "sol": 'o = orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))\n'
            'piv = o.pivot(on="region", index="category", values="revenue",\n'
            '              aggregate_function="sum").with_columns(cs.numeric().fill_null(0))\n'
            'piv.with_columns(total=pl.sum_horizontal(cs.numeric()))'},

    {"md": "**Unpivot** the revenue pivot back into tidy long form: one row per "
           "`category` + `region` with its `revenue`.\n\n"
           "*unpivot ל-pivot ההכנסות בחזרה לצורה ארוכה ומסודרת: שורה לכל "
           "`category`+`region` עם ה-`revenue`.*",
     "sol": 'o = orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))\n'
            'piv = o.pivot(on="region", index="category", values="revenue",\n'
            '              aggregate_function="sum").with_columns(cs.numeric().fill_null(0))\n'
            'piv.unpivot(index="category", variable_name="region", value_name="revenue")\\\n'
            '   .sort("category", "region")'},

    {"md": "**Unpivot** straight from `orders`: turn the `quantity` and `unit_price` "
           "columns into two rows per order, keeping `order_id` as the id.\n\n"
           "*unpivot ישירות מ-`orders`: הפכו את העמודות `quantity` ו-`unit_price` "
           "לשתי שורות לכל הזמנה, עם `order_id` כמזהה.*",
     "sol": 'orders.unpivot(\n'
            '    on=["quantity", "unit_price"],\n'
            '    index="order_id",\n'
            '    variable_name="metric",\n'
            '    value_name="value",\n'
            ').head()'},

    {"md": "**Horizontal concat:** glue two same-height frames side by side — "
           "`orders.select(\"order_id\")` and a one-column revenue frame "
           "(`how=\"horizontal\"`).\n\n"
           "*concat אופקי: הדביקו זו לצד זו שתי טבלאות באותו גובה — "
           "`order_id` ועמודת revenue (`how=\"horizontal\"`).*",
     "sol": 'left = orders.select("order_id")\n'
            'right = orders.select(\n'
            '    revenue=(pl.col("quantity") * pl.col("unit_price"))\n'
            ')\npl.concat([left, right], how="horizontal").head()'},

    {"md": "Build a clean **monthly revenue report**: from the combined table, pivot "
           "revenue by `region` (rows) × month (columns), fill nulls with 0. "
           "(derive month from `order_date`).\n\n"
           "*בנו דוח הכנסות חודשי נקי: מהטבלה המאוחדת, pivot של הכנסות לפי `region` "
           "(שורות) × חודש (עמודות), מלאו null ב-0.*",
     "sol": 'o = pl.concat([h1, h2]).with_columns(\n'
            '    revenue=pl.col("quantity") * pl.col("unit_price"),\n'
            '    month=pl.col("order_date").str.to_date("%Y-%m-%d").dt.month(),\n'
            ')\n'
            'o.pivot(on="month", index="region", values="revenue",\n'
            '        aggregate_function="sum").with_columns(cs.numeric().fill_null(0))'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>שני נושאים של שינוי צורה:</p>"
             "<p><strong>1. Concat (הערמה).</strong> לעיתים קרובות המידע מגיע בחלקים — "
             "קובץ לכל חודש, או לכל מערכת מקור. <code>pl.concat</code> מאחד אותם "
             "לטבלה אחת — אנכית (שורות מתחת לשורות) או אופקית (עמודות לצד עמודות).</p>"
             "<p><strong>2. Pivot / Unpivot.</strong> <code>pivot</code> הופך מידע "
             "\"ארוך\" לטבלה \"רחבה\" (כמו PivotTable). <code>unpivot</code> עושה את "
             "ההפך — מחזיר עמודות לשורות, לצורה מסודרת (tidy) שקל לעבד.</p>"},

    {"type": "text", "h2": "Long לעומת Wide",
     "body": "<p><strong>Wide (רחב):</strong> כל ערך של קטגוריה הופך לעמודה. נוח לקריאה "
             "אנושית ולדוחות.</p>"
             "<p><strong>Long (ארוך / tidy):</strong> כל מדידה בשורה נפרדת. נוח "
             "לעיבוד, לקיבוץ ולגרפים.</p>"
             "<p><code>pivot</code>: long → wide &nbsp;|&nbsp; <code>unpivot</code>: wide → long</p>"},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "שינוי צורה ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>pd.concat([a, b])</code>",
         "<code>df.pivot_table(...)</code>",
         "<code>df.melt(...)</code>",
         "<code>pd.concat([a,b], axis=1)</code>",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>pl.concat([a, b])</code>",
         "<code>df.pivot(on=, index=, values=)</code>",
         "<code>df.unpivot(...)</code>",
         "<code>pl.concat([a,b], how='horizontal')</code>",
     ],
     "note": "💡 ב-pandas \"melt\" וב-Polars \"unpivot\" — אותו רעיון בדיוק. "
             "ול-<code>concat</code> יש <code>how</code>: vertical / horizontal / diagonal."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("איחוד טבלאות", "polars.concat()",
          "https://docs.pola.rs/api/python/stable/reference/api/polars.concat.html"),
         ("long → wide", "DataFrame.pivot()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.pivot.html"),
         ("wide → long", "DataFrame.unpivot()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.unpivot.html"),
         ("סכום אופקי בין עמודות", "polars.sum_horizontal()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.sum_horizontal.html"),
         ("הוספת שורות בתחתית", "DataFrame.vstack()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.vstack.html"),
         ("שחלוף (transpose)", "DataFrame.transpose()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.transpose.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>שימו לב ל-<code>how</code> ב-<code>concat</code> (<code>vertical</code>, "
             "<code>horizontal</code>, <code>diagonal</code>) ולפונקציות ה-horizontal "
             "(<code>sum_horizontal</code>, <code>max_horizontal</code>...).</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל בינוני-ארוך (13 שאלות). נאחד שני קבצי חצי-שנה לטבלה אחת, "
             "ואז נבנה דוחות מסוג PivotTable — הכנסות לפי קטגוריה ואזור, ספירות לפי "
             "ערוץ, ודוח חודשי. נלמד גם להחזיר טבלה רחבה לצורה מסודרת עם "
             "<code>unpivot</code>.</p>"},
    {"type": "tip", "text": "ב-Polars הפעולה נקראת <code>unpivot</code> (ולא "
                            "<code>melt</code> כמו ב-pandas) — אבל זה אותו דבר בדיוק."},
    {"type": "datatable", "h2": "המידע", "intro": "שלושה קבצים:", "rows": [
        ("orders_h1.csv", "~513 שורות", "הזמנות מהחצי הראשון של 2023"),
        ("orders_h2.csv", "~487 שורות", "הזמנות מהחצי השני של 2023"),
        ("orders.csv", "1,000 שורות", "כל ההזמנות יחד (לבדיקה ול-pivot)"),
    ]},
    {"type": "text", "h2": "מבנה כל קובץ הזמנות",
     "body": "<p>לכל הקבצים אותן עמודות: <code>order_id, customer_id, order_date, "
             "region, product_sku, category, product_name, quantity, unit_price, "
             "channel, status, discount_code</code> (כמו בפרקים הקודמים).</p>"},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>pl.concat</code> אנכי, אופקי, ואלכסוני (<code>diagonal</code>)",
        "בדיקת תקינות איחוד לפי מספר שורות",
        "<code>pivot</code> עם <code>sum</code>, <code>len</code>, <code>mean</code>",
        "מילוי תאים ריקים וב-<code>sum_horizontal</code> לסכום-שורה",
        "<code>unpivot</code> להחזרת טבלה רחבה לצורה ארוכה",
        "בניית דוח הכנסות חודשי שלם",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'פתחו את <code>Exercises.ipynb</code> וענו שאלה-שאלה.',
        'בדקו תמיד את <code>.shape</code> אחרי <code>concat</code>.',
        'סיימתם? השוו מול <code>Solutions.ipynb</code>.',
    ]},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 07 — שרשור ושינוי צורה | Polars",
             kicker="Polars for Power Users · פרק 07", kicker_color=H.BRAND2,
             title="שרשור, Pivot ו-Unpivot",
             subtitle="מאחדים קבצים שמגיעים בחלקים, ומשנים את צורת הטבלה — long ↔ wide.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 07 — התרגיל והמידע | Polars",
             kicker="פרק 07 · התרגיל והמידע", kicker_color=H.GREEN,
             title="איחוד קבצים ובניית דוחות Pivot",
             subtitle="מאחדים export חודשי ובונים טבלאות צולבות — כמו דוחות אמיתיים.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
