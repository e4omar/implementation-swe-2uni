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
    def __init__(self):
        self.orders_dict = {}
        self.id_counter = 0  

    def add_new_order(self, table_num, items, special_requests):
        try:
            table_num = int(table_num)
        except ValueError:
            print(f"[ERROR] OrderManagement add_new_order table number not int")
            return None
        
        order_id = self.id_counter + 1
        self.id_counter += 1
        
        self.orders_dict[order_id] = {
            'table_num': table_num,
            'items': items,
            'special_req': special_requests,
            'status': 'New'    # New-> In Progress-> Ready
        }
        return order_id

    def retrieve_current_orders(self):
        return self.orders_dict

    def update_order_progress(self, order_id, new_progress):
        if order_id in self.orders_dict:
            self.orders_dict[order_id]['status'] = new_progress

    def delete_order(self, order_id):
        if order_id in self.orders_dict:
            del self.orders_dict[order_id]




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
        self.order_management = OrderManagement()
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
                print(f"[{self.addr}] individual msg: {msg}")
                #for tetsing 
                if msg == "Omar":
                    self.message_sender.send_message(self.conn, "Order received")

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
        if msg == "!1": # Both: Retrieve current orders
            current_orders = self.order_management.retrieve_current_orders()
            self.message_sender.send_message(self.conn, json.dumps(current_orders))
        elif msg == "!2": # Waitstaff: Add new order
            json_message = self.receive()
            data = json.loads(json_message)
            table_num = data['table_num']
            items = data['items']
            special_requests = data['special_requests']
            order_id = self.order_management.add_new_order(table_num, items, special_requests)
            self.message_sender.send_message(self.conn, f"Order ID {order_id} added successfully.")
            print(F"[Current orders]: {self.order_management.retrieve_current_orders()}")
        elif msg == "!3": # Waitstaff: Delete order
            json_message = self.receive()
            data = json.loads(json_message)
            order_id = int(data['order_id'])
            self.order_management.delete_order(order_id)
            self.message_sender.send_message(self.conn, f"Order ID {order_id} deleted successfully.")
        elif msg == "!4": # Kitchen: Update order progress
            json_message = self.receive()
            data = json.loads(json_message)
            order_id = int(data['order_id'])
            new_progress = data['status']
            self.order_management.update_order_progress(order_id, new_progress)
            self.message_sender.send_message(self.conn, f"Order ID {order_id} updated to {new_progress}.")


if __name__ == "__main__":
    print("[STARTING] server is starting...")
    server = Server(ADDR)
    server.start()


#Error handling
#client leaving handling
#ending thread ond disconnecting
