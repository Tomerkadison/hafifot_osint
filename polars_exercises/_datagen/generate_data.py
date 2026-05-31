"""
Reproducible data generator for the Polars-for-Power-Users exercise course.

We model a small, Palantir-Foundry-style "world" of related tables:

    regions    -> customers -> orders
    products  -----------------^

Every table is generated from a single fixed random seed, so every student
gets byte-for-byte identical files and therefore identical solution outputs.

The data is intentionally a little "dirty" (string dates, nulls, negative
quantities for returns, inconsistent casing, duplicate rows) so that the
cleaning / casting / joining exercises in later chapters have something real
to fix -- exactly like a raw dataset landing in a Foundry pipeline.

Usage:
    python generate_data.py            # writes all chapter data folders
    python generate_data.py --chapter 01
"""

from __future__ import annotations

import argparse
import shutil
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl

SEED = 42
COURSE_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# Reference / dimension tables                                                #
# --------------------------------------------------------------------------- #
def make_regions() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "region_id": ["NA", "EU", "APAC", "LATAM", "MEA"],
            "region_name": [
                "North America",
                "Europe",
                "Asia Pacific",
                "Latin America",
                "Middle East & Africa",
            ],
            "currency": ["USD", "EUR", "USD", "USD", "USD"],
            "tax_rate": [0.0, 0.20, 0.10, 0.15, 0.05],
        }
    )


def make_products() -> pl.DataFrame:
    # SKU -> (name, category, unit_cost, list_price)
    rows = [
        ("PB200", "Gel Pen 12-pack", "pens", 1.10, 3.00),
        ("PB24", "Ballpoint Pen", "pens", 0.40, 1.20),
        ("NB050", "Spiral Notebook", "notebooks", 1.80, 4.50),
        ("NB120", "Hardcover Journal", "notebooks", 4.20, 11.00),
        ("PT010", "Motivational Poster", "posters", 2.30, 7.00),
        ("PT044", "World Map Poster", "posters", 3.10, 9.50),
        ("SH900", "Cotton T-Shirt", "shirts", 5.50, 17.00),
        ("SH901", "Polo Shirt", "shirts", 8.00, 24.00),
        ("BK300", "Paperback Book", "books", 3.00, 9.00),
        ("BK301", "Cookbook", "books", 6.50, 19.00),
        ("MG010", "Ceramic Mug", "mugs", 2.20, 6.50),
        ("ST500", "Sticker Sheet", "stickers", 0.30, 1.50),
    ]
    return pl.DataFrame(
        {
            "product_sku": [r[0] for r in rows],
            "product_name": [r[1] for r in rows],
            "category": [r[2] for r in rows],
            "unit_cost": [r[3] for r in rows],
            "list_price": [r[4] for r in rows],
        }
    )


def make_customers(rng: np.random.Generator, regions: pl.DataFrame) -> pl.DataFrame:
    n = 200
    first = [
        "Realcube", "Zooxo", "Dabtype", "Skipfire", "Bluezoom", "Viva",
        "Photobean", "Mybuzz", "Dabfeed", "Quaxo", "Jaxbean", "Yodel",
        "Kanoodle", "Twinte", "Rhybox", "Skiba", "Vinte", "Voonix",
    ]
    suffix = ["Inc", "LLC", "Group", "Co", "Holdings", "Partners", "Systems"]

    names = [
        f"{rng.choice(first)} {rng.choice(suffix)}" for _ in range(n)
    ]
    region_ids = rng.choice(regions["region_id"].to_list(), size=n,
                            p=[0.40, 0.25, 0.20, 0.10, 0.05])
    segments = rng.choice(["SMB", "Mid-Market", "Enterprise"], size=n,
                          p=[0.55, 0.30, 0.15])

    start = date(2018, 1, 1)
    signup = [start + timedelta(days=int(d))
              for d in rng.integers(0, 365 * 4, size=n)]

    df = pl.DataFrame(
        {
            "customer_id": [f"CUST-{i:04d}" for i in range(1, n + 1)],
            "customer_name": names,
            "region_id": region_ids,
            "segment": segments,
            "signup_date": signup,
        }
    )
    return df


# --------------------------------------------------------------------------- #
# Fact table: orders                                                          #
# --------------------------------------------------------------------------- #
def make_orders(
    rng: np.random.Generator,
    customers: pl.DataFrame,
    products: pl.DataFrame,
    regions: pl.DataFrame,
) -> pl.DataFrame:
    n = 1000

    cust_ids = customers["customer_id"].to_list()
    cust_to_region = dict(zip(customers["customer_id"], customers["region_id"]))
    region_name = dict(zip(regions["region_id"], regions["region_name"]))

    sku_list = products["product_sku"].to_list()
    sku_to_cat = dict(zip(products["product_sku"], products["category"]))
    sku_to_name = dict(zip(products["product_sku"], products["product_name"]))
    sku_to_price = dict(zip(products["product_sku"], products["list_price"]))

    chosen_cust = rng.choice(cust_ids, size=n)
    chosen_sku = rng.choice(sku_list, size=n)

    start = date(2023, 1, 1)
    order_dates = [start + timedelta(days=int(d))
                   for d in rng.integers(0, 365, size=n)]

    quantity = rng.integers(1, 40, size=n)
    # ~4% of rows are returns -> negative quantity
    is_return = rng.random(n) < 0.04
    quantity = np.where(is_return, -rng.integers(1, 6, size=n), quantity)

    # unit price wobbles a little around list price (promotions etc.)
    unit_price = np.array([sku_to_price[s] for s in chosen_sku])
    unit_price = np.round(unit_price * rng.uniform(0.85, 1.10, size=n), 2)

    channel = rng.choice(["online", "store", "partner"], size=n,
                         p=[0.6, 0.3, 0.1])
    status = np.where(
        is_return, "returned",
        rng.choice(["completed", "pending", "cancelled"], size=n,
                   p=[0.85, 0.10, 0.05]),
    )

    df = pl.DataFrame(
        {
            "order_id": [f"ORD-{i:06d}" for i in range(1, n + 1)],
            "customer_id": chosen_cust,
            # order_date stored as STRING on purpose (raw export flavour)
            "order_date": [d.isoformat() for d in order_dates],
            "region": [region_name[cust_to_region[c]] for c in chosen_cust],
            "product_sku": chosen_sku,
            "category": [sku_to_cat[s] for s in chosen_sku],
            "product_name": [sku_to_name[s] for s in chosen_sku],
            "quantity": quantity,
            "unit_price": unit_price,
            "channel": channel,
            "status": status,
        }
    )

    # Add a partly-null business column: a free-text discount code
    codes = rng.choice(["SPRING10", "VIP", "BULK", None, None, None, None],
                       size=n)
    df = df.with_columns(pl.Series("discount_code", codes))

    return df


# --------------------------------------------------------------------------- #
# Deliberately messy orders for the cleaning chapter (08)                     #
# --------------------------------------------------------------------------- #
def make_messy_orders(rng: np.random.Generator, orders: pl.DataFrame) -> pl.DataFrame:
    """Take a clean slice of orders and corrupt it the way real exports arrive."""
    df = orders.head(300).to_dict(as_series=False)
    n = 300

    # region: inconsistent casing + stray whitespace
    region = []
    for r in df["region"]:
        choice = rng.integers(0, 4)
        if choice == 0:
            region.append(r.upper())
        elif choice == 1:
            region.append(f"  {r} ")
        elif choice == 2:
            region.append(r.lower())
        else:
            region.append(r)

    # category: mixed casing + whitespace
    category = [c.upper() if rng.random() < 0.5 else f" {c}" for c in df["category"]]

    # order_date: three different string formats
    dates = []
    for d in df["order_date"]:
        y, m, day = d.split("-")
        fmt = rng.integers(0, 3)
        if fmt == 0:
            dates.append(d)                       # 2023-01-05
        elif fmt == 1:
            dates.append(f"{day}/{m}/{y}")        # 05/01/2023
        else:
            dates.append(f"{y}.{m}.{day}")        # 2023.01.05

    # quantity: stored as strings, some "N/A"
    quantity = [str(q) if rng.random() > 0.05 else "N/A" for q in df["quantity"]]

    # unit_price: stored as money strings ("$3.50")
    unit_price = [f"${p:.2f}" for p in df["unit_price"]]

    # discount: percent strings, mostly missing
    discount = []
    for _ in range(n):
        r = rng.random()
        if r < 0.7:
            discount.append("")
        else:
            discount.append(f"{int(rng.integers(5, 30))}%")

    # status: random casing
    status = [s.upper() if rng.random() < 0.5 else s.title() for s in df["status"]]

    messy = pl.DataFrame(
        {
            "order_id": df["order_id"],
            "customer_id": df["customer_id"],
            "order_date": dates,
            "region": region,
            "category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "status": status,
        }
    )

    # inject ~25 exact duplicate rows
    dupe_idx = rng.integers(0, n, size=25)
    messy = pl.concat([messy, messy[dupe_idx.tolist()]])
    # shuffle so duplicates are scattered
    perm = rng.permutation(messy.height)
    messy = messy[perm.tolist()]
    return messy


# --------------------------------------------------------------------------- #
# Per-chapter writers                                                         #
# --------------------------------------------------------------------------- #
CHAPTER_DIRS = {
    "01": "01_Getting_and_Knowing_Your_Data",
    "02": "02_Selecting_and_Subsetting",
    "03": "03_Filtering_and_Sorting",
    "04": "04_Creating_and_Transforming_Columns",
    "05": "05_Grouping_and_Aggregation",
    "06": "06_Joins_and_Merging",
    "07": "07_Concat_Pivot_and_Unpivot",
    "08": "08_Cleaning_Data",
    "09": "09_Lazy_Evaluation_and_Performance",
    "10": "10_Capstone_GDP_Case_Study",
}


def _data_dir(ch: str) -> Path:
    d = COURSE_ROOT / CHAPTER_DIRS[ch] / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", default="all",
                        help="chapter number (e.g. 01) or 'all'")
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    repo_root = COURSE_ROOT.parent

    regions = make_regions()
    products = make_products()
    customers = make_customers(rng, regions)
    orders = make_orders(rng, customers, products, regions)
    messy = make_messy_orders(rng, orders)

    want = set(CHAPTER_DIRS) if args.chapter == "all" else {args.chapter}

    def put(ch, name, df):
        p = _data_dir(ch) / name
        df.write_csv(p)
        print(f"  [{ch}] {name}  ({df.height} rows)")

    # 01-05 all work on the single orders fact table
    for ch in ["01", "02", "03", "04", "05"]:
        if ch in want:
            put(ch, "orders.csv", orders)

    # 06 joins: the full relational set
    if "06" in want:
        put("06", "orders.csv", orders)
        put("06", "customers.csv", customers)
        put("06", "products.csv", products)
        put("06", "regions.csv", regions)

    # 07 concat/pivot: split orders by half-year + the full table for pivoting
    if "07" in want:
        h1 = orders.filter(pl.col("order_date") < "2023-07-01")
        h2 = orders.filter(pl.col("order_date") >= "2023-07-01")
        put("07", "orders_h1.csv", h1)
        put("07", "orders_h2.csv", h2)
        put("07", "orders.csv", orders)

    # 08 cleaning: the messy export
    if "08" in want:
        put("08", "orders_messy.csv", messy)

    # 09 performance: reuse the existing 1.1M-row CSV from the original repo
    if "09" in want:
        src = repo_root / "code" / "data" / "larger.csv"
        dst = _data_dir("09") / "larger.csv"
        shutil.copyfile(src, dst)
        print(f"  [09] larger.csv  (copied from {src.relative_to(repo_root)})")

    # 10 capstone: reuse the GDP / population / expenditure case-study data
    if "10" in want:
        cs = repo_root / "code" / "casestudy" / "raw"
        for name in ["gdp.csv", "population.csv", "expenditure.csv"]:
            shutil.copyfile(cs / name, _data_dir("10") / name)
            print(f"  [10] {name}  (copied from case study)")

    print("done.")


if __name__ == "__main__":
    main()
