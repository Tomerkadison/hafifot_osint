"""
Reproducible data generator for the **Spark for Power-Users** exercise course.

The students already finished the pandas and Polars courses, so the data here is
deliberately richer and more "Spark-shaped" than a single flat CSV:

    regions   -> customers -> orders          (the classic relational star)
    products  -----------------^

    events.jsonl                              (nested clickstream: structs + arrays)
    web_events.csv                            (a big-ish table for performance work)

Everything is generated from one fixed seed, so every student gets byte-for-byte
identical files and therefore identical Spark output in the Solutions notebooks.

The data is intentionally a little dirty (string timestamps, nulls, negative
quantities for returns, inconsistent casing) so the cleaning / casting / schema
exercises have something real to fix — exactly like a raw dataset landing in a
Palantir Foundry pipeline.

Usage:
    python generate_data.py            # writes all chapter data folders
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

SEED = 42
COURSE_ROOT = Path(__file__).resolve().parent.parent

CHAPTER_DIRS = {
    "01": "01_Spark_Mindset_and_Basics",
    "02": "02_Lazy_Execution_and_the_Plan",
    "03": "03_Spark_SQL",
    "04": "04_Window_Functions",
    "05": "05_Joins_and_Shuffles",
    "06": "06_Nested_and_Semi_Structured_Data",
    "07": "07_UDFs_Builtins_and_Performance",
    "08": "08_Schemas_Reading_and_Writing",
    "09": "09_Capstone_Streamline_Analytics",
}


# --------------------------------------------------------------------------- #
# Reference / dimension tables                                                 #
# --------------------------------------------------------------------------- #
def make_regions() -> list[dict]:
    rows = [
        ("NA", "North America", "USD", 0.00),
        ("EU", "Europe", "EUR", 0.20),
        ("APAC", "Asia Pacific", "USD", 0.10),
        ("LATAM", "Latin America", "USD", 0.15),
        ("MEA", "Middle East & Africa", "USD", 0.05),
    ]
    return [dict(region_id=r[0], region_name=r[1], currency=r[2], tax_rate=r[3])
            for r in rows]


def make_products() -> list[dict]:
    # sku, name, category, brand, unit_cost, list_price
    rows = [
        ("PB200", "Gel Pen 12-pack", "stationery", "Inkwell", 1.10, 3.00),
        ("PB024", "Ballpoint Pen", "stationery", "Inkwell", 0.40, 1.20),
        ("NB050", "Spiral Notebook", "stationery", "PaperCo", 1.80, 4.50),
        ("NB120", "Hardcover Journal", "stationery", "PaperCo", 4.20, 11.00),
        ("PT010", "Motivational Poster", "home", "WallArt", 2.30, 7.00),
        ("PT044", "World Map Poster", "home", "WallArt", 3.10, 9.50),
        ("MG010", "Ceramic Mug", "home", "Kettle", 2.20, 6.50),
        ("MG044", "Travel Tumbler", "home", "Kettle", 4.90, 14.00),
        ("SH900", "Cotton T-Shirt", "apparel", "ThreadWorks", 5.50, 17.00),
        ("SH901", "Polo Shirt", "apparel", "ThreadWorks", 8.00, 24.00),
        ("SH902", "Hoodie", "apparel", "ThreadWorks", 12.00, 39.00),
        ("BK300", "Paperback Novel", "books", "OpenPage", 3.00, 9.00),
        ("BK301", "Cookbook", "books", "OpenPage", 6.50, 19.00),
        ("BK302", "Data Engineering 101", "books", "OpenPage", 11.00, 34.00),
        ("EL500", "USB-C Cable", "electronics", "Voltix", 1.50, 8.00),
        ("EL501", "Wireless Mouse", "electronics", "Voltix", 6.00, 19.00),
        ("EL502", "Bluetooth Speaker", "electronics", "Voltix", 14.00, 45.00),
        ("EL503", "Noise-Cancel Headphones", "electronics", "Voltix", 38.00, 120.00),
        ("ST500", "Sticker Sheet", "stationery", "Inkwell", 0.30, 1.50),
        ("MG777", "Insulated Bottle", "home", "Kettle", 6.20, 18.00),
    ]
    return [dict(product_sku=r[0], product_name=r[1], category=r[2], brand=r[3],
                 unit_cost=r[4], list_price=r[5]) for r in rows]


COUNTRIES = {
    "NA": [("US", "Austin"), ("US", "Seattle"), ("US", "Chicago"), ("CA", "Toronto")],
    "EU": [("DE", "Berlin"), ("FR", "Paris"), ("UK", "London"), ("ES", "Madrid")],
    "APAC": [("JP", "Tokyo"), ("AU", "Sydney"), ("IN", "Bengaluru"), ("SG", "Singapore")],
    "LATAM": [("BR", "Sao Paulo"), ("MX", "Mexico City"), ("AR", "Buenos Aires")],
    "MEA": [("AE", "Dubai"), ("ZA", "Cape Town"), ("IL", "Tel Aviv")],
}


def make_customers(rng) -> list[dict]:
    n = 500
    first = ["Realcube", "Zooxo", "Dabtype", "Skipfire", "Bluezoom", "Viva",
             "Photobean", "Mybuzz", "Dabfeed", "Quaxo", "Jaxbean", "Yodel",
             "Kanoodle", "Twinte", "Rhybox", "Skiba", "Vinte", "Voonix",
             "Brightlane", "Nexora", "Cloudkit", "Pixelplay", "Gigabyte"]
    suffix = ["Inc", "LLC", "Group", "Co", "Holdings", "Partners", "Systems"]
    region_ids = rng.choice(["NA", "EU", "APAC", "LATAM", "MEA"], size=n,
                            p=[0.40, 0.25, 0.20, 0.10, 0.05])
    segments = rng.choice(["Consumer", "SMB", "Enterprise"], size=n,
                          p=[0.55, 0.30, 0.15])
    tiers = rng.choice(["Bronze", "Silver", "Gold", "Platinum"], size=n,
                       p=[0.45, 0.30, 0.18, 0.07])
    start = date(2019, 1, 1)
    rows = []
    for i in range(1, n + 1):
        rid = region_ids[i - 1]
        country, city = COUNTRIES[rid][rng.integers(0, len(COUNTRIES[rid]))]
        name = f"{rng.choice(first)} {rng.choice(suffix)}"
        signup = start + timedelta(days=int(rng.integers(0, 365 * 5)))
        rows.append(dict(
            customer_id=f"CUST-{i:04d}",
            customer_name=name,
            email=f"contact{i}@{name.split()[0].lower()}.example",
            country=country,
            city=city,
            region_id=rid,
            segment=segments[i - 1],
            loyalty_tier=tiers[i - 1],
            signup_date=signup.isoformat(),
        ))
    return rows


# --------------------------------------------------------------------------- #
# Fact table: orders                                                          #
# --------------------------------------------------------------------------- #
def make_orders(rng, customers, products) -> list[dict]:
    n = 8000
    # Only ~92% of customers ever place an order, so that left_anti / left_semi
    # joins (ch05) and the customer-360 fillna step (ch09) are actually meaningful.
    buyers = customers[: int(len(customers) * 0.92)]
    cust_ids = [c["customer_id"] for c in buyers]
    skus = [p["product_sku"] for p in products]
    sku_price = {p["product_sku"]: p["list_price"] for p in products}

    chosen_cust = rng.choice(cust_ids, size=n)
    chosen_sku = rng.choice(skus, size=n)

    base = datetime(2024, 1, 1, 0, 0, 0)
    rows = []
    codes = ["SPRING10", "VIP", "BULK15", "WELCOME", None, None, None, None, None]
    channels = rng.choice(["web", "app", "store", "partner"], size=n,
                          p=[0.45, 0.30, 0.18, 0.07])
    pay = rng.choice(["card", "paypal", "applepay", "giftcard"], size=n,
                     p=[0.55, 0.22, 0.15, 0.08])
    for i in range(1, n + 1):
        sku = chosen_sku[i - 1]
        is_return = rng.random() < 0.04
        qty = -int(rng.integers(1, 6)) if is_return else int(rng.integers(1, 25))
        price = round(sku_price[sku] * rng.uniform(0.85, 1.10), 2)
        ts = base + timedelta(
            days=int(rng.integers(0, 365)),
            hours=int(rng.integers(0, 24)),
            minutes=int(rng.integers(0, 60)),
        )
        if is_return:
            status = "returned"
        else:
            status = rng.choice(["completed", "pending", "cancelled"],
                                p=[0.85, 0.10, 0.05])
        rows.append(dict(
            order_id=f"ORD-{i:06d}",
            customer_id=chosen_cust[i - 1],
            # timestamp stored as a STRING on purpose (raw export flavour)
            order_ts=ts.strftime("%Y-%m-%d %H:%M:%S"),
            product_sku=sku,
            quantity=qty,
            unit_price=price,
            channel=str(channels[i - 1]),
            payment_method=str(pay[i - 1]),
            status=str(status),
            discount_code=rng.choice(codes),
        ))
    return rows


# --------------------------------------------------------------------------- #
# Nested clickstream events (structs + arrays) -> JSON Lines                  #
# --------------------------------------------------------------------------- #
def make_events(rng, customers, products) -> list[dict]:
    n = 2500
    cust_ids = [c["customer_id"] for c in customers]
    cust_geo = {c["customer_id"]: (c["country"], c["city"]) for c in customers}
    skus = [p["product_sku"] for p in products]

    oses = ["iOS", "Android", "Windows", "macOS", "Linux"]
    browsers = ["Safari", "Chrome", "Firefox", "Edge"]
    search_terms = ["headphones", "mug", "notebook", "t-shirt", "poster",
                    "cable", "speaker", "cookbook", "pen", "bottle"]
    types = ["page_view", "search", "add_to_cart", "purchase"]

    base = datetime(2024, 6, 1, 0, 0, 0)
    rows = []
    for i in range(1, n + 1):
        uid = str(rng.choice(cust_ids))
        etype = str(rng.choice(types, p=[0.5, 0.2, 0.2, 0.1]))
        country, city = cust_geo[uid]
        ts = base + timedelta(
            days=int(rng.integers(0, 30)),
            hours=int(rng.integers(0, 24)),
            minutes=int(rng.integers(0, 60)),
            seconds=int(rng.integers(0, 60)),
        )
        ev = {
            "event_id": f"EV-{i:07d}",
            "user_id": uid,
            "event_ts": ts.strftime("%Y-%m-%dT%H:%M:%S"),
            "event_type": etype,
            "session_id": f"S-{int(rng.integers(1, 900)):04d}",
            # nested struct: device
            "device": {
                "os": str(rng.choice(oses)),
                "browser": str(rng.choice(browsers)),
                "is_mobile": bool(rng.random() < 0.6),
            },
            # nested struct: geo
            "geo": {"country": country, "city": city},
        }
        if etype == "search":
            ev["search_term"] = str(rng.choice(search_terms))
        if etype in ("add_to_cart", "purchase"):
            k = int(rng.integers(1, 4))
            ev["items"] = [
                {
                    "sku": str(rng.choice(skus)),
                    "qty": int(rng.integers(1, 5)),
                    "price": round(float(rng.uniform(1.5, 120.0)), 2),
                }
                for _ in range(k)
            ]
        rows.append(ev)
    return rows


# --------------------------------------------------------------------------- #
# Big-ish flat table for the performance chapter                             #
# --------------------------------------------------------------------------- #
def make_web_events(rng, customers) -> dict:
    """Return columns as numpy arrays, written as a wide CSV (~250k rows)."""
    n = 250_000
    cust_ids = np.array([c["customer_id"] for c in customers])
    pages = np.array(["/home", "/search", "/product", "/cart", "/checkout",
                      "/account", "/help", "/blog"])
    etypes = np.array(["view", "click", "scroll", "submit"])
    countries = np.array(["US", "DE", "JP", "UK", "BR", "IN", "FR", "AU",
                          "CA", "MX", "SG", "AE"])

    base = np.datetime64("2024-06-01T00:00:00")
    offsets = rng.integers(0, 30 * 24 * 3600, size=n).astype("timedelta64[s]")
    ts = (base + offsets)

    return {
        "event_ts": np.datetime_as_string(ts, unit="s"),
        "user_id": rng.choice(cust_ids, size=n),
        "page": rng.choice(pages, size=n),
        "event_type": rng.choice(etypes, size=n, p=[0.5, 0.3, 0.15, 0.05]),
        "duration_ms": rng.integers(20, 30000, size=n),
        "country": rng.choice(countries, size=n),
    }


# --------------------------------------------------------------------------- #
# CSV / JSON writers (no pandas/polars dependency in the generator)          #
# --------------------------------------------------------------------------- #
def _esc(v) -> str:
    if v is None:
        return ""
    s = str(v)
    if any(c in s for c in [",", '"', "\n"]):
        return '"' + s.replace('"', '""') + '"'
    return s


def write_csv(path: Path, rows: list[dict]) -> None:
    cols = list(rows[0].keys())
    lines = [",".join(cols)]
    for r in rows:
        lines.append(",".join(_esc(r.get(c)) for c in cols))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(COURSE_ROOT)}  ({len(rows)} rows)")


def write_csv_cols(path: Path, cols: dict) -> None:
    names = list(cols.keys())
    n = len(cols[names[0]])
    out = [",".join(names)]
    arrs = [cols[c] for c in names]
    for i in range(n):
        out.append(",".join(_esc(a[i]) for a in arrs))
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(COURSE_ROOT)}  ({n} rows)")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"  wrote {path.relative_to(COURSE_ROOT)}  ({len(rows)} rows)")


def data_dir(ch: str) -> Path:
    d = COURSE_ROOT / CHAPTER_DIRS[ch] / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


# --------------------------------------------------------------------------- #
def main() -> None:
    rng = np.random.default_rng(SEED)

    regions = make_regions()
    products = make_products()
    customers = make_customers(rng)
    orders = make_orders(rng, customers, products)
    events = make_events(rng, customers, products)
    web = make_web_events(rng, customers)

    # 01 basics: the orders fact table
    write_csv(data_dir("01") / "orders.csv", orders)

    # 02 lazy / plan: orders
    write_csv(data_dir("02") / "orders.csv", orders)

    # 03 spark sql: orders + customers
    write_csv(data_dir("03") / "orders.csv", orders)
    write_csv(data_dir("03") / "customers.csv", customers)

    # 04 windows: orders
    write_csv(data_dir("04") / "orders.csv", orders)

    # 05 joins: the full relational set
    write_csv(data_dir("05") / "orders.csv", orders)
    write_csv(data_dir("05") / "customers.csv", customers)
    write_csv(data_dir("05") / "products.csv", products)
    write_csv(data_dir("05") / "regions.csv", regions)

    # 06 nested: clickstream JSON lines
    write_jsonl(data_dir("06") / "events.jsonl", events)

    # 07 performance: the big flat table + orders
    write_csv_cols(data_dir("07") / "web_events.csv", web)
    write_csv(data_dir("07") / "orders.csv", orders)

    # 08 schemas / read-write: orders (string ts) + customers
    write_csv(data_dir("08") / "orders.csv", orders)
    write_csv(data_dir("08") / "customers.csv", customers)

    # 09 capstone: everything
    write_csv(data_dir("09") / "orders.csv", orders)
    write_csv(data_dir("09") / "customers.csv", customers)
    write_csv(data_dir("09") / "products.csv", products)
    write_csv(data_dir("09") / "regions.csv", regions)
    write_jsonl(data_dir("09") / "events.jsonl", events)

    print("done.")


if __name__ == "__main__":
    main()
