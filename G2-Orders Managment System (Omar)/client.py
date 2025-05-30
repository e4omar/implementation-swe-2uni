import json
import os
import socket
import tkinter as tk
from tkinter import messagebox

HEADER = 4  #  256^(4) max length
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # ip address of current machine
ADDR = (SERVER, PORT)  # (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DIS"


def calculate_checksum(message):
    checksum = 0
    for x in message:
        checksum ^= ord(x)
    return checksum

class MessageSender:
    def __init__(self, client_socket=None):
        self.conn = client_socket

    def send_message(self, message):
        try:
            checksum = calculate_checksum(message)
            checksum_str = str(checksum).encode(FORMAT)
            checksum_str += b" " * (HEADER - len(checksum_str))

            message = message.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b" " * (HEADER - len(send_length)) #Padding to ensure HEADER size

            self.conn.send(send_length)
            self.conn.send(message)
            self.conn.send(checksum_str)
            return True
        except (socket.error, ConnectionResetError) as e:
            print(f"[ERROR] Error sending message: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error in send function: {e}")
            return False        
    
    def recv_message(self):
        full_msg = ""
        try:
            while True:
                part = self.conn.recv(1024).decode(FORMAT)
                full_msg += part
                if "[END]" in full_msg:
                    break

            if "::" in full_msg:
                message_part, checksum_part = full_msg.rsplit("::", 1) #split into msg and checksum
                message = message_part.replace("[END]", "")
                checksum = int(checksum_part.strip())

                if calculate_checksum(message_part) == checksum:
                    return message
                else:
                    print("[ERROR] Checksum mismatch from Server")
                    return None
            else:
                print("[ERROR] Message format incorrect, no checksum found")
                return None
            
        except (socket.error, ConnectionResetError) as e:
            print(f"[ERROR] Error receiving message: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error in receive function: {e}")
            return False



class Client:
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.online = True
        self.client_socket = None
        self.connect_to_server()
        self.start()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
            self.client_socket.connect(self.server_addr)
            print("Connected to the server successfully")
        except socket.error as e:
            print(f"[ERROR] Failed to connect to the server: {e}")
            self.online = False

    def disconnect(self):
        self.online = False
        self.client_socket.close()
        print("Client disconnected")
        os._exit(0)

    def start(self):
        if self.online:
            user_type = input("Enter 1 for waitstaff or 2 for kitchen staff: ")

            while user_type not in ["1", "2"]:
                print("Invalid input. Please enter 1 for waitstaff or 2 for kitchen staff.")
                user_type = input("Enter 1 for waitstaff or 2 for kitchen staff: ")

            if user_type == "1":
                ui_class = WaitstaffUI(self)
            elif user_type == "2":
                ui_class = KitchenStaffUI(self)

class UI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Order Management Client")
        self.message_sender = MessageSender(self.client.client_socket)
        self.create_widgets()
        self.update_orders()
        self.root.mainloop()

    def create_widgets(self):
        self.orders_window = tk.Toplevel(self.root)
        self.orders_window.title("Current Orders")
        self.orders_window.geometry("800x400")
        self.orders_window.resizable(True, True)

        frame = tk.Frame(self.orders_window)
        frame.pack(fill=tk.BOTH, expand=True)
        self.orders_text = tk.Text(frame, wrap=tk.NONE, height=20, width=100)
        self.orders_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame, command=self.orders_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_text.config(yscrollcommand=scrollbar.set)

        # Add column headers
        self.orders_text.insert(tk.END, f"{'Order ID':<10} {'Table Number':<15} {'Items':<30} {'Special Requests':<25} {'Status':<10}\n")
        self.orders_text.insert(tk.END, "-"*90 + "\n\n")
    def update_orders(self):
        if self.client.online:
            self.send("!1")
            response = self.receive()
            if response:
                try:
                    orders = json.loads(response)
                    self.orders_text.delete(3.0, tk.END)  # Keep the headings
                    if isinstance(orders, dict):
                        self.orders_text.insert(tk.END, f"\n\n")
                        for order_id, order in orders.items():
                            table_num = order.get("table_num", "N/A")
                            items = order.get("items", "N/A")
                            special_requests = order.get("special_requests", "N/A")
                            status = order.get("status", "N/A")
                            if status.lower() == "done":
                                status = "**DONE**"
                            order_text = f"{order_id:<10} {table_num:<15} {items:<30} {special_requests:<25} {status:<10}\n"
                            self.orders_text.insert(tk.END, order_text)
                    else:
                        self.orders_text.insert(tk.END, f"Unexpected data: {orders}\n")
                except Exception as e:
                    self.orders_text.insert(tk.END, f"Error parsing orders: {e}\nRaw: {response}\n")
            self.root.after(5000, self.update_orders)

    def send(self, msg):
        success = self.message_sender.send_message(msg)
        if msg == DISCONNECT_MESSAGE:
            self.client.disconnect()
        if not success:
            print("[ERROR] Failed to send message.")
            print("[ERROR] Closing client connection...")
            self.client.disconnect()

    def receive(self):
        full_msg = self.message_sender.recv_message()
        if full_msg:
            if full_msg == DISCONNECT_MESSAGE:
                self.client.disconnect()
            elif full_msg is False:
                self.client.disconnect()
            else:
                return full_msg

class WaitstaffUI(UI):
    def create_widgets(self):
        super().create_widgets()
        self.add_order_frame = tk.Frame(self.root)
        self.add_order_frame.pack()

        tk.Label(self.add_order_frame, text="Table Number:").grid(row=0, column=0)
        self.table_num_entry = tk.Entry(self.add_order_frame)
        self.table_num_entry.grid(row=0, column=1)

        tk.Label(self.add_order_frame, text="Items:").grid(row=1, column=0)
        self.items_entry = tk.Entry(self.add_order_frame)
        self.items_entry.grid(row=1, column=1)

        tk.Label(self.add_order_frame, text="Special Requests:").grid(row=2, column=0)
        self.special_requests_entry = tk.Entry(self.add_order_frame)
        self.special_requests_entry.grid(row=2, column=1)
        
        self.add_order_button = tk.Button(self.add_order_frame, text="Add Order", command=self.add_order)
        self.add_order_button.grid(row=3, columnspan=2)

        self.delete_order_frame = tk.Frame(self.root)
        self.delete_order_frame.pack()

        tk.Label(self.delete_order_frame, text="Order ID:").grid(row=0, column=0)
        self.delete_order_id_entry = tk.Entry(self.delete_order_frame)
        self.delete_order_id_entry.grid(row=0, column=1)

        self.delete_order_button = tk.Button(self.delete_order_frame, text="Delete Order", command=self.delete_order)
        self.delete_order_button.grid(row=1, columnspan=2)

    def add_order(self):
        table_num = self.table_num_entry.get()
        items = self.items_entry.get()
        special_requests = self.special_requests_entry.get()

        # Error handling for blank fields and incorrect data types
        if not table_num.isdigit():
            tk.messagebox.showerror("Input Error", "Table Number must be an integer and not blank.")
            return
        if not items.strip():
            tk.messagebox.showerror("Input Error", "Items must not be blank.")
            return
        if not special_requests.strip():
            tk.messagebox.showerror("Input Error", "Special Requests must not be blank.")
            return

        order_data = json.dumps({
            "table_num": table_num,
            "items": items,
            "special_requests": special_requests
        })
        self.send("!2")
        self.send(order_data)
        replay_msg = self.receive()
        
        if replay_msg.startswith("T:"):
            order_id = replay_msg[2:]
            tk.messagebox.showinfo("Order Confirmation", f"Order ID {order_id} added successfully.")
        else:
            tk.messagebox.showerror("Order Error", "Failed to add order.")
        

    def delete_order(self):
        order_id = self.delete_order_id_entry.get()

        # Error handling for blank fields and incorrect data types
        if not order_id.isdigit():
            tk.messagebox.showerror("Input Error", "Order ID must be an integer and not blank.")
            return

        delete_data = json.dumps({"order_id": order_id})
        self.send("!3")
        self.send(delete_data)
        replay_msg = self.receive()

        if replay_msg.startswith("T:"):
            tk.messagebox.showinfo("Delete Confirmation", f"Order ID {order_id} deleted successfully.")
        elif replay_msg.startswith("F:"):
            tk.messagebox.showerror("Delete Error", f"Delete Failed. Order {order_id} is not present.")
        else:
            tk.messagebox.showerror("Order Error", "Failed to delete order.")

class KitchenStaffUI(UI):
    def create_widgets(self):
        super().create_widgets()
        self.update_order_frame = tk.Frame(self.root)
        self.update_order_frame.pack()

        tk.Label(self.update_order_frame, text="Order ID:").grid(row=0, column=0)
        self.update_order_id_entry = tk.Entry(self.update_order_frame)
        self.update_order_id_entry.grid(row=0, column=1)

        tk.Label(self.update_order_frame, text="New Status:").grid(row=1, column=0)
        self.update_status_entry = tk.Entry(self.update_order_frame)
        self.update_status_entry.grid(row=1, column=1)

        self.update_order_button = tk.Button(self.update_order_frame, text="Update Order", command=self.update_order)
        self.update_order_button.grid(row=2, columnspan=2)

    def update_order(self):
        order_id = self.update_order_id_entry.get()
        status = self.update_status_entry.get()

        # Error handling for blank fields and incorrect data types
        if not order_id.isdigit():
            tk.messagebox.showerror("Input Error", "Order ID must be an integer and not blank.")
            return
        
        if not status.strip():
            tk.messagebox.showerror("Input Error", "Status must not be blank.")
            return

        update_data = json.dumps({"order_id": order_id, "status": status})
        self.send("!4")
        self.send(update_data)
        replay_msg = self.receive()
        
        if replay_msg.startswith("T:"):
            tk.messagebox.showinfo("Order Update Confirmation", f"Order ID {order_id} status updated successfully.")
        elif replay_msg.startswith("F:"):
            tk.messagebox.showerror("Order Update Error", f"Update Failed. Order {order_id} is not present.")
        else:
            tk.messagebox.showerror("Order Update Error", "Failed to update order.")


if __name__ == "__main__":
    client = Client(ADDR)
