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
        # while True:
        #     user_input = input("Enter your choice: ")
        #     if user_input == "0":
        #         self.navigate_back()
        #     else:
        #         self.current_page.handle_input(user_input, self)
    
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
