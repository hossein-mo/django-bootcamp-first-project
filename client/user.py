import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from admin_access import *
from bankaccounts import AccountListPage
from movie import MovieListPage
from order import UserOrdersPage
from showtime import ShowsPage
from subscription import SubscriptionListPage
from theater import TheaterListPage
from utils import create_request, Page, clear_screen, connect_server, CinemaReservationApp
from Validation import AccountValidation

class User:
    def __init__(self, username, email, birth_date, phone_number, subs:str, subs_expires_in, balance, role, last_login, register_date):
        self.username = username
        self.email = email
        self.birth_date = birth_date
        self.phone = phone_number
        self.subscription = subs
        self.subscription_rest_days = subs_expires_in
        self.balance = balance
        self.role = role


class ProfilePage(Page):
    user = None
    def __init__(self, app, user:User):
        super().__init__(app)
        ProfilePage.user = user

    def display(self):
        clear_screen()
        print(f'**** Profile ****\n')
        print(f'username: {self.user.username}')
        print(f'email: {self.user.email}')
        print(f'phone: {self.user.phone}')
        print(f'wallet: {self.user.balance} $')
        print(f'subscription: {self.user.subscription} -> <{self.user.subscription_rest_days}> days left\n')
        print(f'1. edit profile\n2. change password\n3. bank account\n4. buy subscription')
        print(f'5. orders history\n6. shows list\n7. movies list\n8. logout')
        if self.user.role == 'staff':
            print(f'8. theaters list\n9. add show\n10. logout')
        elif self.user.role == 'admin':
            print(f'8. theaters list\n9. add show\n10. change user role\n11. logout')
        while True:
            user_input = input('Where do you want to go? ')
            if self.handle_input(user_input):
                break

    def handle_input(self, user_input):
        flag = True
        if user_input == '1':
            self.app.navigate_to_page(EditProfilePage(self.app, self.user))
        elif user_input == '2':
            self.app.navigate_to_page(ChangePasswordPage(self.app, self.user))
        elif user_input == '3':
            self.app.navigate_to_page(AccountListPage(self.app))
        elif user_input == '4':
            self.app.navigate_to_page(SubscriptionListPage(self.app))
        elif user_input == '5':
            self.app.navigate_to_page(UserOrdersPage(self.app))
        elif user_input == '6':
            self.app.navigate_to_page(ShowsPage(self.app))
        elif user_input == '7':
            self.app.navigate_to_page(MovieListPage(self.app, self.user))
        elif user_input == '8':
            if self.user_role == 'user':
                self.app.restart()
            elif self.user_role == 'admin' or self.user_role == 'staff':
                self.app.navigate_to_page(TheaterListPage(self.app))
            else:
                print(f'Invalid input!')
                flag = False
        elif self.user_role == 'admin' or self.user_role == 'staff':
            if user_input == '9':
                self.app.navigate_to_page(AddShowPage(self.app))
            elif user_input == '10':
                if self.user_role == 'admin':
                    self.app.navigate_to_page(ChangeRolePage(self.app))
                else:
                    self.app.restart()
            elif user_input == '11' and self.user_role == 'admin':
                self.app.restart()
        else:
            print(f'Invalid input!')
            flag = False
        return flag
        


class EditProfilePage(Page):
    
    def __init__(self, app: CinemaReservationApp, user: User):
        super().__init__(app)
        self.user = user

    def display(self):
        clear_screen()
        print(f'**** Edit Profile ****\n')
        print(f'>>> Press Zero to go back <<<\n')
        while True:
            username = input('New username: ')
            self.handle_input(username)
            if not username or AccountValidation.is_valid_username(username):
                break
            else:
                print("\033[91mThe username format is incorrect, please try again (Format: A-Z a-z 0-9).\033[0m")
        while True:
            email = input('new email: ')
            self.handle_input(email)
            if not email or AccountValidation.is_valid_email(email):
                break
            else:
                print("\033[91mThe email format is incorrect, please try again\033[0m")
        while True:
            phone = input('new phone number: ')
            self.handle_input(phone)
            if not phone or AccountValidation.is_valid_phone(phone):
                break
            else:
                print("\033[91mThe email format is incorrect, please try again\033[0m")
        data = {'username': username, 'phone_number': phone, 'email': email}
        request= create_request(type='profile', subtype='update', data = data)
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")


class ChangePasswordPage(Page):
    
    def __init__(self, app: CinemaReservationApp, user: User):
        super().__init__(app)
        self.user = user
        
    def display(self):
        clear_screen()
        print(f'**** Change Password ****\n')
        print(f'>>> Press Zero to go back <<<\n')
        print('*** Password must be at least 8 characters long and contain at least two @#$& characters ***')
        while True:
            old_password = input('Old password: ').strip()
            self.handle_input(old_password)
            new_password = input('New password: ').strip()
            self.handle_input(new_password)
            if AccountValidation.is_valid_password(new_password):
                confirm_new_password = input('Confirm new password: ').strip()
                self.handle_input(confirm_new_password)
                if confirm_new_password == new_password:
                    break
                else:
                    print("\033[91mThe confirm password does not match the new password. Please try again.\033[0m")
            else:
                print("\033[91mThe password is invalid, please try again.\033[0m")
        request= create_request(type='profile', subtype='changepass', data={'old_password': old_password, 'password': new_password})
        response = connect_server(request)
        if response is not None:
            print(response.message)
        else:
            print("Connection Error! try again...")
        input("Press any key to go back... ")
        self.handle_input("0")
