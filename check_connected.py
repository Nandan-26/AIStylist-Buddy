import sqlite3

conn = sqlite3.connect("aistylist.db")

rows = conn.execute("""
SELECT name, image_path
FROM wardrobe
WHERE user_id = 1
AND image_path != ''
""").fetchall()

print("Connected images:")
for row in rows:
    print(row[0], "=>", row[1])

conn.close()