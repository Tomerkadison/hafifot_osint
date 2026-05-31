"""Chapter 06 - Joins & Merging (deep, real-life mission)."""

from pathlib import Path

import htmlgen as H
from nbbuild import build

CH = "06_Joins_and_Merging"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 06 — Joins & Merging"

INTRO_MD = (
    "This is the chapter that matters most for our daily work in Foundry. Real "
    "pipelines are never one table — they are an `orders` fact table plus "
    "`customers`, `products`, and `regions` dimension tables that we **join** "
    "together to build one rich, denormalized analytics table. No more VLOOKUPs.\n\n"
    "We will use every join type — `inner`, `left`, `full`, `semi`, `anti`, "
    "`cross` — joins on differently-named keys (`left_on`/`right_on`), joins on "
    "multiple keys, and the all-important habit of **checking row counts** so a "
    "join never silently explodes our data.\n\n"
    "*זה הפרק הכי חשוב לעבודה היומיומית שלנו ב-Foundry. pipeline אמיתי הוא אף פעם "
    "לא טבלה אחת — יש טבלת `orders` ועוד טבלאות מימד: `customers`, `products`, "
    "`regions`, שאותן מחברים (join) לטבלת אנליטיקה אחת עשירה. בלי VLOOKUP.*\n\n"
    "**Data files:** `data/orders.csv`, `data/customers.csv`, "
    "`data/products.csv`, `data/regions.csv`"
)

ITEMS = [
    {"md": "Import Polars and read all four tables: `orders`, `customers`, "
           "`products`, `regions`.\n\n"
           "*ייבאו את Polars וקראו את ארבע הטבלאות: `orders`, `customers`, "
           "`products`, `regions`.*",
     "sol": 'import polars as pl\n\n'
            'orders = pl.read_csv("data/orders.csv")\n'
            'customers = pl.read_csv("data/customers.csv")\n'
            'products = pl.read_csv("data/products.csv")\n'
            'regions = pl.read_csv("data/regions.csv")\n'
            'orders.shape, customers.shape, products.shape, regions.shape'},

    {"md": "Look at the **keys**: print the columns of each table. Which column "
           "links `orders` to `customers`? to `products`?\n\n"
           "*הסתכלו על המפתחות: הדפיסו את העמודות של כל טבלה. איזו עמודה מקשרת בין "
           "`orders` ל-`customers`? ל-`products`?*",
     "sol": 'for name, df in [("orders", orders), ("customers", customers),\n'
            '                 ("products", products), ("regions", regions)]:\n'
            '    print(name, "->", df.columns)'},

    {"md": "**Left join** `orders` with `customers` on `customer_id` to attach each "
           "order's `segment` and `signup_date`.\n\n"
           "*בצעו left join בין `orders` ל-`customers` על `customer_id` כדי לצרף לכל "
           "הזמנה את ה-`segment` ו-`signup_date` של הלקוח.*",
     "sol": 'orders.join(\n'
            '    customers.select("customer_id", "segment", "signup_date"),\n'
            '    on="customer_id", how="left",\n'
            ').head()'},

    {"md": "A left join must **never add rows**. Confirm that the row count after "
           "the join equals the original `orders` row count.\n\n"
           "*left join אסור שיוסיף שורות. ודאו שמספר השורות אחרי ה-join שווה למספר "
           "השורות המקורי של `orders`.*",
     "sol": 'joined = orders.join(customers, on="customer_id", how="left")\n'
            'orders.height, joined.height, orders.height == joined.height'},

    {"md": "**Inner join** `orders` with `products` on `product_sku` to attach "
           "`unit_cost` and `list_price`.\n\n"
           "*בצעו inner join בין `orders` ל-`products` על `product_sku` כדי לצרף "
           "`unit_cost` ו-`list_price`.*",
     "sol": 'orders.join(\n'
            '    products.select("product_sku", "unit_cost", "list_price"),\n'
            '    on="product_sku", how="inner",\n'
            ').head()'},

    {"md": "After joining `products`, compute each order's **margin** = "
           "`(unit_price - unit_cost) * quantity`. Show the 5 columns "
           "`order_id, quantity, unit_price, unit_cost, margin`.\n\n"
           "*אחרי join ל-`products`, חשבו לכל הזמנה margin = "
           "`(unit_price - unit_cost) * quantity`.*",
     "sol": 'orders.join(products.select("product_sku", "unit_cost"), on="product_sku")\\\n'
            '    .with_columns(\n'
            '        margin=(pl.col("unit_price") - pl.col("unit_cost")) * pl.col("quantity")\n'
            '    ).select("order_id", "quantity", "unit_price", "unit_cost", "margin").head()'},

    {"md": "Join on **differently-named keys**: `orders.region` holds a region "
           "*name*, while `regions.region_name` holds the same names. Left-join them "
           "(`left_on` / `right_on`) to attach `currency` and `tax_rate`.\n\n"
           "*join על מפתחות בעלי שם שונה: `orders.region` מכיל שם אזור, ו-"
           "`regions.region_name` מכיל את אותם שמות. חברו אותם עם `left_on`/`right_on` "
           "כדי לצרף `currency` ו-`tax_rate`.*",
     "sol": 'orders.join(\n'
            '    regions.select("region_name", "currency", "tax_rate"),\n'
            '    left_on="region", right_on="region_name", how="left",\n'
            ').select("order_id", "region", "currency", "tax_rate").head()'},

    {"md": "**Semi join:** which customers placed **at least one** order? Return the "
           "matching customer rows only (no order columns added).\n\n"
           "*semi join: אילו לקוחות ביצעו לפחות הזמנה אחת? החזירו רק את שורות הלקוחות "
           "התואמות (בלי עמודות הזמנה).*",
     "sol": 'customers.join(orders, on="customer_id", how="semi").head()'},

    {"md": "**Anti join:** which customers placed **no** orders at all?\n\n"
           "*anti join: אילו לקוחות לא ביצעו אף הזמנה?*",
     "sol": 'customers.join(orders, on="customer_id", how="anti")'},

    {"md": "**How many** customers have no orders? (count the anti-join rows)\n\n"
           "*כמה לקוחות לא ביצעו אף הזמנה? (ספרו את שורות ה-anti join)*",
     "sol": 'customers.join(orders, on="customer_id", how="anti").height'},

    {"md": "Build a **multi-key join**. First make two summaries per "
           "`region` + `channel`: total revenue, and order count. Then **join them "
           "on both keys** (`on=[\"region\", \"channel\"]`).\n\n"
           "*בנו join על שני מפתחות. קודם הכינו שני סיכומים לכל `region`+`channel`: "
           "סך הכנסה, ומספר הזמנות. ואז חברו אותם על שני המפתחות.*",
     "sol": 'rev = (orders.with_columns(revenue=pl.col("quantity") * pl.col("unit_price"))\n'
            '       .group_by("region", "channel").agg(pl.col("revenue").sum()))\n'
            'cnt = orders.group_by("region", "channel").agg(pl.len().alias("n_orders"))\n'
            'rev.join(cnt, on=["region", "channel"]).sort("revenue", descending=True)'},

    {"md": "Join `products` (for `unit_cost`) and compute the **total margin per "
           "category** (join, then `group_by` + `agg`).\n\n"
           "*חברו את `products` (בשביל `unit_cost`) וחשבו את סך ה-margin לכל "
           "`category`.*",
     "sol": 'orders.join(products.select("product_sku", "unit_cost"), on="product_sku")\\\n'
            '    .with_columns(\n'
            '        margin=(pl.col("unit_price") - pl.col("unit_cost")) * pl.col("quantity")\n'
            '    ).group_by("category").agg(pl.col("margin").sum())\\\n'
            '    .sort("margin", descending=True)'},

    {"md": "Join `customers` and report the **total revenue of Enterprise-segment "
           "orders** (join, filter `segment == \"Enterprise\"`, sum revenue).\n\n"
           "*חברו את `customers` ודווחו את סך ההכנסה של הזמנות בסגמנט Enterprise.*",
     "sol": 'orders.join(customers.select("customer_id", "segment"), on="customer_id")\\\n'
            '    .filter(pl.col("segment") == "Enterprise")\\\n'
            '    .select((pl.col("quantity") * pl.col("unit_price")).sum().alias("enterprise_revenue"))'},

    {"md": "🎯 **Mission — build the enriched analytics table.** Chain the joins: "
           "`orders` + `customers` (segment) + `products` (unit_cost) + `regions` "
           "(tax_rate). Then add `revenue` and `margin`. Show the first rows.\n\n"
           "*משימה: בנו את טבלת האנליטיקה המועשרת. שרשרו את ה-joins: "
           "`orders` + `customers` + `products` + `regions`, והוסיפו `revenue` ו-`margin`.*",
     "sol": 'analytics = (\n'
            '    orders\n'
            '    .join(customers.select("customer_id", "segment"), on="customer_id", how="left")\n'
            '    .join(products.select("product_sku", "unit_cost"), on="product_sku", how="left")\n'
            '    .join(regions.select("region_name", "tax_rate"),\n'
            '          left_on="region", right_on="region_name", how="left")\n'
            '    .with_columns(\n'
            '        revenue=pl.col("quantity") * pl.col("unit_price"),\n'
            '        margin=(pl.col("unit_price") - pl.col("unit_cost")) * pl.col("quantity"),\n'
            '    )\n'
            ')\n'
            'analytics.select(\n'
            '    "order_id", "segment", "category", "tax_rate", "revenue", "margin"\n'
            ').head()'},

    {"md": "Using the enriched table, compute `revenue_with_tax` = "
           "`revenue * (1 + tax_rate)`, rounded to 2 decimals.\n\n"
           "*בעזרת הטבלה המועשרת, חשבו `revenue_with_tax` = "
           "`revenue * (1 + tax_rate)`, מעוגל ל-2 ספרות.*",
     "sol": 'analytics.with_columns(\n'
            '    revenue_with_tax=(pl.col("revenue") * (1 + pl.col("tax_rate"))).round(2)\n'
            ').select("order_id", "revenue", "tax_rate", "revenue_with_tax").head()'},

    {"md": "From the enriched table, the **top 5 customers by total margin** "
           "(group by `customer_id`).\n\n"
           "*מהטבלה המועשרת, 5 הלקוחות המובילים לפי סך ה-margin.*",
     "sol": 'analytics.group_by("customer_id").agg(pl.col("margin").sum())\\\n'
            '    .sort("margin", descending=True).head(5)'},

    {"md": "**Cross join** to build a template of every possible `region_name` × "
           "`category` combination (every region paired with every category).\n\n"
           "*cross join לבניית תבנית של כל הצירופים האפשריים של `region_name` × "
           "`category`.*",
     "sol": 'regions.select("region_name").join(\n'
            '    products.select("category").unique(), how="cross"\n'
            ').sort("region_name", "category")'},

    {"md": "A left join can create **nulls** when there is no match. Left-join "
           "`orders` to **only the Enterprise customers**, then count how many orders "
           "got a null `segment` (i.e. their customer was not Enterprise).\n\n"
           "*left join יכול ליצור ערכי null כשאין התאמה. חברו `orders` ל-לקוחות "
           "Enterprise בלבד, וספרו כמה הזמנות קיבלו `segment` ריק (null).*",
     "sol": 'ent = customers.filter(pl.col("segment") == "Enterprise").select("customer_id", "segment")\n'
            'left = orders.join(ent, on="customer_id", how="left")\n'
            'left.filter(pl.col("segment").is_null()).height'},
]


# --------------------------------------------------------------------------- #
CUSTOMERS_COLS = [
    ("customer_id", "str", "🔑 מפתח — מקשר ל-<code>orders.customer_id</code>"),
    ("customer_name", "str", "שם הלקוח"),
    ("region_id", "str", "מקשר ל-<code>regions.region_id</code>"),
    ("segment", "str", "סגמנט (SMB / Mid-Market / Enterprise)"),
    ("signup_date", "str", "תאריך הצטרפות"),
]
PRODUCTS_COLS = [
    ("product_sku", "str", "🔑 מפתח — מקשר ל-<code>orders.product_sku</code>"),
    ("product_name", "str", "שם המוצר"),
    ("category", "str", "קטגוריה"),
    ("unit_cost", "f64", "עלות ליחידה (לחישוב margin)"),
    ("list_price", "f64", "מחיר מחירון"),
]
REGIONS_COLS = [
    ("region_id", "str", "🔑 מפתח — מקשר ל-<code>customers.region_id</code>"),
    ("region_name", "str", "שם האזור — תואם ל-<code>orders.region</code>"),
    ("currency", "str", "מטבע"),
    ("tax_rate", "f64", "שיעור מס (לחישוב מחיר כולל מע\"מ)"),
]

SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>זה הלב של העבודה שלנו. במציאות המידע אף פעם לא יושב בטבלה אחת — "
             "יש טבלת עובדות (<code>orders</code>) וטבלאות מימד (<code>customers</code>, "
             "<code>products</code>, <code>regions</code>). <strong>join</strong> "
             "מחבר ביניהן לפי מפתח משותף, בדיוק כמו VLOOKUP — רק נכון, מהיר, ובלי "
             "טעויות.</p>"
             "<p>בסוף הפרק תבנו טבלת אנליטיקה מועשרת אחת — בדיוק כמו טרנספורמציה "
             "אמיתית ב-Foundry.</p>"},

    {"type": "text", "h2": "סוגי ה-join — לדעת בעל פה",
     "body": "<table>"
             "<thead><tr><th>how=</th><th>מה הוא מחזיר</th></tr></thead>"
             "<tbody>"
             "<tr><td><code>inner</code></td><td>רק שורות שיש להן התאמה בשתי הטבלאות</td></tr>"
             "<tr><td><code>left</code></td><td>כל השורות משמאל + התאמות מימין (אין התאמה → null)</td></tr>"
             "<tr><td><code>right</code></td><td>כל השורות מימין + התאמות משמאל</td></tr>"
             "<tr><td><code>full</code></td><td>כל השורות משני הצדדים</td></tr>"
             "<tr><td><code>semi</code></td><td>שורות משמאל <em>שיש</em> להן התאמה — בלי להוסיף עמודות</td></tr>"
             "<tr><td><code>anti</code></td><td>שורות משמאל ש<em>אין</em> להן התאמה</td></tr>"
             "<tr><td><code>cross</code></td><td>כל צירוף אפשרי (מכפלה קרטזית)</td></tr>"
             "</tbody></table>"
             "<p class='muted' style='margin-top:10px'><code>semi</code> ו-<code>anti</code> "
             "הם כלים מעולים לבדיקות איכות נתונים: \"אילו לקוחות בלי הזמנות?\".</p>"},

    {"type": "warn", "text": "<strong>הסכנה הגדולה ב-join:</strong> אם המפתח מימין "
                            "אינו ייחודי, מספר השורות יכול <strong>להתפוצץ</strong> "
                            "(שורה משמאל מוכפלת לכל התאמה). תמיד בדקו את מספר השורות "
                            "אחרי join — left join לא אמור להוסיף שורות."},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "חיבור טבלאות ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>a.merge(b, on='k')</code>",
         "<code>a.merge(b, how='left')</code>",
         "<code>a.merge(b, left_on=, right_on=)</code>",
         "semi/anti: ידני ומסורבל",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>a.join(b, on='k')</code>",
         "<code>a.join(b, how='left')</code>",
         "<code>a.join(b, left_on=, right_on=)</code>",
         "<code>how='semi'</code> / <code>how='anti'</code>",
     ],
     "note": "💡 ב-Polars אפשר לשרשר כמה <code>join</code> אחד אחרי השני "
             "בשרשרת אחת — וכך בונים טבלת אנליטיקה מלאה."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("חיבור שתי טבלאות", "DataFrame.join()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join.html"),
         ("חיבור לפי קרבה (זמן)", "DataFrame.join_asof()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join_asof.html"),
         ("הצמדה אופקית פשוטה", "DataFrame.hstack()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.hstack.html"),
         ("שרשור (לפרק הבא)", "polars.concat()",
          "https://docs.pola.rs/api/python/stable/reference/api/polars.concat.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>קראו היטב את התיעוד של <code>join</code> — את כל הערכים של "
             "<code>how</code>, ואת <code>validate</code> ו-<code>coalesce</code>. "
             "אלה הכלים שמונעים באגים שקטים בטרנספורמציות.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>זה התרגיל המרכזי בקורס (18 שאלות, ארוך יותר). תעבדו עם "
             "<strong>ארבע טבלאות</strong> ותתרגלו את כל סוגי ה-join. השיא הוא "
             "<strong>המשימה</strong>: לשרשר את כל החיבורים לטבלת אנליטיקה מועשרת אחת, "
             "בדיוק כמו טרנספורמציה אמיתית ב-Foundry.</p>"},
    {"type": "warn", "text": "אחרי כל join — בדקו את מספר השורות! join לא תקין "
                            "יכול לשכפל שורות בשקט ולקלקל את כל החישובים."},
    {"type": "text", "h2": "מודל הנתונים (הקשרים בין הטבלאות)",
     "body": "<p>ארבע הטבלאות מקושרות כך:</p>"
             "<ul>"
             "<li><code>orders.customer_id</code> → <code>customers.customer_id</code></li>"
             "<li><code>orders.product_sku</code> → <code>products.product_sku</code></li>"
             "<li><code>orders.region</code> (שם) → <code>regions.region_name</code></li>"
             "<li><code>customers.region_id</code> → <code>regions.region_id</code></li>"
             "</ul>"},
    {"type": "datatable", "h2": "טבלה: <code>customers.csv</code>",
     "intro": "200 לקוחות.", "rows": CUSTOMERS_COLS},
    {"type": "datatable", "h2": "טבלה: <code>products.csv</code>",
     "intro": "12 מוצרים.", "rows": PRODUCTS_COLS},
    {"type": "datatable", "h2": "טבלה: <code>regions.csv</code>",
     "intro": "5 אזורים.", "rows": REGIONS_COLS},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>inner</code>, <code>left</code>, <code>full</code> joins",
        "<code>semi</code> ו-<code>anti</code> לבדיקות איכות נתונים",
        "<code>left_on</code> / <code>right_on</code> למפתחות בשם שונה",
        "join על כמה מפתחות (<code>on=[\"a\", \"b\"]</code>)",
        "<code>cross</code> join",
        "שרשור כמה joins לטבלת אנליטיקה אחת",
        "בדיקת מספר שורות וטיפול ב-null אחרי join",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'ודאו שכל ארבעת קובצי ה-CSV נמצאים בתיקיית <code>data/</code>.',
        'פתחו את <code>Exercises.ipynb</code> וענו שאלה-שאלה.',
        'אחרי כל join — בדקו <code>.shape</code> כדי לוודא שלא נוספו שורות.',
        'סיימתם? השוו מול <code>Solutions.ipynb</code>.',
    ]},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 06 — חיבור טבלאות (Joins) | Polars",
             kicker="Polars for Power Users · פרק 06", kicker_color=H.BRAND2,
             title="חיבור טבלאות (Joins)",
             subtitle="הפרק הכי חשוב לעבודה שלנו — מחברים טבלאות לטבלת אנליטיקה אחת, בלי VLOOKUP.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 06 — התרגיל והמידע | Polars",
             kicker="פרק 06 · התרגיל והמידע", kicker_color=H.GREEN,
             title="בניית טבלת אנליטיקה מ-4 טבלאות",
             subtitle="המשימה המרכזית: לשרשר joins לטבלה מועשרת אחת — כמו ב-Foundry.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
