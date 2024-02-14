import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from getpass import getpass
from utils import create_request, clear_screen, Response, Page
from tcp_client import TCPClient

class BankAccount:
    def __init__(self, name, card_number, cvv2, password, balance = 0, id = None):
        self.name = name
        self.card_number = card_number
        self.cvv2 = cvv2
        self.password = password
        self.balance = balance
        self.id = id


class CreationPage(Page):

    def display(self) -> None:
        clear_screen()
        print("Press Zero to go back...")
        account = BankAccount()
        account.name = input("Enter account name:")
        self.handle_input(account.name)
        account.card_number = input("Enter card number: ")
        self.handle_input(account.card_number)
        account.cvv2 = input("Enter CVV2: ")
        self.handle_input(account.cvv2)
        account.password = getpass(prompt="Enter password: ")
        self.handle_input(account.password)
        # send request
        client=TCPClient()
        data = account.__dict__
        request_signup = create_request(type="account", subtype='add', data=data)
        client.send(request_signup)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()
        
        
class AccountListPage(Page):

    account_list = []

    def display(self):
        clear_screen()
        if len(self.account_list) == 0:
            client=TCPClient()
            request = create_request(type="account", subtype='list')
            client.send(request)
            response = client.recive()
            response = Response(**response)
            if response is not None:
                if response.status:
                    AccountListPage.account_list = response.data
                    if len(self.account_list)==0:
                        print('No account register yet!\n')
                        print(f'1. create account\npress any else key to go back...')
                    else:
                        for account in self.account_list:
                            account = BankAccount(**account)
                            print(f'name: {account.name} card number: {account.card_number} balance: {account.balance}')
                        print(f'\n1. create account \n2 deposite\n3. withdraw\n4. transfer\n press any else key to go back...')
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
            for account in self.account_list:
                account = BankAccount(**account)
                print(f'name: {account.name} card number: {account.card_number} balance: {account.balance}')
            print(f'\n1. create account \n2 deposite\n3. withdraw\n4. transfer\n press any else key to go back...')
            self.handle_input(input())

        
    def handle_input(self, user_input):
        if user_input == "1":
            self.app.navigate_to_page(CreationPage(self.app))
        elif len(self.account_list) > 0 and user_input == "2":
            self.app.navigate_to_page(DepositPage(self.app, self.account_list))
        elif len(self.account_list) > 0 and user_input == "3":
            self.app.navigate_to_page(WithdrawPage(self.app, self.account_list))
        elif len(self.account_list) != 0 and user_input == "4":
            self.app.navigate_to_page(TransferPage(self.app, self.account_list))
        else:
            self.app.navigate_back()



class DepositPage(Page):
    def __init__(self, app, account_list):
        super().__init__(app)
        self.account_list = account_list

    def display(self):
        clear_screen()
        for i in range(len(self.account_list)):
            account = BankAccount(**self.account_list[i])
            print(f'{i+1}. name: {account.name} card number: {account.card_number} balance: {account.balance}')
        print(f'\nPress Zero to go back...')
        while True:
            card_number = input("Enter account number:")
            self.handle_input(card_number)
            try:
                if int(card_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    id = self.account_list[card_number-1]['id']
                    break
            except ValueError:
                print("Invalid value!")
        while True:
            try:
                amount = input("Enter amount:")
                self.handle_input(amount)
                amount = int(amount)
                break
            except ValueError:
                print("Invalid value!")
        client=TCPClient()
        request = create_request(type="account", subtype='deposit', data={'account_id':id, 'amount':amount})
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()



class WithdrawPage(Page):
    def __init__(self, app, account_list):
        super().__init__(app)
        self.account_list = account_list

    def display(self):
        clear_screen()
        for i in range(len(self.account_list)):
            account = BankAccount(**self.account_list[i])
            print(f'{i+1}. name: {account.name} card number: {account.card_number} balance: {account.balance}')
        print(f'\nPress Zero to go back...')
        while True:
            card_number = input("Enter account number:")
            self.handle_input(card_number)
            try:
                if int(card_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    id = self.account_list[card_number-1]['id']
                    break
            except ValueError:
                print("Invalid value!")        
        password = input("Enter account password:")
        self.handle_input(password)
        while True:
            cvv2 = input("Enter account cvv2:")
            self.handle_input(cvv2)
            if not card_number.isdigit():
                print("The input consists of digits only.")
            else:
                break
        while True:
            try:
                amount = input("Enter amount:")
                self.handle_input(amount)
                amount = int(amount)
                break
            except ValueError:
                print("Invalid value!")
        client=TCPClient()
        request = create_request(type="account", subtype='withdraw', data={'account_id':id, 'amount':amount, 'password': password, 'cvv2':cvv2})
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()



class TransferPage(Page):
    def __init__(self, app, account_list):
        super().__init__(app)
        self.account_list = account_list

    def display(self):
        clear_screen()
        for i in range(len(self.account_list)):
            account = BankAccount(**self.account_list[i])
            print(f'{i+1}. name: {account.name} card number: {account.card_number} balance: {account.balance}')
        print(f'\nPress Zero to go back...')
        while True:
            card_number = input("Enter origin account number:")
            self.handle_input(card_number)
            try:
                if int(card_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    from_id = self.account_list[card_number-1]['id']
                    break
            except ValueError:
                print("Invalid value!")

        while True:
            card_number = input("Enter destination account number:")
            self.handle_input(card_number)
            try:
                if int(card_number) not in range(1, len(self.account_list)+1):
                    print("Invalid number!")
                else:
                    to_id = self.account_list[card_number-1]['id']
                    break
            except ValueError:
                print("Invalid value!")          
        
        password = input("Enter account password:")
        self.handle_input(password)

        while True:
            cvv2 = input("Enter account cvv2:")
            self.handle_input(cvv2)
            if not card_number.isdigit():
                print("The input consists of digits only.")
            else:
                break

        while True:
            try:
                amount = input("Enter amount:")
                self.handle_input(amount)
                amount = int(amount)
                break
            except ValueError:
                print("Invalid value!")
                
        client=TCPClient()
        request = create_request(type="account", subtype='transfer', data={'from_id':from_id, 'to_id':to_id,'amount':amount, 'password': password, 'cvv2':cvv2})
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
            input("Press any key to go back... ")
            self.app.navigate_back()
        else:
            self.display()
    



