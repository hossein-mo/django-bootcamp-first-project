import socket
import pickle
from utils.utils import create_response

class Request:
    def __init__(self, host='localhost', port=8000, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize

class Request:
    def __init__(self, host='localhost', port=8000, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize

    def send_socket_request(self, status, type, message, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        request = create_response(status, type, message, data)

        serialized_data = pickle.dumps(request)
        client_socket.sendall(serialized_data)

        response_data = client_socket.recv(self.bufsize)
        response = pickle.loads(response_data)

        print(response)

        if response["status"]:
            print(response["data"])
        else:
            print(response["message"])

        client_socket.close()

        return response


if __name__ == "__main__":
    my_instance = Request()
    response = my_instance.send_socket_request(
        status =True,
        type="signup",
        message="This is a message from the client",
        data={"username": "Zahra2", "password": "Az@#1234567", "email": "Zahra@ebi.co", "phone_number":"", "birth_date": "1950-01-20"}
    
        
    )