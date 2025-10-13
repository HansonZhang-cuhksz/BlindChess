import socket
class Comm:
    def __init__(self, swap: bool = False):
        self.MY_IP = "127.0.0.1"
        self.MY_PORT = 12345
        self.OPPO_IP = "127.0.0.1"
        self.OPPO_PORT = 12346

        if swap:
            self.MY_IP, self.OPPO_IP = self.OPPO_IP, self.MY_IP
            self.MY_PORT, self.OPPO_PORT = self.OPPO_PORT, self.MY_PORT

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.MY_IP, self.MY_PORT))

    def send_message(self, message: str):
        self.s.sendto(message.encode(), (self.OPPO_IP, self.OPPO_PORT))

    def receive_message(self) -> str:
        data, addr = self.s.recvfrom(1024)
        message = data.decode()
        return message