#!/usr/bin/env python3
"""
Load AliExpress CSV into the UUID-based schema with keyword deduping and slugs.
"""
import os
import csv, re, ast, unicodedata, psycopg2
from pathlib import Path
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()  # load environment variables from .env file
# ─── ENV  (set yours) ────────────────────────────────────────────────
DB = dict(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    sslmode=os.getenv("DB_SSLMODE"),
)
CSV_FILE = Path("aliexpress_products.csv")
# ─────────────────────────────────────────────────────────────────────

# ─── Helpers ─────────────────────────────────────────────────────────

num_re = re.compile(r"([\d.]+)")

def slugify(text: str) -> str:
    """
    Very small 'slugify': lower‑case, ASCII, spaces/punct → hyphen.
    """
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    text = re.sub(r"[^\w\s-]", "", text)     # drop non‑word chars except space & hyphen
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "product"

def parse_rating(s):   # 4.4★ → 4.4, N/A→None
    if not s or s.lower() == "n/a":
        return None
    m = num_re.search(s)
    return float(m.group(1)) if m else None

def parse_sold(s):     # "10,000+ sold" → 10000
    if not s or s.lower() == "n/a":
        return 0
    clean = (
        s.lower().replace("sold", "")
        .replace(",", "").replace("+", "").strip()
    )
    return int(clean) if clean.isdigit() else 0

def parse_price(s):    # "$12.67" → 12.67
    return float(s.replace("$", "").replace(",", "").strip()) if s else 0.0

def parse_images(s):
    if not s or s.lower() == "n/a":
        return []
    try:
        urls = ast.literal_eval(s)
        if isinstance(urls, list):
            return [u.strip() for u in urls]
    except Exception:
        pass
    return [u.strip() for u in s.strip("[]").split(",") if u.strip()]

# ─── Main loader ─────────────────────────────────────────────────────

def main() -> None:
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()
    print("🔄  Loading data from", CSV_FILE)

    with CSV_FILE.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames:
            raise ValueError("CSV file is empty or has no header row.")
        for raw in rdr:
            # 1️⃣  upsert keyword
            kw = (raw.get("Keyword") or "").strip() or None
            keyword_id = None
            if kw:
                cur.execute(
                    """
                    INSERT INTO keywords (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id
                    """,
                    (kw,),
                )
                keyword_id = cur.fetchone()[0]

            # 2️⃣  clean product fields
            title         = raw["Title"].strip()
            base_slug     = slugify(title)
            slug          = base_slug
            # ensure slug uniqueness (retry w/ numeric suffix)
            suffix = 1
            while True:
                cur.execute("SELECT 1 FROM products WHERE slug = %s", (slug,))
                if cur.fetchone():
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1
                else:
                    break

            rating        = parse_rating(raw.get("Rev_Rate"))
            sold_count    = parse_sold(raw.get("Sold"))
            free_shipping = bool(raw.get("Shipping") and "free" in raw["Shipping"].lower())
            price_usd     = parse_price(raw.get("Price"))

            # 3️⃣  insert product
            cur.execute(
                """
                INSERT INTO products
                  (title, slug, rating, sold_count, free_shipping, price_usd)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (title, slug, rating, sold_count, free_shipping, price_usd),
            )
            product_id: UUID = cur.fetchone()[0]

            # 4️⃣  link product‑keyword
            if keyword_id:
                cur.execute(
                    """
                    INSERT INTO product_keywords (product_id, keyword_id)
                    VALUES (%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    (product_id, keyword_id),
                )

            # 5️⃣  images
            for seq, url in enumerate(parse_images(raw.get("Image")), start=1):
                cur.execute(
                    """
                    INSERT INTO product_images (product_id, seq, url)
                    VALUES (%s,%s,%s)
                    """,
                    (product_id, seq, url),
                )

    conn.commit()
    cur.close()
    conn.close()
    print("✅  Load complete.")

if __name__ == "__main__":
    main()
