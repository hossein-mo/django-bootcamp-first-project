import socket
import pickle


class TCPClient:
    host: str
    port: int
    size_bytes_length: int
    client_socket: socket.socket

    _instance = None
    def __new__(cls, host: str = 'localhost', port: int = 8000, size_length: int = 4) -> 'TCPClient':
        
        """creates a socket connecton to specified host and port

        Args:
            host (str, optional): host adress. Defaults to 'localhost'.
            port (int, optional): port of the host. Defaults to 8000.
            size_length (int, optional): length of the size header. Defaults to 4.

        Returns:
            TCPClient: tcp client object
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.host = host
            cls._instance.port = port
            cls._instance.size_bytes_length = size_length
            cls._instance.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cls._instance.client_socket.connect((cls._instance.host, cls._instance.port))
        return cls._instance

    def recive(self) -> dict | None:
        """recive data from socket

        Returns:
            dict | None: recived data
        """        
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
        """send data through socket

        Args:
            request (dict): request 
        """        
        request = pickle.dumps(request)
        size_bytes = len(request).to_bytes(self.size_bytes_length, byteorder="big")
        self.client_socket.sendall(size_bytes + request)

    def close(self):
        """closes the socket connection
        """        
        self.client_socket.close()
        TCPClient._instance = None