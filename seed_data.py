import random
from datetime import datetime, timedelta, timezone

ADJECTIVES = ["Lightweight", "Powerful", "Compact", "Wireless", "Portable", "Premium", "Budget"]
PRODUCTS = [
    ("Laptop", "Electronics/Computers", "for programming study and everyday productivity"),
    ("Gaming Laptop", "Electronics/Computers", "with graphics performance and fast processing"),
    ("Headphones", "Electronics/Audio", "with clear sound and comfortable fit"),
    ("Smartphone", "Electronics/Mobile", "with long battery life and a sharp camera"),
    ("Keyboard", "Electronics/Accessories", "with responsive keys for work"),
    ("Running Shoes", "Fashion/Footwear", "comfortable shoes for daily running"),
    ("Backpack", "Fashion/Bags", "durable bag for college and travel"),
    ("Monitor", "Electronics/Computers", "high resolution display for productivity"),
    ("Tablet", "Electronics/Mobile", "portable device for reading and notes"),
    ("Desk Lamp", "Home/Lighting", "energy efficient light for study desks"),
]
def seed_database(con):
    random.seed(42)
    rows=[]
    for i in range(1,1001):
        kind, category, desc = random.choice(PRODUCTS)
        title=f"{random.choice(ADJECTIVES)} {kind} Model {i:04d}"
        price=round(random.uniform(650, 85000), 2)
        stock=random.randint(0, 80)
        rows.append((i,title,f"{title} {desc}. Suitable for home, office and students.",
                     category,price,stock,1))
    con.executemany("""INSERT INTO products(id,title,description,category,price,stock,version)
                       VALUES(?,?,?,?,?,?,?)""", rows)
    now=datetime.now(timezone.utc)
    events=[]
    for _ in range(1800):
        p=random.randint(1,1000)
        typ=random.choices(["search","view","purchase"],[0.25,0.65,0.10])[0]
        when=now-timedelta(minutes=random.randint(0,60*24*14))
        events.append((p,typ,f"user_{random.randint(1,280):04d}",when.isoformat()))
    con.executemany("""INSERT INTO events(product_id,event_type,anonymous_user_id,occurred_at)
                       VALUES(?,?,?,?)""", events)
