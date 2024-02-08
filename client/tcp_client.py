import socket
import pickle


class TCPClient:
    host: str
    port: int
    size_bytes_length: int
    client_socket: socket.socket

    def __init__(self, host: str, port: int, size_length: int = 4) -> None:
        self.host = host
        self.port = port
        self.size_bytes_length = size_length
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def recive(self) -> dict | None:
        size = self.client_socket.recv(self.size_bytes_length)
        size = int.from_bytes(size, byteorder="big")
        response=b''
        while len(response) < size:
            chunk = self.client_socket.recv(size - len(response))
            if not chunk:
                break
            response += chunk
        if response:
            return pickle.loads(response)
        else:
            return None

    def send(self, request: dict) -> None:
        request = pickle.dumps(request)
        size_bytes = len(request).to_bytes(self.size_bytes_length, byteorder="big")
        self.client_socket.sendall(size_bytes + request)

    def close(self):
        self.client_socket.close()