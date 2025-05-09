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

    def start(self):
        if self.online:
            sender = Sender(self)
            receiver = Receiver(self)

            send_thread = threading.Thread(target=sender.send_messages)
            recv_thread = threading.Thread(target=receiver.receive_messages)

            send_thread.start()
            recv_thread.start()

            send_thread.join()
            recv_thread.join()

            self.disconnect()


class Sender:
    def __init__(self, client):
        self.client = client

    def send(self, msg):
        try:
            checksum = calculate_checksum(msg)
            checksum_str = str(checksum).encode(FORMAT)
            checksum_str += b' ' * (HEADER - len(checksum_str))

            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length)) #Padding to ensure HEADER size

            self.client.client_socket.send(send_length)
            self.client.client_socket.send(message)
            self.client.client_socket.send(checksum_str)
        except (socket.error, ConnectionResetError) as e:
            print(f"[ERROR] Error sending message: {e}")
            self.client.online = False
        except Exception as e:
            print(f"[ERROR] Unexpected error in send function: {e}")
            self.client.online = False

    def send_messages(self):
        print("send function started")
        while self.client.online:
            try:
                msg = str(input("SEND A MSG: "))
                self.send(msg)
                if msg == DISCONNECT_MESSAGE:
                    self.client.online = False
            except Exception as e:
                print(f"[ERROR] Unexpected error in send_messages function: {e}")
                self.client.online = False

        print("send function terminated")

class Receiver:
    def __init__(self, client):
        self.client = client

    def receive(self):
        full_msg = ''
        try:
            while True:
                part = self.client.client_socket.recv(1024).decode(FORMAT)
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
            self.client.online = False
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error in receive function: {e}")
            self.client.online = False
            return None

    def receive_messages(self):
        print("recv function started")
        while self.client.online:
            full_msg = self.receive()
            if full_msg:
                print("[RECEIVED] ", full_msg)

        print("recv function terminated")


if __name__ == "__main__":
    client = Client(ADDR)
    client.start()
