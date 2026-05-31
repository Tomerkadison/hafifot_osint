"""Chapter 02 - Selecting & Subsetting (short)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "02_Selecting_and_Subsetting"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 02 — Selecting & Subsetting"

INTRO_MD = (
    "Now that we know the data, the next everyday task is **choosing the columns "
    "we actually need** — the building block of every Foundry transform. In Polars "
    "this is done with `select()` and **expressions** (`pl.col`), not with `[[...]]` "
    "bracket lists like in pandas.\n\n"
    "*אחרי שהכרנו את המידע, המשימה הבאה היא לבחור את העמודות שאנחנו באמת צריכים — "
    "אבן הבניין של כל טרנספורמציה. ב-Polars עושים זאת עם `select()` וביטויים "
    "(`pl.col`), לא עם סוגריים מרובעים כמו ב-pandas.*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"md": "Import Polars as `pl`, import the selectors module as `cs`, and read "
           "`data/orders.csv` into `orders`.\n\n"
           "*ייבאו את Polars בשם `pl`, את מודול ה-selectors בשם `cs`, "
           "וקראו את `data/orders.csv` ל-`orders`.*",
     "sol": "import polars as pl\nimport polars.selectors as cs\n\n"
            'orders = pl.read_csv("data/orders.csv")\norders.head()'},

    {"md": "Select only the columns `order_id`, `product_name`, `quantity`.\n\n"
           "*בחרו רק את העמודות `order_id`, `product_name`, `quantity`.*",
     "sol": 'orders.select("order_id", "product_name", "quantity")'},

    {"md": "Do the same selection, but this time using **expressions** "
           "(`pl.col(...)`).\n\n"
           "*אותה בחירה, אבל הפעם באמצעות ביטויים (`pl.col(...)`).*",
     "sol": 'orders.select(pl.col("order_id"), pl.col("product_name"), pl.col("quantity"))'},

    {"md": "Select **all columns except** `quantity` and `unit_price`.\n\n"
           "*בחרו את כל העמודות חוץ מ-`quantity` ו-`unit_price`.*",
     "sol": 'orders.select(pl.exclude("quantity", "unit_price"))'},

    {"md": "**Rename** `region` to `sales_region` and `channel` to `sales_channel`.\n\n"
           "*שנו את שם `region` ל-`sales_region` ואת `channel` ל-`sales_channel`.*",
     "sol": 'orders.rename({"region": "sales_region", "channel": "sales_channel"})'},

    {"md": "**Drop** the `discount_code` column.\n\n"
           "*הסירו (drop) את העמודה `discount_code`.*",
     "sol": 'orders.drop("discount_code")'},

    {"md": "Select all columns, but with `quantity` and `unit_price` **first** "
           "(reorder columns).\n\n"
           "*בחרו את כל העמודות, אבל עם `quantity` ו-`unit_price` בהתחלה (סידור מחדש).*",
     "sol": 'orders.select("quantity", "unit_price", pl.exclude("quantity", "unit_price"))'},

    {"md": "Using **selectors**, select all the **string** columns.\n\n"
           "*באמצעות selectors, בחרו את כל העמודות מסוג מחרוזת (string).*",
     "sol": "orders.select(cs.string())"},

    {"md": "Using **selectors**, select all the **numeric** columns.\n\n"
           "*באמצעות selectors, בחרו את כל העמודות המספריות.*",
     "sol": "orders.select(cs.numeric())"},

    {"md": "Get the `quantity` column **as a Series**.\n\n"
           "*קבלו את העמודה `quantity` כ-Series.*",
     "sol": 'orders.get_column("quantity")'},

    {"md": "Get a **single value**: the `unit_price` of the very first row.\n\n"
           "*קבלו ערך בודד: ה-`unit_price` של השורה הראשונה.*",
     "sol": 'orders.select("unit_price").item(0, 0)'},

    {"md": "Select all columns whose name **starts with `order`** "
           "(use a selector).\n\n"
           "*בחרו את כל העמודות ששמן מתחיל ב-`order` (השתמשו ב-selector).*",
     "sol": 'orders.select(cs.starts_with("order"))'},

    {"md": "Select `unit_price`, but rename it to `price` in the result "
           "(use `.alias`).\n\n"
           "*בחרו את `unit_price`, אבל תנו לו את השם `price` בתוצאה (השתמשו ב-`.alias`).*",
     "sol": 'orders.select(pl.col("unit_price").alias("price"))'},

    {"md": "Select the **first 3 columns by position** (hint: `orders.columns`).\n\n"
           "*בחרו את 3 העמודות הראשונות לפי מיקום (רמז: `orders.columns`).*",
     "sol": "orders.select(orders.columns[:3])"},

    {"md": "Find all the **distinct combinations** of `region` and `channel`.\n\n"
           "*מצאו את כל הצירופים הייחודיים של `region` ו-`channel`.*",
     "sol": 'orders.select("region", "channel").unique().sort("region", "channel")'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>אחרי שהכרנו את ה-DataFrame, השלב הבא הוא <strong>לבחור</strong> "
             "את מה שצריך: עמודות ספציפיות, חלק מהעמודות, או לשנות/להסיר עמודות. "
             "זו הפעולה הכי נפוצה בכל טרנספורמציה — כמעט תמיד מתחילים מ-<code>select</code>.</p>"
             "<p>הרעיון המרכזי ב-Polars הוא ה-<strong>Expression</strong> (ביטוי): "
             "<code>pl.col(\"quantity\")</code> הוא אובייקט שמתאר \"קח את העמודה quantity\". "
             "אפשר לשמור אותו במשתנה, לשרשר עליו פעולות, ולהשתמש בו שוב ושוב.</p>"},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "בחירת עמודות ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>df[['a','b']]</code>",
         "<code>df.drop(columns=['c'])</code>",
         "<code>df.rename(columns={...})</code>",
         "<code>df['a']</code> (עמודה)",
         "בחירה לפי טיפוס: מורכב",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>df.select('a','b')</code>",
         "<code>df.drop('c')</code>",
         "<code>df.rename({...})</code>",
         "<code>df.get_column('a')</code>",
         "<code>df.select(cs.numeric())</code>",
     ],
     "note": "💡 <code>select</code> מקבל גם שמות וגם ביטויים (<code>pl.col</code>) "
             "וגם selectors — וזה מה שהופך אותו לעוצמתי כל כך."},

    {"type": "text", "h2": "Selectors — בחירה חכמה של עמודות",
     "body": "<p>כשיש לנו טבלה רחבה, לא נוח לכתוב את שם כל עמודה. בשביל זה יש "
             "<strong>selectors</strong> — מייבאים אותם כך:</p>"
             "<p><code>import polars.selectors as cs</code></p>"
             "<p>ואז אפשר לבחור לפי טיפוס או לפי שם:</p>"
             "<ul>"
             "<li><code>cs.numeric()</code> — כל העמודות המספריות</li>"
             "<li><code>cs.string()</code> — כל עמודות המחרוזת</li>"
             "<li><code>cs.starts_with(\"order\")</code> — לפי תחילית השם</li>"
             "<li><code>cs.contains(\"date\")</code> — לפי חלק מהשם</li>"
             "</ul>"},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("בחירת עמודות / ביטויים", "DataFrame.select()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.select.html"),
         ("התייחסות לעמודה כביטוי", "pl.col()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.col.html"),
         ("כל העמודות חוץ מ-", "pl.exclude()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.exclude.html"),
         ("שינוי שם עמודה", "DataFrame.rename()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.rename.html"),
         ("הסרת עמודות", "DataFrame.drop()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.drop.html"),
         ("שם חדש לביטוי", "Expr.alias()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.alias.html"),
         ("קבלת עמודה כ-Series", "DataFrame.get_column()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.get_column.html"),
         ("קבלת ערך בודד", "DataFrame.item()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.item.html"),
         ("מודול ה-selectors", "polars.selectors",
          "https://docs.pola.rs/api/python/stable/reference/selectors.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את כל מודול ה-selectors — יש שם הרבה דרכים חכמות לבחור עמודות. "
             "ואת רשימת כל הביטויים (Expressions) — הם הלב של Polars.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל קצר (15 שאלות) שמתרגל <strong>בחירת עמודות</strong> בכל הדרכים: "
             "לפי שם, לפי ביטוי, לפי טיפוס, שינוי שם, והסרה. אלה הפעולות שתשתמשו בהן "
             "בתחילת כמעט כל טרנספורמציה.</p>"},
    {"type": "tip", "text": "נסו קודם לבד ב-<code>Exercises.ipynb</code>, "
                            "ורק אחר כך הציצו ב-<code>Solutions.ipynb</code>."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "אותה טבלת הזמנות מפרק 01 — 1,000 שורות, שורה לכל הזמנה.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>select</code> עם שמות, עם <code>pl.col</code>, ועם selectors",
        "<code>pl.exclude</code> לבחירת הכל חוץ מ-",
        "<code>rename</code> ו-<code>drop</code>",
        "<code>alias</code> למתן שם חדש",
        "<code>get_column</code> ו-<code>item</code> לגישה לעמודה / לערך בודד",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 02 — בחירת עמודות | Polars",
             kicker="Polars for Power Users · פרק 02", kicker_color=H.BRAND2,
             title="בחירת עמודות (Select & Subset)",
             subtitle="לבחור בדיוק את העמודות שצריך — אבן הבניין של כל טרנספורמציה.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 02 — התרגיל והמידע | Polars",
             kicker="פרק 02 · התרגיל והמידע", kicker_color=H.GREEN,
             title="בחירה מתוך טבלת ההזמנות",
             subtitle="תרגול קצר של בחירת עמודות בכל הדרכים ש-Polars מציע.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
