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



class Server:
    def __init__(self, addr):
        self.addr = addr
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.client_sockets = []
        self.msg_history = []
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
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
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
        self.message_sender = MessageSender(conn)


    def handle(self):
        print(f"[NEW CONNECTION] {self.addr} connected")
        connected = True
        while connected:
            try:
                msg = self.message_sender.recv_message()
                if msg == False:
                    print(f"[ERROR] Client connection lost {self.addr}: {e}")
                    connected = False
                    self.server.client_disconnect(self.conn, self.addr)
                if msg:
                    if msg == DISCONNECT_MESSAGE:   
                        connected = False
                        self.server.client_disconnect(self.conn, self.addr)
                        print(f"[DISCONNECT] {self.addr} disconnected")
                    else: 
                        print(f"[{self.addr}] individual msg: {msg}")

            except (socket.error, ConnectionResetError) as e:
                print(f"[ERROR] Client connection lost {self.addr}: {e}")
                connected = False
                self.server.client_disconnect(self.conn, self.addr)

            except Exception as e:
                print(f"[ERROR] Unexpected error in client handling: {e}")
                connected = False
                self.server.client_disconnect(self.conn, self.addr)

        self.conn.close()
        print(f"[ACTIVE CONNECTIONS] After Client Disconnect {threading.active_count() - 1}")



if __name__ == "__main__":
    print("[STARTING] server is starting...")
    server = Server(ADDR)
    server.start()


#Error handling
#client leaving handling
#ending thread ond disconnecting