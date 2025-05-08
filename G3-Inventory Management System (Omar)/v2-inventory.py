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

    def add_new_stock_entry(self, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.db.insert_entry(item_name, quantity_on_hand, reorder_level, supplier_info)

    def modify_stock_entry(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        self.db.modify_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)

    def search_stock_records(self, item_id=None, item_name=None):
        return self.db.search_records(item_id, item_name)

    def monitor_stock_records(self):
        return self.db.get_low_stock_items()
        # This will be complated later

    def generate_usage_report(self):
        return self.db.retrieve_usage_data()
        # This will be complated later

    def close(self):
        self.db.close()

class InventoryUI:
    def __init__(self):
        self.controller = InventoryController()
        self.notify_low_stock()

    def addition_request(self, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.controller.add_new_stock_entry(item_name, quantity_on_hand, reorder_level, supplier_info)

    def modify_request(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        self.controller.modify_stock_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)

    def search_request(self, item_id=None, item_name=None):
        return self.controller.search_stock_records(item_id, item_name)

    def notify_low_stock(self):
        print("Checking for low stock items...")
        low_stock_items = self.controller.monitor_stock_records()
        if not low_stock_items:
            print("No low stock items found.")
            print()
        else:
            print("Low stock items found:")
            for item in low_stock_items:
                print(f"Item ID: {item[0]}, Item Name: {item[1]}, Quantity on Hand: {item[2]}, Reorder Level: {item[3]}, Supplier Info: {item[4]}")
            print()


    def request_usage_report(self):
        usage_data = self.controller.generate_usage_report()
        self.display_usage_report(usage_data)

    def display_usage_report(self, usage_data):
        for record in usage_data:
            print(record)

    def close(self):
        self.controller.close()

def main():
    ui = InventoryUI()
    
    # Test addition of new stock entries
    print("Adding new stock entries...")
    ui.addition_request(item_name="Tomatoes", quantity_on_hand=50, reorder_level=20, supplier_info="Supplier A")
    ui.addition_request(item_name="Potatoes", quantity_on_hand=30, reorder_level=10, supplier_info="Supplier B")
    print("Stock entries added successfully.\n")
    
    # Test modification of stock entries
    print("Modifying stock entries...")
    ui.modify_request(item_id=1, quantity_on_hand=60, supplier_info="Updated Supplier A")
    ui.modify_request(item_id=2, item_name="Sweet Potatoes", quantity_on_hand=12, reorder_level=15, supplier_info="Updated Supplier B")
    print("Stock entries modified successfully.\n")
    
    # Test searching for stock records
    print("Searching for stock records...")
    search_results = ui.search_request(item_id=1)
    print("Search results for item_id=1:", search_results)
    search_results = ui.search_request(item_name="Sweet Potatoes")
    print("Search results for item_name='Sweet Potatoes':", search_results)
    print()
    
    # Test low stock notification
    #print("Checking for low stock items...")
    #ui.notify_low_stock()
    #print()
    
    # Test usage report generation
    print("Generating usage report...")
    ui.request_usage_report()
    print()
    
    # Close the UI
    ui.close()
    print("Inventory UI closed.")

if __name__ == "__main__":
    main()