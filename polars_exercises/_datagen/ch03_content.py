"""Chapter 03 - Filtering & Sorting (short)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "03_Filtering_and_Sorting"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 03 — Filtering & Sorting"

INTRO_MD = (
    "Filtering rows is the Polars version of Excel's *quick filter* and pandas' "
    "boolean masks. We keep only the rows we care about with `filter()`, then put "
    "them in order with `sort()`. Master combining conditions with `&` (and), "
    "`|` (or), `~` (not) — it is the heart of every WHERE clause in our pipelines.\n\n"
    "*סינון שורות הוא הגרסה של Polars ל-quick filter באקסל ול-boolean mask ב-pandas. "
    "שומרים רק את השורות הרלוונטיות עם `filter()`, וממיינים עם `sort()`. "
    "חשוב לשלוט בשילוב תנאים עם `&` (וגם), `|` (או), `~` (לא).*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"md": "Import Polars as `pl` and read `data/orders.csv` into `orders`.\n\n"
           "*ייבאו את Polars וקראו את `data/orders.csv` ל-`orders`.*",
     "sol": 'import polars as pl\n\norders = pl.read_csv("data/orders.csv")\norders.head()'},

    {"md": "Keep only the rows where `status` is `\"completed\"`.\n\n"
           "*השאירו רק שורות ש-`status` שלהן הוא `\"completed\"`.*",
     "sol": 'orders.filter(pl.col("status") == "completed")'},

    {"md": "Keep only orders with `quantity` greater than 20.\n\n"
           "*השאירו רק הזמנות עם `quantity` גדול מ-20.*",
     "sol": 'orders.filter(pl.col("quantity") > 20)'},

    {"md": "Keep online orders **from Europe** (`region == \"Europe\"` **and** "
           "`channel == \"online\"`). Remember the parentheses around each condition.\n\n"
           "*השאירו הזמנות online מאירופה (`region` הוא Europe וגם `channel` הוא online). "
           "זכרו סוגריים סביב כל תנאי.*",
     "sol": 'orders.filter((pl.col("region") == "Europe") & (pl.col("channel") == "online"))'},

    {"md": "Keep orders whose `category` is **either** `\"pens\"` or `\"books\"` "
           "(use `is_in`).\n\n"
           "*השאירו הזמנות שה-`category` שלהן הוא pens או books (השתמשו ב-`is_in`).*",
     "sol": 'orders.filter(pl.col("category").is_in(["pens", "books"]))'},

    {"md": "Keep orders where `quantity` is **between 10 and 20** (inclusive). "
           "Use `is_between`.\n\n"
           "*השאירו הזמנות שבהן `quantity` נמצא בין 10 ל-20 (כולל). השתמשו ב-`is_between`.*",
     "sol": 'orders.filter(pl.col("quantity").is_between(10, 20))'},

    {"md": "Find all the **returns** (rows where `quantity` is negative).\n\n"
           "*מצאו את כל ההחזרות (שורות שבהן `quantity` שלילי).*",
     "sol": 'orders.filter(pl.col("quantity") < 0)'},

    {"md": "Keep orders whose `product_name` **contains** the text `\"Pen\"` "
           "(use `str.contains`).\n\n"
           "*השאירו הזמנות שבהן `product_name` מכיל את הטקסט `\"Pen\"` (השתמשו ב-`str.contains`).*",
     "sol": 'orders.filter(pl.col("product_name").str.contains("Pen"))'},

    {"md": "Keep only rows that **have** a `discount_code` (not null).\n\n"
           "*השאירו רק שורות שיש בהן `discount_code` (לא null).*",
     "sol": 'orders.filter(pl.col("discount_code").is_not_null())'},

    {"md": "Keep only rows that are **missing** a `discount_code` (null).\n\n"
           "*השאירו רק שורות שחסר בהן `discount_code` (null).*",
     "sol": 'orders.filter(pl.col("discount_code").is_null())'},

    {"md": "Keep every order **except** the cancelled ones (use `~` or `!=`).\n\n"
           "*השאירו כל הזמנה חוץ מהמבוטלות (השתמשו ב-`~` או `!=`).*",
     "sol": 'orders.filter(pl.col("status") != "cancelled")'},

    {"md": "Sort the whole table by `unit_price`, cheapest first.\n\n"
           "*מיינו את הטבלה לפי `unit_price`, מהזול ליקר.*",
     "sol": 'orders.sort("unit_price")'},

    {"md": "Sort by `quantity`, **largest first**.\n\n"
           "*מיינו לפי `quantity`, מהגדול לקטן.*",
     "sol": 'orders.sort("quantity", descending=True)'},

    {"md": "Sort by `region` (A→Z), and within each region by `unit_price` "
           "(high→low).\n\n"
           "*מיינו לפי `region` (א→ת), ובתוך כל אזור לפי `unit_price` (גבוה→נמוך).*",
     "sol": 'orders.sort("region", "unit_price", descending=[False, True])'},

    {"md": "Show the **5 most expensive orders** (highest `unit_price`).\n\n"
           "*הציגו את 5 ההזמנות היקרות ביותר.*",
     "sol": 'orders.sort("unit_price", descending=True).head(5)'},

    {"md": "**How many** completed online orders from Europe have "
           "`quantity` of at least 15? (filter, then count the rows)\n\n"
           "*כמה הזמנות online שהושלמו מאירופה הן עם `quantity` של לפחות 15? "
           "(סננו, ואז ספרו את השורות)*",
     "sol": 'orders.filter(\n'
            '    (pl.col("status") == "completed")\n'
            '    & (pl.col("channel") == "online")\n'
            '    & (pl.col("region") == "Europe")\n'
            '    & (pl.col("quantity") >= 15)\n'
            ').height'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p><strong>סינון</strong> = להשאיר רק את השורות שעונות על תנאי. "
             "זו פעולת ה-WHERE של עולם הנתונים. ב-Polars משתמשים ב-<code>filter()</code> "
             "ובתוכו ביטוי בוליאני (נכון/לא נכון לכל שורה).</p>"
             "<p><strong>מיון</strong> עם <code>sort()</code> מסדר את השורות — "
             "לפי עמודה אחת או כמה, בעלייה או בירידה.</p>"},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "סינון ומיון ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>df[df['q'] > 20]</code>",
         "<code>df[(a) & (b)]</code>",
         "<code>df[df['c'].isin([...])]</code>",
         "<code>df.sort_values('p')</code>",
         "<code>df['c'].isna()</code>",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>df.filter(pl.col('q') > 20)</code>",
         "<code>df.filter((a) & (b))</code>",
         "<code>df.filter(pl.col('c').is_in([...]))</code>",
         "<code>df.sort('p')</code>",
         "<code>pl.col('c').is_null()</code>",
     ],
     "note": "💡 שימו לב: כל תנאי חייב להיות בתוך <strong>סוגריים</strong> "
             "כשמשלבים עם <code>&</code> או <code>|</code> — אחרת תקבלו שגיאה."},

    {"type": "text", "h2": "שילוב תנאים — הכלל החשוב ביותר",
     "body": "<ul>"
             "<li><code>&amp;</code> = <strong>וגם</strong> (AND)</li>"
             "<li><code>|</code> = <strong>או</strong> (OR)</li>"
             "<li><code>~</code> = <strong>לא</strong> (NOT)</li>"
             "</ul>"
             "<p>דוגמה: <code>df.filter((pl.col(\"a\") > 1) &amp; (pl.col(\"b\") == \"x\"))</code></p>"
             "<p>ויש קיצורי דרך שימושיים: <code>is_in</code>, <code>is_between</code>, "
             "<code>is_null</code> / <code>is_not_null</code>, ופעולות מחרוזת כמו "
             "<code>str.contains</code>.</p>"},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("סינון שורות לפי תנאי", "DataFrame.filter()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.filter.html"),
         ("מיון שורות", "DataFrame.sort()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.sort.html"),
         ("בדיקת שייכות לרשימה", "Expr.is_in()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.is_in.html"),
         ("בדיקת טווח", "Expr.is_between()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.is_between.html"),
         ("האם ערך חסר", "Expr.is_null()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.is_null.html"),
         ("האם ערך קיים", "Expr.is_not_null()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.is_not_null.html"),
         ("חיפוש טקסט בתוך מחרוזת", "Expr.str.contains()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.contains.html"),
         ("N הערכים הגדולים ביותר", "Expr.top_k()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.top_k.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>עברו על משפחת הפונקציות של מחרוזות (<code>str.*</code>) ושל "
             "בדיקות בוליאניות (<code>is_*</code>) — יש שם המון כלים שימושיים לסינון.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל קצר (16 שאלות) של <strong>סינון ומיון</strong>. תתרגלו תנאים "
             "פשוטים, שילוב של כמה תנאים, סינון לפי null וטקסט, ומיון לפי כמה עמודות. "
             "אלה הכלים שמופיעים בכל טרנספורמציה כמעט.</p>"},
    {"type": "tip", "text": "טעות נפוצה: לשכוח סוגריים סביב כל תנאי כשמשלבים עם "
                            "<code>&</code>. תמיד: <code>(תנאי) &amp; (תנאי)</code>."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "אותה טבלת הזמנות — 1,000 שורות.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>filter</code> עם תנאי בודד ועם כמה תנאים (<code>&</code>, <code>|</code>, <code>~</code>)",
        "<code>is_in</code>, <code>is_between</code>",
        "<code>is_null</code> / <code>is_not_null</code>",
        "<code>str.contains</code> לחיפוש טקסט",
        "<code>sort</code> לפי עמודה אחת וכמה עמודות, בעלייה ובירידה",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 03 — סינון ומיון | Polars",
             kicker="Polars for Power Users · פרק 03", kicker_color=H.BRAND2,
             title="סינון ומיון (Filter & Sort)",
             subtitle="להשאיר רק את השורות הרלוונטיות, ולסדר אותן — ה-WHERE וה-ORDER BY של Polars.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 03 — התרגיל והמידע | Polars",
             kicker="פרק 03 · התרגיל והמידע", kicker_color=H.GREEN,
             title="סינון ומיון של ההזמנות",
             subtitle="תרגול קצר של תנאים, שילובי תנאים, ומיון.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
