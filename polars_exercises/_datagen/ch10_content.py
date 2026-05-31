"""Chapter 10 - Capstone: GDP / Population / R&D Case Study (long mission)."""

from pathlib import Path

import htmlgen as H
from nbbuild import build

CH = "10_Capstone_GDP_Case_Study"
CHAPTER_DIR = Path(__file__).resolve().parent.parent / CH

TITLE = "Polars Exercises 10 — Capstone: GDP Case Study"

INTRO_MD = (
    "The final mission. We bring together **everything** — reading messy files, "
    "cleaning, casting, renaming, window functions, pivoting, and multi-key joins — "
    "to build a real analytics report from three World-Bank / OECD datasets: "
    "**GDP**, **population**, and **R&D expenditure**. The goal: GDP per capita and "
    "R&D spend as a share of GDP, per country and year. This is a complete Foundry "
    "transform, start to finish.\n\n"
    "*המשימה האחרונה. נחבר את הכל — קריאת קבצים מלוכלכים, ניקוי, המרת טיפוסים, "
    "שינוי שמות, window functions, pivot, ו-joins על כמה מפתחות — כדי לבנות דוח "
    "אנליטי אמיתי משלושה מקורות: GDP, אוכלוסייה, והוצאות מו\"פ. זו טרנספורמציה "
    "שלמה מתחילתה ועד סופה.*\n\n"
    "**Data files:** `data/gdp.csv`, `data/population.csv`, `data/expenditure.csv`"
)

ITEMS = [
    {"md": "Import Polars. Read `data/gdp.csv` and **rename** the columns to "
           "`country`, `code`, `year`, `gdp`. Save as `gdp` and show the head.\n\n"
           "*ייבאו את Polars. קראו את `data/gdp.csv` ושנו את שמות העמודות ל-"
           "`country`, `code`, `year`, `gdp`. שמרו כ-`gdp`.*",
     "sol": 'import polars as pl\n\n'
            'gdp = pl.read_csv("data/gdp.csv").rename({\n'
            '    "Country Name": "country", "Country Code": "code",\n'
            '    "Year": "year", "Value": "gdp",\n'
            '})\ngdp.head()'},

    {"md": "Explore: run `describe()` on `gdp`. Over how many years does the data "
           "span (min and max `year`)?\n\n"
           "*חקרו: הריצו `describe()` על `gdp`. על פני כמה שנים פרוש המידע "
           "(min ו-max של `year`)?*",
     "sol": 'gdp.describe()'},

    {"md": "What is the **single largest GDP value** in the whole dataset, and which "
           "`country` and `year` does it belong to?\n\n"
           "*מהו ערך ה-GDP הגדול ביותר בכל המידע, ולאיזו `country` ו-`year` הוא שייך?*",
     "sol": 'top = gdp.select(pl.col("gdp").max()).item()\n'
            'gdp.filter(pl.col("gdp") == top)'},

    {"md": "How many years of data exist **per country**? Then: how many countries "
           "have **fewer than 64** years of data?\n\n"
           "*כמה שנות מידע יש לכל מדינה? וכמה מדינות יש להן פחות מ-64 שנות מידע?*",
     "sol": 'counts = gdp.group_by("country", "code").agg(pl.len())\n'
            'counts.filter(pl.col("len") < 64).height'},

    {"md": "**Window functions.** For each country (`over(\"code\")`), add four "
           "columns: `worst_gdp`, `worst_year`, `best_gdp`, `best_year` — the lowest "
           "and highest GDP and the years they happened. Save back to `gdp`.\n\n"
           "*window functions. לכל מדינה (`over(\"code\")`), הוסיפו ארבע עמודות: "
           "`worst_gdp`, `worst_year`, `best_gdp`, `best_year`. שמרו ל-`gdp`.*",
     "sol": 'gdp = gdp.with_columns(\n'
            '    worst_gdp=pl.col("gdp").get(pl.col("gdp").arg_min()).over("code"),\n'
            '    worst_year=pl.col("year").get(pl.col("gdp").arg_min()).over("code"),\n'
            '    best_gdp=pl.col("gdp").get(pl.col("gdp").arg_max()).over("code"),\n'
            '    best_year=pl.col("year").get(pl.col("gdp").arg_max()).over("code"),\n'
            ')\ngdp.filter(pl.col("code") == "AFG").head()'},

    {"md": "**Pivot** the original GDP figures into a wide table: one row per "
           "`country` + `code`, one column per `year`, values are `gdp`. Save as "
           "`gdp_pivot` and show its shape.\n\n"
           "*pivot של נתוני ה-GDP לטבלה רחבה: שורה לכל `country`+`code`, עמודה לכל "
           "`year`, הערכים הם `gdp`. שמרו כ-`gdp_pivot`.*",
     "sol": 'gdp_pivot = gdp.pivot(\n'
            '    on="year", index=["country", "code"], values="gdp", sort_columns=True\n'
            ')\ngdp_pivot.shape'},

    {"md": "Add a `best_gdp` column to `gdp_pivot` = the maximum across all the year "
           "columns (use `pl.max_horizontal` over the year columns).\n\n"
           "*הוסיפו ל-`gdp_pivot` עמודת `best_gdp` = המקסימום על פני כל עמודות השנים "
           "(השתמשו ב-`pl.max_horizontal`).*",
     "sol": 'year_cols = [c for c in gdp_pivot.columns if c not in ("country", "code")]\n'
            'gdp_pivot = gdp_pivot.with_columns(best_gdp=pl.max_horizontal(year_cols))\n'
            'gdp_pivot.select("country", "code", "best_gdp").head()'},

    {"md": "Write `gdp_pivot` to `processed/gdp_pivot.csv` "
           "(create the `processed` folder first).\n\n"
           "*כתבו את `gdp_pivot` ל-`processed/gdp_pivot.csv` (צרו קודם את התיקייה).*",
     "sol": 'from pathlib import Path\n'
            'Path("processed").mkdir(exist_ok=True)\n'
            'gdp_pivot.write_csv("processed/gdp_pivot.csv")\n'
            'print("wrote processed/gdp_pivot.csv")'},

    {"md": "Read `data/population.csv`. Its `Value` column looks like integers at "
           "first but has decimals later, so the default type inference fails. Read "
           "it robustly with `infer_schema_length=10000` and check the schema.\n\n"
           "*קראו את `data/population.csv`. עמודת `Value` נראית כמו מספרים שלמים "
           "בהתחלה אבל יש בה עשרוניים בהמשך, ולכן זיהוי הטיפוס האוטומטי נכשל. קראו "
           "אותה בעזרת `infer_schema_length=10000`.*",
     "sol": 'pop = pl.read_csv("data/population.csv", infer_schema_length=10000)\n'
            'pop.schema'},

    {"md": "Clean `pop`: rename `Country Name`→`country`, `Country Code`→`code`, "
           "`Year`→`year`, cast the population `Value` to an integer column `pop`, "
           "and keep only `country, code, year, pop`.\n\n"
           "*נקו את `pop`: שנו שמות, המירו את `Value` לעמודה שלמה `pop`, והשאירו רק "
           "`country, code, year, pop`.*",
     "sol": 'pop = pop.rename({\n'
            '    "Country Name": "country", "Country Code": "code", "Year": "year"\n'
            '}).with_columns(\n'
            '    pop=pl.col("Value").cast(pl.Int64)\n'
            ').select("country", "code", "year", "pop")\npop.head()'},

    {"md": "**Join** the population into `gdp` on the three keys "
           "`[\"country\", \"code\", \"year\"]` (left join). Save back to `gdp`.\n\n"
           "*חברו (join) את האוכלוסייה לתוך `gdp` על שלושת המפתחות (left join). "
           "שמרו ל-`gdp`.*",
     "sol": 'gdp = gdp.join(pop, on=["country", "code", "year"], how="left")\n'
            'gdp.select("country", "year", "gdp", "pop").head()'},

    {"md": "Compute **GDP per capita**: add a column `capita` = `gdp / pop`. Save "
           "back to `gdp`.\n\n"
           "*חשבו תוצר לנפש: הוסיפו עמודה `capita` = `gdp / pop`. שמרו ל-`gdp`.*",
     "sol": 'gdp = gdp.with_columns(capita=pl.col("gdp") / pl.col("pop"))\n'
            'gdp.select("country", "year", "gdp", "pop", "capita").head()'},

    {"md": "Quality check: are there suspicious per-capita values? Show rows where "
           "`capita` is above 200,000 (likely data quirks or tiny states).\n\n"
           "*בדיקת איכות: יש ערכי תוצר-לנפש חשודים? הציגו שורות שבהן `capita` מעל "
           "200,000.*",
     "sol": 'gdp.filter(pl.col("capita") > 200_000).select("country", "year", "capita").head()'},

    {"md": "Write the current `gdp` table (with population & per-capita) to "
           "`processed/gdp_report.csv`.\n\n"
           "*כתבו את טבלת `gdp` הנוכחית ל-`processed/gdp_report.csv`.*",
     "sol": 'gdp.write_csv("processed/gdp_report.csv")\nprint("wrote processed/gdp_report.csv")'},

    {"md": "Read `data/expenditure.csv`, keeping only the `LOCATION`, `TIME` and "
           "`Government` columns, and rename them to `code`, `year`, `spend`. "
           "Save as `rd`.\n\n"
           "*קראו את `data/expenditure.csv`, השאירו רק `LOCATION`, `TIME`, "
           "`Government`, ושנו שמות ל-`code`, `year`, `spend`. שמרו כ-`rd`.*",
     "sol": 'rd = pl.read_csv("data/expenditure.csv").select(\n'
            '    code=pl.col("LOCATION"),\n'
            '    year=pl.col("TIME"),\n'
            '    spend=pl.col("Government"),\n'
            ')\nrd.head()'},

    {"md": "The R&D figures are reported in thousands. Convert to absolute spend: "
           "add `k_spend` = `spend * 1000`, then keep only `code, year, k_spend`.\n\n"
           "*נתוני המו\"פ מדווחים באלפים. המירו לסכום מלא: הוסיפו `k_spend` = "
           "`spend * 1000`, והשאירו רק `code, year, k_spend`.*",
     "sol": 'rd = rd.with_columns(k_spend=pl.col("spend") * 1000)\\\n'
            '       .select("code", "year", "k_spend")\nrd.head()'},

    {"md": "**Join** `rd` into `gdp` on `[\"code\", \"year\"]` (left join). Save back "
           "to `gdp`.\n\n"
           "*חברו את `rd` לתוך `gdp` על `[\"code\", \"year\"]` (left join). שמרו ל-`gdp`.*",
     "sol": 'gdp = gdp.join(rd, on=["code", "year"], how="left")\n'
            'gdp.filter(pl.col("code") == "USA").select("year", "gdp", "k_spend").tail(5)'},

    {"md": "Compute R&D as a **share of GDP**: add `spend_pct` = `k_spend / gdp`. "
           "Save back to `gdp`.\n\n"
           "*חשבו את המו\"פ כאחוז מהתוצר: הוסיפו `spend_pct` = `k_spend / gdp`. "
           "שמרו ל-`gdp`.*",
     "sol": 'gdp = gdp.with_columns(spend_pct=pl.col("k_spend") / pl.col("gdp"))\n'
            'gdp.filter(pl.col("code") == "USA")'
            '.select("year", "gdp", "k_spend", "spend_pct").tail(5)'},

    {"md": "Write the full enriched report to `processed/gdp_full_report.csv`.\n\n"
           "*כתבו את הדוח המלא והמועשר ל-`processed/gdp_full_report.csv`.*",
     "sol": 'gdp.write_csv("processed/gdp_full_report.csv")\nprint("wrote processed/gdp_full_report.csv")'},

    {"md": "🎯 **Insight 1:** the **top 10 countries by GDP per capita in 2014** "
           "(filter year, sort, head).\n\n"
           "*תובנה 1: 10 המדינות המובילות לפי תוצר-לנפש בשנת 2014.*",
     "sol": 'gdp.filter((pl.col("year") == 2014) & pl.col("capita").is_not_null())\\\n'
            '   .sort("capita", descending=True)\\\n'
            '   .select("country", "capita").head(10)'},

    {"md": "🎯 **Insight 2:** among rows that *have* R&D data, the **top 10 by "
           "`spend_pct`** (R&D as a share of GDP) — who invests most in research?\n\n"
           "*תובנה 2: מבין השורות שיש בהן נתוני מו\"פ, 10 המובילות לפי `spend_pct` — "
           "מי משקיע הכי הרבה במחקר?*",
     "sol": 'gdp.filter(pl.col("spend_pct").is_not_null())\\\n'
            '   .sort("spend_pct", descending=True)\\\n'
            '   .select("country", "year", "spend_pct").head(10)'},

    {"md": "🎯 **Insight 3:** for the USA, the **average `spend_pct` across all years "
           "that have data** (filter USA + non-null, then mean).\n\n"
           "*תובנה 3: עבור ארה\"ב, ה-`spend_pct` הממוצע על פני כל השנים עם נתונים.*",
     "sol": 'gdp.filter((pl.col("code") == "USA") & pl.col("spend_pct").is_not_null())\\\n'
            '   .select(pl.col("spend_pct").mean().alias("usa_avg_spend_pct"))'},
]


# --------------------------------------------------------------------------- #
SUBJECT_SLIDES = [
    {"type": "text", "h2": "על מה הפרק הזה?",
     "body": "<p>זה <strong>הפרויקט המסכם</strong>. עד עכשיו תרגלנו כל נושא בנפרד — "
             "כאן מחברים את הכל לטרנספורמציה אחת שלמה, בדיוק כמו pipeline אמיתי "
             "ב-Foundry.</p>"
             "<p>ניקח שלושה מקורות נתונים אמיתיים (תוצר, אוכלוסייה, והוצאות מו\"פ), "
             "ננקה אותם, נחבר אותם, ונחשב מדדים: <strong>תוצר לנפש</strong> "
             "ו<strong>הוצאת מו\"פ כאחוז מהתוצר</strong> — לכל מדינה ולכל שנה.</p>"},

    {"type": "list", "h2": "מה נשלב מכל הפרקים", "items": [
        "פרק 01–02: קריאה, היכרות, ובחירת עמודות",
        "פרק 03: סינון לבדיקות איכות",
        "פרק 04: <code>rename</code>, המרת טיפוסים (<code>cast</code>), חישובים",
        "פרק 05: <code>group_by</code> ו-window functions (<code>over</code>, <code>arg_min</code>, <code>arg_max</code>)",
        "פרק 06: <code>join</code> על כמה מפתחות",
        "פרק 07: <code>pivot</code> ו-<code>max_horizontal</code>",
        "פרק 08: טיפול בבעיות זיהוי טיפוס וב-null",
        "ולבסוף — כתיבת התוצאות לקובץ עם <code>write_csv</code>",
    ]},

    {"type": "warn", "text": "שימו לב לבעיה אמיתית: ב-<code>population.csv</code> זיהוי "
                            "הטיפוס האוטומטי נכשל כי השורות הראשונות נראות כמו מספרים "
                            "שלמים אבל בהמשך יש עשרוניים. הפתרון: "
                            "<code>infer_schema_length=10000</code> או "
                            "<code>schema_overrides</code>."},

    {"type": "functable", "h2": "הפונקציות המרכזיות + תיעוד",
     "intro": "לחצו על כל קישור וקראו את התיעוד הרשמי.",
     "rows": [
         ("ערך לפי אינדקס בתוך קבוצה", "Expr.get()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.get.html"),
         ("אינדקס הערך המינימלי", "Expr.arg_min()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.arg_min.html"),
         ("חישוב בתוך קבוצה", "Expr.over()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.over.html"),
         ("long → wide", "DataFrame.pivot()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.pivot.html"),
         ("מקסימום אופקי בין עמודות", "polars.max_horizontal()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.max_horizontal.html"),
         ("המרת טיפוס", "Expr.cast()",
          "https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.cast.html"),
         ("חיבור טבלאות", "DataFrame.join()",
          "https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join.html"),
         ("כתיבה ל-CSV", "DataFrame.write_csv()",
          "https://docs.pola.rs/api/python/stable/reference/api/polars.DataFrame.write_csv.html"),
         ("הגדרות תצוגה לטבלאות גדולות", "polars.Config",
          "https://docs.pola.rs/api/python/stable/reference/config.html"),
     ]},

    {"type": "cta", "h2": "🎯 סיימתם את הקורס!",
     "body": "<p>אם הגעתם עד כאן — אתם יודעים את היסודות של Polars טוב, ויש לכם תמונה "
             "של כל משפחות הפונקציות. מכאן, ההמלצה: בכל פעם שאתם נתקעים, פתחו את "
             "התיעוד הרשמי — אתם כבר יודעים <em>איפה</em> לחפש.</p>",
     "pills": H.DOCS_PILLS},
]

EXERCISE_SLIDES = [
    {"type": "text", "h2": "על מה התרגיל?",
     "body": "<p>הפרויקט המסכם (22 שאלות, ארוך). זו משימה אחת רציפה: בונים דוח אנליטי "
             "שלם משלושה מקורות נתונים אמיתיים. כל שאלה ממשיכה את הקודמת — בדיוק כמו "
             "כתיבת טרנספורמציה אמיתית מתחילתה ועד סופה, כולל כתיבת התוצאות לקובץ.</p>"},
    {"type": "tip", "text": "זה תרגיל <strong>רציף</strong>: המשתנה <code>gdp</code> "
                            "גדל ומתעשר משאלה לשאלה. הריצו את התאים לפי הסדר."},
    {"type": "datatable", "h2": "המקור 1: <code>gdp.csv</code>",
     "intro": "תוצר מקומי גולמי (GDP) לפי מדינה ושנה, 1960–2023.", "rows": [
         ("Country Name", "str", "שם המדינה"),
         ("Country Code", "str", "קוד מדינה בן 3 אותיות (מפתח)"),
         ("Year", "i64", "שנה"),
         ("Value", "f64", "GDP בדולרים"),
     ]},
    {"type": "datatable", "h2": "המקור 2: <code>population.csv</code>",
     "intro": "אוכלוסייה לפי מדינה ושנה. ⚠️ זיהוי טיפוס בעייתי.", "rows": [
         ("Country Name", "str", "שם המדינה"),
         ("Country Code", "str", "קוד מדינה (מפתח)"),
         ("Year", "i64", "שנה"),
         ("Value", "?", "⚠️ אוכלוסייה — מתחיל כמספר שלם, בהמשך עשרוני"),
     ]},
    {"type": "datatable", "h2": "המקור 3: <code>expenditure.csv</code>",
     "intro": "הוצאות מו\"פ (R&D) לפי מקור מימון, 1996–2016. נשתמש בעמודת Government.",
     "rows": [
         ("LOCATION", "str", "קוד מדינה (מפתח, מתאים ל-code)"),
         ("Country", "str", "שם המדינה"),
         ("TIME", "i64", "שנה (מתאים ל-year)"),
         ("Government", "f64", "הוצאת מו\"פ ממשלתית (באלפים)"),
         ("(עוד עמודות)", "f64", "מקורות מימון ופעילויות נוספות — לא נשתמש בהן הפעם"),
     ]},
    {"type": "list", "h2": "מה תתרגלו (הכל ביחד!)", "items": [
        "קריאה, <code>rename</code>, <code>describe</code> וחקירה",
        "window functions: <code>over</code> + <code>arg_min</code>/<code>arg_max</code> + <code>get</code>",
        "<code>pivot</code> ו-<code>max_horizontal</code>",
        "טיפול בבעיית זיהוי טיפוס + <code>cast</code>",
        "<code>join</code> על שני וגם שלושה מפתחות",
        "חישוב מדדים: תוצר לנפש, מו\"פ כאחוז מהתוצר",
        "<code>write_csv</code> לשמירת התוצרים",
    ]},
    {"type": "steps", "h2": "איך מתחילים", "items": [
        'ודאו ש-Polars מותקן: <code>pip install polars</code> (גרסה 1.24.0).',
        'ודאו ששלושת קובצי ה-CSV נמצאים בתיקיית <code>data/</code>.',
        'פתחו את <code>Exercises.ipynb</code> והריצו את התאים <strong>לפי הסדר</strong>.',
        'בסוף ייווצר תיקיית <code>processed/</code> עם שלושה דוחות.',
        'סיימתם? השוו מול <code>Solutions.ipynb</code> — וסיימתם את הקורס! 🎉',
    ]},
]


def build_all():
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
    H.render(CHAPTER_DIR / "subject.html",
             lang_title="פרק 10 — פרויקט מסכם: GDP | Polars",
             kicker="Polars for Power Users · פרק 10", kicker_color=H.BRAND2,
             title="פרויקט מסכם: ניתוח GDP עולמי",
             subtitle="מחברים את כל הקורס לטרנספורמציה אחת שלמה — מנתונים גולמיים לדוח אנליטי.",
             hero_grad=H.SUBJECT_GRAD, slides=SUBJECT_SLIDES)
    H.render(CHAPTER_DIR / "exercise.html",
             lang_title="פרק 10 — התרגיל והמידע | Polars",
             kicker="פרק 10 · הפרויקט המסכם", kicker_color=H.GREEN,
             title="בניית דוח GDP מקצה לקצה",
             subtitle="משימה רציפה: ניקוי, חיבור, חישוב, וכתיבה — כמו pipeline אמיתי.",
             hero_grad=H.EXERCISE_GRAD, slides=EXERCISE_SLIDES)


if __name__ == "__main__":
    build_all()
