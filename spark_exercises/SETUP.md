# התקנה והרצה של Spark — מדריך מהיר

בניגוד ל-pandas ול-Polars, ש"סתם עובדים" אחרי `pip install`, ל-Spark יש דרישה אחת
נוספת: הוא רץ על **JVM**, אז צריך **Java** מותקן. זה כל הסיפור. אחרי שיש Java,
`pip install pyspark` וזהו.

בחרו את הדרך שהכי נוחה לכם — שלושתן נותנות בדיוק את אותה סביבה לתרגילים.

---

## ⭐ הדרך הכי קלה: Google Colab (בלי להתקין כלום)

אם אתם רוצים פשוט להתחיל לתרגל בלי כאב ראש של התקנות:

1. היכנסו ל-[colab.research.google.com](https://colab.research.google.com) ופתחו notebook חדש.
2. בתא הראשון הריצו:

   ```python
   !pip install pyspark==3.5.1 -q
   ```

   ב-Colab כבר יש Java מותקן, אז זה כל מה שצריך.
3. העלו את קובצי ה-`data/` של הפרק (כפתור התיקייה בצד שמאל → Upload), או חברו את
   Google Drive.
4. התחילו לעבוד — כל קוד ה-Spark בתרגילים ירוץ כמו שהוא.

> 💡 מתאים מצוין ללמידה. החיסרון: צריך להעלות את ה-data לכל session.

---

## 💻 הדרך המקומית (מומלצת לעבודה רצינית)

### שלב 1 — התקינו Java (פעם אחת)

Spark 3.5 עובד עם **Java 8 / 11 / 17**. נמליץ על 17.

**macOS** (עם [Homebrew](https://brew.sh)):

```bash
brew install openjdk@17
```

ואז הוסיפו ל-`~/.zshrc` (או `~/.bash_profile`):

```bash
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
export PATH="$JAVA_HOME/bin:$PATH"
```

**Windows**: הורידו את [Temurin 17](https://adoptium.net/temurin/releases/?version=17)
(installer `.msi`), והתקינו. ה-installer מגדיר `JAVA_HOME` אוטומטית. אתחלו את
ה-terminal.

**Linux (Debian/Ubuntu)**:

```bash
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk
```

בדקו שעובד:

```bash
java -version
```

### שלב 2 — התקינו PySpark

מומלץ בתוך סביבה וירטואלית:

```bash
python -m venv .venv
source .venv/bin/activate          # ב-Windows: .venv\Scripts\activate
pip install "pyspark==3.5.1" jupyter pandas pyarrow
```

> `pandas` ו-`pyarrow` נדרשים רק לפרק 07 (ל-`pandas_udf`). שאר הפרקים עובדים בלי.

### שלב 3 — בדקו שהכול עובד

צרו קובץ `check.py` והריצו `python check.py`:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.createDataFrame([(1, "hello"), (2, "spark")], ["id", "word"])
df.show()
print("Spark", spark.version, "— הכול עובד! 🎉")
spark.stop()
```

אם ראיתם טבלה מודפסת — אתם מוכנים.

### שלב 4 — פתחו את התרגילים

```bash
jupyter notebook
```

נווטו לתיקיית הפרק (למשל `01_Spark_Mindset_and_Basics/`), פתחו את
`Exercises.ipynb`, והריצו את התא הראשון — הוא פותח עבורכם `SparkSession`.

---

## 🐳 הדרך עם Docker (סביבה מוכנה לגמרי)

אם יש לכם Docker ואתם לא רוצים להתקין Java/Python בכלל:

```bash
docker run -it --rm -p 8888:8888 \
  -v "$PWD":/home/jovyan/work \
  quay.io/jupyter/pyspark-notebook:spark-3.5.0
```

זה מריץ Jupyter עם Spark ו-Java כבר בפנים. פתחו את הקישור עם ה-token שמודפס
ב-terminal, ותמצאו את הקבצים תחת `work/`.

---

## כמה דברים שכדאי לדעת

- **הרצה ראשונה איטית.** פתיחת `SparkSession` לוקחת 10–20 שניות (ה-JVM עולה). זה
  חד-פעמי לכל notebook — אחרי זה הכול מהיר.
- **רעש בלוג.** Spark מדפיס הרבה הודעות `WARN` באדום. זה תקין. אפשר להשתיק עם
  `spark.sparkContext.setLogLevel("ERROR")` (כבר נמצא בתא הראשון של כל תרגיל).
- **ה-Spark UI.** בזמן ש-session פתוח, גשו ל-[localhost:4040](http://localhost:4040)
  כדי לראות jobs, stages, ו-DAGs בזמן אמת — כלי מעולה להבנת מה שלמדתם בפרק 02.
- **`local[*]`.** אנחנו מריצים Spark על מצב "מקומי" שמשתמש בכל הליבות של המחשב.
  אותו קוד בדיוק ירוץ על cluster אמיתי ב-Foundry — רק בלי לשנות שורה.

---

## איך זה קשור ל-Foundry?

ב-Palantir Foundry לא פותחים `SparkSession` ולא קוראים קבצים ידנית — ה-platform
עושה את זה עבורכם, ומזריק את ה-DataFrames לתוך הטרנספורמציה. **כל השאר זהה**:
אותו `select`, `join`, `groupBy`, `Window`, `explode`. מה שתלמדו כאן מקומית עובר
1:1 ל-Foundry.
