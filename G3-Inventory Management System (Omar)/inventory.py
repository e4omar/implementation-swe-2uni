import sqlite3

conn = sqlite3.connect('restaurant_inventory.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Inventory (
    item_id INTEGER PRIMARY KEY,
    item_name VARCHAR(40) NOT NULL,
    quantity_on_hand INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,
    supplier_info varchar(400)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created successfully.")
