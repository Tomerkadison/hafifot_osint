"""Chapter 08 - Cleaning Data (mission, longer)."""

from pathlib import Path

import htmlgen as H
from nbbuild import build

CH = "08_Cleaning_Data"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 08 — Cleaning Data"

INTRO_MD = (
    "Raw exports are messy: duplicate rows, text in different cases, stray spaces, "
    "numbers stored as strings (`\"$3.50\"`, `\"10%\"`, `\"N/A\"`), and dates in three "
    "different formats. Before *any* analysis is trustworthy, the data must be "
    "cleaned. This is one of the most important real-world skills — and a big part "
    "of what our Foundry transforms actually do.\n\n"
    "*export גולמי תמיד מלוכלך: שורות כפולות, טקסט באותיות שונות, רווחים מיותרים, "
    "מספרים ששמורים כמחרוזות (`\"$3.50\"`, `\"10%\"`, `\"N/A\"`), ותאריכים בשלושה "
    "פורמטים שונים. לפני שאפשר לסמוך על ניתוח כלשהו — חייבים לנקות את המידע.*\n\n"
    "**Data file:** `data/orders_messy.csv`"
)

ITEMS = [
    {"md": "Import Polars and read `data/orders_messy.csv` into `messy`. Look at the "
           "first rows — notice the dirty values.\n\n"
           "*ייבאו את Polars וקראו את `data/orders_messy.csv` ל-`messy`. הסתכלו על "
           "השורות הראשונות — שימו לב לערכים המלוכלכים.*",
     "sol": 'import polars as pl\n\n'
            'messy = pl.read_csv("data/orders_messy.csv")\nmessy.head()'},

    {"md": "Check the schema. Which columns came in as **strings** even though they "
           "should be numbers or dates?\n\n"
           "*בדקו את ה-schema. אילו עמודות הגיעו כמחרוזות למרות שהן אמורות להיות "
           "מספרים או תאריכים?*",
     "sol": "messy.schema"},

    {"md": "How many **fully-duplicate rows** are there? "
           "(hint: `height` minus `unique().height`)\n\n"
           "*כמה שורות כפולות לחלוטין יש? (רמז: `height` פחות `unique().height`)*",
     "sol": "messy.height - messy.unique().height"},

    {"md": "Remove the exact duplicate rows with `unique()`. How many rows remain?\n\n"
           "*הסירו את השורות הכפולות עם `unique()`. כמה שורות נשארו?*",
     "sol": "dedup = messy.unique()\ndedup.height"},

    {"md": "Clean the `region` column: **strip** surrounding spaces and convert to "
           "**Title Case** (so `\"  EUROPE \"` and `\"europe\"` both become "
           "`\"Europe\"`).\n\n"
           "*נקו את `region`: הסירו רווחים מסביב והמירו ל-Title Case.*",
     "sol": 'messy.with_columns(\n'
            '    region=pl.col("region").str.strip_chars().str.to_titlecase()\n'
            ').get_column("region").unique().sort()'},

    {"md": "Clean the `category` column to a consistent lower-case, with no "
           "surrounding spaces.\n\n"
           "*נקו את `category` לאותיות קטנות אחידות, בלי רווחים מסביב.*",
     "sol": 'messy.with_columns(\n'
            '    category=pl.col("category").str.strip_chars().str.to_lowercase()\n'
            ').get_column("category").unique().sort()'},

    {"md": "Fix `quantity`: it is a string with some `\"N/A\"` values. Cast it to an "
           "integer with `strict=False` so bad values become **null**.\n\n"
           "*תקנו את `quantity`: זו מחרוזת עם כמה ערכי `\"N/A\"`. המירו למספר שלם עם "
           "`strict=False` כך שערכים פגומים יהפכו ל-null.*",
     "sol": 'messy.with_columns(\n'
            '    quantity=pl.col("quantity").cast(pl.Int64, strict=False)\n'
            ').get_column("quantity").head(10)'},

    {"md": "**How many** `quantity` values were invalid (became null after the "
           "cast)?\n\n"
           "*כמה ערכי `quantity` היו לא תקינים (הפכו ל-null אחרי ההמרה)?*",
     "sol": 'messy.select(\n'
            '    pl.col("quantity").cast(pl.Int64, strict=False).is_null().sum()\n'
            ')'},

    {"md": "Fix `unit_price`: it looks like `\"$3.50\"`. Strip the leading `$` and "
           "cast to a float.\n\n"
           "*תקנו את `unit_price`: הוא נראה כמו `\"$3.50\"`. הסירו את ה-`$` בהתחלה "
           "והמירו ל-float.*",
     "sol": 'messy.with_columns(\n'
            '    unit_price=pl.col("unit_price").str.strip_chars_start("$").cast(pl.Float64)\n'
            ').get_column("unit_price").head()'},

    {"md": "Fix `discount`: values look like `\"10%\"` (and some are empty). Turn "
           "them into a fraction (`0.10`); empty values should become null. "
           "(strip `%`, cast to float with `strict=False`, divide by 100)\n\n"
           "*תקנו את `discount`: הערכים נראים כמו `\"10%\"` (וחלקם ריקים). הפכו אותם "
           "לשבר (`0.10`); ערכים ריקים יהפכו ל-null.*",
     "sol": 'messy.with_columns(\n'
            '    discount=pl.col("discount").str.strip_chars("%")\n'
            '    .cast(pl.Float64, strict=False) / 100\n'
            ').get_column("discount").head(10)'},

    {"md": "Fix `order_date`: it arrives in **three** formats — `2023-01-05`, "
           "`05/01/2023`, `2023.01.05`. Parse all of them into one real Date column "
           "using `pl.coalesce` over three `to_date` attempts.\n\n"
           "*תקנו את `order_date`: הוא מגיע בשלושה פורמטים. נתחו את כולם לעמודת תאריך "
           "אחת בעזרת `pl.coalesce` על שלושה ניסיונות `to_date`.*",
     "sol": 'messy.with_columns(\n'
            '    order_date=pl.coalesce(\n'
            '        pl.col("order_date").str.to_date("%Y-%m-%d", strict=False),\n'
            '        pl.col("order_date").str.to_date("%d/%m/%Y", strict=False),\n'
            '        pl.col("order_date").str.to_date("%Y.%m.%d", strict=False),\n'
            '    )\n'
            ').get_column("order_date").head()'},

    {"md": "Standardize `status` to lower-case, then show the `value_counts` to "
           "confirm there are only the expected categories.\n\n"
           "*תקננו את `status` לאותיות קטנות, ואז הציגו `value_counts` כדי לוודא שיש "
           "רק את הקטגוריות הצפויות.*",
     "sol": 'messy.with_columns(\n'
            '    status=pl.col("status").str.to_lowercase()\n'
            ').get_column("status").value_counts(sort=True)'},

    {"md": "🎯 **Mission — the full cleaning pipeline.** In one `with_columns` chain, "
           "produce a clean table: dedupe, fix `region`, `category`, `quantity`, "
           "`unit_price`, `discount`, `order_date`, and `status` all together. Save "
           "it as `clean` and show its schema.\n\n"
           "*משימה — צינור הניקוי המלא. בשרשרת אחת, הפיקו טבלה נקייה: הסרת כפילויות "
           "ותיקון כל העמודות יחד. שמרו כ-`clean` והציגו את ה-schema.*",
     "sol": 'clean = messy.unique().with_columns(\n'
            '    region=pl.col("region").str.strip_chars().str.to_titlecase(),\n'
            '    category=pl.col("category").str.strip_chars().str.to_lowercase(),\n'
            '    quantity=pl.col("quantity").cast(pl.Int64, strict=False),\n'
            '    unit_price=pl.col("unit_price").str.strip_chars_start("$").cast(pl.Float64),\n'
            '    discount=pl.col("discount").str.strip_chars("%").cast(pl.Float64, strict=False) / 100,\n'
            '    order_date=pl.coalesce(\n'
            '        pl.col("order_date").str.to_date("%Y-%m-%d", strict=False),\n'
            '        pl.col("order_date").str.to_date("%d/%m/%Y", strict=False),\n'
            '        pl.col("order_date").str.to_date("%Y.%m.%d", strict=False),\n'
            '    ),\n'
            '    status=pl.col("status").str.to_lowercase(),\n'
            ')\nclean.schema'},

    {"md": "From the clean table, **drop the rows where `quantity` is null** "
           "(the invalid `\"N/A\"` rows). How many rows remain?\n\n"
           "*מהטבלה הנקייה, הסירו את השורות שבהן `quantity` הוא null (השורות הפגומות). "
           "כמה שורות נשארו?*",
     "sol": 'clean.drop_nulls(subset="quantity").height'},

    {"md": "In the clean table, fill the remaining null `discount` values with `0`.\n\n"
           "*בטבלה הנקייה, מלאו את ערכי ה-`discount` החסרים שנותרו ב-0.*",
     "sol": 'clean.with_columns(\n'
            '    discount=pl.col("discount").fill_null(0)\n'
            ').get_column("discount").head(10)'},

    {"md": "Prove the data is now usable: add `revenue` "
           "(`quantity * unit_price * (1 - discount filled with 0)`) and show total "
           "revenue **per region**.\n\n"
           "*הוכיחו שהמידע שמיש עכשיו: הוסיפו `revenue` והציגו סך הכנסה לכל `region`.*",
     "sol": 'clean.drop_nulls(subset="quantity").with_columns(\n'
            '    revenue=pl.col("quantity") * pl.col("unit_price")\n'
            '    * (1 - pl.col("discount").fill_null(0))\n'
            ').group_by("region").agg(pl.col("revenue").sum().round(2))\\\n'
            '   .sort("revenue", descending=True)'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>בעולם האמיתי המידע מגיע מלוכלך — וזו לא בעיה נדירה, זה <strong>רוב "
             "העבודה</strong>. לפני כל ניתוח חייבים לנקות: להסיר כפילויות, לאחד "
             "אותיות גדולות/קטנות, להסיר רווחים, להמיר מספרים ותאריכים שנשמרו "
             "כטקסט, ולנתח תאריכים בפורמטים שונים.</p>"
             "<p>הפרק הזה הוא <strong>משימה</strong>: לוקחים קובץ מלוכלך ומפיקים ממנו "
             "טבלה נקייה ומוכנה לעבודה — בדיוק מה שטרנספורמציה ב-Foundry עושה.</p>"},

    {"type": "text", "h2": "הטכניקות המרכזיות לניקוי",
     "body": "<ul>"
             "<li><strong>כפילויות:</strong> <code>unique()</code></li>"
             "<li><strong>טקסט:</strong> <code>str.strip_chars()</code>, "
             "<code>str.to_lowercase()</code>, <code>str.to_titlecase()</code></li>"
             "<li><strong>מספרים מטקסט:</strong> מסירים תווים (<code>$</code>, "
             "<code>%</code>) ואז <code>cast(..., strict=False)</code></li>"
             "<li><strong>ערכים חסרים:</strong> <code>fill_null()</code>, "
             "<code>drop_nulls()</code></li>"
             "<li><strong>תאריכים בכמה פורמטים:</strong> <code>pl.coalesce()</code> על "
             "כמה ניסיונות <code>str.to_date(..., strict=False)</code></li>"
             "</ul>"},

    {"type": "warn", "text": "<strong>הטריק החשוב:</strong> <code>strict=False</code> "
                            "ב-<code>cast</code> וב-<code>to_date</code> הופך ערכים "
                            "פגומים ל-null במקום לזרוק שגיאה — וכך אפשר לזהות ולטפל "
                            "בהם בנפרד."},

    {"type": "compare", "h2": "Polars מול מה שאתם מכירים",
     "intro": "ניקוי נתונים ב-pandas מול Polars:",
     "left_title": "🐼 pandas", "left": [
         "<code>df.drop_duplicates()</code>",
         "<code>df['c'].str.strip().str.title()</code>",
         "<code>pd.to_numeric(s, errors='coerce')</code>",
         "<code>df['c'].fillna(0)</code>",
     ],
     "right_title": "⚡ Polars", "right": [
         "<code>df.unique()</code>",
         "<code>pl.col('c').str.strip_chars().str.to_titlecase()</code>",
         "<code>pl.col('s').cast(pl.Float64, strict=False)</code>",
         "<code>pl.col('c').fill_null(0)</code>",
     ],
     "note": "💡 <code>strict=False</code> הוא המקבילה ל-<code>errors='coerce'</code> "
             "של pandas — ממיר מה שאפשר, ושם null בשאר."},

    {"type": "functable", "h2": "הפונקציות של הפרק + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("הסרת שורות כפולות", "DataFrame.unique()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.unique.html"),
         ("הסרת רווחים", "Expr.str.strip_chars()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.strip_chars.html"),
         ("Title Case", "Expr.str.to_titlecase()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.to_titlecase.html"),
         ("המרת טיפוס", "Expr.cast()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.cast.html"),
         ("הערך הראשון שאינו null", "polars.coalesce()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.coalesce.html"),
         ("מילוי ערכים חסרים", "Expr.fill_null()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.fill_null.html"),
         ("הסרת שורות עם null", "DataFrame.drop_nulls()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.drop_nulls.html"),
         ("החלפת טקסט", "Expr.str.replace()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.replace.html"),
     ]},

    {"type": "cta", "h2": "🎯 לקריאה נוספת",
     "body": "<p>עברו שוב על כל ה-namespace של <code>str</code> — בניקוי נתונים "
             "משתמשים בו יותר מכל דבר אחר. וקראו על <code>fill_null</code> "
             "(יש לו אסטרטגיות: forward, backward, mean ...).</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>תרגיל-משימה ארוך (16 שאלות). תקבלו קובץ הזמנות <strong>מלוכלך</strong> "
             "ותנקו אותו צעד-אחר-צעד, עד שתבנו צינור ניקוי מלא שמפיק טבלה נקייה "
             "ושמישה. זו אחת המיומנויות הכי חשובות בעבודה האמיתית.</p>"},
    {"type": "warn", "text": "המידע מלוכלך בכוונה! כפילויות, אותיות לא אחידות, רווחים, "
                            "מספרים כטקסט (<code>$3.50</code>, <code>10%</code>, "
                            "<code>N/A</code>), ותאריכים בשלושה פורמטים."},
    {"type": "datatable", "h2": "המידע: <code>data/orders_messy.csv</code>",
     "intro": "כ-325 שורות (כולל כפילויות). הבעיה בכל עמודה מסומנת ב-⚠️:",
     "rows": [
         ("order_id", "str", "מזהה ההזמנה (תקין)"),
         ("customer_id", "str", "מזהה הלקוח (תקין)"),
         ("order_date", "str", "⚠️ שלושה פורמטים שונים של תאריך"),
         ("region", "str", "⚠️ אותיות גדולות/קטנות לא אחידות + רווחים"),
         ("category", "str", "⚠️ אותיות לא אחידות + רווחים"),
         ("quantity", "str", "⚠️ מספר ששמור כטקסט, עם ערכי <code>N/A</code>"),
         ("unit_price", "str", "⚠️ מחיר עם סימן <code>$</code> (טקסט)"),
         ("discount", "str", "⚠️ אחוז כטקסט (<code>10%</code>), חלקו ריק"),
         ("status", "str", "⚠️ אותיות גדולות/קטנות לא אחידות"),
     ]},
    {"type": "list", "h2": "מה תתרגלו", "items": [
        "<code>unique()</code> להסרת כפילויות",
        "ניקוי טקסט: <code>strip_chars</code>, <code>to_titlecase</code>, <code>to_lowercase</code>",
        "המרת מספרים מטקסט עם <code>cast(..., strict=False)</code>",
        "ניתוח תאריכים בכמה פורמטים עם <code>coalesce</code>",
        "<code>fill_null</code> ו-<code>drop_nulls</code>",
        "בניית צינור ניקוי מלא בשרשרת אחת",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'פתחו את <code>Exercises.ipynb</code> והסתכלו טוב על המידע המלוכלך.',
        'נקו עמודה-עמודה, ואז אחדו הכל לצינור ניקוי אחד (המשימה).',
        'סיימתם? השוו מול <code>Solutions.ipynb</code>.',
    ]},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 08 — ניקוי נתונים | Polars",
             kicker="Polars for Power Users · פרק 08", kicker_color=H.BRAND2,
             title="ניקוי נתונים",
             subtitle="מהקובץ המלוכלך לטבלה נקייה — אחת המיומנויות הכי חשובות בעבודה.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 08 — התרגיל והמידע | Polars",
             kicker="פרק 08 · התרגיל והמידע", kicker_color=H.GREEN,
             title="משימת ניקוי: מקובץ מלוכלך לטבלה נקייה",
             subtitle="מנקים export אמיתי צעד-אחר-צעד עד לצינור ניקוי שלם.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
