"""Chapter 04 — Window Functions."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "04_Window_Functions"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 04 — Window Functions"

INTRO_MD = (
    "Window functions are the single most useful Spark skill for real Foundry work, "
    "and they are awkward or limited in pandas/Polars. A window lets you compute a "
    "value for each row **relative to a group of related rows** — without collapsing "
    "the rows like `groupBy` does. Think: *ranking*, *running totals*, *“previous "
    "row”*, *“each row’s share of its group”*.\n\n"
    "*פונקציות חלון הן הכלי הכי שימושי ב-Spark לעבודה אמיתית ב-Foundry, והן מסורבלות "
    "או מוגבלות ב-pandas/Polars. חלון מאפשר לחשב ערך לכל שורה ביחס לקבוצת שורות "
    "קשורות — בלי לכווץ את השורות כמו ש-`groupBy` עושה. למשל: דירוג, סכום מצטבר, "
    "\"השורה הקודמת\", \"החלק היחסי של כל שורה בקבוצה שלה\".*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/orders.csv`, keep only positive `quantity`, and add "
           "`revenue = quantity * unit_price`. Call it `o`.\n\n"
           "*קראו את ההזמנות, השאירו כמות חיובית, והוסיפו `revenue`. קראו לזה `o`.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)\n'
            'o = (orders.filter(F.col("quantity") > 0)\n'
            '            .withColumn("revenue", F.round(F.col("quantity") * F.col("unit_price"), 2)))\n'
            'o.select("order_id", "customer_id", "order_ts", "channel", "revenue").show(5)'},

    {"md": "Import the `Window` class.\n\n*ייבאו את המחלקה `Window`.*",
     "sol": "from pyspark.sql.window import Window"},

    {"md": "**Number each customer's orders chronologically.** Define a window "
           "partitioned by `customer_id`, ordered by `order_ts`, and add "
           "`order_seq = row_number()`. Show `customer_id`, `order_ts`, `order_seq` "
           "for 12 rows.\n\n"
           "*מספרו את הזמנות כל לקוח לפי סדר כרונולוגי עם `row_number()`.*",
     "sol": 'w_time = Window.partitionBy("customer_id").orderBy("order_ts")\n'
            'o.withColumn("order_seq", F.row_number().over(w_time)) \\\n'
            ' .select("customer_id", "order_ts", "order_seq").show(12)'},

    {"md": "**Top orders per channel.** Define a window partitioned by `channel`, "
           "ordered by `revenue` descending, add `rnk = rank()`, and keep only the "
           "**top 3** orders in each channel.\n\n"
           "*מצאו את 3 ההזמנות הגדולות ביותר (לפי revenue) בכל channel באמצעות "
           "`rank()`.*",
     "sol": 'w_rev = Window.partitionBy("channel").orderBy(F.col("revenue").desc())\n'
            'o.withColumn("rnk", F.rank().over(w_rev)) \\\n'
            ' .filter(F.col("rnk") <= 3) \\\n'
            ' .select("channel", "order_id", "revenue", "rnk") \\\n'
            ' .orderBy("channel", "rnk").show(12)'},

    {"md": "**`rank` vs `dense_rank` — the difference shows up only on ties.** "
           "`revenue` is almost unique, so instead rank each **customer's** orders "
           "by `quantity` (an integer — lots of ties). Add both `rank()` and "
           "`dense_rank()` and show one customer: after a tie, `rank` **skips** the "
           "next number(s) while `dense_rank` keeps counting without gaps.\n\n"
           "*ההבדל בין `rank` ל-`dense_rank` מתגלה רק כשיש תיקו. `revenue` כמעט "
           "ייחודי, אז נדרג את הזמנות כל לקוח לפי `quantity` (מספר שלם — הרבה תיקו). "
           "אחרי תיקו `rank` מדלג על המספר הבא, ו-`dense_rank` ממשיך בלי פערים.*",
     "sol": 'w_qty = Window.partitionBy("customer_id").orderBy(F.col("quantity").desc())\n'
            'o.withColumn("rnk", F.rank().over(w_qty)) \\\n'
            ' .withColumn("dense", F.dense_rank().over(w_qty)) \\\n'
            ' .filter(F.col("customer_id") == "CUST-0001") \\\n'
            ' .select("order_id", "quantity", "rnk", "dense").show()'},

    {"md": "**Running total.** For each customer, compute the cumulative sum of "
           "`revenue` over time. Use the `w_time` window with "
           "`rowsBetween(Window.unboundedPreceding, Window.currentRow)`.\n\n"
           "*חשבו סכום מצטבר של `revenue` לכל לקוח לאורך זמן (running total).*",
     "sol": 'w_run = w_time.rowsBetween(Window.unboundedPreceding, Window.currentRow)\n'
            'o.withColumn("running_total", F.round(F.sum("revenue").over(w_run), 2)) \\\n'
            ' .select("customer_id", "order_ts", "revenue", "running_total").show(12)'},

    {"md": "**Compare to the previous order.** Add `prev_revenue = lag(revenue)` "
           "over `w_time`, and `delta = revenue - prev_revenue`. Show 12 rows.\n\n"
           "*הוסיפו את `revenue` של ההזמנה הקודמת (`lag`) וההפרש מההזמנה הנוכחית.*",
     "sol": 'o.withColumn("prev_revenue", F.lag("revenue").over(w_time)) \\\n'
            ' .withColumn("delta", F.round(F.col("revenue") - F.col("prev_revenue"), 2)) \\\n'
            ' .select("customer_id", "order_ts", "revenue", "prev_revenue", "delta").show(12)'},

    {"md": "**Each order's share of its customer's total.** Define a window "
           "partitioned by `customer_id` **without** `orderBy` (so it spans the "
           "whole partition), and compute "
           "`pct = revenue / sum(revenue) over that window`, as a percentage.\n\n"
           "*חשבו את החלק היחסי (%) של כל הזמנה מסך ההזמנות של אותו לקוח (window "
           "ללא `orderBy`).*",
     "sol": 'w_cust = Window.partitionBy("customer_id")\n'
            'o.withColumn("cust_total", F.sum("revenue").over(w_cust)) \\\n'
            ' .withColumn("pct", F.round(F.col("revenue") / F.col("cust_total") * 100, 1)) \\\n'
            ' .select("customer_id", "order_id", "revenue", "cust_total", "pct").show(12)'},

    {"md": "**Moving average.** For each customer, compute a 3-order moving average "
           "of `revenue` (current row + 2 previous) with "
           "`rowsBetween(-2, 0)`.\n\n"
           "*חשבו ממוצע נע של 3 הזמנות (הנוכחית + 2 הקודמות) לכל לקוח.*",
     "sol": 'w_ma = w_time.rowsBetween(-2, 0)\n'
            'o.withColumn("moving_avg", F.round(F.avg("revenue").over(w_ma), 2)) \\\n'
            ' .select("customer_id", "order_ts", "revenue", "moving_avg").show(12)'},

    {"md": "**One row per customer: their biggest order.** Use `row_number()` over "
           "`w_rev_cust` (partition by `customer_id`, order by `revenue` desc) and "
           "keep only `rn == 1`. Show 10 customers and their top order.\n\n"
           "*החזירו שורה אחת לכל לקוח — ההזמנה הגדולה ביותר שלו (`row_number()==1`).*",
     "sol": 'w_rev_cust = Window.partitionBy("customer_id").orderBy(F.col("revenue").desc())\n'
            'o.withColumn("rn", F.row_number().over(w_rev_cust)) \\\n'
            ' .filter(F.col("rn") == 1) \\\n'
            ' .select("customer_id", "order_id", "revenue").orderBy("customer_id").show(10)'},

    {"md": "**Split each customer into spend quartiles.** Add "
           "`quartile = ntile(4)` over `w_rev_cust`. Show 12 rows.\n\n"
           "*חלקו את הזמנות כל לקוח ל-4 רבעונים לפי `revenue` עם `ntile(4)`.*",
     "sol": 'o.withColumn("quartile", F.ntile(4).over(w_rev_cust)) \\\n'
            ' .select("customer_id", "order_id", "revenue", "quartile").show(12)'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "מה זה window function?",
     "body": "<p><code>groupBy</code> מכווץ שורות: 1000 הזמנות הופכות ל-4 שורות "
             "(אחת לכל status). <strong>window function</strong> שומרת את כל השורות, "
             "אבל לכל שורה מחשבת ערך שמסתכל על שורות אחרות באותה קבוצה.</p>"
             "<p>דוגמאות מהחיים: \"מה הדירוג של ההזמנה הזו בתוך ה-channel שלה?\", "
             "\"מה הסכום המצטבר עד עכשיו?\", \"מה היה ב-הזמנה הקודמת?\", \"איזה אחוז "
             "מסך ההזמנות של הלקוח זו ההזמנה הזו?\".</p>"},

    {"type": "text", "h2": "האנטומיה של חלון",
     "body": "<p>בונים חלון משלושה חלקים:</p>"
             "<ul>"
             "<li><code>partitionBy(...)</code> — לאיזו קבוצה כל שורה שייכת (כמו "
             "<code>GROUP BY</code>, אבל בלי לכווץ).</li>"
             "<li><code>orderBy(...)</code> — הסדר בתוך הקבוצה (חובה ל-ranking, "
             "ל-<code>lag</code>, ול-running totals).</li>"
             "<li><code>rowsBetween(...)</code> / <code>rangeBetween(...)</code> — "
             "המסגרת: אילו שורות נכנסות לחישוב (למשל \"מההתחלה עד השורה הנוכחית\").</li>"
             "</ul>"
             "<p><code>w = Window.partitionBy(\"customer_id\").orderBy(\"order_ts\")</code><br>"
             "<code>df.withColumn(\"seq\", F.row_number().over(w))</code></p>"},

    {"type": "text", "h2": "משפחות הפונקציות",
     "body": "<ul>"
             "<li><strong>דירוג</strong>: <code>row_number</code> (ייחודי), "
             "<code>rank</code> (מדלג על תיקו), <code>dense_rank</code> (לא מדלג), "
             "<code>ntile(n)</code> (חלוקה ל-n דליים).</li>"
             "<li><strong>שורות שכנות</strong>: <code>lag</code> (קודמת), "
             "<code>lead</code> (הבאה), <code>first</code>, <code>last</code>.</li>"
             "<li><strong>אגרגציה על חלון</strong>: <code>sum</code>, "
             "<code>avg</code>, <code>min</code>, <code>max</code>, <code>count</code> "
             "— עם מסגרת ל-running totals וממוצע נע.</li>"
             "</ul>"},

    {"type": "warn", "text": "<strong>partition של חלון ≠ partition פיזי.</strong> "
                             "<code>partitionBy</code> בחלון הוא קיבוץ לוגי לחישוב. "
                             "חלון בלי <code>partitionBy</code> שם את <em>כל</em> "
                             "המידע ב-partition אחד — איטי וזולל זיכרון. כמעט תמיד "
                             "תרצו <code>partitionBy</code>."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("הגדרת חלון", "Window.partitionBy()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Window.partitionBy.html"),
         ("מספר שורה רץ", "F.row_number()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.row_number.html"),
         ("דירוג עם דילוג", "F.rank()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.rank.html"),
         ("דירוג צפוף", "F.dense_rank()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.dense_rank.html"),
         ("ערך מהשורה הקודמת", "F.lag()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.lag.html"),
         ("ערך מהשורה הבאה", "F.lead()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.lead.html"),
         ("חלוקה ל-n דליים", "F.ntile()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.ntile.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את מדריך ה-Window Functions הרשמי — שם מוסבר ההבדל בין "
             "<code>rowsBetween</code> ל-<code>rangeBetween</code>, שחשוב מאוד.</p>",
     "pills": [("Window Functions Guide",
                "https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-window.html")] + H.DOCS_PILLS[:2]},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>הפרק הכי חשוב לעבודה אמיתית ב-Foundry. תתרגלו דירוג (top-N לכל "
             "קבוצה), running totals, השוואה לשורה קודמת (<code>lag</code>), חלק "
             "יחסי בקבוצה, וממוצע נע — כולם עם <code>Window</code>.</p>"},
    {"type": "tip", "text": "ההבדל המנטלי מ-<code>groupBy</code>: חלון "
                            "<strong>לא מכווץ</strong> שורות. כל שורה נשארת, ומקבלת "
                            "עמודה חדשה שמחושבת ביחס לקבוצה שלה."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>row_number</code>, <code>rank</code>, <code>dense_rank</code>, <code>ntile</code>",
        "Top-N לכל קבוצה (תבנית נפוצה מאוד)",
        "running total ו-moving average עם <code>rowsBetween</code>",
        "<code>lag</code> / <code>lead</code> להשוואה לשורות שכנות",
        "חלק יחסי של שורה בתוך הקבוצה שלה",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 04 — פונקציות חלון",
             kicker="Spark for Power Users · פרק 04", kicker_color=H.BRAND2,
             title="פונקציות חלון (Window Functions)",
             subtitle="הכלי הכי שימושי לעבודה אמיתית: דירוג, סכום מצטבר, והשוואה בין שורות.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 04 — התרגיל והמידע",
             kicker="פרק 04 · התרגיל והמידע", kicker_color=H.GREEN,
             title="דירוגים, סכומים מצטברים והשוואות",
             subtitle="לתרגל את כל משפחות פונקציות החלון על טבלת ההזמנות.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
