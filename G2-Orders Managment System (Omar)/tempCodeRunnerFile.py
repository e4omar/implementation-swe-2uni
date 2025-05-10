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
