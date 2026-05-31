"""Chapter 04 - Creating & Transforming Columns (medium)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "04_Creating_and_Transforming_Columns"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 04 — Creating & Transforming Columns"

INTRO_MD = (
    "This is where transforms come alive. We use `with_columns()` to **add or "
    "change** columns: arithmetic (revenue = quantity × price), fixing data types "
    "(the string `order_date` → a real date), string cleaning, and conditional "
    "logic with `when/then/otherwise`. These are the exact operations we write all "
    "day long in Foundry.\n\n"
    "*כאן הטרנספורמציות מתעוררות לחיים. נשתמש ב-`with_columns()` כדי להוסיף או לשנות "
    "עמודות: חישובים (revenue = quantity × price), תיקון טיפוסים (ה-`order_date` "
    "כמחרוזת → תאריך אמיתי), ניקוי מחרוזות, ולוגיקה מותנית עם `when/then/otherwise`.*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"md": "Import Polars as `pl` and read `data/orders.csv` into `orders`.\n\n"
           "*ייבאו את Polars וקראו את `data/orders.csv` ל-`orders`.*",
     "sol": 'import polars as pl\n\norders = pl.read_csv("data/orders.csv")\norders.head()'},

    {"md": "Add a new column `revenue` = `quantity` × `unit_price`.\n\n"
           "*הוסיפו עמודה חדשה `revenue` ששווה ל-`quantity` כפול `unit_price`.*",
     "sol": 'orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))'},

    {"md": "Add `revenue` again, but **rounded to 2 decimals** (use `.round(2)`).\n\n"
           "*הוסיפו שוב את `revenue`, אבל מעוגל ל-2 ספרות (השתמשו ב-`.round(2)`).*",
     "sol": 'orders.with_columns(\n'
            '    revenue=(pl.col("quantity") * pl.col("unit_price")).round(2)\n'
            ')'},

    {"md": "The `order_date` column is a **string**. Convert it to a real **Date** "
           "column (format `\"%Y-%m-%d\"`).\n\n"
           "*העמודה `order_date` היא מחרוזת. המירו אותה לעמודת תאריך אמיתית "
           "(פורמט `\"%Y-%m-%d\"`).*",
     "sol": 'orders.with_columns(\n'
            '    pl.col("order_date").str.to_date("%Y-%m-%d")\n'
            ')'},

    {"md": "From `order_date`, create a new integer column `order_month` "
           "(1–12).\n\n"
           "*מתוך `order_date`, צרו עמודה שלמה חדשה `order_month` (1–12).*",
     "sol": 'orders.with_columns(\n'
            '    order_month=pl.col("order_date").str.to_date("%Y-%m-%d").dt.month()\n'
            ')'},

    {"md": "Add two columns from `order_date`: `order_year` and `order_quarter`.\n\n"
           "*הוסיפו שתי עמודות מתוך `order_date`: `order_year` ו-`order_quarter`.*",
     "sol": 'd = pl.col("order_date").str.to_date("%Y-%m-%d")\n'
            'orders.with_columns(\n'
            '    order_year=d.dt.year(),\n'
            '    order_quarter=d.dt.quarter(),\n'
            ')'},

    {"md": "Add a boolean column `is_return` that is `True` when `quantity` is "
           "negative.\n\n"
           "*הוסיפו עמודה בוליאנית `is_return` ששווה `True` כש-`quantity` שלילי.*",
     "sol": 'orders.with_columns(is_return=pl.col("quantity") < 0)'},

    {"md": "Add a column `order_size` using `when/then/otherwise`: "
           "`\"small\"` if quantity < 10, `\"medium\"` if 10–25, `\"large\"` if > 25.\n\n"
           "*הוסיפו עמודה `order_size` בעזרת `when/then/otherwise`: "
           "`\"small\"` אם quantity קטן מ-10, `\"medium\"` אם 10–25, `\"large\"` אם מעל 25.*",
     "sol": 'orders.with_columns(\n'
            '    order_size=pl.when(pl.col("quantity") < 10).then(pl.lit("small"))\n'
            '    .when(pl.col("quantity") <= 25).then(pl.lit("medium"))\n'
            '    .otherwise(pl.lit("large"))\n'
            ')'},

    {"md": "Add `region_upper` = the `region` in UPPERCASE (use `str.to_uppercase`).\n\n"
           "*הוסיפו `region_upper` = ה-`region` באותיות גדולות.*",
     "sol": 'orders.with_columns(region_upper=pl.col("region").str.to_uppercase())'},

    {"md": "Add `sku_prefix` = the **first 2 characters** of `product_sku` "
           "(use `str.slice`).\n\n"
           "*הוסיפו `sku_prefix` = 2 התווים הראשונים של `product_sku` "
           "(השתמשו ב-`str.slice`).*",
     "sol": 'orders.with_columns(sku_prefix=pl.col("product_sku").str.slice(0, 2))'},

    {"md": "Add `channel_clean` where the value `\"online\"` is replaced by "
           "`\"web\"` (use `str.replace`).\n\n"
           "*הוסיפו `channel_clean` שבה הערך `\"online\"` מוחלף ב-`\"web\"` "
           "(השתמשו ב-`str.replace`).*",
     "sol": 'orders.with_columns(\n'
            '    channel_clean=pl.col("channel").str.replace("online", "web")\n'
            ')'},

    {"md": "Add `name_length` = the number of characters in `product_name` "
           "(use `str.len_chars`).\n\n"
           "*הוסיפו `name_length` = מספר התווים ב-`product_name`.*",
     "sol": 'orders.with_columns(name_length=pl.col("product_name").str.len_chars())'},

    {"md": "Fill the missing `discount_code` values with the text `\"NONE\"` "
           "(use `fill_null`).\n\n"
           "*מלאו את הערכים החסרים ב-`discount_code` בטקסט `\"NONE\"` "
           "(השתמשו ב-`fill_null`).*",
     "sol": 'orders.with_columns(\n'
            '    discount_code=pl.col("discount_code").fill_null("NONE")\n'
            ')'},

    {"md": "Add **two columns at once** in a single `with_columns`: "
           "`revenue` (quantity × price) and `is_return` (quantity < 0).\n\n"
           "*הוסיפו שתי עמודות בבת אחת ב-`with_columns` אחד: "
           "`revenue` ו-`is_return`.*",
     "sol": 'orders.with_columns(\n'
            '    revenue=pl.col("quantity") * pl.col("unit_price"),\n'
            '    is_return=pl.col("quantity") < 0,\n'
            ')'},

    {"md": "Add `price_with_tax` = `unit_price` × 1.17, rounded to 2 decimals.\n\n"
           "*הוסיפו `price_with_tax` = `unit_price` כפול 1.17, מעוגל ל-2 ספרות.*",
     "sol": 'orders.with_columns(\n'
            '    price_with_tax=(pl.col("unit_price") * 1.17).round(2)\n'
            ')'},

    {"md": "Build a `segment` column by joining `region` and `channel` with "
           "`\" / \"` between them (use `pl.concat_str`).\n\n"
           "*בנו עמודת `segment` שמחברת את `region` ו-`channel` עם `\" / \"` ביניהם "
           "(השתמשו ב-`pl.concat_str`).*",
     "sol": 'orders.with_columns(\n'
            '    segment=pl.concat_str(["region", "channel"], separator=" / ")\n'
            ')'},

    {"md": "Add `priority` = `\"high\"` when `revenue` (quantity × price) is over "
           "500, otherwise `\"normal\"`.\n\n"
           "*הוסיפו `priority` ששווה `\"high\"` כש-`revenue` מעל 500, אחרת `\"normal\"`.*",
     "sol": 'orders.with_columns(\n'
            '    priority=pl.when(pl.col("quantity") * pl.col("unit_price") > 500)\n'
            '    .then(pl.lit("high"))\n'
            '    .otherwise(pl.lit("normal"))\n'
            ')'},

    {"md": "Add `abs_quantity` = the **absolute value** of `quantity` "
           "(returns become positive).\n\n"
           "*הוסיפו `abs_quantity` = הערך המוחלט של `quantity` (החזרות הופכות לחיוביות).*",
     "sol": 'orders.with_columns(abs_quantity=pl.col("quantity").abs())'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>כאן מתחילה העבודה האמיתית של טרנספורמציה: <strong>ליצור עמודות "
             "חדשות</strong> ו<strong>לשנות קיימות</strong>. הכלי המרכזי הוא "
             "<code>with_columns()</code> — הוא מקבל ביטוי אחד או יותר, ומחזיר "
             "DataFrame חדש עם העמודות שהוספנו/שינינו.</p>"
             "<p>בתוך הביטויים אפשר לעשות הכל: חשבון (<code>+ - * /</code>), המרת "
             "טיפוסים (<code>cast</code>, <code>str.to_date</code>), פעולות על "
             "מחרוזות (<code>str.*</code>), על תאריכים (<code>dt.*</code>), "
             "ולוגיקה מותנית (<code>when/then/otherwise</code>).</p>"},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "יצירת עמודות ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>df['r'] = df['q'] * df['p']</code>",
         "<code>pd.to_datetime(df['d'])</code>",
         "<code>df['c'].str.upper()</code>",
         "<code>np.where(cond, a, b)</code>",
         "<code>df['d'].dt.month</code>",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>df.with_columns(r=pl.col('q')*pl.col('p'))</code>",
         "<code>pl.col('d').str.to_date()</code>",
         "<code>pl.col('c').str.to_uppercase()</code>",
         "<code>pl.when(cond).then(a).otherwise(b)</code>",
         "<code>pl.col('d').dt.month()</code>",
     ],
     "note": "💡 ב-Polars לא מציבים לתוך עמודה (<code>df['x'] = ...</code>). "
             "תמיד מחזירים DataFrame חדש מ-<code>with_columns</code>."},

    {"type": "text", "h2": "המרת טיפוסים (Casting) — קריטי ל-Foundry",
     "body": "<p>מערכות שולחות תאריכים, מספרים ואחוזים לעיתים קרובות כ<strong>מחרוזות</strong>. "
             "לפני שמחשבים — חייבים להמיר לטיפוס הנכון:</p>"
             "<ul>"
             "<li><code>str.to_date(\"%Y-%m-%d\")</code> — מחרוזת → תאריך</li>"
             "<li><code>cast(pl.Int64)</code> / <code>cast(pl.Float64)</code> — בין מספרים</li>"
             "<li>אחרי שיש תאריך אמיתי, אפשר: <code>dt.year()</code>, <code>dt.month()</code>, "
             "<code>dt.quarter()</code>, <code>dt.weekday()</code></li>"
             "</ul>"},

    {"type": "text", "h2": "לוגיקה מותנית: when / then / otherwise",
     "body": "<p>זה ה-<code>IF</code> של Polars, והוא משרשרת:</p>"
             "<p><code>pl.when(cond1).then(val1).when(cond2).then(val2).otherwise(default)</code></p>"
             "<p>שימו לב: ערך קבוע נכתב עם <code>pl.lit(\"small\")</code> "
             "(כדי שיהיה ברור שזה ערך ולא שם עמודה).</p>"},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("הוספת / שינוי עמודות", "DataFrame.with_columns()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.with_columns.html"),
         ("המרת מחרוזת לתאריך", "Expr.str.to_date()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.to_date.html"),
         ("המרת טיפוס", "Expr.cast()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.cast.html"),
         ("לוגיקה מותנית", "polars.when()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.when.html"),
         ("ערך קבוע", "polars.lit()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.lit.html"),
         ("עיגול", "Expr.round()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.round.html"),
         ("מילוי ערכים חסרים", "Expr.fill_null()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.fill_null.html"),
         ("חיבור מחרוזות", "polars.concat_str()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.concat_str.html"),
         ("רכיבי תאריך", "Expr.dt (namespace)",
          "https://docs.pola.rs/api/python/stable/reference/expressions/temporal.html"),
         ("פעולות מחרוזת", "Expr.str (namespace)",
          "https://docs.pola.rs/api/python/stable/reference/expressions/string.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת — חשוב מאוד",
     "body": "<p>שני ה-namespaces <code>str</code> ו-<code>dt</code> הם עשירים מאוד. "
             "עברו על <em>כל</em> הפונקציות שם — אלה הכלים שתשתמשו בהם הכי הרבה "
             "בניקוי ובעיבוד נתונים אמיתיים.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל בינוני (18 שאלות) שמתחיל להרגיש כמו טרנספורמציה אמיתית: "
             "מחשבים <code>revenue</code>, מתקנים את עמודת התאריך, מפיקים חודש ורבעון, "
             "מסמנים החזרות, ומסווגים הזמנות לפי גודל. כל אלה צעדים שאנחנו עושים "
             "בעבודה היומיומית.</p>"},
    {"type": "warn", "text": "שימו לב: <code>order_date</code> מגיעה כ<strong>מחרוזת</strong>. "
                            "לפני שמפיקים ממנה חודש/שנה — חייבים להמיר אותה לתאריך עם "
                            "<code>str.to_date</code>."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "אותה טבלת הזמנות — 1,000 שורות. הפעם ניצור ממנה עמודות חדשות.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>with_columns</code> להוספת עמודה אחת או כמה בבת אחת",
        "חישובים אריתמטיים ו-<code>round</code>",
        "המרת טיפוסים: <code>str.to_date</code>, ורכיבי תאריך <code>dt.*</code>",
        "פעולות מחרוזת: <code>str.to_uppercase</code>, <code>str.slice</code>, <code>str.replace</code>, <code>str.len_chars</code>",
        "<code>when/then/otherwise</code> ללוגיקה מותנית",
        "<code>fill_null</code>, <code>abs</code>, <code>concat_str</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 04 — יצירת ועיבוד עמודות | Polars",
             kicker="Polars for Power Users · פרק 04", kicker_color=H.BRAND2,
             title="יצירת ועיבוד עמודות",
             subtitle="with_columns, חישובים, המרת טיפוסים, ולוגיקה מותנית — כאן הטרנספורמציות מתעוררות לחיים.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 04 — התרגיל והמידע | Polars",
             kicker="פרק 04 · התרגיל והמידע", kicker_color=H.GREEN,
             title="בניית עמודות מתוך ההזמנות",
             subtitle="מחשבים, מתקנים טיפוסים, ומוסיפים לוגיקה — כמו בטרנספורמציה אמיתית.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
