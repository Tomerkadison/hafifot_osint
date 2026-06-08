"""Chapter 09 — Capstone: Streamline Analytics."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "09_Capstone_Streamline_Analytics"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 09 — Capstone: Streamline Analytics"

INTRO_MD = (
    "You are a data engineer at **Streamline**, an online store. Two worlds of data "
    "have landed: the **transactional** tables (orders, customers, products, regions) "
    "and the **behavioural** clickstream (`events.jsonl`). Your mission: build an "
    "end-to-end analytics pipeline that a business team could actually use — clean, "
    "enrich, rank, pivot, fuse transactions with behaviour into a *customer-360* "
    "table, and write the result. This capstone uses everything from chapters 1–8.\n\n"
    "*אתם מהנדסי דאטה ב-Streamline, חנות אונליין. הגיעו שני עולמות: הטבלאות "
    "הטרנזקציוניות (orders, customers, products, regions) וה-clickstream ההתנהגותי "
    "(`events.jsonl`). המשימה: לבנות pipeline אנליטי מקצה-לקצה — לנקות, להעשיר, לדרג, "
    "לעשות pivot, לאחד טרנזקציות עם התנהגות לטבלת customer-360, ולכתוב את התוצאה. "
    "הפרויקט משתמש בכל מה שלמדתם בפרקים 1–8.*\n\n"
    "**Data:** `orders.csv`, `customers.csv`, `products.csv`, `regions.csv`, "
    "`events.jsonl`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read all five sources: `orders`, `customers`, `products`, `regions` "
           "(CSV, inferSchema) and `events` (JSON).\n\n*קראו את כל חמשת המקורות.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)\n'
            'customers = spark.read.csv("data/customers.csv", header=True, inferSchema=True)\n'
            'products = spark.read.csv("data/products.csv", header=True, inferSchema=True)\n'
            'regions = spark.read.csv("data/regions.csv", header=True, inferSchema=True)\n'
            'events = spark.read.json("data/events.jsonl")\n'
            'print(orders.count(), customers.count(), products.count(), regions.count(), events.count())'},

    {"md": "**Clean the orders.** Keep only real sales (`status == 'completed'` and "
           "`quantity > 0`), and add `revenue = round(quantity * unit_price, 2)`. "
           "Call it `sales`. How many rows remain?\n\n"
           "*נקו: רק מכירות אמיתיות (`completed`, כמות חיובית), והוסיפו `revenue`.*",
     "sol": 'sales = (orders\n'
            '         .filter((F.col("status") == "completed") & (F.col("quantity") > 0))\n'
            '         .withColumn("revenue", F.round(F.col("quantity") * F.col("unit_price"), 2)))\n'
            'sales.count()'},

    {"md": "**Enrich.** Join `sales` to `customers`, then `regions` (on `region_id`), "
           "then `products` (on `product_sku`) into `fact`. Show "
           "`order_id, region_name, category, segment, revenue` for 5 rows.\n\n"
           "*העשירו: חברו את `sales` ל-customers, regions, products לטבלת `fact`.*",
     "sol": 'fact = (sales\n'
            '        .join(customers, "customer_id")\n'
            '        .join(regions, "region_id")\n'
            '        .join(products, "product_sku"))\n'
            'fact.select("order_id", "region_name", "category", "segment", "revenue").show(5)'},

    {"md": "**KPI 1 — revenue by region.** Total revenue per `region_name`, highest "
           "first.\n\n*הכנסה כוללת לכל אזור.*",
     "sol": 'fact.groupBy("region_name") \\\n'
            '    .agg(F.round(F.sum("revenue"), 2).alias("revenue")) \\\n'
            '    .orderBy(F.col("revenue").desc()).show()'},

    {"md": "**KPI 2 — a region × category matrix.** Use `pivot` to get total revenue "
           "with `region_name` as rows and `category` as columns.\n\n"
           "*מטריצת אזור × קטגוריה עם `pivot`.*",
     "sol": 'fact.groupBy("region_name").pivot("category") \\\n'
            '    .agg(F.round(F.sum("revenue"), 0)) \\\n'
            '    .orderBy("region_name").show()'},

    {"md": "**KPI 3 — top 3 products per region.** Sum revenue per "
           "(`region_name`, `product_name`), then use a window ranked by revenue "
           "within each region and keep the top 3.\n\n"
           "*3 המוצרים המובילים בכל אזור (groupBy + window).*",
     "sol": 'from pyspark.sql.window import Window\n\n'
            'prod_rev = fact.groupBy("region_name", "product_name") \\\n'
            '               .agg(F.round(F.sum("revenue"), 2).alias("revenue"))\n'
            'w = Window.partitionBy("region_name").orderBy(F.col("revenue").desc())\n'
            'prod_rev.withColumn("rnk", F.row_number().over(w)) \\\n'
            '        .filter(F.col("rnk") <= 3) \\\n'
            '        .orderBy("region_name", "rnk").show(15)'},

    {"md": "**Customer value.** Per customer, compute `total_spent`, `n_orders`, and "
           "`last_order` (max `order_ts`). Call it `cust_value`. Show the top 5 "
           "spenders.\n\n"
           "*ערך לקוח: סך הוצאה, מספר הזמנות, ותאריך הזמנה אחרון לכל לקוח.*",
     "sol": 'cust_value = sales.groupBy("customer_id").agg(\n'
            '    F.round(F.sum("revenue"), 2).alias("total_spent"),\n'
            '    F.count("*").alias("n_orders"),\n'
            '    F.max("order_ts").alias("last_order"),\n'
            ')\n'
            'cust_value.orderBy(F.col("total_spent").desc()).show(5)'},

    {"md": "**Rank customers into spend deciles.** Add `decile = ntile(10)` over a "
           "window ordered by `total_spent` descending (decile 1 = top spenders). "
           "Show 10 rows.\n\n"
           "*דרגו לקוחות ל-10 עשירונים לפי הוצאה (`ntile(10)`).*",
     "sol": 'w_spend = Window.orderBy(F.col("total_spent").desc())\n'
            'cust_ranked = cust_value.withColumn("decile", F.ntile(10).over(w_spend))\n'
            'cust_ranked.select("customer_id", "total_spent", "decile").show(10)'},

    {"md": "**Behavioural side — the funnel.** From `events`, count events per "
           "`event_type`, ordered most to least (the classic page_view → search → "
           "add_to_cart → purchase funnel).\n\n"
           "*משפך התנהגותי: ספירת אירועים לכל `event_type`.*",
     "sol": 'events.groupBy("event_type").count().orderBy(F.col("count").desc()).show()'},

    {"md": "**Purchases by device.** Explode the `items` array of `purchase` events "
           "and compute purchase revenue (`qty * price`) per `device.os`.\n\n"
           "*הכנסה מרכישות לכל מערכת הפעלה (explode של `items`).*",
     "sol": 'purchase_lines = (events\n'
            '    .filter(F.col("event_type") == "purchase")\n'
            '    .select("device.os", F.explode("items").alias("item")))\n'
            'purchase_lines.groupBy("os") \\\n'
            '    .agg(F.round(F.sum(F.col("item.qty") * F.col("item.price")), 2).alias("revenue")) \\\n'
            '    .orderBy(F.col("revenue").desc()).show()'},

    {"md": "**Fuse the two worlds — customer-360.** Build per-user event counts from "
           "`events` (rename `user_id` → `customer_id`), then **left join** "
           "`customers` → `cust_value` → event counts so every customer appears even "
           "with no orders/events. Fill missing numbers with 0. Show 10 rows of "
           "`customer_id, segment, total_spent, n_orders, n_events`.\n\n"
           "*אחדו את שני העולמות לטבלת customer-360 עם left joins ומילוי 0.*",
     "sol": 'event_counts = events.groupBy(F.col("user_id").alias("customer_id")) \\\n'
            '                      .agg(F.count("*").alias("n_events"))\n'
            'c360 = (customers\n'
            '        .join(cust_value, "customer_id", "left")\n'
            '        .join(event_counts, "customer_id", "left")\n'
            '        .fillna({"total_spent": 0, "n_orders": 0, "n_events": 0}))\n'
            'c360.select("customer_id", "segment", "total_spent", "n_orders", "n_events").show(10)'},

    {"md": "**A KPI in pure SQL.** Register `c360` as a temp view and, with "
           "`spark.sql`, return average `total_spent` and average `n_events` "
           "**per `segment`**.\n\n"
           "*KPI ב-SQL טהור: ממוצע הוצאה וממוצע אירועים לכל segment.*",
     "sol": 'c360.createOrReplaceTempView("c360")\n'
            'spark.sql("""\n'
            '    SELECT segment,\n'
            '           round(avg(total_spent), 2) AS avg_spent,\n'
            '           round(avg(n_events), 1)   AS avg_events\n'
            '    FROM c360\n'
            '    GROUP BY segment\n'
            '    ORDER BY avg_spent DESC\n'
            '""").show()'},

    {"md": "**Ship it.** Write the enriched `fact` table as Parquet, partitioned by "
           "`region_name`, into a temp folder. List the partition directories to "
           "confirm.\n\n"
           "*שלחו לפרודקשן: כתבו את `fact` כ-Parquet מחולק לפי `region_name`.*",
     "sol": 'import tempfile, os\n'
            'OUT = tempfile.mkdtemp()\n'
            'path = os.path.join(OUT, "fact")\n'
            'fact.write.mode("overwrite").partitionBy("region_name").parquet(path)\n'
            'print(sorted(os.listdir(path)))'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "המשימה",
     "body": "<p>זה הפרויקט המסכם. אין כאן חומר חדש — יש כאן <strong>הרכבה</strong> "
             "של הכול למשהו שדומה ל-pipeline אמיתי ב-Foundry: ניקוי, העשרה (joins), "
             "אגרגציות ו-pivot, דירוגים עם window, פיצוץ אירועים מקוננים, איחוד "
             "טרנזקציות עם התנהגות, וכתיבה מחולקת.</p>"
             "<p>קחו את הזמן. כל שאלה בונה על הקודמת.</p>"},

    {"type": "list", "h2": "צעדי ה-pipeline",
     "ordered": True,
     "items": [
         "<strong>Ingest</strong> — לקרוא 5 מקורות (CSV + JSON).",
         "<strong>Clean</strong> — לסנן מכירות אמיתיות, לחשב <code>revenue</code>.",
         "<strong>Enrich</strong> — join של 4 טבלאות לטבלת <code>fact</code>.",
         "<strong>Aggregate</strong> — הכנסה לפי אזור, ו-pivot אזור × קטגוריה.",
         "<strong>Rank</strong> — top-3 מוצרים לאזור, ועשירוני לקוחות (window).",
         "<strong>Behaviour</strong> — funnel, ו-explode של רכישות לפי מכשיר.",
         "<strong>Fuse</strong> — טבלת customer-360 (left joins + fillna).",
         "<strong>Ship</strong> — כתיבת Parquet מחולק.",
     ]},

    {"type": "text", "h2": "מה ייבדק",
     "body": "<p>האם אתם יודעים לשלב את כל הכלים: לבחור את ה-join הנכון, לדעת מתי "
             "<code>groupBy</code> ומתי <code>Window</code>, לטפל ב-null אחרי left "
             "join, ולפצח מבנה מקונן. זה בדיוק מה שעושים ביום-יום על datasets "
             "אמיתיים.</p>"},

    {"type": "tip", "text": "תקועים בשאלה? חזרו לפרק הרלוונטי — כל כלי כאן הופיע כבר "
                            "באחד הפרקים 1–8."},

    {"type": "cta", "h2": "🎯 אחרי שתסיימו",
     "body": "<p>השוו את הפלט שלכם ל-<code>Solutions.ipynb</code>. ואז — נסו לשפר: "
             "אילו joins כדאי ל-broadcast? איפה <code>cache</code> יעזור? הריצו "
             "<code>explain</code> על ה-pipeline המלא.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על הפרויקט",
     "body": "<p>פרויקט מסכם מקצה-לקצה: מ-5 מקורות גולמיים ועד טבלת customer-360 "
             "ו-Parquet מחולק. 14 שלבים שמרכיבים pipeline אמיתי.</p>"},
    {"type": "datatable", "h2": "טבלת העובדות: <code>orders.csv</code>",
     "rows": shared.ORDERS_COLS},
    {"type": "datatable", "h2": "טבלת לקוחות: <code>customers.csv</code>",
     "rows": shared.CUSTOMERS_COLS},
    {"type": "list", "h2": "מקורות נוספים", "items": [
        "<code>products.csv</code> — <code>product_sku, product_name, category, "
        "brand, unit_cost, list_price</code>",
        "<code>regions.csv</code> — <code>region_id, region_name, currency, "
        "tax_rate</code>",
        "<code>events.jsonl</code> — clickstream מקונן עם <code>device</code>, "
        "<code>geo</code>, ומערך <code>items</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 09 — פרויקט מסכם",
             kicker="Spark for Power Users · פרק 09", kicker_color=H.BRAND2,
             title="פרויקט מסכם: Streamline Analytics",
             subtitle="להרכיב את הכול ל-pipeline אנליטי אמיתי מקצה לקצה.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 09 — הפרויקט והמידע",
             kicker="פרק 09 · הפרויקט המסכם 🎯", kicker_color=H.GREEN,
             title="מ-5 מקורות גולמיים ל-customer-360",
             subtitle="ניקוי, העשרה, דירוג, איחוד התנהגות וטרנזקציות, וכתיבה.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
