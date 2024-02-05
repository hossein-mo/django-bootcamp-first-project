import socket
import threading
import os
import sys
import pickle
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import models.models as models
import controllers.handlers.user_handlers as uHandlers
import controllers.exceptions as cExcept
import models.model_exceptions as mExcept
from controllers.response import Request, Response
from models.base_models import UserRole


class TCPServer:
    HOST: str
    PORT: int
    BUFSIZE: int

    def __init__(self, host: str, port: int, bufsize: int) -> None:
        self.HOST = host
        self.PORT = port
        self.BUFSIZE = bufsize

    def user_authentication(self, request):
        data = request["data"]
        print(request)
        if request["type"] == "login":
            login_handler = uHandlers.UserLoginHandler()
            user = login_handler.handle(data)

        elif request["type"] == "signup":
            data["role"] = UserRole.USER
            signup_handler = uHandlers.NewUserInfoHandler()
            password_policy = uHandlers.PasswordPolicyHandler()
            create_user = uHandlers.CreateUserHandler()
            signup_handler.set_next(password_policy).set_next(create_user)
            user = signup_handler.handle(data)
        else:
            raise cExcept.AuthenticationFaild
        return user

    def client_authenticatation_handler(self, client_socket: socket.socket):
        request = client_socket.recv(self.BUFSIZE)
        print(sys.getsizeof(request))
        request = pickle.loads(request)
        print(request)
        try:
            user = self.user_authentication(request)
            response = Response(True, "user", "Authentication succesfull.", {})
        except mExcept.WrongCredentials:
            print("Invalid Credentials")
            response = Response(
                False, "user", "Wrong credential, please try again!", {}
            )
        except cExcept.InvalidUserInfo as err:
            print(err)
            response = Response(False, "user", "Invalid user info!", {})
        except cExcept.PasswordPolicyNotPassed as err:
            print(err)
            response = Response(False, "user", "Invalid password!", {})
        except mExcept.DuplicatedEntry as err:
            print(err)
            response = Response(False, "user", "Username or email are in use!", {})
        except cExcept.AuthenticationFaild as err:
            print(err)
            response = Response(
                False, "user", "User authentication faild. Please login.", {}
            )
        else:
            print(user.id)
        finally:
            response = pickle.dumps(response)
            client_socket.sendall(response)
            self.user_request_handler(client_socket)
        client_socket.close()

    def user_request_handler(self, client_socket: socket.socket):
        pass

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
                target=self.client_authenticatation_handler, args=(client,)
            )
            client_handler.start()


if __name__ == "__main__":
    server = TCPServer("localhost", 8888, 4096)
    server.start_server()
