"""Shared content snippets reused across chapters (DRY)."""

# Data dictionary for the orders fact table (chapters 01-05, 06, 07).
ORDERS_COLS = [
    ("order_id", "str", "מזהה ייחודי של ההזמנה (למשל <code>ORD-000123</code>)"),
    ("customer_id", "str", "מזהה הלקוח (<code>CUST-0042</code>) — משמש ל-joins"),
    ("order_date", "str", "תאריך ההזמנה. ⚠️ נשמר כמחרוזת, לא כתאריך אמיתי"),
    ("region", "str", "אזור גאוגרפי (Europe, North America…)"),
    ("product_sku", "str", "קוד המוצר"),
    ("category", "str", "קטגוריית המוצר (pens, books, shirts…)"),
    ("product_name", "str", "שם המוצר המלא"),
    ("quantity", "i64", "כמות. ⚠️ ערך שלילי = החזרה (return)"),
    ("unit_price", "f64", "מחיר ליחידה"),
    ("channel", "str", "ערוץ המכירה (online / store / partner)"),
    ("status", "str", "סטטוס (completed / pending / cancelled / returned)"),
    ("discount_code", "str", "קוד הנחה. ⚠️ ברוב השורות חסר (null)"),
]

# Standard "how to start" steps, parameterised by the exercises notebook note.
def start_steps(extra: str = "") -> list[str]:
    base = [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'פתחו את <code>Exercises.ipynb</code> בתיקייה של הפרק.',
        'ענו על השאלות אחת-אחת. אל תפחדו לטעות — זו הדרך ללמוד.',
        'תקועים? פתחו את <code>subject.html</code> וקראו את התיעוד הרשמי של הפונקציה.',
        'סיימתם? פתחו את <code>Solutions.ipynb</code> כדי לבדוק את עצמכם מול הפלט האמיתי.',
    ]
    if extra:
        base.insert(0, extra)
    return base
