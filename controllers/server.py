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
    BUFSIZE: int

    def __init__(self, host: str, port: int, bufsize: int) -> None:
        self.HOST = host
        self.PORT = port
        self.BUFSIZE = bufsize

    @staticmethod
    def client_handler(client_socket: socket.socket, bufsize):
        request = client_socket.recv(bufsize)
        request = pickle.loads(request)
        response, user = UserManagement.client_authenticatation(client_socket, bufsize)
        client_socket.sendall(pickle.dumps(response))
        if user:
            while True:
                request = client_socket.recv(bufsize)
                request = pickle.loads(request)
                if not request:
                    break
                if request["type"] == "profile":
                    if request["subtype"] == "update":
                        response, user = UserManagement.edit_profile(
                            request["data"], user
                        )
                    if request["subtype"] == "changepass":
                        response.user = UserManagement.change_password(
                            request["data"], user
                        )
                client_socket.sendall(pickle.dumps(response))

        client_socket.close()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(5)
        print(f"Server listening on port {self.PORT}")
        while True:
            client, addr = server.accept()
            print(type(addr[0]), type(addr[1]))
            print(client.__class__)
            client_handler = threading.Thread(
                target=TCPServer.client_handler, args=(client, self.BUFSIZE)
            )
            client_handler.start()


if __name__ == "__main__":
    server = TCPServer("localhost", 8001, 4096)
    server.start_server()
