import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .utils import create_request, Page, clear_screen, Response, CinemaReservationApp
from user import User, ProfilePage
from datetime import datetime
from getpass import getpass
from Validation import AcountValidation
from tcp_client import TCPClient


class LoginPage(Page):
    def __init__(self, app:CinemaReservationApp):
        super().__init__(app)
        self.acount = AcountValidation("", "", "", "")

    def handle_response(self, client, response):
        response = Response(**response)
        if response is not None:
            if response.status:
                user = response.data['userinfo']
                user = User(**user)
                self.app.navigate_to_page(ProfilePage(self.app, user))
            else:
                client.close()
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            client.close()
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")

    def display(self):
        clear_screen()
        print("\n---Login---")
        while True:
            acount_input = input("Enter username or email:")
            self.acount.username = self.acount.email = acount_input
            username_format = self.acount.is_valid_username()
            email_format = self.acount.is_valid_email()
            password = getpass(prompt="Password:")
            client = TCPClient()
            if username_format:
                data_to_send = {"username": self.acount.username, "password": password}
                request_signup= create_request("login",data=data_to_send)
                client.send(request_signup)
                response = client.recive()
                self.handle_response(client, response)
            elif email_format:
                data_to_send = {"email": self.acount.email, "password": password}
                request_signup= create_request("login",data=data_to_send)
                client.send(request_signup)
                response = client.recive()
                self.handle_response(client, response)
            else:
                print("\033[91mUsername or email format is not correct.\033[0m")


class SignUpPage(Page):
    def __init__(self, app:CinemaReservationApp):
        super().__init__(app)
        self.user = AcountValidation("", "", "", "")

    def handle_response(self, client, response):
        response = Response(**response)
        if response is not None:
            if response.status:
                user = response.data['userinfo']
                user = User(**user)
                self.app.navigate_to_page(ProfilePage(self.app, user))
            else:
                client.close()
                print("Connection Error! try again...")
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            client.close()
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")

    def display(self):
        clear_screen()
        print("\n---Create Account---")
        print("\nPress Zero to go back...\n")
        # Username
        while True:
            self.user.username = input("Username:")
            self.handle_input(self.user.username)
            if self.user.is_valid_username():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe username format is incorrect, please try again (Format: A-Z a-z 0-9).\033[0m")

        # Email
        while True:
            self.user.email = input("Email:")
            self.handle_input(self.user.email)
            if self.user.is_valid_email():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe email format is incorrect, please try again\033[0m")

        # PhoneNumber
        while True:
            self.user.phone = input("Contact Number (Optional):")
            self.handle_input(self.user.phone)
            if self.user.is_valid_phone():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe PhoneNumber is invalid. please try again.\033[0m")

        # Password
        while True:
            self.user.password = getpass(prompt="Password (Password must be at least 8 characters long and contain at least two @#$& characters): ")
            self.handle_input(self.user.password)
            if self.user.is_valid_password(self.user.password):
                print("\033[92mOK!\033[0m")
                break
            else:
                print("\033[91mThe password is invalid, please try again.\033[0m")

        # Birthdate
        while True:
            self.user.birthdate = input("Enter your birthdate (Year-Month-Day): ")
            self.handle_input(self.user.birthdate)
            if self.user.validate_date_format() is not False:
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mInvalid date format. please try again.\033[0m")

        self.user.registration_date = datetime.now()
        self.user.update_last_login_date()
        
        data_to_send = {"username": self.user.username, "password": self.user.password,\
            "email": self.user.email, "phone_number":self.user.phone, "birth_date": self.user.birthdate}
        
        request_signup= create_request("signup", data=data_to_send)
        client = TCPClient()
        client.send(request_signup)
        response = client.recive()
        self.handle_response(client, response)


class HomePage(Page):

    def display(self):
        while True:
            clear_screen()
            print("1. Create Account")
            print("2. Login")
            user_choice = input("Enter your choice: ")
            self.handle_input(user_choice)
    
    def handle_input(self, user_input):
        if user_input == "1":
            self.app.navigate_to_page(SignUpPage(self.app))
        elif user_input == "2":
            self.app.navigate_to_page(LoginPage(self.app))
        else:
            print("Invalid input!")
        
