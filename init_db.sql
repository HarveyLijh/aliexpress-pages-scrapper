/* ============================================================
   AliExpress Scraper – Initial Schema
   ============================================================ */
BEGIN;

/* ----------  Extensions  ----------------------------------- */
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- for uuid_generate_v4()

/* ----------  Core table: products  -------------------------- */
CREATE TABLE products (
    id            UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    title         TEXT            NOT NULL,
    slug          TEXT            NOT NULL UNIQUE,          -- human-readable key
    rating        NUMERIC(2,1),                             -- NULL when “N/A”
    sold_count    INTEGER         NOT NULL,
    free_shipping BOOLEAN         NOT NULL,
    price_usd     NUMERIC(10,2)   NOT NULL,
    search        TSVECTOR,                                 -- title + keywords
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_sold   ON products (sold_count DESC);
CREATE INDEX idx_products_search ON products USING GIN (search);

/* ----------  1-N: product_images  --------------------------- */
CREATE TABLE product_images (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID  NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    seq        INTEGER NOT NULL,              -- preserves original order
    url        TEXT    NOT NULL,
    UNIQUE (product_id, seq)
);

/* ----------  lookup: keywords  ------------------------------ */
CREATE TABLE keywords (
    id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE
);

/* ----------  M-N link: product_keywords  -------------------- */
CREATE TABLE product_keywords (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, keyword_id)
);

/* ----------  Utility triggers  ------------------------------ */
-- Keep updated_at current
CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_touch
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

/* ----------  Full-text search maintenance  ----------------- */
-- Combine title + all linked keywords into one tsvector
CREATE OR REPLACE FUNCTION f_products_to_tsvector(p_id UUID)
RETURNS tsvector AS $$
  SELECT
      setweight(to_tsvector('simple', coalesce(p.title, '')), 'A') ||
      setweight(to_tsvector('simple', string_agg(k.name, ' ')), 'B')
  FROM products p
  LEFT JOIN product_keywords pk ON pk.product_id = p.id
  LEFT JOIN keywords k          ON k.id = pk.keyword_id
  WHERE p.id = p_id
  GROUP BY p.id;
$$ LANGUAGE sql;

-- Refresh search column when products row changes
CREATE OR REPLACE FUNCTION trg_products_search_upd()
RETURNS trigger AS $$
BEGIN
  NEW.search := f_products_to_tsvector(NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_search_tsv
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION trg_products_search_upd();

-- Refresh when product-keyword links change
CREATE OR REPLACE FUNCTION trg_pk_search_refresh()
RETURNS trigger AS $$
BEGIN
  UPDATE products
  SET search = f_products_to_tsvector(NEW.product_id)
  WHERE id = NEW.product_id;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pk_search_ins
AFTER INSERT ON product_keywords
FOR EACH ROW EXECUTE FUNCTION trg_pk_search_refresh();

CREATE TRIGGER pk_search_del
AFTER DELETE ON product_keywords
FOR EACH ROW EXECUTE FUNCTION trg_pk_search_refresh();

-- Refresh when keyword text changes
CREATE OR REPLACE FUNCTION trg_keywords_refresh()
RETURNS trigger AS $$
BEGIN
  UPDATE products
  SET search = f_products_to_tsvector(pk.product_id)
  FROM product_keywords pk
  WHERE pk.keyword_id = NEW.id
    AND pk.product_id = products.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER keywords_search_upd
AFTER UPDATE ON keywords
FOR EACH ROW EXECUTE FUNCTION trg_keywords_refresh();

/* ----------  Done  ----------------------------------------- */
COMMIT;

/*
 * OPTIONAL one-time back-fill after loading historical data:
 *   UPDATE products SET search = f_products_to_tsvector(id);
 *
 * Full-text query pattern:
 *   SELECT * FROM products
 *   WHERE search @@ plainto_tsquery('simple', 'wireless bluetooth headset')
 *   ORDER BY ts_rank(search, plainto_tsquery('simple', 'wireless bluetooth headset')) DESC
 *   LIMIT 20;
 */
