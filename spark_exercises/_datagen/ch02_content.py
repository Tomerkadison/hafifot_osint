"""Chapter 02 — Lazy Execution & the Catalyst Plan."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "02_Lazy_Execution_and_the_Plan"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 02 — Lazy Execution & the Catalyst Plan"

INTRO_MD = (
    "Polars taught you *lazy* evaluation with `scan` / `collect`. Spark takes the "
    "same idea much further: **every** DataFrame is lazy, and behind the scenes the "
    "**Catalyst optimizer** rewrites your plan before a single row is read. In this "
    "chapter you will *see* the plan with `explain()`, watch Catalyst merge filters "
    "and prune columns, and learn when to `cache()`.\n\n"
    "*ב-Polars הכרתם חישוב עצל עם `scan`/`collect`. ב-Spark הרעיון מוקצן: כל "
    "DataFrame הוא עצל, ומאחורי הקלעים ה-Catalyst optimizer משכתב את התוכנית שלכם "
    "לפני שנקראת ולו שורה אחת. בפרק הזה תראו את התוכנית עם `explain()`, תצפו "
    "ב-Catalyst מאחד פילטרים וזורק עמודות מיותרות, ותלמדו מתי כדאי `cache()`.*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/orders.csv` (`header=True`, `inferSchema=True`) into "
           "`orders`.\n\n*קראו את `data/orders.csv` ל-`orders`.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)'},

    {"md": "Build a **chain of transformations** without any action and store it in "
           "`pipeline`: keep only positive `quantity`, select a few columns, and add "
           "`revenue = quantity * unit_price`. Then evaluate `pipeline` — it returns "
           "instantly and shows only the schema. **No job ran yet.**\n\n"
           "*בנו שרשרת טרנספורמציות בלי action ושמרו ב-`pipeline`. כתבו `pipeline` — "
           "זה מחזיר מיד ומראה רק schema. שום job לא רץ.*",
     "sol": 'pipeline = (\n'
            '    orders\n'
            '    .filter(F.col("quantity") > 0)\n'
            '    .select("order_id", "product_sku", "quantity", "unit_price")\n'
            '    .withColumn("revenue", F.col("quantity") * F.col("unit_price"))\n'
            ')\n'
            'pipeline'},

    {"md": "Now call an **action** — `pipeline.show(5)` — and the whole chain finally "
           "runs.\n\n*עכשיו קראו action — `pipeline.show(5)` — וכל השרשרת רצה.*",
     "sol": "pipeline.show(5)"},

    {"md": "Print the **physical plan** with `pipeline.explain()`. Read it bottom-up: "
           "the bottom is the file scan, the top is the final step.\n\n"
           "*הדפיסו את התוכנית הפיזית עם `pipeline.explain()`. קוראים מלמטה למעלה.*",
     "sol": "pipeline.explain()"},

    {"md": "Print the **full set of plans** (parsed → analyzed → optimized → "
           "physical) with `pipeline.explain(mode=\"extended\")`.\n\n"
           "*הדפיסו את כל שלבי התוכנית עם `pipeline.explain(mode=\"extended\")`.*",
     "sol": 'pipeline.explain(mode="extended")'},

    {"md": "**Catalyst merges filters.** Build `two = orders.filter(quantity > 0)"
           ".filter(unit_price > 5)` and call `two.explain()`. Notice the physical "
           "plan has **one** combined `Filter`, not two.\n\n"
           "*Catalyst מאחד פילטרים. בנו שני פילטרים נפרדים והריצו `explain()` — "
           "תראו Filter אחד משולב.*",
     "sol": 'two = orders.filter(F.col("quantity") > 0).filter(F.col("unit_price") > 5)\n'
            'two.explain()'},

    {"md": "**Column pruning (projection pushdown).** Call "
           "`orders.select(\"order_id\", \"quantity\").explain()` and look at the "
           "scan's `ReadSchema` — Spark only reads the two columns it needs.\n\n"
           "*בחרו שתי עמודות בלבד והריצו `explain()` — שימו לב ל-`ReadSchema` בסריקה: "
           "Spark קורא רק את העמודות הדרושות.*",
     "sol": 'orders.select("order_id", "quantity").explain()'},

    {"md": "How many **partitions** does `orders` have? "
           "(`orders.rdd.getNumPartitions()`) — this is how many chunks Spark "
           "processes in parallel.\n\n"
           "*כמה partitions יש ל-`orders`? זה מספר החתיכות שמעובדות במקביל.*",
     "sol": "orders.rdd.getNumPartitions()"},

    {"md": "Without caching, **every action recomputes the whole chain**. "
           "`cache()` the pipeline, then run an action (`count()`) to materialize "
           "it.\n\n"
           "*בלי cache, כל action מחשב מחדש את כל השרשרת. עשו `cache()` ל-pipeline "
           "ואז הריצו `count()` כדי לממש אותו בזיכרון.*",
     "sol": "pipeline.cache()\npipeline.count()"},

    {"md": "Check `pipeline.storageLevel` — now that it is cached you will see it "
           "is stored in memory.\n\n"
           "*בדקו את `pipeline.storageLevel` — עכשיו רואים שהוא שמור בזיכרון.*",
     "sol": "pipeline.storageLevel"},

    {"md": "Free the cache with `pipeline.unpersist()` and confirm "
           "`storageLevel` is back to none.\n\n"
           "*שחררו את ה-cache עם `unpersist()` ובדקו ש-`storageLevel` חזר לריק.*",
     "sol": "pipeline.unpersist()\npipeline.storageLevel"},

    {"md": "You can also write expressions as SQL strings. Use `selectExpr` to "
           "compute `quantity * unit_price as revenue` for 5 rows.\n\n"
           "*אפשר גם לכתוב ביטויים כמחרוזות SQL. השתמשו ב-`selectExpr`.*",
     "sol": 'orders.selectExpr("order_id", "quantity * unit_price as revenue").show(5)'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "עצלות, אבל ברצינות",
     "body": "<p>ב-Spark <strong>כל</strong> DataFrame עצל. כשאתם כותבים "
             "<code>filter</code>, <code>select</code>, <code>withColumn</code> — "
             "אתם רק מוסיפים שלב למתכון. שום מידע לא נקרא ושום חישוב לא רץ.</p>"
             "<p>רק כשמגיע <strong>action</strong> (כמו <code>show</code>, "
             "<code>count</code>, <code>write</code>) — Spark לוקח את כל המתכון, "
             "מעביר אותו דרך ה-<strong>Catalyst optimizer</strong>, ורק אז מריץ "
             "תוכנית מיטבית על ה-cluster.</p>"},

    {"type": "text", "h2": "מה Catalyst עושה עבורכם",
     "body": "<p>Catalyst הוא מנוע אופטימיזציה שמשכתב את התוכנית לפני ההרצה:</p>"
             "<ul>"
             "<li><strong>Predicate pushdown</strong> — דוחף פילטרים קרוב ככל האפשר "
             "למקור, כדי לקרוא פחות מידע.</li>"
             "<li><strong>Projection pruning</strong> — קורא רק את העמודות שבאמת "
             "צריך (ראו <code>ReadSchema</code> ב-plan).</li>"
             "<li><strong>Filter combining</strong> — מאחד כמה <code>filter</code> "
             "לתנאי אחד.</li>"
             "<li><strong>Constant folding</strong> ועוד עשרות חוקים.</li>"
             "</ul>"
             "<p>בגלל זה הסדר שבו אתם כותבים את הפעולות פחות קריטי מאשר ב-pandas — "
             "Catalyst יסדר מחדש בכל מקרה.</p>"},

    {"type": "text", "h2": "לקרוא תוכנית עם <code>explain()</code>",
     "body": "<p><code>df.explain()</code> מדפיס את התוכנית <strong>הפיזית</strong>. "
             "קוראים אותה <strong>מלמטה למעלה</strong>: למטה ה-<code>FileScan</code> "
             "(קריאת הקובץ), ולמעלה הצעד האחרון.</p>"
             "<p><code>df.explain(mode=\"extended\")</code> מראה את כל ארבעת השלבים: "
             "Parsed → Analyzed → Optimized → Physical. כך רואים בדיוק מה Catalyst "
             "שינה.</p>"
             "<p>סימן ה-<code>*</code> ליד צעד (למשל <code>*(1) Filter</code>) אומר "
             "ש-Spark ייצר עבורו קוד Java מהיר (Whole-Stage Codegen).</p>"},

    {"type": "compare", "h2": "Polars lazy מול Spark lazy",
     "left_title": "⚡ Polars", "left": [
         "<code>pl.scan_csv(...)</code> עצל",
         "<code>pl.read_csv(...)</code> להוט",
         "<code>.collect()</code> מריץ",
         "<code>.explain()</code> מראה plan",
         "רץ על מחשב אחד",
     ],
     "right_title": "🔥 Spark", "right": [
         "<strong>כל</strong> DataFrame עצל",
         "אין גרסה \"להוטה\"",
         "<code>show/count/collect</code> מריצים",
         "<code>.explain()</code> מראה plan",
         "רץ במקביל על cluster",
     ],
     "note": "💡 ב-Polars אתם בוחרים lazy מול eager. ב-Spark <strong>תמיד</strong> "
             "lazy — וזה הופך את ה-Catalyst optimizer לחזק במיוחד."},

    {"type": "text", "h2": "מתי לעשות <code>cache()</code>",
     "body": "<p>כי הכול עצל, אם תשתמשו באותו DataFrame בכמה actions — Spark "
             "<strong>יחשב אותו מחדש כל פעם</strong>. אם זה יקר (join, aggregation), "
             "עשו <code>df.cache()</code> ואז action אחד כדי לממש אותו בזיכרון. "
             "מהפעם הבאה הוא יישלף מהזיכרון.</p>"
             "<p>סיימתם? <code>df.unpersist()</code> כדי לשחרר. שימו לב: cache עצמו "
             "עצל — הוא נכנס לתוקף רק אחרי ה-action הבא.</p>"},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "rows": [
         ("הצגת התוכנית", "DataFrame.explain()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.explain.html"),
         ("שמירה בזיכרון", "DataFrame.cache()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.cache.html"),
         ("שמירה עם רמת אחסון", "DataFrame.persist()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.persist.html"),
         ("שחרור מהזיכרון", "DataFrame.unpersist()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.unpersist.html"),
         ("רמת האחסון הנוכחית", "DataFrame.storageLevel",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.storageLevel.html"),
         ("ביטויים כמחרוזת SQL", "DataFrame.selectExpr()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.selectExpr.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו על Catalyst ועל ה-Tungsten execution engine במדריך הרשמי, "
             "ושחקו עם <code>explain(mode=\"formatted\")</code> לקריאות טובה יותר.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל שמראה לכם את <strong>המנוע</strong>: איך לבנות שרשרת עצלה, "
             "מתי היא רצה, ואיך לקרוא את התוכנית של Catalyst עם <code>explain</code>. "
             "בסוף תתרגלו <code>cache</code> / <code>unpersist</code>.</p>"},
    {"type": "tip", "text": "הסתכלו טוב בפלט של <code>explain()</code> — חפשו "
                            "<code>FileScan</code>, <code>PushedFilters</code>, "
                            "ו-<code>ReadSchema</code>. שם רואים את הקסם."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "בניית שרשרת transformations עצלה",
        "ההבדל בין transformation ל-action — הלכה למעשה",
        "קריאת התוכנית עם <code>explain()</code> ו-<code>explain(mode=...)</code>",
        "לראות את Catalyst מאחד פילטרים וזורק עמודות",
        "<code>cache</code> / <code>unpersist</code> / <code>storageLevel</code>",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 02 — חישוב עצל והתוכנית",
             kicker="Spark for Power Users · פרק 02", kicker_color=H.BRAND2,
             title="חישוב עצל ותוכנית Catalyst",
             subtitle="הכול עצל, ו-Catalyst משכתב את התוכנית שלכם לפני שנקראת שורה אחת.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 02 — התרגיל והמידע",
             kicker="פרק 02 · התרגיל והמידע", kicker_color=H.GREEN,
             title="להציץ אל מתחת למכסה המנוע",
             subtitle="לבנות שרשרת עצלה, להריץ אותה, ולקרוא את התוכנית של Catalyst.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
