"""Chapter 05 - Grouping & Aggregation (medium-long)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "05_Grouping_and_Aggregation"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 05 — Grouping & Aggregation"

INTRO_MD = (
    "Grouping is how we answer business questions: *revenue per region*, *orders "
    "per customer*, *average basket per channel*. It replaces Excel's `SUMIF`, "
    "`COUNTIF` and PivotTables. The pattern is always `group_by(...).agg(...)`. "
    "We will also meet **window functions** (`.over(...)`), which aggregate "
    "*without collapsing* the rows.\n\n"
    "*קיבוץ הוא הדרך לענות על שאלות עסקיות: הכנסה לכל אזור, הזמנות לכל לקוח, סל ממוצע "
    "לכל ערוץ. זה מחליף את SUMIF, COUNTIF וטבלאות ה-Pivot באקסל. התבנית היא תמיד "
    "`group_by(...).agg(...)`. נכיר גם window functions (`.over(...)`) שמסכמים בלי "
    "לכווץ את השורות.*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"md": "Import Polars, read `data/orders.csv`, and add a `revenue` column "
           "(`quantity` × `unit_price`). Keep it in `orders` — we reuse it below.\n\n"
           "*ייבאו את Polars, קראו את `data/orders.csv`, והוסיפו עמודת `revenue` "
           "(`quantity` כפול `unit_price`). שמרו ב-`orders` — נשתמש בה בהמשך.*",
     "sol": 'import polars as pl\n\n'
            'orders = pl.read_csv("data/orders.csv").with_columns(\n'
            '    revenue=pl.col("quantity") * pl.col("unit_price")\n'
            ')\norders.head()'},

    {"md": "Total `quantity` **per category**.\n\n"
           "*סך ה-`quantity` לכל `category`.*",
     "sol": 'orders.group_by("category").agg(pl.col("quantity").sum())'},

    {"md": "Number of orders **per region** (count the rows in each group).\n\n"
           "*מספר ההזמנות לכל `region` (ספירת השורות בכל קבוצה).*",
     "sol": 'orders.group_by("region").agg(pl.len().alias("n_orders"))'},

    {"md": "Average `unit_price` **per category**.\n\n"
           "*המחיר הממוצע ליחידה לכל `category`.*",
     "sol": 'orders.group_by("category").agg(pl.col("unit_price").mean())'},

    {"md": "Total `revenue` **per region**, sorted from highest to lowest.\n\n"
           "*סך ה-`revenue` לכל `region`, ממוין מהגבוה לנמוך.*",
     "sol": 'orders.group_by("region").agg(pl.col("revenue").sum()).sort("revenue", descending=True)'},

    {"md": "**Per category**, compute three things at once: total quantity "
           "(`total_qty`), average price (`avg_price`), and order count (`n_orders`).\n\n"
           "*לכל `category` חשבו שלושה דברים בבת אחת: סך הכמות, המחיר הממוצע, "
           "ומספר ההזמנות.*",
     "sol": 'orders.group_by("category").agg(\n'
            '    total_qty=pl.col("quantity").sum(),\n'
            '    avg_price=pl.col("unit_price").mean(),\n'
            '    n_orders=pl.len(),\n'
            ')'},

    {"md": "Number of orders for **each combination** of `region` and `channel`.\n\n"
           "*מספר ההזמנות לכל צירוף של `region` ו-`channel`.*",
     "sol": 'orders.group_by("region", "channel").agg(pl.len().alias("n_orders"))'},

    {"md": "Number of **distinct customers** per region (use `n_unique`).\n\n"
           "*מספר הלקוחות הייחודיים לכל `region` (השתמשו ב-`n_unique`).*",
     "sol": 'orders.group_by("region").agg(pl.col("customer_id").n_unique().alias("n_customers"))'},

    {"md": "**Per category**, the minimum and maximum `quantity`.\n\n"
           "*לכל `category`, הכמות המינימלית והמקסימלית.*",
     "sol": 'orders.group_by("category").agg(\n'
            '    min_qty=pl.col("quantity").min(),\n'
            '    max_qty=pl.col("quantity").max(),\n'
            ')'},

    {"md": "Total `revenue` **per status**.\n\n"
           "*סך ה-`revenue` לכל `status`.*",
     "sol": 'orders.group_by("status").agg(pl.col("revenue").sum())'},

    {"md": "**Per category**, the total revenue **of completed orders only** "
           "(aggregate with a filter inside: "
           "`pl.col(\"revenue\").filter(...).sum()`).\n\n"
           "*לכל `category`, סך ה-revenue של הזמנות שהושלמו בלבד "
           "(אגרגציה עם סינון בפנים).*",
     "sol": 'orders.group_by("category").agg(\n'
            '    completed_revenue=pl.col("revenue")\n'
            '    .filter(pl.col("status") == "completed").sum()\n'
            ')'},

    {"md": "Total `revenue` **per month**. Derive the month from `order_date` "
           "and sort by month.\n\n"
           "*סך ה-`revenue` לכל חודש. הפיקו את החודש מ-`order_date` ומיינו לפי חודש.*",
     "sol": 'orders.group_by(\n'
            '    month=pl.col("order_date").str.to_date("%Y-%m-%d").dt.month()\n'
            ').agg(pl.col("revenue").sum()).sort("month")'},

    {"md": "The **top 3 categories** by total revenue.\n\n"
           "*3 הקטגוריות המובילות לפי סך ה-revenue.*",
     "sol": 'orders.group_by("category").agg(pl.col("revenue").sum())'
            '.sort("revenue", descending=True).head(3)'},

    {"md": "The **average order value** (mean `revenue`) per `channel`.\n\n"
           "*ערך ההזמנה הממוצע (revenue ממוצע) לכל `channel`.*",
     "sol": 'orders.group_by("channel").agg(pl.col("revenue").mean().round(2).alias("avg_order_value"))'},

    {"md": "**Per region**, the **earliest** `order_date` (min).\n\n"
           "*לכל `region`, התאריך המוקדם ביותר (min) של `order_date`.*",
     "sol": 'orders.group_by("region").agg(pl.col("order_date").min().alias("first_order"))'},

    {"md": "Count the number of **returns** (quantity < 0) per category.\n\n"
           "*ספרו את מספר ההחזרות (quantity קטן מ-0) לכל `category`.*",
     "sol": 'orders.group_by("category").agg(\n'
            '    n_returns=(pl.col("quantity") < 0).sum()\n'
            ')'},

    {"md": "The **5 customers** with the highest total revenue.\n\n"
           "*5 הלקוחות עם סך ה-revenue הגבוה ביותר.*",
     "sol": 'orders.group_by("customer_id").agg(pl.col("revenue").sum())'
            '.sort("revenue", descending=True).head(5)'},

    {"md": "**Window function:** add a column `category_total` next to every row, "
           "holding the total revenue of that row's category — *without* collapsing "
           "the table (use `.over(\"category\")`).\n\n"
           "*window function: הוסיפו עמודה `category_total` ליד כל שורה, עם סך ה-revenue "
           "של הקטגוריה שלה — בלי לכווץ את הטבלה (השתמשו ב-`.over(\"category\")`).*",
     "sol": 'orders.with_columns(\n'
            '    category_total=pl.col("revenue").sum().over("category")\n'
            ').select("order_id", "category", "revenue", "category_total").head()'},

    {"md": "Using the window result, add `pct_of_category` = each order's revenue "
           "as a **percent of its category total**, rounded to 1 decimal.\n\n"
           "*בעזרת ה-window, הוסיפו `pct_of_category` = ה-revenue של ההזמנה כאחוז מסך "
           "הקטגוריה, מעוגל לספרה אחת.*",
     "sol": 'orders.with_columns(\n'
            '    pct_of_category=(\n'
            '        pl.col("revenue") / pl.col("revenue").sum().over("category") * 100\n'
            '    ).round(1)\n'
            ').select("order_id", "category", "revenue", "pct_of_category").head()'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p><strong>קיבוץ</strong> (group_by) הוא איך עונים על שאלות עסקיות: "
             "כמה הכנסה לכל אזור? כמה הזמנות לכל לקוח? זה בדיוק מה שעושים עם "
             "PivotTable או SUMIF באקסל — רק מהיר פי כמה.</p>"
             "<p>התבנית קבועה: <code>df.group_by(\"col\").agg( ... )</code>. "
             "בתוך <code>agg</code> מציינים אילו חישובים לעשות לכל קבוצה — סכום, "
             "ממוצע, ספירה, מינימום, מקסימום, ערכים ייחודיים, ועוד.</p>"},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "קיבוץ ואגרגציה ב-pandas מול Polars:",
     "left_title": "🐼 pandas / Excel", "left": [
         "<code>df.groupby('r')['v'].sum()</code>",
         "<code>df.groupby('r').agg({...})</code>",
         "PivotTable",
         "<code>SUMIF</code> / <code>COUNTIF</code>",
         "<code>df.groupby('r')['c'].nunique()</code>",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>df.group_by('r').agg(pl.col('v').sum())</code>",
         "<code>df.group_by('r').agg(...)</code>",
         "<code>group_by().agg()</code>",
         "<code>pl.col('v').filter(cond).sum()</code>",
         "<code>pl.col('c').n_unique()</code>",
     ],
     "note": "💡 אפשר לחשב כמה אגרגציות בבת אחת בתוך <code>agg</code>, "
             "ואפשר לסנן בתוך האגרגציה: <code>pl.col('v').filter(cond).sum()</code>."},

    {"type": "text", "h2": "Window functions: .over()",
     "body": "<p>לפעמים רוצים סכום-קבוצה אבל <strong>בלי לאבד את השורות</strong> — "
             "למשל, ליד כל הזמנה להציג את סך ההכנסה של הקטגוריה שלה. בשביל זה יש "
             "<code>.over()</code>:</p>"
             "<p><code>pl.col(\"revenue\").sum().over(\"category\")</code></p>"
             "<p>זה מחשב את הסכום לכל קטגוריה, ו\"מורח\" אותו חזרה על כל השורות. "
             "כלי חזק מאוד לחישובי אחוז-מתוך-קבוצה, דירוג, וסכומים מצטברים.</p>"},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("קיבוץ", "DataFrame.group_by()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.group_by.html"),
         ("אגרגציה על קבוצה", "GroupBy.agg()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.dataframe.group_by.GroupBy.agg.html"),
         ("ספירת שורות בקבוצה", "polars.len()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.len.html"),
         ("סכום", "Expr.sum()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.sum.html"),
         ("ממוצע", "Expr.mean()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.mean.html"),
         ("מספר ערכים ייחודיים", "Expr.n_unique()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.n_unique.html"),
         ("סינון בתוך אגרגציה", "Expr.filter()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.filter.html"),
         ("window function", "Expr.over()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.over.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>עברו על כל פעולות האגרגציה (<code>sum</code>, <code>mean</code>, "
             "<code>median</code>, <code>std</code>, <code>first</code>, <code>last</code>, "
             "<code>quantile</code>...) וקראו על <code>over</code> — הוא יחזור הרבה.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל בינוני-ארוך (19 שאלות) של קיבוץ ואגרגציה. נחשב הכנסות לכל אזור, "
             "הזמנות לכל לקוח, סל ממוצע לכל ערוץ, ועוד — בדיוק כמו דוחות עסקיים אמיתיים. "
             "בסוף נטעם גם <code>over()</code> לחישובי אחוז-מתוך-קבוצה.</p>"},
    {"type": "tip", "text": "בשאלה הראשונה מוסיפים עמודת <code>revenue</code> "
                            "ושומרים אותה ב-<code>orders</code> — כל השאר מסתמכות עליה."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "אותה טבלת הזמנות — 1,000 שורות.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>group_by</code> לפי מפתח אחד וכמה מפתחות",
        "<code>agg</code> עם <code>sum</code>, <code>mean</code>, <code>min</code>, <code>max</code>, <code>n_unique</code>, <code>len</code>",
        "כמה אגרגציות בבת אחת",
        "סינון בתוך אגרגציה: <code>pl.col(...).filter(...).sum()</code>",
        "מיון וחיתוך של תוצאות (Top-N)",
        "<code>.over()</code> ל-window functions ולחישובי אחוז",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 05 — קיבוץ ואגרגציה | Polars",
             kicker="Polars for Power Users · פרק 05", kicker_color=H.BRAND2,
             title="קיבוץ ואגרגציה",
             subtitle="group_by + agg — מחליפים את PivotTable ו-SUMIF, ומכירים גם window functions.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 05 — התרגיל והמידע | Polars",
             kicker="פרק 05 · התרגיל והמידע", kicker_color=H.GREEN,
             title="דוחות עסקיים מתוך ההזמנות",
             subtitle="מחשבים הכנסות, ספירות וממוצעים לכל קבוצה — כמו דוחות אמיתיים.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
