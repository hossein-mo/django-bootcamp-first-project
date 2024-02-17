import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, Page, clear_screen, Response, CinemaReservationApp, connect_server
from user import User, ProfilePage
from getpass import getpass
from Validation import AccountValidation
from tcp_client import TCPClient


class LoginPage(Page):

    def handle_response(self, response):
        client = TCPClient()
        if response is not None:
            if response.status:
                user = User(**response.data)
                self.app.navigate_to_page(ProfilePage(self.app, user))
            else:
                client.close()
                print(response.message)
                input('Press any key to go back... ')
                self.handle_input('0')
        else:
            client.close()
            print('Connection Error! try again...')
            input('Press any key to go back... ')
            self.handle_input('0')

    def display(self):
        clear_screen()
        print('\n**** Login ****\n')
        print('\n>>> Press Zero to go back <<<\n')
        while True:
            account_input = input('Enter username or email:')
            self.handle_input(account_input)
            password = getpass(prompt='Password:')
            self.handle_input(password)
            username_format = AccountValidation.is_valid_username(account_input)
            email_format = AccountValidation.is_valid_email(account_input)
            if username_format:
                data_to_send = {'username': account_input, 'password': password}
                request_signup= create_request('login', data=data_to_send)
                response = connect_server(request_signup)
                self.handle_response(response)
            elif email_format:
                data_to_send = {'email': account_input, 'password': password}
                request_signup= create_request('login',data=data_to_send)
                response = connect_server(request_signup)
                self.handle_response(response)
            else:
                print('\033[91mUsername or email format is not correct.\033[0m')


class SignUpPage(Page):
    def __init__(self, app:CinemaReservationApp):
        super().__init__(app)

    def handle_response(self, client, response):
        response = Response(**response)
        if response is not None:
            if response.status:
                user = User(**response.data)
                self.app.navigate_to_page(ProfilePage(self.app, user))
            else:
                client.close()
                print(response.message)
                input('Press any key to go back... ')
                self.handle_input('0')
        else:
            client.close()
            print('Connection Error! try again...')
            input('Press any key to go back... ')
            self.handle_input('0')

    def display(self):
        clear_screen()
        print('\n**** Create Account ****\n')
        print('\nPress Zero to go back...\n')
        # Username
        while True:
            username = input('Username:')
            self.handle_input(username)
            if AccountValidation.is_valid_username(username):
                break
            else:
                print('\033[91mThe username format is incorrect, please try again (Format: A-Z a-z 0-9).\033[0m')

        # Email
        while True:
            email = input('Email:')
            self.handle_input(email)
            if AccountValidation.is_valid_email(email):
                break
            else:
                print('\033[91mThe email format is incorrect, please try again\033[0m')

        # PhoneNumber
        while True:
            phone = input('Contact Number (Optional):')
            self.handle_input(self.user.phone)
            if AccountValidation.is_valid_phone(phone):
                break
            else:
                print('\033[91mThe PhoneNumber is invalid. please try again.\033[0m')

        # Password
        while True:
            password = getpass(prompt='Password (Password must be at least 8 characters long and contain at least two @#$& characters): ')
            self.handle_input(password)
            if AccountValidation.is_valid_password(password):
                # print('\033[92mOK!\033[0m')
                break
            else:
                print('\033[91mThe password is invalid, please try again.\033[0m')

        # Birthdate
        while True:
            birthdate = input('Enter your birthdate (Year-Month-Day): ')
            self.handle_input(birthdate)
            if AccountValidation.validate_date_format(birthdate) is not False:
                break
            else:
                print('\033[91mInvalid date format. please try again.\033[0m')
        
        data_to_send = {'username': username, 'password': password,\
            'email': email, 'phone_number': phone, 'birth_date': birthdate}
        request_signup= create_request('signup', data=data_to_send)
        response = connect_server(request_signup)
        self.handle_response(response)


class HomePage(Page):

    def display(self):
        print('\n**** Cinema Reservation App ****\n')
        while True:
            clear_screen()
            print('1. Create Account')
            print('2. Login')
            user_choice = input('Enter your choice: ')
            self.handle_input(user_choice)
    
    def handle_input(self, user_input):
        if user_input == '1':
            self.app.navigate_to_page(SignUpPage(self.app))
        elif user_input == '2':
            self.app.navigate_to_page(LoginPage(self.app))
        else:
            print('Invalid input!')
        
