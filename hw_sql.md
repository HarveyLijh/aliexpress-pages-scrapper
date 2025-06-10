## 📋 Assignment: “Headphone Scraper” Database Design & Queries

### 🥅 Learning Goals

By the end of this assignment, you should be able to:

1. **Design** a normalized PostgreSQL schema for semi‑structured scraped data
2. **Write** DDL (`CREATE TABLE`) statements with sensible data types, keys and constraints
3. **Import** CSV data into your tables (via `COPY` or `INSERT`)
4. **Write** SQL queries (SELECT, WHERE, JOIN, GROUP BY, ORDER BY) to answer business‑style questions
5. **Apply** normalization principles (1NF–3NF) and think about data cleaning

---

### 📦 Data You Have

find details in the `aliexpress_products.csv` file, which contains scraped data about headphones from an e-commerce site. The columns are:
> **Notes on fields:**
>
> * **Rev\_Rate**: star rating, or NULL if “N/A”
> * **Sold**: number sold, may include commas or “+”
> * **Shipping**: text (“Free shipping” or NULL)
> * **Price**: string with “\$” prefix
> * **Image**: comma‑delimited URLs or “N/A”

---

### 🛠️ Part 1: Schema Design & DDL (worth 50%)

1. **Identify your tables.**

2. **Define columns & types.**

3. **Write your DDL.**
   Produce `CREATE TABLE` statements for each table, including:

   * Primary keys
   * NOT NULL and DEFAULT constraints
   * Foreign key relationships

---

### 📊 Part 2: Data Loading (worth 10%)

Write the SQL (or outline the steps) to load your scraped CSV into your schema. You can use either:

* `COPY products (…) FROM '/path/to/file.csv' WITH (FORMAT csv, HEADER true);`
* Or a series of `INSERT INTO products (…) VALUES (…);`

Make sure you strip the “\$”, “ sold”, commas, and convert “Free shipping” into a boolean.

---

### 🔍 Part 3: SQL Queries (worth 40%)

Write **one** SQL query for each of these questions. Show both the SQL and a one‑sentence description of what it returns.

1. **Top 5 best‑selling** products (highest `sold_count`).
2. **Average price** of products with a rating ≥ 4.0.
3. **Count of products** offering free shipping vs. not.
4. **List products** with **no rating** (i.e. `rating IS NULL`).
5. **Number of images** per product (join & `COUNT`).
6. **Products sold > 100** and **free shipping**, ordered by price ascending.
7. **Price buckets**: how many products fall into \$0–\$10, \$10–\$20, \$20+?
8. *(Advanced)* **Best “value”** = `sold_count / price_usd`: list top 5.

---

### 📅 Deliverables

* A single SQL script (`homework.sql`) containing all your `CREATE TABLE`, data‐loading statements, and your eight query solutions.
* A short README explaining any design decisions (e.g., why you chose certain data types, how you handled nulls).
