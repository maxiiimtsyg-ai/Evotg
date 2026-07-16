import sqlite3
from datetime import datetime

DB_NAME = "receipts.db"


def today_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT 
            COUNT(*),
            SUM(total)
        FROM receipts
        WHERE datetime LIKE ?
    """, (today + "%",))

    result = cur.fetchone()

    conn.close()

    checks = result[0] or 0
    total = result[1] or 0

    average = total / checks if checks else 0

    return {
        "checks": checks,
        "total": round(total, 2),
        "average": round(average, 2)
    }


def top_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, COUNT(*)
        FROM items
        GROUP BY name
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """)

    result = cur.fetchall()

    conn.close()

    return result
