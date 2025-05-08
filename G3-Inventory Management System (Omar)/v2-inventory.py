import sqlite3

# Create the database and table with auto-incrementing item_id
conn = sqlite3.connect('restaurant_inventory.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(40) NOT NULL,
    quantity_on_hand INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,
    supplier_info VARCHAR(400)
)
''')

conn.commit()
conn.close()

print("Database created successfully.")


class StockDatabase:
    def __init__(self, db_name='restaurant_inventory.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def insert_entry(self, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.cursor.execute('''
        INSERT INTO Inventory (item_name, quantity_on_hand, reorder_level, supplier_info)
        VALUES (?, ?, ?, ?)
        ''', (item_name, quantity_on_hand, reorder_level, supplier_info))
        self.conn.commit()

    def retrun_entries(self):
        self.cursor.execute('SELECT * FROM Inventory')
        rows = self.cursor.fetchall()
        return rows

def main():
    db = StockDatabase()
    db.insert_entry('Tomatoes', 50, 20, 'Supplier A')
    db.insert_entry('Potatoes', 30, 10, 'Supplier B')
    db.insert_entry('Onions', 20, 5, 'Supplier C')
    entries = db.retrun_entries()
    for entry in entries:
        print(entry)
    print("Entries inserted successfully.")

    db.conn.close()

if __name__ == "__main__":
    main()  