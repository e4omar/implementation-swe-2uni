import sqlite3
import tkinter as tk
from tkinter import messagebox

conn = sqlite3.connect("restaurant_inventory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(40) NOT NULL,
    quantity_on_hand INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,
    supplier_info VARCHAR(400)
)
""")

conn.commit()
conn.close()

print("Database created successfully.")

class StockDatabase:
    def __init__(self, db_name="restaurant_inventory.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {e}")

    def insert_entry(self, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.cursor.execute("""
        INSERT INTO Inventory (item_name, quantity_on_hand, reorder_level, supplier_info)
        VALUES (?, ?, ?, ?)
        """, (item_name, quantity_on_hand, reorder_level, supplier_info))
        self.conn.commit()

    def modify_entry(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        query = "UPDATE Inventory SET "
        params = []
        if item_name is not None:
            query += "item_name = ?, "
            params.append(item_name)
        if quantity_on_hand is not None:
            query += "quantity_on_hand = ?, "
            params.append(quantity_on_hand)
        if reorder_level is not None:
            query += "reorder_level = ?, "
            params.append(reorder_level)
        if supplier_info is not None:
            query += "supplier_info = ?, "
            params.append(supplier_info)
        query = query.rstrip(", ") + " WHERE item_id = ?"
        params.append(item_id)
        self.cursor.execute(query, params)
        self.conn.commit()

    def delete_entry(self, item_id):
        self.cursor.execute("DELETE FROM Inventory WHERE item_id = ?", (item_id,))
        self.conn.commit()

    def search_records(self, item_id=None, item_name=None):
        query = "SELECT * FROM Inventory WHERE "
        params = []
        if item_id is not None:
            query += "item_id = ? AND "
            params.append(item_id)
        if item_name is not None:
            query += "item_name = ? AND "
            params.append(item_name)
        query = query.rstrip(" AND ")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_low_stock_items(self):
        self.cursor.execute("SELECT * FROM Inventory WHERE quantity_on_hand < reorder_level")
        return self.cursor.fetchall()

    def retrieve_usage_data(self):
        self.cursor.execute("SELECT * FROM Inventory")
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.conn.close()

class InventoryController:
    def __init__(self):
        try:
            self.db = StockDatabase()
        except Exception as e:
            raise Exception(f"Controller initialization error: {e}")

    def add_new_stock_entry(self, item_name, quantity_on_hand, reorder_level, supplier_info):
        self.db.insert_entry(item_name, quantity_on_hand, reorder_level, supplier_info)

    def modify_stock_entry(self, item_id, item_name=None, quantity_on_hand=None, reorder_level=None, supplier_info=None):
        self.db.modify_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)

    def delete_stock_entry(self, item_id):
        self.db.delete_entry(item_id)

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
        try:
            self.controller = InventoryController()
            self.root = root
            self.root.title("Restaurant Inventory Management")
            self.set_main_window()
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Initialization error: {e}")

    def set_main_window(self):
        # Set fixed size and center on screen
        width, height = 400, 300
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.main_x = x
        self.main_y = y
        self.main_width = width
        self.main_height = height

    def get_child_window_position(self, longer_width = False):

        # Position child window to the right of the main menu
        width = 400
        height = 300

        if longer_width:
            width = 650
        
        child_x = self.main_x + self.main_width + 20
        child_y = self.main_y
        return f"{width}x300+{child_x}+{child_y}"

    def create_widgets(self):
        try:
            self.add_button = tk.Button(self.root, text="Add New Entry", command=self.add_new_entry)
            self.add_button.pack(pady=5)

            self.view_button = tk.Button(self.root, text="View Current Records", command=self.view_records)
            self.view_button.pack(pady=5)

            self.low_stock_button = tk.Button(self.root, text="Notify Low Stock", command=self.notify_low_stock)
            self.low_stock_button.pack(pady=5)

            self.modify_button = tk.Button(self.root, text="Modify Stock Entry", command=self.modify_entry)
            self.modify_button.pack(pady=5)

            self.delete_button = tk.Button(self.root, text="Delete Stock Entry", command=self.delete_entry)
            self.delete_button.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating main menu widgets: {e}")

    def add_new_entry(self):
        try:
            self.new_entry_window = tk.Toplevel(self.root)
            self.new_entry_window.title("Add New Entry")
            self.new_entry_window.geometry(self.get_child_window_position())
            self.new_entry_window.resizable(False, False)

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

            tk.Button(self.new_entry_window, text="Submit", command=self.submit_new_entry).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Add New Entry window: {e}")

    def submit_new_entry(self):
        item_name = self.item_name_entry.get()
        quantity_on_hand = self.quantity_entry.get()
        reorder_level = self.reorder_entry.get()
        supplier_info = self.supplier_entry.get()

        if not item_name or not quantity_on_hand or not reorder_level:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        try:
            quantity_on_hand = int(quantity_on_hand)
            reorder_level = int(reorder_level)
        except ValueError:
            messagebox.showerror("Error", "Quantity on Hand and Reorder Level must be integers.")
            return

        try:
            self.controller.add_new_stock_entry(item_name, quantity_on_hand, reorder_level, supplier_info)
            messagebox.showinfo("Success", "New entry added successfully!")
            self.new_entry_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add entry: {e}")

    def view_records(self):
        try:
            records = self.controller.generate_usage_report()
            self.records_window = tk.Toplevel(self.root)
            self.records_window.title("Current Records")
            
            # Set width to 650 instead of 400. height of 300 
            # position to the right of main menu
            self.records_window.geometry(self.get_child_window_position(longer_width=True))
            self.records_window.resizable(True, True)

            # Setting up a Text widget with a scrollbar for better display
            frame = tk.Frame(self.records_window)
            frame.pack(fill=tk.BOTH, expand=True)
            text = tk.Text(frame, wrap=tk.NONE, height=15, width=50)
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(frame, command=text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text.config(yscrollcommand=scrollbar.set)

            # Add column headers
            text.insert(tk.END, f"{'ID':<5} {'Name':<20} {'Qty':<6} {'Reorder':<8} {'Supplier':<20}\n")
            text.insert(tk.END, "-"*65 + "\n")
            for record in records:
                text.insert(
                    tk.END,
                    f"{str(record[0]):<5} {str(record[1]):<20} {str(record[2]):<6} {str(record[3]):<8} {str(record[4]):<20}\n"
                )
            text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view records: {e}")

    def notify_low_stock(self):
        try:
            low_stock_items = self.controller.monitor_stock_records()
            self.low_stock_window = tk.Toplevel(self.root)
            self.low_stock_window.title("Low Stock Items")
            self.low_stock_window.geometry(self.get_child_window_position(longer_width=True))
            self.low_stock_window.resizable(False, False)

            text = tk.Text(self.low_stock_window, wrap=tk.NONE, height=15, width=100)
            text.pack(fill=tk.BOTH, expand=True)

            # Add column headers
            text.insert(tk.END, f"{'ID':<5} {'Name':<30} {'Qty':<10} {'Reorder':<10} {'Supplier':<40}\n")
            text.insert(tk.END, "-"*110 + "\n")

            if not low_stock_items:
                text.insert(tk.END, "No low stock items found.\n")
            else:
                for item in low_stock_items:
                    text.insert(
                        tk.END,
                        f"{str(item[0]):<5} {str(item[1]):<30} {str(item[2]):<10} {str(item[3]):<10} {str(item[4]):<40}\n"
                    )
            text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to notify low stock: {e}")

    def modify_entry(self):
        try:
            self.modify_window = tk.Toplevel(self.root)
            self.modify_window.title("Modify Stock Entry")
            self.modify_window.geometry(self.get_child_window_position())
            self.modify_window.resizable(False, False)

            tk.Label(self.modify_window, text="Item ID").pack()
            self.modify_item_id_entry = tk.Entry(self.modify_window)
            self.modify_item_id_entry.pack()

            tk.Label(self.modify_window, text="Item Name").pack()
            self.modify_item_name_entry = tk.Entry(self.modify_window)
            self.modify_item_name_entry.pack()

            tk.Label(self.modify_window, text="Quantity on Hand").pack()
            self.modify_quantity_entry = tk.Entry(self.modify_window)
            self.modify_quantity_entry.pack()

            tk.Label(self.modify_window, text="Reorder Level").pack()
            self.modify_reorder_entry = tk.Entry(self.modify_window)
            self.modify_reorder_entry.pack()

            tk.Label(self.modify_window, text="Supplier Info").pack()
            self.modify_supplier_entry = tk.Entry(self.modify_window)
            self.modify_supplier_entry.pack()

            tk.Button(self.modify_window, text="Submit", command=self.submit_modify_entry).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Modify Entry window: {e}")

    def submit_modify_entry(self):
        item_id = self.modify_item_id_entry.get()
        item_name = self.modify_item_name_entry.get()
        quantity_on_hand = self.modify_quantity_entry.get()
        reorder_level = self.modify_reorder_entry.get()
        supplier_info = self.modify_supplier_entry.get()

        if not item_id:
            messagebox.showerror("Error", "Item ID must be provided.")
            return

        try:
            item_id = int(item_id)
        except ValueError:
            messagebox.showerror("Error", "Item ID must be an integer.")
            return

        if quantity_on_hand:
            try:
                quantity_on_hand = int(quantity_on_hand)
            except ValueError:
                messagebox.showerror("Error", "Quantity on Hand must be an integer.")
                return
        else:
            quantity_on_hand = None

        if reorder_level:
            try:
                reorder_level = int(reorder_level)
            except ValueError:
                messagebox.showerror("Error", "Reorder Level must be an integer.")
                return
        else:
            reorder_level = None

        if not item_name:
            item_name = None

        if not supplier_info:
            supplier_info = None

        try:
            self.controller.modify_stock_entry(item_id, item_name, quantity_on_hand, reorder_level, supplier_info)
            messagebox.showinfo("Success", "Stock entry modified successfully!")
            self.modify_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify entry: {e}")

    def delete_entry(self):
        try:
            self.delete_window = tk.Toplevel(self.root)
            self.delete_window.title("Delete Stock Entry")
            self.delete_window.geometry(self.get_child_window_position())
            self.delete_window.resizable(False, False)

            tk.Label(self.delete_window, text="Item ID").pack()
            self.delete_item_id_entry = tk.Entry(self.delete_window)
            self.delete_item_id_entry.pack()

            tk.Button(self.delete_window, text="Submit", command=self.submit_delete_entry).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Delete Entry window: {e}")

    def submit_delete_entry(self):
        item_id = self.delete_item_id_entry.get()

        if not item_id:
            messagebox.showerror("Error", "Item ID must be provided.")
            return

        try:
            item_id = int(item_id)
        except ValueError:
            messagebox.showerror("Error", "Item ID must be an integer.")
            return

        try:
            self.controller.delete_stock_entry(item_id)
            messagebox.showinfo("Success", "Stock entry deleted successfully!")
            self.delete_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete entry: {e}")

    def close(self):
        try:
            self.controller.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error closing the application: {e}")


def main():
    root = tk.Tk()
    ui = InventoryUI(root)
    root.mainloop()
    ui.close()
    print("Inventory UI closed.")

if __name__ == "__main__":
    main()
