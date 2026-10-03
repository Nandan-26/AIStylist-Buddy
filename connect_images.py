import sqlite3
import os

db = "aistylist.db"

images = {
    "White Oxford Shirt": "white_oxford_shirt.jpg",
    "Black T-Shirt": "black_tshirt.jpg",
    "Navy Polo": "navy_polo.jpg",
    "Beige Linen Shirt": "beige_linen_shirt.jpg",
    "Green Casual Shirt": "green_casual_shirt.jpg",
    "Dark Blue Jeans": "dark_blue_jeans.jpg",
    "Black Jeans": "black_jeans.jpg",
    "Beige Chinos": "beige_chinos.jpg",
    "Black Formal Trousers": "black_formal_trousers.jpg",
    "Grey Cargo Pants": "grey_cargo_pants.jpg",
    "White Sneakers": "white_sneakers.jpg",
    "Black Sneakers": "black_sneakers.jpg",
    "Brown Loafers": "brown_loafers.jpg",
    "Black Formal Shoes": "black_formal_shoes.jpg",
    "Running Shoes": "running_shoes.jpg",
    "Black Leather Belt": "black_leather_belt.jpg",
    "Brown Leather Belt": "brown_leather_belt.jpg",
    "Black Watch": "black_watch.jpg",
    "Silver Watch": "silver_watch.jpg",
    "Black Sunglasses": "black_sunglasses.jpg",
}

conn = sqlite3.connect(db)

for name, filename in images.items():
    path = os.path.join(
        "sample_wardrobe",
        "nandan",
        filename
    )

    conn.execute(
        """
        UPDATE wardrobe
        SET image_path = ?
        WHERE user_id = 1 AND name = ?
        """,
        (path, name)
    )

conn.commit()

count = conn.execute(
    """
    SELECT COUNT(*)
    FROM wardrobe
    WHERE user_id = 1
    AND image_path != ''
    """
).fetchone()[0]

print("Images connected:", count)

conn.close()