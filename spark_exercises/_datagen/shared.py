"""Shared snippets reused across Spark chapters (DRY)."""

# Boilerplate that opens a local SparkSession. Pre-filled in BOTH notebooks
# (it is setup, not an exercise to re-derive). Every chapter's question #1 uses it.
SPARK_INIT = (
    "from pyspark.sql import SparkSession\n"
    "from pyspark.sql import functions as F\n\n"
    "spark = (\n"
    '    SparkSession.builder\n'
    '    .appName("spark-course")\n'
    '    .master("local[*]")\n'
    '    .config("spark.sql.shuffle.partitions", "8")\n'
    '    .config("spark.ui.showConsoleProgress", "false")\n'
    "    .getOrCreate()\n"
    ")\n"
    'spark.sparkContext.setLogLevel("ERROR")\n'
    'print("Spark", spark.version)'
)

SPARK_INIT_MD = (
    "**Setup** — open a local `SparkSession` (already written for you). "
    "In Foundry the session is created for you; locally we open one ourselves. "
    "`F` is the functions module — almost every column expression lives there.\n\n"
    "*פותחים SparkSession מקומי (כבר כתוב עבורכם). ב-Foundry ה-session נוצר "
    "אוטומטית; כאן אנחנו פותחים אותו לבד. `F` הוא מודול הפונקציות — כמעט כל "
    "ביטוי על עמודה מגיע משם.*"
)

# Data dictionary for the orders fact table (used in several chapters).
ORDERS_COLS = [
    ("order_id", "string", "מזהה ייחודי של ההזמנה (למשל <code>ORD-000123</code>)"),
    ("customer_id", "string", "מזהה הלקוח (<code>CUST-0042</code>) — משמש ל-joins"),
    ("order_ts", "string", "חותמת זמן של ההזמנה. ⚠️ נשמרה כמחרוזת, לא כ-timestamp"),
    ("product_sku", "string", "קוד המוצר"),
    ("quantity", "int", "כמות. ⚠️ ערך שלילי = החזרה (return)"),
    ("unit_price", "double", "מחיר ליחידה"),
    ("channel", "string", "ערוץ המכירה (web / app / store / partner)"),
    ("payment_method", "string", "אמצעי תשלום (card / paypal / applepay / giftcard)"),
    ("status", "string", "סטטוס (completed / pending / cancelled / returned)"),
    ("discount_code", "string", "קוד הנחה. ⚠️ ברוב השורות חסר (null)"),
]

CUSTOMERS_COLS = [
    ("customer_id", "string", "מזהה הלקוח — מפתח ה-join"),
    ("customer_name", "string", "שם הלקוח"),
    ("email", "string", "כתובת אימייל"),
    ("country", "string", "קוד מדינה (US, DE, JP…)"),
    ("city", "string", "עיר"),
    ("region_id", "string", "מזהה אזור (NA, EU, APAC…) — join אל regions"),
    ("segment", "string", "פלח (Consumer / SMB / Enterprise)"),
    ("loyalty_tier", "string", "דרגת נאמנות (Bronze / Silver / Gold / Platinum)"),
    ("signup_date", "string", "תאריך הצטרפות (מחרוזת)"),
]


def start_steps(extra: str = "") -> list[str]:
    base = [
        'ודאו ש-Spark מותקן ורץ — ראו את <code>SETUP.md</code> בתיקיית הקורס.',
        'פתחו את <code>Exercises.ipynb</code> בתיקייה של הפרק.',
        'התא הראשון כבר פותח עבורכם <code>SparkSession</code> — רק הריצו אותו.',
        'ענו על השאלות אחת-אחת. אל תפחדו לטעות — זו הדרך ללמוד.',
        'תקועים? פתחו את <code>subject.html</code> וקראו את התיעוד הרשמי של Spark.',
        'סיימתם? פתחו את <code>Solutions.ipynb</code> כדי לבדוק את עצמכם מול הפלט האמיתי.',
    ]
    if extra:
        base.insert(0, extra)
    return base
