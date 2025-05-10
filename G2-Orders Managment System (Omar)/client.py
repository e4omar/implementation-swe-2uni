import json
import os
import socket
import threading

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
            sender = Sender(self)
            receiver = Receiver(self)

            send_thread = threading.Thread(target=sender.sending_thread)
            recv_thread = threading.Thread(target=receiver.receiving_thread)

            send_thread.start()
            recv_thread.start()

            send_thread.join()
            recv_thread.join()

            self.disconnect()


class Sender:
    def __init__(self, client):
        self.client = client
        self.message_sender = MessageSender(self.client.client_socket)

    def send(self, msg):
        success = self.message_sender.send_message(msg)
        if msg == DISCONNECT_MESSAGE:
            self.client.disconnect()
        if not success:
            print("[ERROR] Failed to send message.")
            print("[ERROR] Closing client connection...")
            self.client.disconnect()

    def sending_thread(self):
        print("send function started")
        while self.client.online:
            try:
                msg = str(input("SEND A MSG: "))
                self.send(msg)
                
                # Handle message options
                if msg == "!1":  # Retrieve current orders
                    #self.send(msg)
                    pass
                elif msg == "!2":  # Add new order
                    table_num = input("Enter table number: ")
                    items = input("Enter items: ")
                    special_requests = input("Enter special requests: ")
                    order_data = json.dumps({
                        'table_num': table_num,
                        'items': items,
                        'special_requests': special_requests
                    })
                    self.send(order_data)
                elif msg == "!3":  # Delete order
                    order_id = input("Enter order ID to delete: ")
                    delete_data = json.dumps({'order_id': order_id})
                    self.send(delete_data)
                elif msg == "!4":  # Update order progress
                    order_id = input("Enter order ID to update: ")
                    status = input("Enter new status: ")
                    update_data = json.dumps({'order_id': order_id, 'status': status})
                    self.send(update_data)

            except Exception as e:
                print(f"[ERROR] Unexpected error in sending_thread function: {e}")
                self.client.disconnect()
                break

        print("send function terminated")


class Receiver:
    def __init__(self, client):
        self.client = client
        self.message_sender = MessageSender(self.client.client_socket)

    def receive(self):
        full_msg = self.message_sender.recv_message()
        if full_msg:
            if full_msg == DISCONNECT_MESSAGE:
                self.client.disconnect()
            elif full_msg is False:
                self.client.disconnect()
            else:
                print(f"RECEIVED: {full_msg}")

        return full_msg

    def receiving_thread(self):
        print("recv function started")
        while self.client.online:
            full_msg = self.message_sender.recv_message()
            print(f"RECEIVED: {full_msg}")

        print("recv function terminated")


if __name__ == "__main__":
    client = Client(ADDR)
    client.start()



if __name__ == "__main__":
    client = Client(ADDR)
    client.start()
