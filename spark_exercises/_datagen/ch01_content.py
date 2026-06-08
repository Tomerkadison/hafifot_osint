"""Chapter 01 — Spark Mindset & Basics (Fast Track)."""

from pathlib import Path

import htmlgen as H
import shared
from nbbuild import build

CH = "01_Spark_Mindset_and_Basics"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Spark Exercises 01 — Spark Mindset & Basics (Fast Track)"

INTRO_MD = (
    "You already know pandas and Polars, so the **syntax** here will feel familiar. "
    "This short chapter is a fast tour of the basics — but its real goal is to plant "
    "the **one idea that makes Spark different**: a DataFrame is not data sitting in "
    "your RAM, it is a *recipe* that runs on a cluster, and **nothing runs until you "
    "ask for a result** (an *action*).\n\n"
    "*אתם כבר מכירים pandas ו-Polars — אז ה-syntax כאן ירגיש לכם כמו בית. הפרק הזה "
    "קצר בכוונה: סיור מהיר על הבסיס. אבל יש לו מטרה אחת גדולה — להכניס לכם לראש את "
    "הרעיון שהופך את Spark למשהו אחר לגמרי. ב-Spark, ה-DataFrame הוא לא טבלה שיושבת "
    "לכם בזיכרון. הוא מתכון: רשימת הוראות שרצה על אשכול שלם של מחשבים (cluster). "
    "והכי חשוב — שום דבר לא באמת קורה עד שאתם מבקשים תוצאה. את הבקשה הזאת קוראים "
    "action.*\n\n"
    "**Data file:** `data/orders.csv` — 8,000 rows, one row per order line."
)

ITEMS = [
    {"setup": True, "md": shared.SPARK_INIT_MD, "sol": shared.SPARK_INIT},

    {"md": "Read `data/orders.csv` into a DataFrame called `orders` "
           "(`header=True`, `inferSchema=True`).\n\n"
           "*קראו את הקובץ `data/orders.csv` לתוך DataFrame בשם `orders`.*",
     "sol": 'orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)'},

    {"md": "Now just evaluate `orders`. **Surprise:** unlike pandas/Polars it does "
           "**not** print the rows — only the schema. A Spark DataFrame is a plan, "
           "not data.\n\n"
           "*עכשיו פשוט כתבו `orders` (רק את השם). הפתעה קטנה: בניגוד ל-pandas "
           "ול-Polars, לא יודפסו שום שורות — רק ה-schema. זה כי ב-Spark, DataFrame "
           "הוא תוכנית, לא המידע עצמו.*",
     "sol": "orders"},

    {"md": "To actually see data you call an **action**. Show the first 5 rows with "
           "`show(5)`.\n\n"
           "*כדי לראות מידע אמיתי צריך action. הציגו את 5 השורות הראשונות עם "
           "`show(5)`.*",
     "sol": "orders.show(5)"},

    {"md": "Wide rows get truncated. Show **3 rows vertically** "
           "(`show(3, vertical=True)`) — much easier to read.\n\n"
           "*שורות רחבות נחתכות על המסך. הציגו 3 שורות במאונך עם "
           "`show(3, vertical=True)` — הרבה יותר נוח לקריאה.*",
     "sol": "orders.show(3, vertical=True)"},

    {"md": "Print the **schema** (column names + types) with `printSchema()`. "
           "Notice the type Spark inferred for `order_ts`.\n\n"
           "*הדפיסו את ה-schema (שמות העמודות + הטיפוסים) עם `printSchema()`. שימו "
           "לב איזה טיפוס Spark נתן ל-`order_ts`.*",
     "sol": "orders.printSchema()"},

    {"md": "How many **rows**? Use `count()`. (This is an action — Spark scans the "
           "whole dataset to answer.)\n\n"
           "*כמה שורות יש בטבלה? השתמשו ב-`count()`. (זה action — Spark סורק את כל "
           "המידע כדי לענות.)*",
     "sol": "orders.count()"},

    {"md": "What are the **column names**, and how many columns are there?\n\n"
           "*מהם שמות העמודות, וכמה עמודות יש?*",
     "sol": "print(orders.columns)\nprint(len(orders.columns))"},

    {"md": "Select only `order_id`, `product_sku`, `quantity` and show 5 rows. "
           "Note there is no `df[['a','b']]` in Spark — you use `select`.\n\n"
           "*בחרו רק את העמודות `order_id`, `product_sku`, `quantity` והציגו 5 "
           "שורות. שימו לב — אין ב-Spark `df[['a','b']]`, משתמשים ב-`select`.*",
     "sol": 'orders.select("order_id", "product_sku", "quantity").show(5)'},

    {"md": "Get summary statistics for `quantity` and `unit_price` with "
           "`describe()`.\n\n"
           "*קבלו סטטיסטיקה מסכמת ל-`quantity` ו-`unit_price` עם `describe()`.*",
     "sol": 'orders.describe("quantity", "unit_price").show()'},

    {"md": "How many **distinct products** (`product_sku`) appear?\n\n"
           "*כמה מוצרים שונים (`product_sku`) מופיעים?*",
     "sol": 'orders.select("product_sku").distinct().count()'},

    {"md": "How many orders are there **per `status`**? "
           "(`groupBy(...).count()`)\n\n"
           "*כמה הזמנות יש לכל `status`?*",
     "sol": 'orders.groupBy("status").count().show()'},

    {"md": "Show 5 orders whose `status` is `completed`. Use `filter` with "
           "`F.col(...)`.\n\n"
           "*הציגו 5 הזמנות שה-`status` שלהן הוא `completed`. השתמשו ב-`filter` עם "
           "`F.col(...)`.*",
     "sol": 'orders.filter(F.col("status") == "completed").show(5)'},

    {"md": "Add a new column `line_total = quantity * unit_price` with "
           "`withColumn`, then show `order_id`, `quantity`, `unit_price`, "
           "`line_total` for 5 rows.\n\n"
           "*הוסיפו עמודה `line_total = quantity * unit_price` ב-`withColumn`, "
           "והציגו 5 שורות.*",
     "sol": 'orders.withColumn("line_total", F.col("quantity") * F.col("unit_price")) \\\n'
            '      .select("order_id", "quantity", "unit_price", "line_total").show(5)'},

    {"md": "Confirm Spark DataFrames are **immutable**: print `orders.columns` "
           "again — `line_total` is **not** there, because `withColumn` returned a "
           "*new* DataFrame and we never reassigned `orders`.\n\n"
           "*בואו נוכיח ש-DataFrames ב-Spark הם immutable (לא ניתנים לשינוי): הדפיסו "
           "שוב את `orders.columns`. העמודה `line_total` לא שם! כי `withColumn` החזיר "
           "DataFrame חדש, ואנחנו מעולם לא שמרנו אותו בחזרה ל-`orders`.*",
     "sol": "orders.columns"},

    {"md": "`show()` only prints. To pull rows back into Python as objects, use "
           "`collect()` (or `take`). Get the **first 3 rows** as a Python list of "
           "`Row` objects with `orders.limit(3).collect()`. ⚠️ Never `collect()` a "
           "huge DataFrame — it all flows to the driver's memory.\n\n"
           "*`show()` רק מדפיס למסך. כדי להחזיר שורות ל-Python כאובייקטים אמיתיים, "
           "משתמשים ב-`collect()`. החזירו את 3 השורות הראשונות עם "
           "`orders.limit(3).collect()`. ⚠️ אף פעם אל תריצו `collect()` על DataFrame "
           "ענק — הכול זורם לזיכרון של ה-driver.*",
     "sol": "orders.limit(3).collect()"},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "מה שונה ב-Spark?",
     "body": "<p>ב-pandas וב-Polars כל המידע יושב בזיכרון של <strong>מחשב אחד</strong>. "
             "ב-Spark הסיפור אחר: המידע מפוזר על פני <strong>אשכול</strong> שלם של "
             "מחשבים (cluster). יש מנהל אחד (ה-<em>driver</em>) שמחלק את העבודה, "
             "והרבה עובדים (<em>executors</em>) שעובדים במקביל, כל אחד על חתיכה "
             "מהמידע (partition).</p>"
             "<p>בגלל זה <code>DataFrame</code> ב-Spark הוא לא טבלה בזיכרון — הוא "
             "<strong>מתכון</strong>. הוא מתאר <em>איך</em> להגיע לתוצאה, אבל לא מבשל "
             "כלום עד שאתם מבקשים לטעום.</p>"},

    {"type": "text", "h2": "Transformations מול Actions",
     "body": "<p>זה הלב של Spark — ותשתמשו בזה כל הזמן. יש שני סוגי פעולות:</p>"
             "<ul>"
             "<li><strong>Transformation</strong> (פעולה עצלה / lazy): רק מוסיפה שלב "
             "למתכון ומחזירה DataFrame חדש. למשל <code>select</code>, "
             "<code>filter</code>, <code>withColumn</code>, <code>groupBy</code>, "
             "<code>join</code>. עדיין לא רץ כלום.</li>"
             "<li><strong>Action</strong> (פעולה להוטה / eager): מבקשת תוצאה אמיתית "
             "— וזה הרגע שבו כל שרשרת המתכון סוף-סוף רצה. למשל <code>show</code>, "
             "<code>count</code>, <code>collect</code>, <code>write</code>, "
             "<code>take</code>.</li>"
             "</ul>"
             "<p>לכן אם תכתבו <code>orders</code> לבד — לא תראו מידע. רק כשתוסיפו "
             "<code>orders.show()</code>, Spark באמת יתחיל לעבוד.</p>"},

    {"type": "compare", "h2": "מה שאתם מכירים מול Spark",
     "intro": "אותן פעולות, syntax מעט שונה:",
     "left_title": "🐼 pandas / ⚡ Polars", "left": [
         "<code>df.head()</code> מדפיס מידע",
         "<code>df[['a','b']]</code>",
         "<code>df['a']</code>",
         "<code>df.shape</code>",
         "<code>df.iloc[5]</code> (לפי מיקום)",
         "המידע תמיד בזיכרון",
     ],
     "right_title": "🔥 Spark", "right": [
         "<code>df.show()</code> (action)",
         "<code>df.select('a','b')</code>",
         "<code>F.col('a')</code>",
         "<code>(df.count(), len(df.columns))</code>",
         "אין גישה לפי מיקום שורה!",
         "המידע מפוזר על cluster",
     ],
     "note": "💡 ההבדל הכי חשוב: ב-Spark <strong>אין index ואין גישה לשורה לפי "
             "מיקום</strong> (<code>iloc</code>). אין בכלל מושג של \"השורה החמישית\", "
             "כי המידע מפוזר על הרבה מכונות ולא ממוין כברירת מחדל."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("קריאת CSV", "spark.read.csv()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.csv.html"),
         ("הצגת שורות (action)", "DataFrame.show()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.show.html"),
         ("הדפסת ה-schema", "DataFrame.printSchema()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.printSchema.html"),
         ("ספירת שורות (action)", "DataFrame.count()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.count.html"),
         ("בחירת עמודות", "DataFrame.select()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.select.html"),
         ("הפניה לעמודה כביטוי", "F.col()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.col.html"),
         ("סינון שורות", "DataFrame.filter()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.filter.html"),
         ("הוספת/עדכון עמודה", "DataFrame.withColumn()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.withColumn.html"),
         ("החזרת שורות ל-driver (action)", "DataFrame.collect()",
          "https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.collect.html"),
     ]},

    {"type": "warn", "text": "<code>collect()</code> ו-<code>toPandas()</code> "
                             "מושכים את <strong>כל</strong> המידע אל מחשב אחד "
                             "(ה-driver). על טבלה של מיליארד שורות זה פשוט יקרוס. "
                             "תמיד סננו או צמצמו קודם, ורק אז משכו."},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו את ה-Quickstart הרשמי של PySpark DataFrames, ושימו לב להבחנה "
             "בין transformations ל-actions לאורך כל התיעוד.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>16 שאלות קצרות שמכסות את כל הבסיס של Spark: קריאת קובץ, "
             "<code>show</code>/<code>collect</code>, <code>printSchema</code>, "
             "<code>count</code>, <code>select</code>, <code>filter</code> "
             "ו-<code>withColumn</code>. את הרעיונות אתם כבר מכירים מ-pandas/Polars "
             "— כאן תלמדו את ה-syntax, ובעיקר את ההבדל הקריטי בין transformation "
             "ל-action.</p>"},
    {"type": "tip", "text": "התא הראשון פותח עבורכם <code>SparkSession</code> — רק "
                            "הריצו אותו. נסו קודם לבד, ורק אם נתקעתם — הציצו "
                            "בפתרונות."},
    {"type": "datatable", "h2": "המידע: <code>data/orders.csv</code>",
     "intro": "טבלת הזמנות — 8,000 שורות, שורה לכל פריט בהזמנה.",
     "rows": shared.ORDERS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "פתיחת <code>SparkSession</code> וקריאת CSV",
        "ההבדל בין <code>show</code> (מדפיס) ל-<code>collect</code> (מחזיר ל-Python)",
        "<code>printSchema</code>, <code>count</code>, <code>columns</code>",
        "<code>select</code>, <code>filter</code>, <code>withColumn</code>",
        "להבין למה DataFrame ב-Spark הוא immutable ועצל (lazy)",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": shared.start_steps()},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 01 — חשיבה ובסיס ב-Spark",
             kicker="Spark for Power Users · פרק 01", kicker_color=H.BRAND2,
             title="חשיבה ובסיס ב-Spark",
             subtitle="הכול מוכר מ-pandas/Polars — חוץ מרעיון אחד גדול: עצלות (lazy) ועבודה מבוזרת.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 01 — התרגיל והמידע",
             kicker="פרק 01 · התרגיל והמידע", kicker_color=H.GREEN,
             title="צעדים ראשונים עם טבלת ההזמנות",
             subtitle="סיור מהיר על הבסיס, עם דגש על ההבדל בין transformation ל-action.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
