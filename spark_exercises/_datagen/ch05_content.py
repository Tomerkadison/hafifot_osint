"""Chapter 05 — Joins & Shuffles (mission chapter)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "05_Joins_and_Shuffles"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 05 — Joins & Shuffles"

INTRO_MD = (
    "Joins are the heart of every Foundry pipeline — and in Spark a join is also "
    "where the most expensive thing in distributed computing happens: a **shuffle**, "
    "where data flies across the network so matching keys end up on the same "
    "machine. This mission chapter covers every join type (including the "
    "SQL-flavoured `semi` / `anti`), how to read a join in `explain()`, and the "
    "**broadcast join** trick that avoids the shuffle for small tables.\n\n"
    "*Joins הם הלב של כל pipeline ב-Foundry — וב-Spark join הוא גם המקום שבו קורה "
    "הדבר היקר ביותר בחישוב מבוזר: shuffle, שבו מידע עף ברשת כדי שמפתחות תואמים "
    "ינחתו על אותו מחשב. פרק-המשימה הזה מכסה כל סוגי ה-join (כולל `semi`/`anti`), "
    "איך לקרוא join ב-`explain()`, ואת טריק ה-broadcast join שחוסך shuffle לטבלאות "
    "קטנות.*\n\n"
    "**Data files:** `orders.csv`, `customers.csv`, `products.csv`, `regions.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read all four files (`header=True`, `inferSchema=True`): `orders`, "
           "`customers`, `products`, `regions`.\n\n*קראו את כל ארבעת הקבצים.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)\n'
            'customers = spark.read.csv("data/customers.csv", header=True, inferSchema=True)\n'
            'products = spark.read.csv("data/products.csv", header=True, inferSchema=True)\n'
            'regions = spark.read.csv("data/regions.csv", header=True, inferSchema=True)\n'
            'print(orders.count(), customers.count(), products.count(), regions.count())'},

    {"md": "**Inner join** `orders` to `customers` on `customer_id` (pass the key as "
           "a string so the column is not duplicated). Show `order_id`, "
           "`customer_name`, `segment`, `quantity` for 5 rows.\n\n"
           "*חברו (inner) את orders ל-customers על `customer_id`.*",
     "sol": 'enriched = orders.join(customers, "customer_id", "inner")\n'
            'enriched.select("order_id", "customer_name", "segment", "quantity").show(5)'},

    {"md": "Confirm the inner join kept every order: compare "
           "`orders.join(customers, \"customer_id\").count()` to "
           "`orders.count()`.\n\n"
           "*ודאו שה-join שמר על כל ההזמנות — השוו את הספירות.*",
     "sol": 'print("joined:", orders.join(customers, "customer_id").count())\n'
            'print("orders:", orders.count())'},

    {"md": "**Left anti join** — find customers who have **no orders at all**. "
           "(`customers.join(orders, \"customer_id\", \"left_anti\")`). How many are "
           "there, and show 5.\n\n"
           "*מצאו לקוחות בלי אף הזמנה עם `left_anti`.*",
     "sol": 'no_orders = customers.join(orders, "customer_id", "left_anti")\n'
            'print("customers with no orders:", no_orders.count())\n'
            'no_orders.select("customer_id", "customer_name", "segment").show(5)'},

    {"md": "**Left semi join** — keep only the customers who **do** have orders. "
           "Note a semi join returns **only the left table's columns** (it is a "
           "filter, not a real join). How many?\n\n"
           "*שמרו רק לקוחות שיש להם הזמנות עם `left_semi` — מחזיר רק עמודות "
           "מהטבלה השמאלית.*",
     "sol": 'with_orders = customers.join(orders, "customer_id", "left_semi")\n'
            'print("customers with orders:", with_orders.count())\n'
            'with_orders.show(5)'},

    {"md": "**Multi-table join.** Enrich `orders` with `customers`, then `regions` "
           "(on `region_id`), then `products` (on `product_sku`). Add "
           "`revenue = quantity * unit_price` and show "
           "`order_id, region_name, category, segment, revenue` for 5 rows.\n\n"
           "*שרשרו join של 4 טבלאות לטבלה מועשרת אחת.*",
     "sol": 'full = (orders\n'
            '        .join(customers, "customer_id")\n'
            '        .join(regions, "region_id")\n'
            '        .join(products, "product_sku")\n'
            '        .withColumn("revenue", F.round(F.col("quantity") * F.col("unit_price"), 2)))\n'
            'full.select("order_id", "region_name", "category", "segment", "revenue").show(5)'},

    {"md": "Using the `full` table, compute **revenue per `region_name`** (positive "
           "quantities only), highest first.\n\n"
           "*חשבו הכנסה לכל `region_name` מהטבלה המועשרת.*",
     "sol": 'full.filter(F.col("quantity") > 0) \\\n'
            '    .groupBy("region_name") \\\n'
            '    .agg(F.round(F.sum("revenue"), 2).alias("revenue")) \\\n'
            '    .orderBy(F.col("revenue").desc()).show()'},

    {"md": "**See the shuffle.** Call `.explain()` on "
           "`orders.join(customers, \"customer_id\")` and find the `Exchange` "
           "(that is the shuffle) and the `SortMergeJoin`.\n\n"
           "*ראו את ה-shuffle: הריצו `explain()` על join רגיל וחפשו `Exchange` "
           "ו-`SortMergeJoin`.*",
     "sol": 'orders.join(customers, "customer_id").explain()'},

    {"md": "**Broadcast join.** `regions` is tiny (5 rows), so broadcasting it "
           "avoids the shuffle entirely. Wrap it in `F.broadcast(...)`, join, and "
           "call `.explain()` — you should now see `BroadcastHashJoin` instead of "
           "`SortMergeJoin`.\n\n"
           "*Broadcast join: עטפו את `regions` ב-`F.broadcast` והריצו `explain` — "
           "תראו `BroadcastHashJoin` במקום `SortMergeJoin`.*",
     "sol": 'customers.join(F.broadcast(regions), "region_id").explain()'},

    {"md": "**Watch out for ambiguous columns.** Both `orders` and a renamed "
           "`customers` share `customer_id`. Join on an explicit condition "
           "`orders.customer_id == customers.customer_id` and then try to select "
           "`\"customer_id\"`... it is ambiguous. The fix: join on the **string "
           "key** (as we did), or `drop` one side. Here, do it the safe way and "
           "select the customer's `region_id`.\n\n"
           "*זהירות מעמודות כפולות אחרי join. הדרך הבטוחה: join על מפתח כמחרוזת.*",
     "sol": '# safe: string key -> single customer_id column, no ambiguity\n'
            'orders.join(customers, "customer_id").select("order_id", "customer_id", "region_id").show(5)'},

    {"md": "Per `segment`, count **distinct customers who placed orders** and total "
           "revenue. Join orders+customers, then `groupBy('segment')` with "
           "`countDistinct('customer_id')` and `sum(quantity*unit_price)`.\n\n"
           "*לכל segment: כמה לקוחות שונים הזמינו, ומה ההכנסה הכוללת.*",
     "sol": 'orders.join(customers, "customer_id") \\\n'
            '      .filter(F.col("quantity") > 0) \\\n'
            '      .groupBy("segment") \\\n'
            '      .agg(F.countDistinct("customer_id").alias("buyers"),\n'
            '           F.round(F.sum(F.col("quantity") * F.col("unit_price")), 2).alias("revenue")) \\\n'
            '      .orderBy(F.col("revenue").desc()).show()'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "join ב-Spark — ומה זה shuffle",
     "body": "<p>join מחבר שתי טבלאות לפי מפתח. ב-pandas/Polars זה קורה בזיכרון של "
             "מחשב אחד. ב-Spark, השורות של כל טבלה מפוזרות על מכונות שונות — אז כדי "
             "ש-מפתחות תואמים ייפגשו, Spark חייב <strong>להזיז מידע ברשת</strong>. "
             "זה ה-<strong>shuffle</strong>, והפעולה היקרה ביותר בחישוב מבוזר.</p>"
             "<p>ב-<code>explain()</code> ה-shuffle מופיע בתור <code>Exchange</code>, "
             "וה-join עצמו בתור <code>SortMergeJoin</code>.</p>"},

    {"type": "text", "h2": "סוגי join",
     "body": "<ul>"
             "<li><code>inner</code> — רק שורות עם התאמה בשני הצדדים.</li>"
             "<li><code>left</code> / <code>right</code> / <code>outer</code> — "
             "שומר את כל השורות מצד אחד / שני / שניהם, עם <code>null</code> בחוסר.</li>"
             "<li><code>left_semi</code> — כמו <code>inner</code>, אבל מחזיר "
             "<strong>רק את עמודות הצד השמאלי</strong>. זה בעצם \"סנן לשורות שיש "
             "להן התאמה\".</li>"
             "<li><code>left_anti</code> — ההפך: שורות שמאליות <strong>בלי</strong> "
             "התאמה. מצוין למציאת \"יתומים\".</li>"
             "</ul>"
             "<p><code>semi</code>/<code>anti</code> כמעט לא קיימים ב-pandas — שם "
             "צריך טריקים. ב-Spark זה join מובנה.</p>"},

    {"type": "text", "h2": "Broadcast join — לעקוף את ה-shuffle",
     "body": "<p>אם אחת הטבלאות <strong>קטנה</strong> (טבלת ממדים: regions, "
             "products), אפשר לשלוח עותק שלה לכל executor במקום להזיז את הטבלה "
             "הגדולה. זה <strong>broadcast join</strong>, והוא חוסך את ה-shuffle "
             "לגמרי.</p>"
             "<p><code>big.join(F.broadcast(small), \"key\")</code></p>"
             "<p>ב-<code>explain()</code> תראו <code>BroadcastHashJoin</code>. Spark "
             "גם עושה זאת אוטומטית לטבלאות מתחת ל-<code>spark.sql."
             "autoBroadcastJoinThreshold</code> (10MB כברירת מחדל).</p>"},

    {"type": "compare", "h2": "join: pandas מול Spark",
     "left_title": "🐼 pandas", "left": [
         "<code>pd.merge(a, b, on='k')</code>",
         "<code>how='inner'/'left'/...</code>",
         "אין <code>semi</code>/<code>anti</code> מובנה",
         "הכול בזיכרון, ללא shuffle",
     ],
     "right_title": "🔥 Spark", "right": [
         "<code>a.join(b, 'k', 'inner')</code>",
         "<code>'inner'/'left'/'left_semi'/'left_anti'</code>",
         "<code>semi</code>/<code>anti</code> מובנים",
         "shuffle על פני הרשת (או broadcast)",
     ],
     "note": "💡 חברו על מפתח כ<strong>מחרוזת</strong> "
             "(<code>a.join(b, \"customer_id\")</code>) כדי שלא תיווצר עמודה כפולה "
             "מעורפלת."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("חיבור טבלאות", "DataFrame.join()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.join.html"),
         ("רמז ל-broadcast join", "F.broadcast()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.broadcast.html"),
         ("ספירת ערכים ייחודיים", "F.countDistinct()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.count_distinct.html"),
         ("הצגת התוכנית", "DataFrame.explain()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.explain.html"),
         ("הסרת עמודה אחרי join", "DataFrame.drop()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.drop.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את מדריך ה-Performance Tuning על join strategies — מתי Spark "
             "בוחר SortMerge, מתי Broadcast, ומה זה shuffle hash join.</p>",
     "pills": [("Join Hints",
                "https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-hints.html")] + H.DOCS_PILLS[:2]},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>פרק-משימה: תבנו טבלה מועשרת מ-4 מקורות, תכירו את כל סוגי ה-join "
             "(כולל <code>semi</code>/<code>anti</code>), תראו shuffle ב-"
             "<code>explain</code>, ותשתמשו ב-broadcast join לטבלאות קטנות.</p>"},
    {"type": "tip", "text": "חברו על מפתח כ<strong>מחרוזת</strong> — "
                            "<code>a.join(b, \"customer_id\")</code> — וכך תימנעו "
                            "מעמודת מפתח כפולה ומעורפלת."},
    {"type": "datatable", "h2": "טבלת העובדות: <code>orders.csv</code>",
     "rows": shared.ORDERS_COLS},
    {"type": "datatable", "h2": "טבלת לקוחות: <code>customers.csv</code>",
     "rows": shared.CUSTOMERS_COLS},
    {"type": "list", "h2": "טבלאות הממדים הקטנות", "items": [
        "<code>products.csv</code> — <code>product_sku, product_name, category, "
        "brand, unit_cost, list_price</code>",
        "<code>regions.csv</code> — <code>region_id, region_name, currency, "
        "tax_rate</code> (5 שורות — מועמדת מושלמת ל-broadcast)",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 05 — Joins ו-Shuffles",
             kicker="Spark for Power Users · פרק 05", kicker_color=H.BRAND2,
             title="Joins ו-Shuffles",
             subtitle="לחבר טבלאות — ולהבין את ה-shuffle, הפעולה היקרה ביותר בחישוב מבוזר.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 05 — התרגיל והמידע",
             kicker="פרק 05 · התרגיל והמידע 🎯", kicker_color=H.GREEN,
             title="חיבור 4 טבלאות לאנליטיקה אחת",
             subtitle="כל סוגי ה-join, broadcast, וקריאת ה-shuffle ב-explain.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
