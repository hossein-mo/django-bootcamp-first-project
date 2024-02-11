import socket
import threading
import os
import sys
import pickle
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.utils import create_response
from utils.exceptions import DatabaseError
from controllers.systems import (
    UserManagement,
    AccountManagement,
    CinemaManagement,
    Reports,
)
from loging.log import Log


class TCPServer:
    HOST: str
    PORT: int
    SIZE_BYTES_LENGTH: int
    loging: Log

    def __init__(
        self, host: str = "localhost", port: int = 8000, size_length: int = 4
    ) -> None:
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
        user = None
        request = TCPServer.socket_recive(client_socket, size_length)
        try:
            response, user = UserManagement.client_authenticatation(request)
        except DatabaseError as err:
            response = create_response(
                False,
                "user",
                "We had a problem processing your request. Please try again later.",
            )
        except (KeyError, TypeError) as err:
            response = create_response(False, "user", "Invalid request.")
        TCPServer.socket_send(client_socket, response, size_length)
        if user:
            while True:
                request = TCPServer.socket_recive(client_socket, size_length)
                try:
                    if not request:
                        break
                    if request["type"] == "profile":
                        if request["subtype"] == "update":
                            response, user = UserManagement.edit_profile(
                                user, request["data"]
                            )
                        elif request["subtype"] == "changepass":
                            response = UserManagement.change_password(
                                user, request["data"]
                            )
                        elif request["subtype"] == "changerole":
                            response = UserManagement.change_user_role(
                                user, request["data"]
                            )
                    elif request["type"] == "account":
                        if request["subtype"] == "add":
                            response = AccountManagement.add_account_user(
                                user, request["data"]
                            )
                        elif request["subtype"] == "list":
                            response = AccountManagement.get_user_accounts(user)
                    elif request["type"] == "management":
                        response = CinemaManagement.process(user, request)
                    elif request["type"] == "report":
                        response = Reports.process(user, request)
                    else:
                        response = create_response(False, "user", "Invalid request.")
                except DatabaseError as err:
                    response = create_response(
                        False,
                        "user",
                        "We had a problem processing your request. Please try again later.",
                    )
                except (KeyError, TypeError, ValueError) as err:
                    print(err)
                    response = create_response(False, "user", "Invalid request.")
                TCPServer.socket_send(client_socket, response, size_length)
            TCPServer.loging.log_action(
                f"User logged out. username: {user.username}, id: {user.id}"
            )
        addr = client_socket.getpeername()
        client_socket.close()
        TCPServer.loging.log_action(f"Connection closed for {addr}")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(5)
        print(f"Server listening on {self.HOST}:{self.PORT}")
        TCPServer.loging.log_action(
            f"Server started and listening on {self.HOST}:{self.PORT}"
        )
        while True:
            client, addr = server.accept()
            TCPServer.loging.log_action(f"Connection accepted for {addr}")
            client_handler = threading.Thread(
                target=TCPServer.client_handler, args=(client, self.SIZE_BYTES_LENGTH)
            )
            client_handler.start()
