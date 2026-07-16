import sqlite3

DB_NAME = "receipts.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id TEXT PRIMARY KEY,
        datetime TEXT,
        total REAL,
        payment TEXT,
        employee TEXT,
        shift TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id TEXT,
        name TEXT,
        price REAL,
        quantity REAL
    )
    """)

    conn.commit()
    conn.close()


def save_receipt(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    receipt = data["data"]

    cur.execute("""
        INSERT OR IGNORE INTO receipts
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        receipt["id"],
        receipt["dateTime"],
        receipt["totalAmount"],
        receipt["paymentSource"],
        receipt["employeeId"],
        receipt["shiftId"]
    ))

    for item in receipt["items"]:
        cur.execute("""
            INSERT INTO items
            (receipt_id, name, price, quantity)
            VALUES (?, ?, ?, ?)
        """, (
            receipt["id"],
            item["name"],
            item["price"],
            1
        ))

    conn.commit()
    conn.close()
