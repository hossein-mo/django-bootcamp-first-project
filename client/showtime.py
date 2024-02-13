import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, clear_screen, Response, Page
from tcp_client import TCPClient
from theater import Theater, TheaterSeatsPage


class Show:
    def __init__(self, id, movie_id, theater_id, start_date, end_date, price, movie, theater: Theater):
        self.id = id
        self.movie_id = movie_id
        self.theater_id = theater_id
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.movie = movie
        self.theater = theater


class ShowsPage(Page):
    show_list = []

    def display_list(self):
        for i in range(self.show_list):
            show = Show(**self.order_show_listlist[i])
            show.movie = Movie(**show.movie)
            show.theater = Theater(**show.theater)
            print(f'{i+1}. movie: {show.movie.m_name}, {show.movie.duration} minutes, +{show.movie.age_rating},\
                {show.movie.screening_number} screening(s), rate = {show.movie.rate}\n\
                theater: {show.theater.t_name}, rate = {show.theater.rate}\n\
                date: {show.start_date}')
    
    def buy_process(self):
        while True:
            print(f'\nPress Zero to go back...')
            ticket_number = input(f'\n*** buy ticket ***\n Enter show number:')
            self.handle_input(ticket_number)
            try:
                if int(ticket_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    selected_show = self.show_list[ticket_number-1]
                    self.app.navigate_to_page((TheaterSeatsPage(self.app, selected_show)))
                    break
            except ValueError:
                print("Invalid value!")
        

    def display(self):
        clear_screen()
        if len(self.show_list) == 0:
            client=TCPClient()
            request = create_request(type="report", subtype='showlist')
            client.send(request)
            response = client.recive()
            response = Response(**response)
            if response is not None:
                if response.status:
                    ShowsPage.show_list = response.data
                    self.display_list()
                    self.buy_process()
                else:
                    print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
            else:
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            self.display_list()
            self.buy_process()