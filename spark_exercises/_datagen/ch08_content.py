"""Chapter 08 — Schemas, Reading & Writing."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "08_Schemas_Reading_and_Writing"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 08 — Schemas, Reading & Writing"

INTRO_MD = (
    "In pandas you `read_csv` and move on. In Spark — and especially in Foundry — "
    "**the schema is a first-class decision**. `inferSchema` is convenient but reads "
    "your data an extra time; in production you give Spark an explicit schema. This "
    "chapter covers schema-on-read, casting dirty string columns, and writing "
    "**Parquet** — including `partitionBy`, the layout that powers fast, "
    "partition-pruned reads on real datasets.\n\n"
    "*ב-pandas עושים `read_csv` וממשיכים. ב-Spark — ובמיוחד ב-Foundry — ה-schema "
    "היא החלטה מרכזית. `inferSchema` נוח אבל קורא את המידע פעם נוספת; בפרודקשן נותנים "
    "ל-Spark schema מפורש. הפרק מכסה schema-on-read, casting של עמודות מחרוזת "
    "מלוכלכות, וכתיבת Parquet — כולל `partitionBy`, המבנה שמאפשר קריאות מהירות עם "
    "partition pruning.*\n\n"
    "**Data files:** `data/orders.csv`, `data/customers.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/orders.csv` with **just** `header=True` (no `inferSchema`). "
           "`printSchema()` — **everything is a string**, even `quantity` and "
           "`order_ts`. This is the default and it is fast.\n\n"
           "*קראו את ההזמנות עם `header=True` בלבד (בלי `inferSchema`). הכול "
           "מחרוזות.*",
     "sol": 'raw = spark.read.csv("data/orders.csv", header=True)\n'
            'raw.printSchema()'},

    {"md": "Now read it **with** `inferSchema=True` and `printSchema()`. Convenient "
           "— but Spark had to scan the file an **extra time** to guess the types.\n\n"
           "*עכשיו קראו עם `inferSchema=True` — נוח, אבל Spark סרק את הקובץ פעם "
           "נוספת.*",
     "sol": 'inferred = spark.read.csv("data/orders.csv", header=True, inferSchema=True)\n'
            'inferred.printSchema()'},

    {"md": "**Best practice: an explicit schema.** Build a `StructType` for the "
           "orders file and read with `schema=...` (no inference pass, no "
           "surprises). `printSchema()` to confirm.\n\n"
           "*שיטה מומלצת: schema מפורש עם `StructType`, בלי שלב ניחוש.*",
     "sol": 'from pyspark.sql.types import (StructType, StructField, StringType,\n'
            '                               IntegerType, DoubleType)\n\n'
            'orders_schema = StructType([\n'
            '    StructField("order_id", StringType()),\n'
            '    StructField("customer_id", StringType()),\n'
            '    StructField("order_ts", StringType()),\n'
            '    StructField("product_sku", StringType()),\n'
            '    StructField("quantity", IntegerType()),\n'
            '    StructField("unit_price", DoubleType()),\n'
            '    StructField("channel", StringType()),\n'
            '    StructField("payment_method", StringType()),\n'
            '    StructField("status", StringType()),\n'
            '    StructField("discount_code", StringType()),\n'
            '])\n'
            'orders = spark.read.csv("data/orders.csv", header=True, schema=orders_schema)\n'
            'orders.printSchema()'},

    {"md": "Starting from the all-string `raw`, **cast** `quantity` to int and "
           "`unit_price` to double, and parse `order_ts` into a real timestamp with "
           "`F.to_timestamp(..., \"yyyy-MM-dd HH:mm:ss\")`. Show the schema and 3 "
           "rows.\n\n"
           "*מ-`raw` המחרוזתי: בצעו cast ל-int/double, ופרסרו את `order_ts` "
           "ל-timestamp אמיתי.*",
     "sol": 'typed = (raw\n'
            '    .withColumn("quantity", F.col("quantity").cast("int"))\n'
            '    .withColumn("unit_price", F.col("unit_price").cast("double"))\n'
            '    .withColumn("order_ts", F.to_timestamp("order_ts", "yyyy-MM-dd HH:mm:ss")))\n'
            'typed.printSchema()\n'
            'typed.select("order_id", "quantity", "unit_price", "order_ts").show(3)'},

    {"md": "Now that `order_ts` is a real timestamp, extract `year` and `month`, and "
           "count orders **per month**.\n\n"
           "*עכשיו ש-`order_ts` הוא timestamp — חלצו שנה וחודש וספרו הזמנות לכל "
           "חודש.*",
     "sol": 'typed.withColumn("year", F.year("order_ts")) \\\n'
            '     .withColumn("month", F.month("order_ts")) \\\n'
            '     .groupBy("year", "month").count().orderBy("year", "month").show()'},

    {"md": "**Write Parquet.** Create a temp output folder, then write `typed` as "
           "Parquet with `mode(\"overwrite\")`. List the folder — note Parquet is a "
           "**directory** of part-files, not one file.\n\n"
           "*כתבו את `typed` כ-Parquet לתיקיית פלט זמנית. שימו לב ש-Parquet הוא "
           "תיקייה של part-files.*",
     "sol": 'import tempfile, os\n'
            'OUT = tempfile.mkdtemp()\n'
            'path = os.path.join(OUT, "orders_parquet")\n'
            'typed.write.mode("overwrite").parquet(path)\n'
            'print(sorted(os.listdir(path))[:5])'},

    {"md": "**Read the Parquet back.** Parquet stores the schema inside the files — "
           "so no `inferSchema` is needed and types come back exactly. "
           "`printSchema()` to prove it.\n\n"
           "*קראו את ה-Parquet בחזרה — ה-schema נשמר בתוך הקבצים, בלי `inferSchema`.*",
     "sol": 'back = spark.read.parquet(path)\n'
            'back.printSchema()\n'
            'back.count()'},

    {"md": "**Partitioned write.** Write `typed` as Parquet **partitioned by "
           "`channel`** into a new temp path. List the directory — you'll see "
           "`channel=web`, `channel=app`, … sub-folders.\n\n"
           "*כתבו Parquet מחולק לפי `channel` (`partitionBy`). ראו את תיקיות "
           "ה-`channel=...`.*",
     "sol": 'ppath = os.path.join(OUT, "orders_by_channel")\n'
            'typed.write.mode("overwrite").partitionBy("channel").parquet(ppath)\n'
            'print(sorted(os.listdir(ppath)))'},

    {"md": "**Partition pruning.** Read the partitioned dataset and filter "
           "`channel == 'web'`, then `.explain()`. Look for `PartitionFilters` — "
           "Spark reads **only the `channel=web` folder**, skipping the rest.\n\n"
           "*קראו את ה-dataset המחולק וסננו ל-`channel='web'`. ב-`explain` חפשו "
           "`PartitionFilters` — Spark קורא רק את התיקייה הרלוונטית.*",
     "sol": 'part = spark.read.parquet(ppath)\n'
            'part.filter(F.col("channel") == "web").explain()'},

    {"md": "Finally, write a single CSV (coalesce to 1 file) of the per-channel order "
           "counts, with a header, then read it back to confirm.\n\n"
           "*לבסוף: כתבו CSV אחד (עם header) של ספירת הזמנות לכל channel, וקראו "
           "בחזרה.*",
     "sol": 'summary = typed.groupBy("channel").count()\n'
            'cpath = os.path.join(OUT, "channel_summary_csv")\n'
            'summary.coalesce(1).write.mode("overwrite").option("header", True).csv(cpath)\n'
            'spark.read.csv(cpath, header=True, inferSchema=True).show()'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "schema זה לא פרט טכני",
     "body": "<p>ב-pandas הטיפוסים \"קורים\". ב-Spark, ובמיוחד ב-Foundry, ה-schema "
             "הוא חלק מהחוזה של ה-dataset. שלוש דרכים לקבוע אותו בקריאה:</p>"
             "<ul>"
             "<li><strong>ברירת מחדל</strong> — הכול string. מהיר, אבל צריך לעשות "
             "cast ידני.</li>"
             "<li><code>inferSchema=True</code> — נוח, אבל <strong>קורא את הקובץ "
             "פעם נוספת</strong> כדי לנחש. יקר על מידע גדול.</li>"
             "<li><code>schema=StructType(...)</code> — <strong>הדרך הנכונה "
             "לפרודקשן</strong>: בלי ניחוש, בלי הפתעות, מהיר.</li>"
             "</ul>"},

    {"type": "text", "h2": "casting ו-timestamps",
     "body": "<p>מידע גולמי מגיע כמחרוזות. ממירים עם:</p>"
             "<ul>"
             "<li><code>F.col(\"quantity\").cast(\"int\")</code> — המרת טיפוס.</li>"
             "<li><code>F.to_timestamp(\"order_ts\", \"yyyy-MM-dd HH:mm:ss\")</code> "
             "— מחרוזת ל-timestamp עם פורמט.</li>"
             "<li><code>F.to_date</code>, ואז <code>F.year</code> / "
             "<code>F.month</code> / <code>F.dayofweek</code>.</li>"
             "</ul>"
             "<p>שימו לב: תבנית התאריך של Spark היא בסגנון Java "
             "(<code>yyyy-MM-dd</code>), לא בסגנון Python (<code>%Y-%m-%d</code>).</p>"},

    {"type": "text", "h2": "למה Parquet, ולמה partitionBy",
     "body": "<p>CSV הוא טקסט: כבד, בלי טיפוסים, בלי דחיסה. <strong>Parquet</strong> "
             "הוא פורמט עמודתי בינארי — דחוס, שומר schema, ומאפשר ל-Spark לקרוא רק "
             "את העמודות שצריך.</p>"
             "<p><code>write.partitionBy(\"channel\")</code> מפצל את הפלט לתיקיות "
             "(<code>channel=web/</code>, <code>channel=app/</code>...). כשמסננים "
             "אחר כך לפי <code>channel</code>, Spark <strong>מדלג על תיקיות שלמות</strong> "
             "(partition pruning) — קוראים פחות, רץ מהר יותר.</p>"},

    {"type": "compare", "h2": "כתיבה: pandas מול Spark",
     "left_title": "🐼 pandas", "left": [
         "<code>df.to_csv('f.csv')</code> — קובץ אחד",
         "<code>to_parquet('f.parquet')</code>",
         "אין מושג partitions",
     ],
     "right_title": "🔥 Spark", "right": [
         "<code>df.write.csv(path)</code> — <strong>תיקייה</strong> של part-files",
         "<code>df.write.parquet(path)</code>",
         "<code>.partitionBy('channel')</code> לתיקיות",
     ],
     "note": "💡 פלט ב-Spark הוא כמעט תמיד <strong>תיקייה</strong>, כי כל partition "
             "נכתב בנפרד ובמקביל. רוצים קובץ אחד? <code>coalesce(1)</code> לפני "
             "הכתיבה (בזהירות — מאבד מקביליות)."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("בניית schema", "StructType / StructField",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.types.StructType.html"),
         ("המרת טיפוס", "Column.cast()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Column.cast.html"),
         ("מחרוזת ל-timestamp", "F.to_timestamp()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.to_timestamp.html"),
         ("כתיבת Parquet", "DataFrameWriter.parquet()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.parquet.html"),
         ("כתיבה מחולקת", "DataFrameWriter.partitionBy()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.partitionBy.html"),
         ("קריאת Parquet", "spark.read.parquet()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.parquet.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו על Data Sources ו-Parquet Files במדריך הרשמי, ועל "
             "<code>save modes</code> (<code>overwrite</code> / <code>append</code> "
             "/ <code>errorifexists</code>).</p>",
     "pills": [("Data Sources",
                "https://spark.apache.org/docs/latest/sql-data-sources.html")] + H.DOCS_PILLS[:2]},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל על schema ו-IO: שלוש דרכים לקבוע schema בקריאה, casting של "
             "עמודות מחרוזת ל-int/double/timestamp, וכתיבה/קריאה של Parquet — כולל "
             "<code>partitionBy</code> ו-partition pruning.</p>"},
    {"type": "tip", "text": "תבנית התאריך ב-Spark היא בסגנון Java: "
                            "<code>yyyy-MM-dd HH:mm:ss</code> — שימו לב לאותיות "
                            "הגדולות/קטנות."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "אותה טבלת הזמנות — הפעם נתייחס ברצינות ל-schema ולטיפוסים.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "ברירת מחדל מול <code>inferSchema</code> מול <code>StructType</code> מפורש",
        "<code>cast</code> ו-<code>to_timestamp</code> על עמודות מחרוזת",
        "כתיבת Parquet וקריאתו בחזרה (schema נשמר)",
        "<code>partitionBy</code> ו-partition pruning ב-<code>explain</code>",
        "כתיבת CSV יחיד עם <code>coalesce(1)</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 08 — Schemas, קריאה וכתיבה",
             kicker="Spark for Power Users · פרק 08", kicker_color=H.BRAND2,
             title="Schemas, קריאה וכתיבה",
             subtitle="schema-on-read, casting, ו-Parquet מחולק — כמו שעובדים ב-Foundry.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 08 — התרגיל והמידע",
             kicker="פרק 08 · התרגיל והמידע", kicker_color=H.GREEN,
             title="לשלוט ב-schema וב-IO",
             subtitle="מ-CSV מחרוזתי גולמי ל-Parquet מחולק ומוקלד היטב.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
