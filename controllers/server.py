import socket
import threading
import os
import sys
import pickle
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.utils import create_response
from controllers.systems import UserManagement


class TCPServer:
    HOST: str
    PORT: int
    SIZE_BYTES_LENGTH: int

    def __init__(self, host: str, port: int, size_length: int = 4) -> None:
        self.HOST = host
        self.PORT = port
        self.SIZE_BYTES_LENGTH = size_length

    @staticmethod
    def socket_recive(client_socket: socket.socket, size_length: int):
        size = client_socket.recv(size_length)
        size = int.from_bytes(size, byteorder="big")
        request = b""
        while len(request) < size:
            chunk = client_socket.recv(size - len(request))
            if not chunk:
                break
            request += chunk
        if request:
            return pickle.loads(request)
        else:
            return None

    @staticmethod
    def socket_send(client_socket: socket.socket, response: dict, size_length: int):
        response = pickle.dumps(response)
        size_bytes = len(response).to_bytes(size_length, byteorder="big")
        client_socket.sendall(size_bytes + response)

    @staticmethod
    def client_handler(client_socket: socket.socket, size_length: int):
        request = TCPServer.socket_recive(client_socket, size_length)
        if "type" in request:
            response, user = UserManagement.client_authenticatation(request)
        else:
            user = None
            response = create_response(False, "user", "Please login.")
        TCPServer.socket_send(client_socket, response, size_length)
        if user:
            while True:
                request = TCPServer.socket_recive(client_socket, size_length)
                if not request:
                    break
                if request["type"] == "profile":
                    if request["subtype"] == "update":
                        response, user = UserManagement.edit_profile(
                            request["data"], user
                        )
                    if request["subtype"] == "changepass":
                        response, user = UserManagement.change_password(
                            request["data"], user
                        )
                TCPServer.socket_send(client_socket, response, size_length)

        client_socket.close()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(5)
        print(f"Server listening on port {self.PORT}")
        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(
                target=TCPServer.client_handler, args=(client, self.SIZE_BYTES_LENGTH)
            )
            client_handler.start()


if __name__ == "__main__":
    server = TCPServer("localhost", 8000)
    server.start_server()
