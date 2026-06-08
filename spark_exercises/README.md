# Spark Exercises — תרגילים ב-Apache Spark

תרגילים מעשיים ללימוד **Apache Spark (PySpark)**, בהמשך ישיר לקורסי ה-pandas
וה-Polars. הקורס הזה **לא** חוזר על אותם תרגילים — אתם כבר יודעים לסנן, לקבץ
ולחבר טבלאות. כאן מתמקדים ב**מה שמייחד את Spark**: חישוב מבוזר ועצל, פונקציות
חלון, SQL, מידע מקונן (JSON), ביצועים, ו-IO בסגנון **Palantir Foundry**.

## הפילוסופיה של הקורס

> הבסיס — בקצרה. הייחוד של Spark — לעומק.

הסטודנטים סיפרו שחלק מקורס ה-Polars היה חזרתי מול pandas. לכן כאן:

- **פרק 01 לבד** מכסה את כל הבסיס (read / select / filter / groupBy) במהירות,
  עם דגש על הרעיון הגדול: **transformation עצל מול action**.
- כל שאר הפרקים עוסקים בדברים ש-pandas/Polars **לא** עושים טוב (או בכלל):
  פונקציות חלון, shuffles, מידע מקונן, UDFs מול מובנות, ו-Parquet מחולק.

## איך זה בנוי / Structure

הקורס מחולק לפרקים ממוספרים. **בכל פרק** יש:

| קובץ | מה זה |
|------|-------|
| `data/` | קובצי המידע (CSV / JSON) שעליהם רצים התרגילים |
| `Exercises.ipynb` | התרגיל — שאלות עם תאי קוד ריקים שאתם ממלאים |
| `Solutions.ipynb` | אותן שאלות עם הפתרונות ו**הפלט האמיתי** של Spark |
| `subject.html` | מצגת בעברית על נושא הפרק + קישורים לתיעוד הרשמי של Spark |
| `exercise.html` | הסבר בעברית על התרגיל ועל המידע |
| `download.zip` | חבילה להורדה: Exercises + Solutions + `data/` |

> התא הראשון בכל `Exercises.ipynb` כבר פותח עבורכם `SparkSession` — רק הריצו אותו.

## הפרקים / Chapters

| # | פרק | מה מיוחד בו |
|---|-----|-------------|
| 01 | **Spark Mindset & Basics** | כל הבסיס במהירות + ההבדל transformation/action |
| 02 | **Lazy Execution & the Plan** | `explain()`, Catalyst optimizer, `cache` |
| 03 | **Spark SQL** | temp views, `spark.sql`, ערבוב SQL ו-API |
| 04 | **Window Functions** 🎯 | דירוג, running totals, `lag`/`lead` — הכלי המרכזי ב-Foundry |
| 05 | **Joins & Shuffles** 🎯 | כל סוגי ה-join, broadcast, ו-shuffle ב-`explain` |
| 06 | **Nested & Semi-structured Data** 🎯 | structs, arrays, `explode`, `from_json` |
| 07 | **UDFs, Built-ins & Performance** | UDF מול מובנה, `pandas_udf`, partitions, `cache` |
| 08 | **Schemas, Reading & Writing** | `StructType`, casting, Parquet, `partitionBy` |
| 09 | **Capstone: Streamline Analytics** 🎯 | pipeline מקצה-לקצה שמרכיב את הכול |

> 🎯 = פרק עתיר תוכן בסגנון "החיים האמיתיים". מורים — ראו `TEACHER_GUIDE.md`.

## התקנה / Setup

ל-Spark צריך **Java** (פעם אחת) ואז `pip install pyspark`. המדריך המלא — עם
אופציות של Colab ו-Docker למי שלא רוצה להתקין — נמצא ב-**`SETUP.md`**.

בקצרה (macOS):

```bash
brew install openjdk@17
python -m venv .venv && source .venv/bin/activate
pip install "pyspark==3.5.1" jupyter pandas pyarrow
```

## למפתחי הקורס / Regenerating

הכול נבנה דטרמיניסטית (seed קבוע) כך שלכל הסטודנטים יוצא פלט זהה:

```bash
# צריך JAVA_HOME מוגדר ו-venv עם pyspark + jupyter + pandas + pyarrow + setuptools
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
python _datagen/build_all.py     # מייצר data, בונה ומריץ את כל ה-notebooks, ויוצר zips
```

> ה-Solutions notebooks **מורצים באמת** מול Spark מקומי, כך שהפלט שמוטמע בהם הוא
> הפלט האמיתי — לא הומצא ידנית.
