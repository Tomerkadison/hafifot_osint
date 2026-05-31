# Polars Exercises — תרגילים ב-Polars

תרגילים מעשיים ללימוד **Polars**, בפורמט שאתם כבר מכירים מקורס ה-pandas
([pandas_exercises](https://github.com/guipsamora/pandas_exercises)).
הדגש הוא על עבודה עם DataFrames, joins, וטרנספורמציות אמיתיות בסגנון
שאנחנו עושים ב-**Palantir Foundry**.

## איך זה בנוי / Structure

הקורס מחולק לפרקים ממוספרים. **בכל פרק** יש:

| קובץ | מה זה |
|------|-------|
| `data/` | קובצי המידע (CSV / Excel) שעליהם רצים התרגילים |
| `Exercises.ipynb` | התרגיל — שאלות עם תאי קוד ריקים שאתם ממלאים |
| `Solutions.ipynb` | אותן שאלות עם הפתרונות והפלט הצפוי |
| `subject.html` | מצגת בעברית על נושא הפרק + קישורים לתיעוד הרשמי של Polars |
| `exercise.html` | הסבר בעברית על התרגיל הספציפי ועל המידע |

> פתחו תחילה את `subject.html` ו-`exercise.html` בדפדפן, ואז עברו ל-`Exercises.ipynb`.

## הפרקים / Chapters

1. **Getting & Knowing Your Data** — היכרות עם המידע
2. **Selecting & Subsetting** — בחירת עמודות וביטויים
3. **Filtering & Sorting** — סינון ומיון
4. **Creating & Transforming Columns** — יצירת ועיבוד עמודות
5. **Grouping & Aggregation** — קיבוץ ואגרגציה
6. **Joins & Merging** — חיבור טבלאות 🎯
7. **Concat, Pivot & Unpivot** — שרשור ושינוי צורה
8. **Cleaning Data** — ניקוי מידע 🎯
9. **Lazy Evaluation & Performance** — חישוב עצל וביצועים
10. **Capstone Case Study (GDP)** — פרויקט מסכם 🎯

> 🎯 = פרק-משימה ארוך בסגנון "החיים האמיתיים". מורים — ראו `TEACHER_GUIDE.md`
> לתוכנית זמנים מלאה (4–5 ימים).

## התקנה / Setup

```bash
pip install "polars==1.24.0" "fastexcel==0.13.0" "XlsxWriter==3.2.2"
```

## למפתחי הקורס / Regenerating the data

קובצי המידע נוצרים באופן דטרמיניסטי (seed קבוע) כך שלכל הסטודנטים יוצא מידע זהה:

```bash
python _datagen/generate_data.py          # כל הפרקים
python _datagen/ch01_content.py            # בונה מחדש את ה-notebooks של פרק 01
```
