from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from theater import RatingTheaterPage
from utils import create_request, clear_screen, Page, connect_server

class Order:
    def __init__(self, id, movie_name, theater_name, show_start_date, seat_number, price, discount, buy_date, cancel_date=None):
        self.id = id
        self.movie_name = movie_name
        self.theater_name = theater_name
        self.seat_number = seat_number
        self.price = price
        self.discount = discount
        self.show_start_date = show_start_date
        self.buy_date = buy_date
        self.cancel_date = cancel_date


class UserOrdersPage(Page):
    order_list = []
    firts_user_input = ''

    def display_list(self):
        for i in range(len(self.order_list)):
            order = Order(**self.order_list[i])
            print(f'{i+1}. movie: {order.movie_name}, theater: {order.theater_name},\
                    date: {order.show_start_date}, seat number: {order.seat_number},\
                        price: {order.price}, discount: {order.discount}', end='')
            if order.cancel_date is not None:
                print(
                    f', cancel date: {order.cancel_date}' if order.cancel_date is not None else '')

    def get_user_input(self):
        while True:
            print(f'\n1. cancel ticket\n2. Rate a theater\npress any else key to go back...')
            self.handle_input(input())
            if self.firts_user_input == '2':
                break
        while True:    
            self.handle_input(input('\nEnter an order ID to rate it\'s theater:'))

    def display(self):
        clear_screen()
        print(f'**** Your Orders ****\n')   
        if self.order_list:
            request = create_request(type="report", subtype='getorders')
            response = connect_server(request)
            if response is not None:
                if response.status:
                    UserOrdersPage.order_list = response.data
                    if not self.order_list:
                        print('No order yet!?\n')
                        print(f'\npress any else key to go back...')
                        self.handle_input('0')
                    else:
                        self.display_list()
                        self.get_user_input()
                else:
                    print(response.message)
                    input("Press any key to go back... ")
                    self.handle_input("0")
            else:
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input('0')
        else:
            self.display_list()
            self.get_user_input()

    def handle_input(self, user_input):
        try:
            if user_input == '0':
                self.app.navigate_back()
            elif self.firts_user_input and int(user_input) in range(1, len(self.order_list)+1):
                self.app.navigate_to_page(RatingTheaterPage(self.app, int(user_input)))
            if self.order_list and user_input == '1':
                now = datetime.now()
                date_format = '%Y-%m-%d %H:%M:%S.%f'
                self.app.navigate_to_page(CancelOrderPage(self.app,
                                            list(filter(lambda x: 
                                                datetime.strptime(x['show_start_date'], date_format) > now and x['cancel_date'] == None, self.order_list))))
            elif self.order_list and user_input == '2':
                self.firts_user_input = '2'
            else:
                raise ValueError()
        except ValueError:
            print('Invalid input...')


class CancelOrderPage(Page):
    def __init__(self, app, order_list):
        super().__init__(app)
        self.order_list = order_list

    def display(self):
        clear_screen()
        print(f'**** Cancel Order ****\n')   
        for i in range(len(self.order_list)):
            order = Order(**self.order_list[i])
            print(f'{i+1}. movie: {order.movie_name}, theater: {order.theater_name},\
                        date: {order.show_start_date}, seat number: {order.seat_number},\
                            price: {order.price}, discount: {order.discount}')
        print(f'\n>>> Press Zero to go back <<<')
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
        request = create_request(
            type="order", subtype='cancel', data={'order_id': id})
        response = connect_server(request)
        if response is not None:
            print(response.message)
            input("Press any key to go back... ")
            self.handle_input("0")
        else:
            print("Connection Error! try again...")
            self.display()
