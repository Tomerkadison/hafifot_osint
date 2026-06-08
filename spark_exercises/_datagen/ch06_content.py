"""Chapter 06 — Nested & Semi-structured Data (mission chapter)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "06_Nested_and_Semi_Structured_Data"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 06 — Nested & Semi-structured Data"

INTRO_MD = (
    "This is where Spark leaves a flat pandas/Polars table behind. Real event data "
    "arrives as **nested JSON**: a `device` object, a `geo` object, and an `items` "
    "**array** of products. Spark reads this natively into `struct` and `array` "
    "columns and gives you first-class tools — dot access, `explode`, `from_json` — "
    "to work with it without ever flattening to messy strings.\n\n"
    "*כאן Spark משאיר מאחור טבלה שטוחה של pandas/Polars. מידע אמיתי של אירועים מגיע "
    "כ-JSON מקונן: אובייקט `device`, אובייקט `geo`, ומערך `items` של מוצרים. Spark "
    "קורא את זה ישירות לעמודות `struct` ו-`array`, ונותן כלים מובנים — גישה עם נקודה, "
    "`explode`, `from_json` — לעבוד עם זה בלי לשטח למחרוזות מלוכלכות.*\n\n"
    "**Data file:** `data/events.jsonl` — 2,500 clickstream events (JSON Lines)."
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read the JSON Lines file with `spark.read.json(\"data/events.jsonl\")` "
           "into `events`, then `printSchema()`. Notice the **nested structs** "
           "(`device`, `geo`) and the **array** (`items`).\n\n"
           "*קראו את קובץ ה-JSON וראו ב-`printSchema` את ה-structs והמערך.*",
     "sol": 'events = spark.read.json("data/events.jsonl")\n'
            'events.printSchema()'},

    {"md": "Show 2 events **vertically** so you can see the nested structure "
           "rendered.\n\n*הציגו 2 אירועים במאונך כדי לראות את המבנה המקונן.*",
     "sol": "events.show(2, vertical=True, truncate=False)"},

    {"md": "**Dot access.** Reach into the structs: select `event_id`, `event_type`, "
           "`device.os`, `device.is_mobile`, `geo.country`. Show 8 rows.\n\n"
           "*גשו לשדות מקוננים עם נקודה: `device.os`, `geo.country` וכו'.*",
     "sol": 'events.select("event_id", "event_type", "device.os",\n'
            '              "device.is_mobile", "geo.country").show(8)'},

    {"md": "Count events **per operating system** (`device.os`), most common "
           "first.\n\n*ספרו אירועים לכל מערכת הפעלה (`device.os`).*",
     "sol": 'events.groupBy("device.os").count().orderBy(F.col("count").desc()).show()'},

    {"md": "**Flatten a struct.** Use `select(\"device.*\")` to expand all of "
           "`device`'s fields into top-level columns. Show 5 rows.\n\n"
           "*שטחו struct שלם עם `select(\"device.*\")`.*",
     "sol": 'events.select("device.*").show(5)'},

    {"md": "**Filter on nested fields.** Keep only events from mobile devices using "
           "the `Chrome` browser. How many are there?\n\n"
           "*סננו לאירועים ממכשירים ניידים עם דפדפן `Chrome`.*",
     "sol": 'mobile_chrome = events.filter(\n'
            '    (F.col("device.is_mobile") == True) & (F.col("device.browser") == "Chrome")\n'
            ')\n'
            'mobile_chrome.count()'},

    {"md": "The `items` array is only present for `add_to_cart` / `purchase` events. "
           "Add a column `n_items = size(items)` and show it for 8 events (events "
           "without items show `-1`).\n\n"
           "*הוסיפו עמודה עם אורך המערך `items` באמצעות `F.size`.*",
     "sol": 'events.withColumn("n_items", F.size("items")) \\\n'
            '      .select("event_id", "event_type", "n_items").show(8)'},

    {"md": "**Explode the array.** Take only `purchase` events, then `explode` "
           "`items` so each product in a basket becomes its **own row**. Select "
           "`event_id`, `user_id`, `item.sku`, `item.qty`, `item.price`. Show 10.\n\n"
           "*פוצצו (explode) את מערך `items` — כל מוצר בסל הופך לשורה משלו.*",
     "sol": 'purchases = events.filter(F.col("event_type") == "purchase")\n'
            'lines = purchases.select(\n'
            '    "event_id", "user_id",\n'
            '    F.explode("items").alias("item")\n'
            ')\n'
            'lines.select("event_id", "user_id", "item.sku", "item.qty", "item.price").show(10)'},

    {"md": "From the exploded `lines`, compute total **purchase revenue** "
           "(`sum(qty * price)`), rounded to 2 decimals.\n\n"
           "*חשבו את סך ההכנסה מרכישות מתוך השורות שפוצצו.*",
     "sol": 'lines.select(F.round(F.sum(F.col("item.qty") * F.col("item.price")), 2).alias("revenue")).show()'},

    {"md": "Which **5 SKUs** were purchased most often (count of exploded item "
           "rows)?\n\n*אילו 5 מוצרים נרכשו הכי הרבה פעמים?*",
     "sol": 'lines.groupBy(F.col("item.sku").alias("sku")) \\\n'
            '     .count().orderBy(F.col("count").desc()).show(5)'},

    {"md": "**`posexplode`** also gives the position within the array. On `purchases` "
           "use `posexplode(items)` to get `pos` and `item`, and show the first "
           "item (`pos == 0`) of 8 baskets.\n\n"
           "*`posexplode` נותן גם את המיקום במערך. הציגו את הפריט הראשון בכל סל.*",
     "sol": 'purchases.select("event_id", F.posexplode("items").alias("pos", "item")) \\\n'
            '         .filter(F.col("pos") == 0) \\\n'
            '         .select("event_id", "item.sku", "item.qty").show(8)'},

    {"md": "**Build and parse JSON.** Turn the `device` struct back into a JSON "
           "string with `F.to_json`, then parse it back into a struct with "
           "`F.from_json` using an explicit schema. Show `os` and `browser` from the "
           "re-parsed struct.\n\n"
           "*המירו struct ל-JSON עם `to_json`, ופרסרו בחזרה עם `from_json` וסכמה "
           "מפורשת.*",
     "sol": 'from pyspark.sql.types import StructType, StructField, StringType, BooleanType\n\n'
            'device_schema = StructType([\n'
            '    StructField("os", StringType()),\n'
            '    StructField("browser", StringType()),\n'
            '    StructField("is_mobile", BooleanType()),\n'
            '])\n'
            'events.withColumn("device_json", F.to_json("device")) \\\n'
            '      .withColumn("parsed", F.from_json("device_json", device_schema)) \\\n'
            '      .select("device_json", "parsed.os", "parsed.browser").show(5, truncate=False)'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "מידע אמיתי הוא מקונן",
     "body": "<p>אירועים, לוגים, ותגובות API כמעט תמיד מגיעים כ-JSON מקונן: אובייקט "
             "בתוך אובייקט, ומערכים בתוך שדות. ב-pandas/Polars זה כאב ראש — לרוב "
             "משטחים הכול או שומרים מחרוזות JSON.</p>"
             "<p>Spark קורא JSON ישירות לטיפוסים מובנים: <code>struct</code> "
             "(אובייקט), <code>array</code> (מערך), ו-<code>map</code> (מילון). "
             "ה-schema נשמר, וה-Catalyst optimizer יודע לעבוד איתו.</p>"},

    {"type": "text", "h2": "structs — גישה עם נקודה",
     "body": "<p>שדה מקונן הוא פשוט <code>parent.child</code>:</p>"
             "<ul>"
             "<li><code>events.select(\"device.os\")</code> — שדה בודד.</li>"
             "<li><code>events.select(\"device.*\")</code> — לשטח את כל השדות.</li>"
             "<li><code>F.col(\"geo.country\")</code> — בתוך <code>filter</code> "
             "או <code>groupBy</code>.</li>"
             "</ul>"
             "<p>אפשר גם <strong>לבנות</strong> struct עם "
             "<code>F.struct(\"a\", \"b\")</code>.</p>"},

    {"type": "text", "h2": "arrays — explode הוא הכוכב",
     "body": "<p>מערך בתוך שורה (סל קניות, רשימת תגיות) זה נפוץ מאוד. הכלים:</p>"
             "<ul>"
             "<li><code>F.size(arr)</code> — אורך המערך.</li>"
             "<li><code>F.explode(arr)</code> — <strong>שורה לכל איבר</strong> "
             "(שורה אחת עם 3 פריטים → 3 שורות). זו הפעולה המרכזית.</li>"
             "<li><code>F.posexplode(arr)</code> — כמו explode, אבל גם המיקום.</li>"
             "<li><code>F.array_contains</code>, <code>arr[0]</code>, "
             "<code>F.explode_outer</code> (שומר שורות עם מערך ריק/null).</li>"
             "</ul>"
             "<p>אחרי explode עובדים על השורות כרגיל — groupBy, sum, join.</p>"},

    {"type": "compare", "h2": "מידע מקונן: pandas/Polars מול Spark",
     "left_title": "🐼 pandas / ⚡ Polars", "left": [
         "JSON לרוב משוטח ידנית",
         "מערכים בעמודה = object dtype מסורבל",
         "<code>json_normalize</code> / list-cols",
         "אין schema אכיפה",
     ],
     "right_title": "🔥 Spark", "right": [
         "<code>read.json</code> שומר struct/array",
         "<code>device.os</code> גישה ישירה",
         "<code>explode</code> / <code>from_json</code> מובנים",
         "schema מלא ונאכף",
     ],
     "note": "💡 ב-Foundry הרבה datasets הם בדיוק כאלה — אירועים מקוננים. "
             "<code>explode</code> ו-<code>from_json</code> הם לחם-חוק."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("קריאת JSON", "spark.read.json()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.json.html"),
         ("שורה לכל איבר במערך", "F.explode()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.explode.html"),
         ("explode עם מיקום", "F.posexplode()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.posexplode.html"),
         ("אורך מערך", "F.size()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.size.html"),
         ("בניית struct", "F.struct()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.struct.html"),
         ("פרסור JSON לפי schema", "F.from_json()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.from_json.html"),
         ("המרה ל-JSON", "F.to_json()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.to_json.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו על Complex Types (struct/array/map) ועל פונקציות המערך הרבות "
             "ב-<code>F.*</code> — <code>transform</code>, <code>filter</code>, "
             "<code>aggregate</code> על מערכים.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>פרק-משימה על מידע מקונן אמיתי: לקרוא JSON עם structs ומערכים, לגשת "
             "עם נקודה, לסנן על שדות מקוננים, ובעיקר — <code>explode</code> של מערך "
             "ה-<code>items</code> כדי לחשב הכנסות ומוצרים מובילים.</p>"},
    {"type": "tip", "text": "אחרי <code>explode</code> כל איבר במערך הוא שורה רגילה "
                            "— משם ממשיכים עם <code>groupBy</code>, <code>sum</code> "
                            "ו-<code>join</code> כרגיל."},
    {"type": "datatable", "h2": "המידע: <code>data/events.jsonl</code>",
     "intro": "אירועי clickstream מקוננים. שדות מרכזיים:",
     "rows": [
         ("event_id", "string", "מזהה אירוע"),
         ("user_id", "string", "מזהה משתמש (<code>CUST-...</code>)"),
         ("event_ts", "string", "חותמת זמן ISO"),
         ("event_type", "string", "page_view / search / add_to_cart / purchase"),
         ("device", "struct", "אובייקט מקונן: <code>os, browser, is_mobile</code>"),
         ("geo", "struct", "אובייקט מקונן: <code>country, city</code>"),
         ("items", "array&lt;struct&gt;", "מערך מוצרים: <code>sku, qty, price</code> (רק ברכישה/הוספה לסל)"),
         ("search_term", "string", "מונח חיפוש (רק באירועי search)"),
     ]},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>read.json</code> ו-schema מקונן",
        "גישה עם נקודה ו-<code>select(\"struct.*\")</code>",
        "<code>explode</code> / <code>posexplode</code> של מערכים",
        "חישוב הכנסות ומוצרים מובילים מתוך סלים",
        "<code>to_json</code> / <code>from_json</code> עם schema מפורש",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 06 — מידע מקונן",
             kicker="Spark for Power Users · פרק 06", kicker_color=H.BRAND2,
             title="מידע מקונן וחצי-מובנה",
             subtitle="structs, arrays ו-explode — כאן Spark עוקף בענק את pandas/Polars.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 06 — התרגיל והמידע",
             kicker="פרק 06 · התרגיל והמידע 🎯", kicker_color=H.GREEN,
             title="לפצח אירועי JSON מקוננים",
             subtitle="גישה לשדות מקוננים, explode של סלים, וחישוב הכנסות אמיתי.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
