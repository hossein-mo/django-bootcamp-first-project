import os

from tcp_client import TCPClient

def create_request(type: str, subtype: str = '', data: dict = {}) -> dict:
    """creates request dictionary

    Args:
        type (str): type of request
        subtype (str, optional): subtype of request. Defaults to ''.
        data (dict, optional): data . Defaults to {}.

    Returns:
        dict: request dictionary to send with socket
    """    
    if subtype:
        return {"type": type, 'subtype': subtype, "data": data}
    else:
        return {"type": type, "data": data}
    
def clear_screen():
    """clear terminal screen
    """    
    os.system('cls' if os.name == 'nt' else 'clear')

def connect_server(request:dict):
    response = None
    try:
        client = TCPClient()
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
    # except TimeoutError:
    #     print("connection error! try again...")
    except OSError:
        print("no connection! try again...")
    except Exception:
        print("We had a problem processing your request. Please try again later.")
    return response

    
class Response:
    def __init__(self, status, type, message, data):
        self.status = status
        self.type = type
        self.message = message
        self.data = data

class CinemaReservationApp:
    def __init__(self):
        self.current_page = None
        self.page_cache = []

    def navigate_to_page(self, page):
        if self.current_page:
            self.page_cache.append(self.current_page)
        self.current_page = page
        self.current_page.display()

    def navigate_back(self):
        if self.page_cache:
            self.current_page = self.page_cache.pop()
            self.current_page.display()
        else:
            print("Cannot navigate back. Already at the home page.")

    def start(self, home_page):
        self.navigate_to_page(home_page)
    
    def restart(self):
        TCPClient().close()
        self.current_page = self.page_cache[0]
        self.page_cache = []
        self.current_page.display()


from abc import ABC, abstractmethod
class Page(ABC):
    def __init__(self, app:CinemaReservationApp):
        self.app = app

    @abstractmethod
    def display(self):
        pass

    def handle_input(self, user_input):
        if user_input == "0":
            self.app.navigate_back()

class OutOfRangeError(Exception):
    def __init__(self, message="Input is not within the specified range."):
        self.message = message
        super().__init__(self.message)