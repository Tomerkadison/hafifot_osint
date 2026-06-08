"""Chapter 01 - Getting & Knowing Your Data. Content + build entrypoint."""

from pathlib import Path

from nbbuild import build

CHAPTER_DIR = Path(__file__).resolve().parent.parent / "01_Getting_and_Knowing_Your_Data"

TITLE = "Polars Exercises 01 — Getting & Knowing Your Data"

INTRO_MD = (
    "A raw `orders` dataset just landed in our pipeline (think of a new dataset "
    "in Palantir Foundry). Before we build *any* transform on top of it, we have "
    "to **get to know the data**: its shape, its columns, its types, and where it "
    "is dirty.\n\n"
    "*הגיע אלינו dataset גולמי של הזמנות (כמו dataset חדש ב-Foundry). "
    "לפני שכותבים טרנספורמציה כלשהי — חייבים קודם להכיר את המידע: כמה שורות, "
    "אילו עמודות, אילו טיפוסים, ואיפה המידע “מלוכלך”.*\n\n"
    "**Data file:** `data/orders.csv`"
)

ITEMS = [
    {
        "md": "Import Polars under the alias `pl`.\n\n"
              "*ייבאו את Polars תחת השם `pl`.*",
        "sol": "import polars as pl",
    },
    {
        "md": "Read `data/orders.csv` into a DataFrame called `orders`.\n\n"
              "*קראו את הקובץ `data/orders.csv` ל-DataFrame בשם `orders`.*",
        "sol": 'orders = pl.read_csv("data/orders.csv")\norders',
    },
    {
        "md": "Show the **first 10 rows**.\n\n"
              "*הציגו את 10 השורות הראשונות.*",
        "sol": "orders.head(10)",
    },
    {
        "md": "Show the **last 5 rows**.\n\n"
              "*הציגו את 5 השורות האחרונות.*",
        "sol": "orders.tail(5)",
    },
    {
        "md": "How many **rows and columns** does the dataset have?\n\n"
              "*כמה שורות ועמודות יש ב-dataset?*",
        "sol": "orders.shape",
    },
    {
        "md": "What are the **column names**?\n\n"
              "*מהם שמות העמודות?*",
        "sol": "orders.columns",
    },
    {
        "md": "What is the **data type of every column**? "
              "Notice which type `order_date` got.\n\n"
              "*מהו הטיפוס של כל עמודה? שימו לב איזה טיפוס קיבלה `order_date`.*",
        "sol": "orders.schema",
    },
    {
        "md": "Get **summary statistics** for all columns in one call.\n\n"
              "*קבלו סטטיסטיקה מסכמת לכל העמודות בקריאה אחת.*",
        "sol": "orders.describe()",
    },
    {
        "md": "Use **`glimpse()`** for a transposed, one-line-per-column overview "
              "(great for wide datasets).\n\n"
              "*השתמשו ב-`glimpse()` לתצוגה הפוכה, שורה לכל עמודה.*",
        "sol": "orders.glimpse()",
    },
    {
        "md": "Select **only the `product_name` column**.\n\n"
              "*בחרו רק את העמודה `product_name`.*",
        "sol": 'orders.select("product_name")',
    },
    {
        "md": "Select the columns `order_id`, `product_name`, `quantity`, "
              "`unit_price`.\n\n"
              "*בחרו את העמודות `order_id`, `product_name`, `quantity`, `unit_price`.*",
        "sol": 'orders.select("order_id", "product_name", "quantity", "unit_price")',
    },
    {
        "md": "How many **distinct products** (`product_sku`) appear in the data?\n\n"
              "*כמה מוצרים שונים (`product_sku`) מופיעים במידע?*",
        "sol": 'orders["product_sku"].n_unique()',
    },
    {
        "md": "List the **distinct categories**.\n\n"
              "*הציגו את הקטגוריות השונות.*",
        "sol": 'orders["category"].unique().sort()',
    },
    {
        "md": "How many orders are there **per `status`**? "
              "(use `value_counts`)\n\n"
              "*כמה הזמנות יש לכל `status`? (השתמשו ב-`value_counts`)*",
        "sol": 'orders["status"].value_counts(sort=True)',
    },
    {
        "md": "Which **category** has the most orders?\n\n"
              "*לאיזו קטגוריה יש הכי הרבה הזמנות?*",
        "sol": 'orders["category"].value_counts(sort=True).head(1)',
    },
    {
        "md": "What are the **minimum and maximum `quantity`**? "
              "(remember: returns are negative)\n\n"
              "*מהם הערך המינימלי והמקסימלי של `quantity`? (זכרו: החזרות הן שליליות)*",
        "sol": 'orders["quantity"].min(), orders["quantity"].max()',
    },
    {
        "md": "What is the **average `unit_price`**, rounded to 2 decimals?\n\n"
              "*מהו המחיר הממוצע ליחידה, מעוגל ל-2 ספרות?*",
        "sol": 'orders.select(pl.col("unit_price").mean().round(2))',
    },
    {
        "md": "How many **null (missing) values** does each column have? "
              "Which column is dirty?\n\n"
              "*כמה ערכים חסרים (null) יש בכל עמודה? איזו עמודה “מלוכלכת”?*",
        "sol": "orders.null_count()",
    },
    {
        "md": "Take a **random sample of 5 rows** (use `seed=0` so it is "
              "reproducible).\n\n"
              "*קחו מדגם אקראי של 5 שורות (השתמשו ב-`seed=0` כדי שיהיה ניתן לשחזור).*",
        "sol": "orders.sample(5, seed=0)",
    },
    {
        "md": "What is the **estimated in-memory size** of the DataFrame, in MB?\n\n"
              "*מהו הגודל המשוער בזיכרון של ה-DataFrame, ב-MB?*",
        "sol": 'orders.estimated_size("mb")',
    },
    {
        "md": "Show the **5 largest orders by `quantity`** "
              "(highest quantity first).\n\n"
              "*הציגו את 5 ההזמנות הגדולות ביותר לפי `quantity`.*",
        "sol": 'orders.sort("quantity", descending=True).head(5)',
    },
    {
        "md": "Select rows **10 through 14** (a 5-row slice) using `slice`. "
              "Add a row index first with `with_row_index()` so you can see the "
              "0-based positions in the output.\n\n"
              "*בחרו את השורות 10 עד 14 (חיתוך של 5 שורות) באמצעות `slice`. "
              "הוסיפו קודם אינדקס שורה עם `with_row_index()` כדי לראות את המיקומים "
              "(0-based) בפלט.*",
        "sol": "orders.with_row_index().slice(10, 5)",
    },
]


if __name__ == "__main__":
    build(CHAPTER_DIR, TITLE, INTRO_MD, ITEMS)
