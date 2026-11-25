import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).with_name("marketplace.db")

@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS product_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            version INTEGER NOT NULL,
            saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            event_type TEXT NOT NULL,
            anonymous_user_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        CREATE INDEX IF NOT EXISTS idx_events_time ON events(occurred_at);
        """)
        count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            from seed_data import seed_database
            seed_database(con)

def get_products():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM products ORDER BY id")]

def add_product(title, description, category, price, stock):
    with connect() as con:
        cur = con.execute("""INSERT INTO products(title,description,category,price,stock,version)
                             VALUES(?,?,?,?,?,1)""",
                          (title, description, category, float(price), int(stock)))
        return cur.lastrowid

def update_stock(product_id, stock):
    with connect() as con:
        row = con.execute("SELECT * FROM products WHERE id=?", (int(product_id),)).fetchone()
        if not row:
            raise ValueError("Product not found")
        con.execute("""INSERT INTO product_history
            (product_id,title,description,category,price,stock,version)
            VALUES(?,?,?,?,?,?,?)""",
            (row["id"], row["title"], row["description"], row["category"],
             row["price"], row["stock"], row["version"]))
        con.execute("""UPDATE products SET stock=?, version=version+1,
                       updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                    (int(stock), int(product_id)))

def get_history(product_id=None):
    with connect() as con:
        if product_id:
            rows = con.execute("SELECT * FROM product_history WHERE product_id=? ORDER BY history_id DESC",
                               (int(product_id),)).fetchall()
        else:
            rows = con.execute("SELECT * FROM product_history ORDER BY history_id DESC LIMIT 200").fetchall()
        return [dict(r) for r in rows]

def add_event(product_id, event_type, user_id):
    from datetime import datetime, timezone
    with connect() as con:
        con.execute("INSERT INTO events(product_id,event_type,anonymous_user_id,occurred_at) VALUES(?,?,?,?)",
                    (product_id, event_type, user_id, datetime.now(timezone.utc).isoformat()))

def get_events():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM events ORDER BY occurred_at DESC LIMIT 5000")]

def event_count():
    with connect() as con:
        return con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
