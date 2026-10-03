import sqlite3

conn = sqlite3.connect("aistylist.db")

rows = conn.execute("""
SELECT name
FROM wardrobe
WHERE user_id = 1
AND (image_path IS NULL OR image_path = '')
""").fetchall()

print("Missing images:")
for row in rows:
    print("-", row[0])

conn.close()
