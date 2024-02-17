import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, Page, clear_screen, connect_server
from Validation import AccountValidation

class AddMoviePage(Page):

    def display(self):
        clear_screen()
        print(f'**** Add Movie ****\n')        
        print(f'>>> Press Zero to go back <<<\n')
        while True:
            movie_name = input('Movie name: ')
            self.handle_input(movie_name)
            if movie_name:
                try:
                    duration = int(input('Duration: '))
                    self.handle_input(str(duration))
                    age_rating = int(input('Age Rating: '))
                    self.handle_input(str(age_rating))
                    break
                except ValueError:
                    print('Invalid value!')
        data = {'m_name': movie_name, 'duration': duration, 'age_rating': age_rating}
        request= create_request(type='management', subtype='addmovie', data = data)
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")

class AddShowPage(Page):

    def display(self):
        clear_screen()
        print(f'**** Add Show ****\n')
        print(f'>>> Press Zero to go back <<<\n')
        while True:
            try:
                theater_id = int(input('Theater ID: '))
                self.handle_input(str(theater_id))
                movie_id = int(input('Movie ID: '))
                self.handle_input(str(movie_id))
                start_date = input('Start date (2024-02-11 14:00:00): ')
                datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                end_date = input('End date (2024-02-11 16:00:00): ')
                self.handle_input(end_date)
                datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                price = int(input('Price: '))
                self.handle_input(price)
                break
            except ValueError:
                print('Invalid value!')
        data = {'theater_id': theater_id, 'movie_id': movie_id, 'start_date': start_date, 'end_date': end_date, 'price' : price}
        request= create_request(type='management', subtype='addshow', data = data)
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")

class ChangeRolePage(Page):

    def convert_role_input(self, user_input):
        dict = {'1':'user', '2':'staff', '3':'admin'}
        try:
            return dict[user_input]
        except:
            raise ValueError

    def display(self):
        clear_screen()
        print(f'**** Change Role ****\n')
        print(f'>>> Press Zero to go back <<<\n')
        while True:
            user_input = input('Username or Email of User: ')
            self.handle_input(user_input)
            username_format = AccountValidation.is_valid_username(user_input)
            email_format = AccountValidation.is_valid_email(user_input)
            if username_format or email_format:
                try:
                    new_role = int(input('New Role >> (1.user 2.staff 3.admin): '))
                    self.handle_input(new_role)
                    new_role = self.convert_role_input(new_role)
                    break
                except ValueError:
                    print('Invalid value for role!')
            else:
                print("\033[91mUsername or email format is not correct.\033[0m")
        if username_format:
            data = {"username": user_input, 'new_role': new_role}
        else:
            data = {'email': user_input, 'new_role': new_role}
        request= create_request(type='profile', subtype='changerole', data = data)
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")

class AddTheaterPage(Page):

    def display(self):
        clear_screen()
        print(f'**** Add Theater ****\n')
        print(f'>>> Press Zero to go back <<<\n')
        while True:
            theater_name = input('Theater name: ')
            self.handle_input(theater_name)
            if theater_name:
                try:
                    capacity = int(input('Capacity: '))
                    self.handle_input(str(capacity))
                    break
                except ValueError:
                    print('Invalid value for capacity!')
        data = {'t_name': theater_name, 'capacity': capacity}
        request= create_request(type='management', subtype='addtheater', data = data)
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")
