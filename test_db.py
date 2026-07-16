import sqlite3

conn = sqlite3.connect("receipts.db")
cur = conn.cursor()

cur.execute("SELECT * FROM receipts")

for row in cur.fetchall():
    print(row)

print("ITEMS:")

cur.execute("SELECT * FROM items")

for row in cur.fetchall():
    print(row)

conn.close()
