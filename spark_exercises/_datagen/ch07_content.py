"""Chapter 07 — UDFs, Built-ins & Performance."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "07_UDFs_Builtins_and_Performance"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 07 — UDFs, Built-ins & Performance"

INTRO_MD = (
    "This chapter is about what Spark **lets you do** and what it **punishes you "
    "for**. You *can* write a plain Python UDF — but it becomes a black box that "
    "Catalyst cannot optimize and that serializes every row to Python. You'll see "
    "the native alternative, the vectorized `pandas_udf` middle ground, and the "
    "partition controls (`repartition` / `coalesce` / `cache`) that decide how fast "
    "a job runs on 250,000 rows.\n\n"
    "*הפרק הזה עוסק במה ש-Spark מרשה לכם לעשות — ועל מה הוא מעניש. אפשר לכתוב UDF "
    "רגיל ב-Python, אבל הוא הופך לקופסה שחורה ש-Catalyst לא יכול לייעל, ושמסריאלת כל "
    "שורה ל-Python. תראו את החלופה המובנית, את ה-`pandas_udf` הוקטורי, ואת בקרות "
    "ה-partitions שקובעות כמה מהר job רץ על 250,000 שורות.*\n\n"
    "**Data files:** `data/web_events.csv` (250k rows), `data/orders.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/web_events.csv` (250,000 rows) into `web` "
           "(`header=True`, `inferSchema=True`) and `count()` it.\n\n"
           "*קראו את `web_events.csv` (רבע מיליון שורות) וספרו.*",
     "sol": 'web = spark.read.csv("data/web_events.csv", header=True, inferSchema=True)\n'
            'web.count()'},

    {"md": "How many **partitions** is `web` split into? "
           "(`web.rdd.getNumPartitions()`)\n\n"
           "*לכמה partitions `web` מחולק?*",
     "sol": "web.rdd.getNumPartitions()"},

    {"md": "**The tempting way — a Python UDF.** Write a Python function that labels "
           "`duration_ms` as `'fast'` (< 1000), `'medium'` (< 5000) or `'slow'`, "
           "wrap it with `F.udf`, and apply it. Show 5 rows. ⚠️ This works, but "
           "every row is shipped to a Python worker and Catalyst sees a black "
           "box.\n\n"
           "*הדרך המפתה — UDF ב-Python. עטפו פונקציה עם `F.udf` והפעילו. עובד, אבל "
           "איטי וקופסה שחורה.*",
     "sol": 'from pyspark.sql.types import StringType\n\n'
            'def speed_label(ms):\n'
            '    if ms < 1000:\n'
            '        return "fast"\n'
            '    elif ms < 5000:\n'
            '        return "medium"\n'
            '    return "slow"\n\n'
            'speed_udf = F.udf(speed_label, StringType())\n'
            'web.withColumn("speed", speed_udf("duration_ms")) \\\n'
            '   .select("page", "duration_ms", "speed").show(5)'},

    {"md": "**The Spark way — native built-ins.** Reproduce the exact same labelling "
           "with `F.when(...).otherwise(...)`. This stays inside the JVM, is "
           "vectorized, and Catalyst can optimize it. Show 5 rows.\n\n"
           "*הדרך של Spark — פונקציות מובנות. אותה לוגיקה עם `F.when` — נשאר ב-JVM "
           "ומהיר.*",
     "sol": 'native = web.withColumn(\n'
            '    "speed",\n'
            '    F.when(F.col("duration_ms") < 1000, "fast")\n'
            '     .when(F.col("duration_ms") < 5000, "medium")\n'
            '     .otherwise("slow"),\n'
            ')\n'
            'native.select("page", "duration_ms", "speed").show(5)'},

    {"md": "Confirm both approaches agree: count rows **per `speed`** using the "
           "native version.\n\n"
           "*ודאו ששתי הגישות מסכימות — ספירה לכל `speed` בגרסה המובנית.*",
     "sol": 'native.groupBy("speed").count().orderBy(F.col("count").desc()).show()'},

    {"md": "**The middle ground — a vectorized `pandas_udf`.** When you truly need "
           "Python, a `pandas_udf` processes a whole batch as a pandas Series (using "
           "Arrow), far faster than a row-by-row UDF. Write one that converts "
           "`duration_ms` to seconds and apply it. Show 5 rows.\n\n"
           "*דרך הביניים — `pandas_udf` וקטורי שמעבד batch שלם כ-Series. ממירים "
           "מילישניות לשניות.*",
     "sol": 'from pyspark.sql.functions import pandas_udf\n'
            'import pandas as pd\n\n'
            '@pandas_udf("double")\n'
            'def to_seconds(ms: pd.Series) -> pd.Series:\n'
            '    return ms / 1000.0\n\n'
            'web.withColumn("seconds", to_seconds("duration_ms")) \\\n'
            '   .select("duration_ms", "seconds").show(5)'},

    {"md": "**`repartition`** reshuffles the data into a chosen number of partitions "
           "(a full shuffle). Repartition `web` into 16 partitions and confirm the "
           "new count.\n\n"
           "*`repartition` מפזר מחדש ל-מספר partitions שתבחרו (shuffle מלא).*",
     "sol": 'web16 = web.repartition(16)\n'
            'web16.rdd.getNumPartitions()'},

    {"md": "**`coalesce`** only *reduces* partitions, and avoids a full shuffle — "
           "ideal right before writing output. Coalesce `web` down to 2 partitions "
           "and confirm.\n\n"
           "*`coalesce` רק מקטין מספר partitions, בלי shuffle מלא — מצוין לפני "
           "כתיבה.*",
     "sol": 'web.coalesce(2).rdd.getNumPartitions()'},

    {"md": "A realistic aggregation: **average `duration_ms` and event count per "
           "`page`**, slowest pages first (round the average).\n\n"
           "*אגרגציה מציאותית: ממוצע משך וספירה לכל `page`.*",
     "sol": 'web.groupBy("page") \\\n'
            '   .agg(F.round(F.avg("duration_ms"), 1).alias("avg_ms"),\n'
            '        F.count("*").alias("events")) \\\n'
            '   .orderBy(F.col("avg_ms").desc()).show()'},

    {"md": "If you will reuse a filtered DataFrame several times, **`cache`** it so "
           "Spark does not recompute it each time. Cache the `submit` events, "
           "materialize with `count()`, then check `storageLevel`.\n\n"
           "*אם תשתמשו שוב ושוב ב-DataFrame מסונן — `cache`. ממשו עם `count` ובדקו "
           "`storageLevel`.*",
     "sol": 'submits = web.filter(F.col("event_type") == "submit").cache()\n'
            'print("rows:", submits.count())\n'
            'print(submits.storageLevel)'},

    {"md": "**`count()` scans everything; `take()` does not.** `count()` the whole "
           "table (an action over all 250k rows), then `take(3)` — which stops as "
           "soon as it has 3 rows. Notice `take` returns a small Python list.\n\n"
           "*`count` סורק הכול; `take` עוצר ברגע שיש מספיק. השוו.*",
     "sol": 'print("total rows:", web.count())\n'
            'web.take(3)'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "למה UDF ב-Python הוא בעיה",
     "body": "<p>ב-pandas כותבים <code>df.apply(my_func)</code> בלי לחשוב. ב-Spark "
             "אותו דבר (<code>F.udf</code>) הוא <strong>מלכודת ביצועים</strong>:</p>"
             "<ul>"
             "<li>כל שורה עוברת serialization מה-JVM ל-Python ובחזרה.</li>"
             "<li>Catalyst רואה <strong>קופסה שחורה</strong> — הוא לא יכול לדחוף "
             "פילטר דרכה או לייעל אותה.</li>"
             "<li>זה רץ שורה-שורה, לא וקטורי.</li>"
             "</ul>"
             "<p>הכלל: <strong>חפשו תמיד פונקציה מובנית ב-<code>F.*</code> קודם</strong>. "
             "יש מאות.</p>"},

    {"type": "compare", "h2": "שלוש הדרכים לאותה לוגיקה",
     "left_title": "🐢 Python UDF", "left": [
         "<code>F.udf(my_func)</code>",
         "serialization שורה-שורה",
         "קופסה שחורה ל-Catalyst",
         "הכי איטי",
     ],
     "right_title": "🚀 מובנה / pandas_udf", "right": [
         "<code>F.when().otherwise()</code> — הכי מהיר",
         "<code>@pandas_udf</code> — batch וקטורי עם Arrow",
         "שקוף יחסית למנוע",
         "סדרי גודל מהיר יותר",
     ],
     "note": "💡 סדר העדיפות: (1) פונקציה מובנית, (2) <code>pandas_udf</code> אם "
             "חייבים Python, (3) <code>udf</code> רגיל רק כמוצא אחרון."},

    {"type": "text", "h2": "partitions — יחידת המקביליות",
     "body": "<p>Spark מעבד את המידע ב-<strong>partitions</strong> במקביל. מספר "
             "ה-partitions קובע כמה משימות רצות בו-זמנית.</p>"
             "<ul>"
             "<li><code>df.rdd.getNumPartitions()</code> — כמה יש עכשיו.</li>"
             "<li><code>repartition(n)</code> — קובע מספר חדש ב-<strong>shuffle "
             "מלא</strong> (יכול גם להגדיל וגם לאזן מחדש).</li>"
             "<li><code>coalesce(n)</code> — רק <strong>מקטין</strong>, בלי shuffle "
             "מלא. מושלם ממש לפני <code>write</code>, כדי לא לייצר אלפי קבצים "
             "קטנטנים.</li>"
             "</ul>"},

    {"type": "text", "h2": "actions יקרים וזולים",
     "body": "<p>כי הכול עצל, חשוב לדעת מה כל action עולה:</p>"
             "<ul>"
             "<li><code>count()</code> — סורק את <strong>כל</strong> המידע. יקר.</li>"
             "<li><code>collect()</code> / <code>toPandas()</code> — מביא הכול "
             "ל-driver. מסוכן על מידע גדול.</li>"
             "<li><code>take(n)</code> / <code>show(n)</code> — עוצרים מוקדם. זולים.</li>"
             "<li><code>cache()</code> — שמרו DataFrame שתשתמשו בו שוב, כדי לא לחשב "
             "מחדש בכל action.</li>"
             "</ul>"},

    {"type": "warn", "text": "<code>toPandas()</code> ו-<code>collect()</code> "
                             "מביאים את כל ה-DataFrame אל זיכרון ה-driver. על מידע "
                             "אמיתי בסקייל זה יקרוס — תמיד צמצמו (filter/agg/limit) "
                             "לפני."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("UDF רגיל (להימנע)", "F.udf()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.udf.html"),
         ("UDF וקטורי", "F.pandas_udf()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.pandas_udf.html"),
         ("תנאי מובנה", "F.when()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.when.html"),
         ("פיזור מחדש (shuffle)", "DataFrame.repartition()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.repartition.html"),
         ("הקטנת partitions", "DataFrame.coalesce()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.coalesce.html"),
         ("שמירה בזיכרון", "DataFrame.cache()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.cache.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את מדריך ה-Performance Tuning ואת עמוד ה-Pandas UDFs (Arrow). "
             "לפני שכותבים UDF — חפשו בעמוד הפונקציות, סביר שזה כבר קיים.</p>",
     "pills": [("Performance Tuning",
                "https://spark.apache.org/docs/latest/sql-performance-tuning.html")] + H.DOCS_PILLS[:2]},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל ביצועים: תכתבו UDF ב-Python, תחליפו אותו בפונקציה מובנית, "
             "תכירו <code>pandas_udf</code>, ותשלטו ב-partitions עם "
             "<code>repartition</code> / <code>coalesce</code> / <code>cache</code> "
             "— הכול על 250 אלף שורות.</p>"},
    {"type": "tip", "text": "הכלל המנחה: אם יש פונקציה מובנית ב-<code>F.*</code> — "
                            "השתמשו בה. UDF הוא מוצא אחרון."},
    {"type": "datatable", "h2": "המידע: <code>data/web_events.csv</code>",
     "intro": "אירועי גלישה — 250,000 שורות.",
     "rows": [
         ("event_ts", "string", "חותמת זמן"),
         ("user_id", "string", "מזהה משתמש"),
         ("page", "string", "הדף (<code>/home, /cart, /checkout...</code>)"),
         ("event_type", "string", "view / click / scroll / submit"),
         ("duration_ms", "int", "משך האירוע במילישניות"),
         ("country", "string", "קוד מדינה"),
     ]},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "כתיבת UDF ב-Python — ולמה כדאי להימנע",
        "החלפה בפונקציה מובנית (<code>F.when</code>)",
        "<code>pandas_udf</code> וקטורי עם Arrow",
        "<code>repartition</code> מול <code>coalesce</code>",
        "<code>cache</code>, ועלות של <code>count</code> מול <code>take</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 07 — UDFs, מובנות וביצועים",
             kicker="Spark for Power Users · פרק 07", kicker_color=H.BRAND2,
             title="UDFs, פונקציות מובנות וביצועים",
             subtitle="מה Spark מרשה — ועל מה הוא מעניש. UDF, vectorization, ו-partitions.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 07 — התרגיל והמידע",
             kicker="פרק 07 · התרגיל והמידע", kicker_color=H.GREEN,
             title="ביצועים: UDF מול מובנה, ו-partitions",
             subtitle="לכתוב UDF, להחליפו במובנה, ולשלוט בפיזור ובזיכרון.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
