import json
import os
import socket
import threading
import tkinter as tk
import threading
import time

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
            checksum_str += b' ' * (HEADER - len(checksum_str))

            message = message.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length)) #Padding to ensure HEADER size

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
        full_msg = ''
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
            ui_class = UI(self)

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
        self.orders_text = tk.Text(self.root, height=15, width=50)
        self.orders_text.pack()

        # Add orders section
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

        # Update orders section
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

        # Delete orders section
        self.delete_order_frame = tk.Frame(self.root)
        self.delete_order_frame.pack()

        tk.Label(self.delete_order_frame, text="Order ID:").grid(row=0, column=0)
        self.delete_order_id_entry = tk.Entry(self.delete_order_frame)
        self.delete_order_id_entry.grid(row=0, column=1)

        self.delete_order_button = tk.Button(self.delete_order_frame, text="Delete Order", command=self.delete_order)
        self.delete_order_button.grid(row=1, columnspan=2)

    def update_orders(self):
        return
        if self.client.online:
            self.send("!1")
            response = self.receive()
            if response:
                orders = json.loads(response)
                self.orders_text.delete(1.0, tk.END)
                for order in orders:
                    self.orders_text.insert(tk.END, f"Order ID: {order['order_id']}, Table: {order['table_num']}, Items: {order['items']}, Status: {order['status']}\n")
            self.root.after(20000, self.update_orders)

    def add_order(self):
        table_num = self.table_num_entry.get()
        items = self.items_entry.get()
        special_requests = self.special_requests_entry.get()
        order_data = json.dumps({
            'table_num': table_num,
            'items': items,
            'special_requests': special_requests
        })
        self.send("!2")
        self.send(order_data)
        replay_msg = self.receive()
        print(f"[add_order]: {replay_msg}")

    def update_order(self):
        order_id = self.update_order_id_entry.get()
        status = self.update_status_entry.get()
        update_data = json.dumps({'order_id': order_id, 'status': status})
        self.send("!4")
        self.send(update_data)
        replay_msg = self.receive()
        print(f"[update_order]: {replay_msg}")

    def delete_order(self):
        order_id = self.delete_order_id_entry.get()
        delete_data = json.dumps({'order_id': order_id})
        self.send("!3")
        self.send(delete_data)
        replay_msg = self.receive()
        print(f"[delete_order]: {replay_msg}")

    def main_thread(self):
        while self.client.online:
            try:
                msg = str(input("SEND A MSG: "))
                self.client.client_socket.sendall(msg.encode())
                if msg == DISCONNECT_MESSAGE:
                    self.client.disconnect()
                    break
            except Exception as e:
                print(f"[ERROR] Unexpected error in sending_thread function: {e}")
                self.client.disconnect()
                break

    def receiving_thread(self):
        while self.client.online:
            try:
                full_msg = self.client.client_socket.recv(4096).decode()
                if full_msg:
                    print(f"RECEIVED: {full_msg}")
                    if full_msg == DISCONNECT_MESSAGE:
                        self.client.disconnect()
                        break
            except Exception as e:
                print(f"[ERROR] Unexpected error in receiving_thread function: {e}")
                self.client.disconnect()
                break

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
                print(f"[receieve func bfore returning ]RECEIVED: {full_msg}")

        return full_msg

if __name__ == "__main__":
    client = Client(ADDR)

