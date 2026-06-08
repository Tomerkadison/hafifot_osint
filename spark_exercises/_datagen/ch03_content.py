"""Chapter 03 — Spark SQL."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "03_Spark_SQL"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 03 — Spark SQL"

INTRO_MD = (
    "Here is something pandas and Polars simply do not have: you can write "
    "**plain SQL** against your DataFrames and get a DataFrame back. Register a "
    "DataFrame as a *temp view*, then `spark.sql(\"SELECT ...\")`. The SQL engine "
    "and the DataFrame API are the *same engine* — you can switch between them "
    "freely, mid-pipeline. In Foundry many transforms are written exactly this "
    "way.\n\n"
    "*הנה משהו של-pandas ול-Polars פשוט אין: אפשר לכתוב SQL רגיל על ה-DataFrames "
    "ולקבל DataFrame בחזרה. רושמים DataFrame כ-temp view, ואז "
    "`spark.sql(\"SELECT ...\")`. מנוע ה-SQL ו-DataFrame API הם אותו מנוע — אפשר "
    "לעבור ביניהם חופשי באמצע ה-pipeline.*\n\n"
    "**Data files:** `data/orders.csv`, `data/customers.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/orders.csv` and `data/customers.csv` (both `header=True`, "
           "`inferSchema=True`).\n\n*קראו את שני הקבצים.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)\n'
            'customers = spark.read.csv("data/customers.csv", header=True, inferSchema=True)'},

    {"md": "Register both as **temp views** named `orders` and `customers` using "
           "`createOrReplaceTempView`.\n\n"
           "*רשמו את שניהם כ-temp views בשמות `orders` ו-`customers`.*",
     "sol": 'orders.createOrReplaceTempView("orders")\n'
            'customers.createOrReplaceTempView("customers")'},

    {"md": "Run your first SQL query: `SELECT * FROM orders LIMIT 5`. Note that "
           "`spark.sql(...)` returns a **DataFrame**, so you still call `show()`.\n\n"
           "*הריצו שאילתת SQL ראשונה. שימו לב ש-`spark.sql` מחזיר DataFrame.*",
     "sol": 'spark.sql("SELECT * FROM orders LIMIT 5").show()'},

    {"md": "Using SQL, count how many orders have `status = 'completed'`.\n\n"
           "*ב-SQL, ספרו כמה הזמנות הן `completed`.*",
     "sol": 'spark.sql("SELECT count(*) AS n FROM orders WHERE status = \'completed\'").show()'},

    {"md": "Using SQL, compute **revenue per channel** "
           "(`sum(quantity*unit_price)`), only for positive quantities, rounded to "
           "2 decimals, highest first.\n\n"
           "*ב-SQL, חשבו הכנסה לכל channel (רק כמויות חיוביות), ממוין מהגבוה לנמוך.*",
     "sol": 'spark.sql("""\n'
            '    SELECT channel,\n'
            '           round(sum(quantity * unit_price), 2) AS revenue\n'
            '    FROM orders\n'
            '    WHERE quantity > 0\n'
            '    GROUP BY channel\n'
            '    ORDER BY revenue DESC\n'
            '""").show()'},

    {"md": "**Mix the two worlds.** Run a SQL query that returns completed orders, "
           "keep the result in a Python variable `completed`, then continue with the "
           "**DataFrame API** — `completed.select(...).show()`.\n\n"
           "*ערבבו את שני העולמות: הריצו SQL, שמרו את התוצאה, והמשיכו עם DataFrame "
           "API.*",
     "sol": 'completed = spark.sql("SELECT * FROM orders WHERE status = \'completed\'")\n'
            'completed.select("order_id", "channel", "unit_price").show(5)'},

    {"md": "**JOIN in SQL.** Join `orders` to `customers` on `customer_id` and "
           "compute revenue **per customer `segment`** (positive quantities only), "
           "highest first.\n\n"
           "*JOIN ב-SQL: חברו orders ל-customers וחשבו הכנסה לכל segment.*",
     "sol": 'spark.sql("""\n'
            '    SELECT c.segment,\n'
            '           round(sum(o.quantity * o.unit_price), 2) AS revenue\n'
            '    FROM orders o\n'
            '    JOIN customers c ON o.customer_id = c.customer_id\n'
            '    WHERE o.quantity > 0\n'
            '    GROUP BY c.segment\n'
            '    ORDER BY revenue DESC\n'
            '""").show()'},

    {"md": "Use a **CTE** (`WITH`) to first compute revenue per customer, then "
           "return the **top 5 customers** by revenue.\n\n"
           "*השתמשו ב-CTE (`WITH`) כדי לחשב הכנסה לכל לקוח, והחזירו את 5 הלקוחות "
           "המובילים.*",
     "sol": 'spark.sql("""\n'
            '    WITH per_customer AS (\n'
            '        SELECT customer_id,\n'
            '               sum(quantity * unit_price) AS revenue\n'
            '        FROM orders\n'
            '        WHERE quantity > 0\n'
            '        GROUP BY customer_id\n'
            '    )\n'
            '    SELECT customer_id, round(revenue, 2) AS revenue\n'
            '    FROM per_customer\n'
            '    ORDER BY revenue DESC\n'
            '    LIMIT 5\n'
            '""").show()'},

    {"md": "**SQL inside the DataFrame API.** Use `F.expr(...)` to add a column "
           "`revenue = quantity * unit_price` written as a SQL string, and a "
           "`CASE WHEN` column `size` ('big' if revenue ≥ 100 else 'small'). Show 5 "
           "rows.\n\n"
           "*SQL בתוך ה-API: השתמשו ב-`F.expr` להוספת עמודה ו-`CASE WHEN`.*",
     "sol": 'orders.withColumn("revenue", F.expr("quantity * unit_price")) \\\n'
            '      .withColumn("size", F.expr("CASE WHEN quantity * unit_price >= 100 THEN \'big\' ELSE \'small\' END")) \\\n'
            '      .select("order_id", "revenue", "size").show(5)'},

    {"md": "Register the `completed` DataFrame from earlier as a temp view "
           "`completed_orders`, then query it with SQL to count rows per "
           "`payment_method`.\n\n"
           "*רשמו את `completed` כ-view ושאלו אותו ב-SQL — ספירה לכל "
           "`payment_method`.*",
     "sol": 'completed.createOrReplaceTempView("completed_orders")\n'
            'spark.sql("""\n'
            '    SELECT payment_method, count(*) AS n\n'
            '    FROM completed_orders\n'
            '    GROUP BY payment_method\n'
            '    ORDER BY n DESC\n'
            '""").show()'},

    {"md": "List all the temp views you have registered with "
           "`spark.catalog.listTables()`.\n\n"
           "*הציגו את כל ה-views שרשמתם עם `spark.catalog.listTables()`.*",
     "sol": "spark.catalog.listTables()"},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "אותו מנוע, שתי שפות",
     "body": "<p>זו אחת התכונות הכי שימושיות ב-Spark: <code>DataFrame</code> ו-SQL "
             "הם <strong>אותו מנוע</strong> בדיוק. כל שאילתת SQL עוברת דרך אותו "
             "Catalyst optimizer כמו ה-API, ומחזירה DataFrame רגיל.</p>"
             "<p>המשמעות: אתם יכולים לכתוב חלק מה-pipeline ב-SQL, חלק ב-API, "
             "ולעבור ביניהם באמצע — מה שנוח יותר לכל שלב.</p>"},

    {"type": "text", "h2": "שלושת השלבים",
     "body": "<ol>"
             "<li>רושמים DataFrame כ-<strong>temp view</strong>: "
             "<code>df.createOrReplaceTempView(\"orders\")</code></li>"
             "<li>כותבים SQL: <code>spark.sql(\"SELECT ... FROM orders\")</code></li>"
             "<li>מקבלים DataFrame בחזרה — וממשיכים עם <code>show</code>, "
             "<code>filter</code>, או SQL נוסף.</li>"
             "</ol>"
             "<p>ל-multi-line SQL השתמשו במחרוזת משולשת <code>\"\"\"...\"\"\"</code>.</p>"},

    {"type": "compare", "h2": "API מול SQL — אותה תוצאה",
     "intro": "שתי הדרכים שקולות לחלוטין:",
     "left_title": "DataFrame API", "left": [
         "<code>orders.filter(F.col('quantity')>0)</code>",
         "<code>.groupBy('channel')</code>",
         "<code>.agg(F.sum('unit_price'))</code>",
     ],
     "right_title": "Spark SQL", "right": [
         "<code>SELECT channel, sum(unit_price)</code>",
         "<code>FROM orders WHERE quantity>0</code>",
         "<code>GROUP BY channel</code>",
     ],
     "note": "💡 גם <code>F.expr(\"...\")</code> מאפשר לשתול קטע SQL בתוך ה-API — "
             "מושלם ל-<code>CASE WHEN</code> מסובך."},

    {"type": "warn", "text": "<code>createOrReplaceTempView</code> חי רק כל עוד "
                             "ה-SparkSession פתוח, ורק ב-session הנוכחי. ל-view "
                             "שנראה מכל ה-sessions יש <code>createGlobalTempView</code>."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("רישום temp view", "DataFrame.createOrReplaceTempView()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.createOrReplaceTempView.html"),
         ("הרצת SQL", "spark.sql()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.sql.html"),
         ("ביטוי SQL בתוך ה-API", "F.expr()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.expr.html"),
         ("בחירה עם ביטויי SQL", "DataFrame.selectExpr()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.selectExpr.html"),
         ("רשימת הטבלאות/views", "spark.catalog.listTables()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.listTables.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את ה-SQL Programming Guide ואת רשימת פונקציות ה-SQL המובנות "
             "— הן זהות לפונקציות שב-<code>F.*</code>.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל שכולו על כוח ה-SQL של Spark: temp views, "
             "<code>spark.sql</code>, JOIN ו-GROUP BY ב-SQL, CTE עם "
             "<code>WITH</code>, וערבוב חופשי בין SQL ל-DataFrame API.</p>"},
    {"type": "tip", "text": "כל <code>spark.sql(...)</code> מחזיר DataFrame — אז "
                            "תמיד אפשר להוסיף אחריו <code>.show()</code> או "
                            "<code>.filter()</code>."},
    {"type": "datatable", "h2": "המידע: <code>orders.csv</code> + <code>customers.csv</code>",
     "intro": "טבלת ההזמנות וטבלת הלקוחות — מחוברות דרך <code>customer_id</code>.",
     "rows": shared.ORDERS_COLS + [("—", "", "")] + shared.CUSTOMERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>createOrReplaceTempView</code> ו-<code>spark.sql</code>",
        "<code>WHERE</code>, <code>GROUP BY</code>, <code>ORDER BY</code> ב-SQL",
        "<code>JOIN</code> ב-SQL בין שתי טבלאות",
        "<code>WITH</code> (CTE) לשאילתה רב-שלבית",
        "ערבוב SQL ו-API, ו-<code>F.expr</code> / <code>CASE WHEN</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 03 — Spark SQL",
             kicker="Spark for Power Users · פרק 03", kicker_color=H.BRAND2,
             title="Spark SQL",
             subtitle="לכתוב SQL רגיל על DataFrames — אותו מנוע, שתי שפות.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 03 — התרגיל והמידע",
             kicker="פרק 03 · התרגיל והמידע", kicker_color=H.GREEN,
             title="שאילתות SQL על ההזמנות",
             subtitle="temp views, JOIN ו-CTE ב-SQL, וערבוב חופשי עם ה-DataFrame API.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
