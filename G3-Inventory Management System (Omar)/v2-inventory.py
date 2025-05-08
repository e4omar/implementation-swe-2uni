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

    def modify_entry(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        query = 'UPDATE Inventory SET '
        params = []
        if item_name is not None:
            query += 'item_name = ?, '
            params.append(item_name)
        if quantity_on_hand is not None:
            query += 'quantity_on_hand = ?, '
            params.append(quantity_on_hand)
        if reorder_level is not None:
            query += 'reorder_level = ?, '
            params.append(reorder_level)
        if supplier_info is not None:
            query += 'supplier_info = ?, '
            params.append(supplier_info)
        query = query.rstrip(', ') + ' WHERE item_id = ?'
        params.append(item_id)
        self.cursor.execute(query, params)
        self.conn.commit()

    def search_records(self, item_id=None, item_name=None):
        query = 'SELECT * FROM Inventory WHERE '
        params = []
        if item_id is not None:
            query += 'item_id = ? AND '
            params.append(item_id)
        if item_name is not None:
            query += 'item_name = ? AND '
            params.append(item_name)
        query = query.rstrip(' AND ')
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_low_stock_items(self):
        self.cursor.execute('SELECT * FROM Inventory WHERE quantity_on_hand < reorder_level')
        return self.cursor.fetchall()

    def retrieve_usage_data(self):
        self.cursor.execute('SELECT * FROM Inventory')
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.conn.close()


class InventoryController:
    def __init__(self):
        self.db = StockDatabase()

    def add_new_stock_entry(self, item_id, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.db.insert_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)

    def modify_stock_entry(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        self.db.modify_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)

    def search_stock_records(self, item_id=None, item_name=None):
        return self.db.search_records(item_id, item_name)

    def monitor_stock_records(self):
        return self.db.get_low_stock_items()

    def generate_usage_report(self):
        return self.db.retrieve_usage_data()

    def close(self):
        self.db.close()




def main():
    controller = InventoryController()
    
    # Modify stock entries using the controller
    controller.modify_stock_entry(1, quantity_on_hand=60, supplier_info='Supplier B')
    controller.modify_stock_entry(2, item_name='Potatodsades', quantity_on_hand=30, reorder_level=10, supplier_info='Supplier C')
    
    # Retrieve and print usage data using the controller
    entries = controller.generate_usage_report()
    for entry in entries:
        print(entry)
    print("Entries modified successfully.")
    
    # Close the controller
    controller.close()

if __name__ == "__main__":
    main()