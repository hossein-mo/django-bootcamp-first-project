import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, clear_screen, Response, Page
from tcp_client import TCPClient

class Order:
    def __init__(self, id, showtime_id, seat_number, discount, create_date, cancel_date = None):
        self.id = id
        self.showtime_id = showtime_id
        self.seat_number = seat_number
        self.discount = discount
        self.create_date = create_date
        self.cancel_date = cancel_date


class UserOrdersPage(Page):
    order_list = []

    def display(self):
        clear_screen()
        if len(self.order_list) == 0:
            client=TCPClient()
            request = create_request(type="report", subtype='getorders')
            client.send(request)
            response = client.recive()
            response = Response(**response)
            if response is not None:
                if response.status:
                    UserOrdersPage.order_list = response.data
                    for i in range(self.order_list):
                        order = Order(**self.order_list[i])
                        print(f'{i+1}. showtime: {order.showtime_id}, seat number: {order.seat_number}', end='')
                        if order.cancel_date is not None:
                            print(f', cancel date: {order.cancel_date}' if order.cancel_date is not None else '')
                    print(f'\n1. cancel ticket\n press any else key to go back...')
                    self.handle_input(input())
                else:
                    print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
            else:
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            for i in range(self.order_list):
                order = Order(**self.order_list[i])
                print(f'{i+1}. showtime: {order.showtime_id}, seat number: {order.seat_number}', end='')
                if order.cancel_date is not None:
                    print(f', cancel date: {order.cancel_date}' if order.cancel_date is not None else '')
            print(f'\n1. cancel ticket\n press any else key to go back...')
            self.handle_input(input())
        
    def handle_input(self, user_input):
        if user_input == "1":
            self.app.navigate_to_page(CancelOrderPage(self.app, self.order_list))
        else:
            self.app.navigate_back()


class CancelOrderPage(Page):
    def __init__(self, app, order_list):
        super().__init__(app)
        self.order_list = order_list

    def display(self):
        clear_screen()
        for i in range(len(self.order_list)):
            order = Order(**self.order_list[i])
            print(f'{i+1}. showtime: {order.showtime_id}, seat number: {order.seat_number}', end='')
            if order.cancel_date is not None:
                print(f', cancel date: {order.cancel_date}' if order.cancel_date is not None else '')
        print(f'\nPress Zero to go back...')
        while True:
            order_number = input("Enter showtime number:")
            self.handle_input(order_number)
            try:
                if int(order_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    id = self.order_list[order_number-1]['id']
                    break
            except ValueError:
                print("Invalid value!")
        client=TCPClient()
        request = create_request(type="order", subtype='cancel', data={'order_id':id})
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()