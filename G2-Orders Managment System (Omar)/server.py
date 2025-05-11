import json
import socket
import threading
import time

HEADER = 4  # 256^(4) max length
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # ip address
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

    def send_message(self, client_socket, message):
        message += "[END]"  # Add delimiter to help client find message end
        checksum = calculate_checksum(message)
        full_message = f"{message}::{checksum}"
        client_socket.send(full_message.encode(FORMAT))
    
    def recv_message(self):
        try:
            msg_length = self.conn.recv(HEADER).decode(FORMAT)  # recv the msg_length
            if msg_length:
                msg_length = int(msg_length)
                msg = self.conn.recv(msg_length).decode(FORMAT)  # recv actual msg
                checksum = int(self.conn.recv(HEADER).decode(FORMAT))  # HEADER recv not msg_length
                if calculate_checksum(msg) == checksum:
                    return msg
                else:
                    print(f"[ERROR] Checksum mismatch from {self.addr}")
                    return None
            else:
                print(f"[ERROR] No message length received from {self.addr}")
                return None
        except (socket.error, ConnectionResetError) as e:
            print(f"[ERROR] Client connection lost {self.addr}: {e}")
            return False

class OrderManagement:

    orders_dict = {
        1: {
            "table_num": 5,
            "items": "Burger x 3, Fries x 1",
            "special_requests": "Extra ketchup",
            "status": "New"
        },
        2: {
            "table_num": 3,
            "items": "Pazza x 2, Salad x 1",
            "special_requests": "No onions",
            "status": "In Progress"
        },
        3: {
            "table_num": 8,
            "items": "pasta x 7, Garlic Bread x 1",
            "special_requests": "Gluten-free pasta",
            "status": "**READY**"
        }
    }
    id_counter = 3  # Start from 3 since we have 3 orders in the dict
    def __init__(self):
        pass

    def add_new_order(self, table_num, items, special_requests):
        try:
            table_num = int(table_num)
        except ValueError:
            print(f"[ERROR] OrderManagement add_new_order table number not int")
            return None
        
        order_id = OrderManagement.id_counter + 1
        OrderManagement.id_counter += 1
        
        OrderManagement.orders_dict[order_id] = {
            "table_num": table_num,
            "items": items,
            "special_requests": special_requests,
            "status": "New"    # New-> In Progress-> Ready
        }
        return order_id

    def retrieve_current_orders(self):
        return OrderManagement.orders_dict

    def update_order_progress(self, order_id, new_progress):
        if order_id in self.orders_dict:
            OrderManagement.orders_dict[order_id]["status"] = new_progress
            return True
        else:   
            return False

    def delete_order(self, order_id):
        if order_id in self.orders_dict:
            del OrderManagement.orders_dict[order_id]
            return True
        else:
            return False

class OrderFacade:
    def __init__(self):
        self.order_management = OrderManagement()

    def add_order(self, table_num, items, special_requests):
        return self.order_management.add_new_order(table_num, items, special_requests)

    def get_orders(self):
        return self.order_management.retrieve_current_orders()

    def update_order(self, order_id, new_status):
        return self.order_management.update_order_progress(order_id, new_status)

    def delete_order(self, order_id):
        return self.order_management.delete_order(order_id)

class Server:
    def __init__(self, addr):
        self.addr = addr
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.client_sockets = []
        self.message_sender = MessageSender()

    def start(self):
        self.server_socket.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            try:
                conn, addr = self.server_socket.accept()
                client_handler = ClientHandler(conn, addr, self)
                thread = threading.Thread(target=client_handler.handle)
                thread.start()
                self.client_sockets.append(conn)
            except socket.error as e:
                print(f"[ERROR] Error accepting client connections: {e}")
                break

    def client_disconnect(self, conn, addr):
        try:
            self.client_sockets.remove(conn)
        except ValueError as e:
            print(f"[ERROR] Error removing client socket from list: {e}")

class ClientHandler:
    def __init__(self, conn, addr, server):
        self.conn = conn
        self.addr = addr
        self.server = server
        self.connected = True
        self.facade = OrderFacade()  # Use the facade
        self.message_sender = MessageSender(conn)

    def receive(self):
        msg = self.message_sender.recv_message()
        if msg == False:
            print(f"[ERROR] Client connection lost {self.addr}")
            self.connected = False
            self.server.client_disconnect(self.conn, self.addr)
        if msg:
            if msg == DISCONNECT_MESSAGE:   
                self.connected = False
                self.server.client_disconnect(self.conn, self.addr)
                print(f"[DISCONNECT] {self.addr} disconnected")
            else: 
                return msg
            
        return False
            
    def handle(self):
        print(f"[NEW CONNECTION] {self.addr} connected")
        while self.connected:
            try:
                msg = self.receive()
                if msg == False:
                    break
                self.message_options(msg)                

            except (socket.error, ConnectionResetError) as e:
                print(f"[ERROR] Client connection lost {self.addr}: {e}")
                self.connected = False
                self.server.client_disconnect(self.conn, self.addr)

            except Exception as e:
                print(f"[ERROR] Unexpected error in client handling: {e}")
                self.connected = False
                self.server.client_disconnect(self.conn, self.addr)

        self.conn.close()
        print(f"[ACTIVE CONNECTIONS] After Client Disconnect {threading.active_count() - 1}")

    def message_options(self, msg):
        if msg == "!1":  # Retrieve current orders
            current_orders = self.facade.get_orders()
            self.message_sender.send_message(self.conn, json.dumps(current_orders))
        elif msg == "!2":  # Add new order
            json_message = self.receive()
            data = json.loads(json_message)
            table_num = data["table_num"]
            items = data["items"]
            special_requests = data["special_requests"]
            order_id = self.facade.add_order(table_num, items, special_requests)
            self.message_sender.send_message(self.conn, f"T:{order_id}")
        elif msg == "!3":  # Delete order
            json_message = self.receive()
            data = json.loads(json_message)
            order_id = int(data["order_id"])
            deleted = self.facade.delete_order(order_id)
            if deleted:
                self.message_sender.send_message(self.conn, f"T:Order ID {order_id} deleted successfully.")
            else:
                self.message_sender.send_message(self.conn, f"F:Order ID {order_id} not found.")
        elif msg == "!4":  # Update order progress
            json_message = self.receive()
            data = json.loads(json_message)
            order_id = int(data["order_id"])
            new_progress = data["status"]
            updated = self.facade.update_order(order_id, new_progress)
            if updated:
                self.message_sender.send_message(self.conn, f"T:Order ID {order_id} updated to {new_progress}.")
            else:
                self.message_sender.send_message(self.conn, f"F:Order ID {order_id} not found.")
        else:
            print(f"[{self.addr}] not 4 options. msg: {msg}")

if __name__ == "__main__":
    print("[STARTING] server is starting...")
    server = Server(ADDR)
    server.start()

# Error handling
# client leaving handling
# ending thread ond disconnecting
