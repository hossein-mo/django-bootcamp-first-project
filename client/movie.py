import os
import sys
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from admin_access import AddMoviePage
from utils import create_request, clear_screen, Page, connect_server


class Movie:
    def __init__(self, id, m_name, duration, age_rating, screening_number, rate):
        self.id = id
        self.m_name = m_name
        self.duration = duration
        self.age_rating = age_rating
        self.screening_number = screening_number
        self.rate = rate


class Comment:
    def __init__(self, id, username, m_name, movie_id, parent_id, text, created_at, depth):
        self.id = id
        self.user_name = username
        self.movie_id = movie_id
        self.m_name = m_name
        self.parent_id = parent_id
        self.text = text
        self.created_at = created_at
        self.depth = depth


class User:
    def __init__(self, username, email, birth_date, phone_number, subs:str, subs_expires_in, balance, role):
        self.username = username
        self.email = email
        self.birth_date = birth_date
        self.phone = phone_number
        self.subscription = subs
        self.subscription_rest_days = subs_expires_in
        self.balance = balance
        self.role = role


class MovieListPage(Page):

    def __init__(self, app, user: User):
        super().__init__(app)
        self.user = user
        self.movie_list : List[Movie] = []
        self.firts_user_input = ''


    def display_movie_list(self):
        for i in range(len(self.movie_list)):
            print(f'{i+1}. {self.movie_list[i].m_name} (+{self.movie_list[i].age_rating}),\
                    {self.movie_list[i].duration} minutes\n{self.movie_list[i].screening_number} screenings,\
                        rate = {self.movie_list[i].rate}')
            

    def display(self):
        clear_screen()
        print(f'**** Movies List ****\n')  
        if not self.movie_list:
            request = create_request(type="report", subtype="movielist")
            response = connect_server(request)
            if response is not None:
                if response.status:
                    self.movie_list = list(map(lambda x: Movie(**x), response.data))
                    self.display_movie_list()
                    print(f'\n>>> Press Zero to go back <<<\n')
                    while True:
                        print('1. Rate\n2. Comments')
                        if self.user.role == 'admin' or self.user.role == 'staff':
                            print('3. Add movie')
                        self.firts_user_input = ''
                        self.handle_input(input())
                else:
                    print(response.message)
                    input("Press any key to go back... ")
                    self.handle_input("0")
            else:
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            self.display_movie_list()
            while True:
                print("\nPress Zero to go back...\n")
                print("1. Rate\n2. Comments")
                self.firts_user_input = ''
                self.handle_input(input())


    def handle_input(self, user_input):
        try:
            if user_input == "0":
                self.app.navigate_back()
            elif user_input == "1" and not self.firts_user_input:
                self.firts_user_input = "1"
                while True:
                    self.handle_input(input('\nEnter a movie ID to rate:\n'))
            elif user_input == "2" and not self.firts_user_input:
                self.firts_user_input = "2"
                while True:
                    self.handle_input(input('\nEnter a movie ID to view it\'s comments:\n'))
            elif user_input == "3" and not self.firts_user_input:
                self.app.navigate_to_page(AddMoviePage(self.app))
            elif int(user_input) in range(1, len(self.movie_list)+1):
                if self.firts_user_input == "1":
                    self.app.navigate_to_page(RatingMoviePage(self.app, self.movie_list[int(user_input)-1].id))
                else:
                    self.app.navigate_to_page(CommentListPage(self.app, self.movie_list[int(user_input)-1].id))
            else:
                raise ValueError()
        except ValueError:
                print('Invalid id!')


class RatingMoviePage(Page):
    def __init__(self, app, movie_id):
        super().__init__(app)
        self.movie_id = movie_id

    def display(self):
        clear_screen()
        print(f'**** Rate Movie ****\n')  
        print('\n>>> Press Zero to go back <<<\n')
        while True:
            user_input = input('On a scale of 1 to 5, how would you rate this movie?')
            rate = self.handle_input(user_input)
            if rate:
                break
        request = create_request(type="review", subtype='movierate', data={'movie_id': id, 'rate': rate})
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


class CommentListPage(Page):

    def __init__(self, app, movie_id):
        super().__init__(app)
        self.movie_id = movie_id
        self.comment_list: List[Comment] = []
        self.comment_parent_id: int = None


    def display_list(self):
        for i in range(len(self.comment_list)):
            tabs = '\t' * self.comment_list[i].depth
            print(f'{i+1}. {tabs}{self.comment_list[i].user_name}:\n{self.comment_list[i].text}\n\
                    {self.comment_list[i].created_at}')

    def display(self):
        clear_screen()
        print(f'**** Comment List ****\n')  
        request = create_request(
            type="report", subtype="getcomments", data={"movie_id": self.movie_id}
        )
        response = connect_server(request)
        if response is not None:
            if response.status:
                for comm in response.data['comments']: 
                    self.comment_list.append(Comment(**comm))
                self.display_list()
                print(f'\n>>> Press Zero to go back <<<')
                while True:
                    print('Enter comment ID to reply or comment the movie:')
                    request = self.handle_input(input())
                    if request:
                        response = connect_server(request)
                        if response is not None:
                            print(response.message)
                            if response.status:
                                break
                        else:
                            print("Connection Error! try again...")

            else:
                print(response.message)
                input("Press any key to go back... ")
                self.handle_input('0')
        else:
            print("Connection Error! Try again...")
            input("Press any key to go back... ")
            self.handle_input('0')


    def handle_input(self, user_input):
        request = None
        try:
            if user_input == "0":
                self.app.navigate_back()
            elif int(user_input) in range(1, len(self.comment_list)+1):
                comment_text = input(f'your reply to comment number {user_input}:\n')
                self.parent_id = int(user_input)
                request = self.handle_input(comment_text)
            else:
                print(f'Comment number {user_input} is not exist.')
        except ValueError:
            confirm = input('Are you sure about your comment? (y/n):')
            if confirm == 'y':
                if self.comment_parent_id:
                    data={'movie_id': self.movie_id, 'parent_id':self.comment_parent_id, 'text':user_input}
                else:
                    data={'movie_id': self.movie_id, 'text':user_input}
                request = create_request(
                    type='review', subtype='comment', data=data
                )
        return request
