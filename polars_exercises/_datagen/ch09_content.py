"""Chapter 09 - Lazy Evaluation & Performance (medium)."""

from pathlib import Path

import htmlgen as H
from nbbuild import build

CH = "09_Lazy_Evaluation_and_Performance"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 09 — Lazy Evaluation & Performance"

INTRO_MD = (
    "This is Polars' superpower for big data. Instead of loading a whole file into "
    "memory (`read_csv`) and then filtering, we describe the *whole query* lazily "
    "with `scan_csv`, and Polars builds an optimized plan — reading only the columns "
    "and rows we actually need. This is exactly how we keep Foundry transforms fast "
    "on millions of rows.\n\n"
    "*זה הכוח-על של Polars לנתונים גדולים. במקום לטעון קובץ שלם לזיכרון (`read_csv`) "
    "ואז לסנן, אנחנו מתארים את כל השאילתה בעצלות (lazy) עם `scan_csv`, ו-Polars בונה "
    "תוכנית מיטבית — קורא רק את העמודות והשורות שבאמת צריך.*\n\n"
    "**Data file:** `data/larger.csv` (about 1.1 million rows!)"
)

ITEMS = [
    {"md": "Import `polars` and the `time` module. Read `data/larger.csv` **eagerly** "
           "with `read_csv`, and show its `shape` and `estimated_size(\"mb\")`.\n\n"
           "*ייבאו את `polars` ואת `time`. קראו את `data/larger.csv` באופן רגיל "
           "(eager) והציגו את ה-`shape` ואת `estimated_size(\"mb\")`.*",
     "sol": 'import polars as pl\nimport time\n\n'
            'df = pl.read_csv("data/larger.csv")\n'
            'df.shape, round(df.estimated_size("mb"), 1)'},

    {"md": "Now create a **LazyFrame** with `scan_csv`. Print its type — note that no "
           "data has been read yet; it is just a query plan.\n\n"
           "*עכשיו צרו LazyFrame עם `scan_csv`. הדפיסו את הטיפוס שלו — שימו לב שעדיין "
           "לא נקרא שום מידע; זו רק תוכנית שאילתה.*",
     "sol": 'lf = pl.scan_csv("data/larger.csv")\ntype(lf)'},

    {"md": "Build a lazy query: from the scan, **filter** `category == \"pens\"` and "
           "**select** `cust_num, qty, invoice_total` — but do **not** collect yet. "
           "Print the optimized plan with `.explain()`.\n\n"
           "*בנו שאילתה עצלה: סננו `category == \"pens\"` ובחרו 3 עמודות — אבל אל "
           "תאספו (collect) עדיין. הדפיסו את התוכנית עם `.explain()`.*",
     "sol": 'q = (\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .filter(pl.col("category") == "pens")\n'
            '    .select("cust_num", "qty", "invoice_total")\n'
            ')\nprint(q.explain())'},

    {"md": "Look at the plan above: Polars pushed the filter into the scan "
           "(`SELECTION`) and reads only 3 of 10 columns (`PROJECT 3/10`). Now run the "
           "query with `.collect()` and show the result shape.\n\n"
           "*הסתכלו בתוכנית: Polars דחף את הסינון לתוך הקריאה וקורא רק 3 מתוך 10 "
           "עמודות. הריצו עכשיו עם `.collect()` והציגו את צורת התוצאה.*",
     "sol": 'q = (\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .filter(pl.col("category") == "pens")\n'
            '    .select("cust_num", "qty", "invoice_total")\n'
            ')\nq.collect().shape'},

    {"md": "Lazily compute the **total `invoice_total` per `category`**, sorted from "
           "highest to lowest. Remember to `collect()`.\n\n"
           "*חשבו בעצלות את סך ה-`invoice_total` לכל `category`, ממוין מהגבוה לנמוך. "
           "זכרו `collect()`.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by("category")\n'
            '    .agg(pl.col("invoice_total").sum().alias("total"))\n'
            '    .sort("total", descending=True)\n'
            '    .collect()\n'
            ')'},

    {"md": "Lazily count how many invoices there are **per `category`**.\n\n"
           "*ספרו בעצלות כמה חשבוניות יש לכל `category`.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by("category")\n'
            '    .agg(pl.len().alias("n_invoices"))\n'
            '    .collect()\n'
            ')'},

    {"md": "Lazily find the **top 10 `sku`** by total `qty` sold.\n\n"
           "*מצאו בעצלות את 10 ה-`sku` המובילים לפי סך ה-`qty` שנמכר.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by("sku")\n'
            '    .agg(pl.col("qty").sum().alias("total_qty"))\n'
            '    .sort("total_qty", descending=True)\n'
            '    .head(10)\n'
            '    .collect()\n'
            ')'},

    {"md": "Lazily compute the **average `discount_rate` per `category`**, rounded to "
           "3 decimals.\n\n"
           "*חשבו בעצלות את `discount_rate` הממוצע לכל `category`, מעוגל ל-3 ספרות.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by("category")\n'
            '    .agg(pl.col("discount_rate").mean().round(3).alias("avg_discount"))\n'
            '    .collect()\n'
            ')'},

    {"md": "Lazily count rows where `qty > 10` **and** `category` is in "
           "`[\"pens\", \"books\"]`.\n\n"
           "*ספרו בעצלות שורות שבהן `qty > 10` וגם `category` ב-`[\"pens\", \"books\"]`.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .filter((pl.col("qty") > 10) & (pl.col("category").is_in(["pens", "books"])))\n'
            '    .select(pl.len())\n'
            '    .collect()\n'
            ')'},

    {"md": "**Profile** the per-category revenue query with `.profile()`. It returns "
           "`(result, timings)` — show the `timings` table to see how long each step "
           "took.\n\n"
           "*הריצו `.profile()` על שאילתת ההכנסה לפי קטגוריה. היא מחזירה "
           "`(result, timings)` — הציגו את טבלת ה-`timings`.*",
     "sol": 'q = (\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by("category")\n'
            '    .agg(pl.col("invoice_total").sum())\n'
            ')\nresult, timings = q.profile()\ntimings'},

    {"md": "See the optimizer at work: print `.explain(optimized=False)` and compare "
           "it to `.explain()`. The optimized plan pushes the projection/filter into "
           "the scan.\n\n"
           "*ראו את ה-optimizer בפעולה: הדפיסו `.explain(optimized=False)` והשוו ל-"
           "`.explain()`. התוכנית המיטבית דוחפת את הבחירה/סינון לתוך הקריאה.*",
     "sol": 'q = (\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .filter(pl.col("category") == "pens")\n'
            '    .select("cust_num", "qty")\n'
            ')\nprint("=== NOT optimized ===")\nprint(q.explain(optimized=False))\n'
            'print("\\n=== optimized ===")\nprint(q.explain())'},

    {"md": "**Eager vs lazy timing.** Time (a) reading the whole file then filtering "
           "+ grouping eagerly, versus (b) doing the same with `scan_csv` + "
           "`collect`. Print both durations.\n\n"
           "*תזמון eager מול lazy. מדדו (א) קריאת כל הקובץ ואז סינון+קיבוץ, מול "
           "(ב) אותו דבר עם `scan_csv` + `collect`. הדפיסו את שני הזמנים.*",
     "sol": 't0 = time.perf_counter()\n'
            'eager = (pl.read_csv("data/larger.csv")\n'
            '         .filter(pl.col("qty") > 5)\n'
            '         .group_by("category").agg(pl.col("invoice_total").sum()))\n'
            'eager_time = time.perf_counter() - t0\n\n'
            't0 = time.perf_counter()\n'
            'lazy = (pl.scan_csv("data/larger.csv")\n'
            '        .filter(pl.col("qty") > 5)\n'
            '        .group_by("category").agg(pl.col("invoice_total").sum())\n'
            '        .collect())\n'
            'lazy_time = time.perf_counter() - t0\n\n'
            'print(f"eager: {eager_time:.3f}s")\nprint(f"lazy : {lazy_time:.3f}s")'},

    {"md": "Lazily parse `invoice_date_time` (string) into a real datetime and find "
           "the **earliest and latest** invoice timestamps.\n\n"
           "*נתחו בעצלות את `invoice_date_time` לתאריך-שעה אמיתי ומצאו את החשבונית "
           "המוקדמת והמאוחרת ביותר.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .select(\n'
            '        first=pl.col("invoice_date_time").str.to_datetime().min(),\n'
            '        last=pl.col("invoice_date_time").str.to_datetime().max(),\n'
            '    )\n'
            '    .collect()\n'
            ')'},

    {"md": "Build a **monthly revenue report** lazily: parse the timestamp, group by "
           "month, sum `invoice_total`, sort by month.\n\n"
           "*בנו דוח הכנסות חודשי בעצלות: נתחו את החותמת, קבצו לפי חודש, סכמו "
           "`invoice_total`, מיינו לפי חודש.*",
     "sol": '(\n'
            '    pl.scan_csv("data/larger.csv")\n'
            '    .group_by(\n'
            '        month=pl.col("invoice_date_time").str.to_datetime().dt.month()\n'
            '    )\n'
            '    .agg(pl.col("invoice_total").sum().round(2).alias("revenue"))\n'
            '    .sort("month")\n'
            '    .collect()\n'
            ')'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>עד עכשיו עבדנו ב-<strong>eager</strong>: כל פעולה רצה מיד וטוענת את "
             "כל המידע לזיכרון. ל-Polars יש מצב שני, חזק בהרבה לנתונים גדולים: "
             "<strong>lazy</strong> (עצל).</p>"
             "<p>במצב lazy מתארים את <em>כל</em> השאילתה מראש (עם <code>scan_csv</code> "
             "במקום <code>read_csv</code>), Polars בונה תוכנית, <strong>ממטב</strong> "
             "אותה (קורא רק עמודות ושורות שצריך), ורק כש-קוראים ל-<code>collect()</code> "
             "הוא מריץ הכל ביעילות.</p>"},

    {"type": "text", "h2": "הקסם: Predicate &amp; Projection Pushdown",
     "body": "<p>ה-optimizer של Polars \"דוחף\" את הסינון ואת בחירת העמודות עד לתוך "
             "קריאת הקובץ עצמה:</p>"
             "<ul>"
             "<li><strong>Projection pushdown:</strong> קורא רק את העמודות שצריך "
             "(<code>PROJECT 3/10 COLUMNS</code>)</li>"
             "<li><strong>Predicate pushdown:</strong> מסנן שורות כבר בקריאה "
             "(<code>SELECTION</code>)</li>"
             "</ul>"
             "<p>זה אומר פחות קריאה מהדיסק, פחות זיכרון, והרבה יותר מהירות. רואים את "
             "זה עם <code>.explain()</code>.</p>"},

    {"type": "compare", "h2": "Eager מול Lazy",
     "intro": "אותו חישוב, שתי גישות:",
     "left_title": "🐌 Eager", "left": [
         "<code>pl.read_csv(path)</code>",
         "טוען את כל הקובץ לזיכרון",
         "כל פעולה רצה מיד",
         "פשוט — מעולה לנתונים קטנים",
     ],
     "right_title": "⚡ Lazy", "right": [
         "<code>pl.scan_csv(path)</code>",
         "בונה תוכנית, לא טוען כלום",
         "<code>.collect()</code> מריץ הכל ביחד",
         "ממטב אוטומטית — מעולה לנתונים גדולים",
     ],
     "note": "💡 כלל אצבע: לנתונים גדולים, התחילו תמיד מ-<code>scan_csv</code> "
             "וסיימו ב-<code>collect</code>."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("קריאה עצלה של CSV", "polars.scan_csv()",
          "https://docs.pola.rs/api/python/stable/reference/api/polars.scan_csv.html"),
         ("הרצת השאילתה העצלה", "LazyFrame.collect()",
          "https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.collect.html"),
         ("הצגת תוכנית השאילתה", "LazyFrame.explain()",
          "https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.explain.html"),
         ("מדידת זמני שלבים", "LazyFrame.profile()",
          "https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.profile.html"),
         ("מעבר ל-lazy מ-DataFrame", "DataFrame.lazy()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.lazy.html"),
         ("כתיבה עצלה (streaming) לדיסק", "LazyFrame.sink_csv()",
          "https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.sink_csv.html"),
         ("ה-API המלא של LazyFrame", "LazyFrame",
          "https://docs.pola.rs/api/python/stable/reference/lazyframe/index.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>עברו על כל ה-API של <code>LazyFrame</code> — רובו זהה ל-DataFrame, אבל "
             "עצל. קראו גם על המנוע ה-streaming החדש (<code>sink_*</code>) שמאפשר לעבד "
             "קבצים גדולים מהזיכרון בלי לטעון הכל.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל בינוני (14 שאלות) על קובץ אמיתי של <strong>1.1 מיליון שורות</strong>. "
             "תבנו שאילתות עצלות, תראו את תוכנית האופטימיזציה עם <code>explain</code>, "
             "תמדדו זמני ריצה, ותרגישו למה lazy הוא כלי כל-כך חשוב לנתונים גדולים.</p>"},
    {"type": "tip", "text": "תמיד התחילו מ-<code>scan_csv</code>, בנו את כל השרשרת, "
                            "וסיימו ב-<code>collect()</code>. בלי <code>collect</code> "
                            "יש לכם רק תוכנית — לא תוצאה."},
    {"type": "datatable", "h2": "המידע: <code>data/larger.csv</code>",
     "intro": "כ-1,100,000 חשבוניות מכירה. שורה לכל פריט בחשבונית.",
     "rows": [
         ("cust_num", "str", "מזהה לקוח"),
         ("sku", "str", "קוד מוצר"),
         ("category", "str", "קטגוריה (pens / pencils / books)"),
         ("qty", "i64", "כמות"),
         ("list_price", "f64", "מחיר מחירון"),
         ("discount_rate", "f64", "שיעור הנחה"),
         ("invoice_price", "f64", "מחיר אחרי הנחה ליחידה"),
         ("invoice_num", "str", "מספר חשבונית"),
         ("invoice_date_time", "str", "חותמת זמן (כמחרוזת)"),
         ("invoice_total", "f64", "סכום השורה בחשבונית"),
     ]},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>scan_csv</code> לבניית LazyFrame",
        "<code>explain</code> לראיית תוכנית השאילתה והאופטימיזציה",
        "קיבוץ וסינון בעצלות, ואז <code>collect</code>",
        "<code>profile</code> למדידת זמני שלבים",
        "השוואת זמני ריצה eager מול lazy",
        "ניתוח חותמות זמן ובניית דוח חודשי",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'הקובץ גדול (~1.1M שורות) — הריצה עשויה לקחת שנייה-שתיים, זה תקין.',
        'פתחו את <code>Exercises.ipynb</code> וענו שאלה-שאלה.',
        'הסתכלו טוב בפלט של <code>explain</code> — שם רואים את הקסם.',
        'סיימתם? השוו מול <code>Solutions.ipynb</code>.',
    ]},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 09 — חישוב עצל וביצועים | Polars",
             kicker="Polars for Power Users · פרק 09", kicker_color=H.BRAND2,
             title="חישוב עצל וביצועים (Lazy)",
             subtitle="scan_csv, collect ו-explain — הכוח-על של Polars למיליוני שורות.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 09 — התרגיל והמידע | Polars",
             kicker="פרק 09 · התרגיל והמידע", kicker_color=H.GREEN,
             title="עבודה עצלה על 1.1 מיליון שורות",
             subtitle="בונים שאילתות עצלות, קוראים תוכניות, ומודדים ביצועים.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
