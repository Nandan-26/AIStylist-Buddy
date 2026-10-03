import sqlite3

conn = sqlite3.connect("aistylist.db")

conn.execute("""
DELETE FROM wardrobe
WHERE user_id = 1
AND image_path = ''
""")

conn.commit()

count = conn.execute("""
SELECT COUNT(*)
FROM wardrobe
WHERE user_id = 1
""").fetchone()[0]

print("Remaining wardrobe items:", count)

conn.close()