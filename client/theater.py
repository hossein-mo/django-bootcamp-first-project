import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, clear_screen, Response, Page
from tcp_client import TCPClient


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
    
    def send_buy_request(self, seat_number):
        client=TCPClient()
        request = create_request(type="order", subtype='reserve', data={'show_id':self.show.id, 'seat_number':seat_number})
        client.send(request)
        response = client.recive()
        response = Response(**response)
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()


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

    def buy_process(self, reserved_seats):
        while True:
            print(f'\nPress Zero to go back...')
            seat_number = input(f'\nEnter unreserved seat number:')
            self.handle_input(seat_number)
            try:
                if int(seat_number) not in range(1, len(self.theater_capacity)+1):
                    print("Invalid number!")
                elif int(seat_number) in reserved_seats:
                    print("This seat is reserved!")
                else:
                    self.send_buy_request(seat_number)
                    break
            except ValueError:
                print("Invalid value!")


    def display(self):
        clear_screen()
        client=TCPClient()
        request = create_request(type="report", subtype='showseats', data={'show_id':self.show_id})
        client.send(request)
        response = client.recive()
        response = Response(**response)
        if response is not None:
            if response.status:
                reserved_seats = response.data['reserved_seats']
                self.display_seats(reserved_seats)
                self.buy_process()
            else:
                print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")
        else:
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")


class TheaterListPage(Page):

    def display(self):
        pass