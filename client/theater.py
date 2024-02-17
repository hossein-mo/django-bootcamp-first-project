import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from admin_access import AddTheaterPage
from utils import create_request, clear_screen, Page, connect_server


class Theater:
    def __init__(self, id, t_name, capacity, rate):
        self.id = id
        self.t_name = t_name
        self.capacity = capacity
        self.rate = rate


class TheaterSeatsPage(Page):
    def __init__(self, app, show_id:int, theater_capacity:int):
        super().__init__(app)
        self.show_id = show_id
        self.theater_capacity = theater_capacity
        self.reserved_seats = None
    
    def send_buy_request(self, seat_number):
        request = create_request(type='order', subtype='reserve', data={'show_id':self.show_id, 'seat_number':seat_number})
        response = connect_server(request)
        if response is not None:
            print(response.message)
            if response.status:
                data = response.data
                print(f'You has reserved seat number {data["seat_number"]} in showtime {self.show_id}')
            input('Press any key to go back... ')
            self.handle_input('0')
        else:
            print('Connection Error! try again...')
            self.buy_process()

    def display_seats(self, reserved_seats):
        column = self.theater_capacity//10
        last_row_column = self.theater_capacity % 10
        for i in range(0, 10):
            for j in range(1, column+1):
                seat_number = i*column+j
                print(f'{seat_number:3d}.[*]' if seat_number in reserved_seats else f'{seat_number:3d}.[ ]', end=' ')
            print()
        for j in range(1, last_row_column+1):
            seat_number = 10*column+j
            print(f'{seat_number:3d}.[*]' if seat_number in reserved_seats else f'{seat_number:3d}.[ ]', end='')

    def buy_process(self):
        print(f'\n>>> Press Zero to go back <<<')
        while True:
            seat_number = input(f'\nEnter unreserved seat number:')
            self.handle_input(seat_number)
            try:
                if int(seat_number) not in range(1, len(self.theater_capacity)+1):
                    print('Invalid number!')
                elif int(seat_number) in self.reserved_seats:
                    print('This seat is reserved!')
                else:
                    self.send_buy_request(seat_number)
                    break
            except ValueError:
                print('Invalid value!')


    def display(self):
        clear_screen()
        request = create_request(type='report', subtype='showseats', data={'show_id':self.show_id})
        response = connect_server(request)
        if response is not None:
            if response.status:
                self.reserved_seats = response.data['reserved_seats']
                self.display_seats()
                self.buy_process()
            else:
                print(response.message)
                input('Press any key to go back... ')
                self.handle_input('0')
        else:
            print('Connection Error! try again...')
            input('Press any key to go back... ')
            self.handle_input('0')


class TheaterListPage(Page):

    def handle_input(self, user_input):
        if user_input == "1":
            self.app.navigate_to_page(AddTheaterPage(self.app))
        else:
            self.app.navigate_back()

    def display(self):
        clear_screen()
        print(f'**** Theaters List ****\n')
        request = create_request(type="report", subtype='theaterlist')
        response = connect_server(request)
        if response is not None:
            if response.status:
                theater_list = response.data
                if not theater_list:
                    print('No account register yet!\n')
                else:
                    for i in range(len(theater_list)):
                        theater = Theater(**theater_list[i])
                        print(f'{i+1}. name: {theater.t_name} capacity: {theater.capacity} rate: {theater.rate}')
                print(f'1. add theater\npress any else key to go back...')
                self.handle_input(input())
            else:
                print(response.message)
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")


class RatingTheaterPage(Page):
    def __init__(self, app, theater_id):
        super().__init__(app)
        self.theater_id = theater_id

    def display(self):
        clear_screen()
        print(f'**** Rate a Theater ****\n')
        print(f'\n>>> Press Zero to go back <<<')
        while True:
            user_input = input('On a scale of 1 to 5, how would you rate this theater?')
            rate = self.handle_input(user_input)
            if rate:
                break
        request = create_request(type="review", subtype='theaterrate', data={'theater_id': id, 'rate': rate})
        response = connect_server(request)
        if response is not None:
            print(response.message)
            if response.status:
                input("Press any key to go back... ")
                self.handle_input("0")
            else:
                self.display()
        else:
            print("Connection Error! try again...")
            self.display()

    def handle_input(self, user_input):
        try:
            if user_input == "0":
                self.app.navigate_back()
            elif int(user_input) in range(1, 6):
                return int(user_input)
            else:
                raise ValueError()
        except ValueError:
                print('Invalid input...')
        return None