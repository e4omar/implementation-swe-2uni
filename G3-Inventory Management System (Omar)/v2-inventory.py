import sqlite3
import tkinter as tk
from tkinter import messagebox

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

    def generate_usage_report(self):
        return self.db.retrieve_usage_data()

    def close(self):
        self.db.close()

class InventoryUI:
    def __init__(self, root):
        self.controller = InventoryController()
        self.root = root
        self.root.title("Restaurant Inventory Management")
        self.create_widgets()

    def create_widgets(self):
        # Main Menu 
        # Create buttons and entry fields
        self.add_button = tk.Button(self.root, text="Add New Entry", command=self.add_new_entry)
        self.add_button.pack()

        self.view_button = tk.Button(self.root, text="View Current Records", command=self.view_records)
        self.view_button.pack()

        self.low_stock_button = tk.Button(self.root, text="Notify Low Stock", command=self.notify_low_stock)
        self.low_stock_button.pack()

    def add_new_entry(self):

        # Creates a new window for adding a new entry
        self.new_entry_window = tk.Toplevel(self.root)
        self.new_entry_window.title("Add New Entry")

        #Label is text that is displayed to the user
        #Entry is a widget that store user input
        tk.Label(self.new_entry_window, text="Item Name").pack()
        self.item_name_entry = tk.Entry(self.new_entry_window)
        self.item_name_entry.pack()

        tk.Label(self.new_entry_window, text="Quantity on Hand").pack()
        self.quantity_entry = tk.Entry(self.new_entry_window)
        self.quantity_entry.pack()

        tk.Label(self.new_entry_window, text="Reorder Level").pack()
        self.reorder_entry = tk.Entry(self.new_entry_window)
        self.reorder_entry.pack()

        tk.Label(self.new_entry_window, text="Supplier Info").pack()
        self.supplier_entry = tk.Entry(self.new_entry_window)
        self.supplier_entry.pack()

        tk.Button(self.new_entry_window, text="Submit", command=self.submit_new_entry).pack()

    def submit_new_entry(self):
        # get() is used to retrieve the text from the entry box widget
        item_name = self.item_name_entry.get()
        quantity_on_hand = int(self.quantity_entry.get())
        reorder_level = int(self.reorder_entry.get())
        supplier_info = self.supplier_entry.get()

        self.controller.add_new_stock_entry(item_name, quantity_on_hand, reorder_level, supplier_info)
        messagebox.showinfo("Success", "New entry added successfully!")
        self.new_entry_window.destroy()

    def view_records(self):
        records = self.controller.generate_usage_report()
        self.records_window = tk.Toplevel(self.root)
        self.records_window.title("Current Records")

        for record in records:
            tk.Label(self.records_window, text=str(record)).pack()

    def notify_low_stock(self):
        low_stock_items = self.controller.monitor_stock_records()
        if not low_stock_items:
            messagebox.showinfo("Low Stock", "No low stock items found.")
        else:
            self.low_stock_window = tk.Toplevel(self.root)
            self.low_stock_window.title("Low Stock Items")
            for item in low_stock_items:
                tk.Label(self.low_stock_window, text=f"Item ID: {item[0]}, Item Name: {item[1]}, Quantity on Hand: {item[2]}, Reorder Level: {item[3]}, Supplier Info: {item[4]}").pack()

    def close(self):
        self.controller.close()

def main():
    root = tk.Tk()
    ui = InventoryUI(root)
    root.mainloop()
    ui.close()
    print("Inventory UI closed.")

if __name__ == "__main__":
    main()
