import socket
import threading
import pickle
from utils.utils import create_response
from utils.exceptions import DatabaseError, InvalidRequest
from controllers.systems import (
    OrderManagement,
    UserManagement,
    AccountManagement,
    CinemaManagement,
    Reports,
    Review,
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
        """create a server instance

        Args:
            host (str, optional): host addres of the server. Defaults to "localhost".
            port (int, optional): port addres to listen. Defaults to 8000.
            size_length (int, optional): size header of the socket packages. Defaults to 4.
        """        
        self.HOST = host
        self.PORT = port
        self.SIZE_BYTES_LENGTH = size_length

    @staticmethod
    def socket_recive(client_socket: socket.socket, size_length: int) -> dict | None:
        """recive through socket

        Args:
            client_socket (socket.socket): socket instance
            size_length (int): size header of the socket packages

        Returns:
            dict | None: return the client request
        """        
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
    def socket_send(client_socket: socket.socket, response: dict, size_length: int) -> None:
        """send through socket

        Args:
            client_socket (socket.socket): client socket
            response (dict): response to the client
            size_length (int): size header of the socket packages
        """        
        response = pickle.dumps(response)
        size_bytes = len(response).to_bytes(size_length, byteorder="big")
        client_socket.sendall(size_bytes + response)

    @staticmethod
    def client_handler(client_socket: socket.socket, size_length: int) -> None:
        """handles client requests, server gateway for each client

        Args:
            client_socket (socket.socket): client socket
            size_length (int): size header of the socket packages
        """        
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
                        response = UserManagement.process(user, request)
                    elif request["type"] == "account":
                        response = AccountManagement.process(user, request)
                    elif request["type"] == "management":
                        response = CinemaManagement.process(user, request)
                    elif request["type"] == "report":
                        response = Reports.process(user, request)
                    elif request["type"] == "report":
                        response = Reports.process(user, request)
                    elif request["type"] == "review":
                        response = Review.process(user, request)
                    elif request["type"] == "order":
                        response = OrderManagement.process(user, request)
                    else:
                        response = create_response(False, "user", "Invalid request.")
                except DatabaseError as err:
                    response = create_response(
                        False,
                        "user",
                        "We had a problem processing your request. Please try again later.",
                    )
                except (KeyError, TypeError, ValueError, InvalidRequest) as err:
                    # for debuging
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
        """starts the server, this will opens a thread for each client
        """        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(5)
        print(f"Server listening on {self.HOST}:{self.PORT}")
        TCPServer.loging.log_info(
            f"Server started and listening on {self.HOST}:{self.PORT}"
        )
        while True:
            client, addr = server.accept()
            TCPServer.loging.log_info(f"Connection accepted for {addr}")
            client_handler = threading.Thread(
                target=TCPServer.client_handler, args=(client, self.SIZE_BYTES_LENGTH)
            )
            client_handler.start()
