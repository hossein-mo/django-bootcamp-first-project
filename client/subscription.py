import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, Page, clear_screen, connect_server

class Subscription:
    def __init__(self, id, s_name, discount, duration, order_number, price):
        self.id = id
        self.s_name = s_name
        self.discount = discount
        self.duration = duration
        self.order_number = order_number
        self.price = price


class SubscriptionListPage(Page):

    def display_sub_list(self):
        for i in range(len(self.sub_list)):
            print(f'{i+1}. {self.sub_list[i].s_name} discount: {self.sub_list[i].discount},\
                    duration: {self.sub_list[i].duration}, {f"times: {self.sub_list[i].order_number}," if self.sub_list[i].order_number else ""}\
                        price: {self.sub_list[i].price} $')
    
    def buy_process(self, subs_id):
        request = create_request(type="order", subtype="subs", data={'subs_id': subs_id})
        response = connect_server(request)
        if response:
            print(response.message)
            if response.status:
                data = response.data
                exp_date = data["expire_date"]
                print(f'You has {data["subs_name"]} subscription until {data["exp_date"][:exp_date.rfind(":")]}')
            input("Press any key to go back... ")
            self.handle_input("0")
        else:
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")

    def display(self):
        clear_screen()
        print(f'**** Buy a Subscription ****\n') 
        request = create_request(type="report", subtype="getsubs")
        response = connect_server(request)
        if response is not None:
            if response.status:
                self.sub_list = list(map(lambda x: Subscription(**x), response.data))
                self.display_sub_list()
                print(f'\n>>> Press Zero to go back <<<\n')
                while True:
                    print('Enter the ID to buy a new subscription:')
                    subs_id = self.handle_input(input())
                    if subs_id:
                        self.buy_process(subs_id)
            else:
                print(response.message)
                input("Press any key to go back... ")
                self.handle_input("0")
        else:
            print("Connection Error! try again...")
            input("Press any key to go back... ")
            self.handle_input("0")

    def handle_input(self, user_input):
        try:
            if user_input == "0":
                self.app.navigate_back()
            elif int(user_input) in range(1, len(self.sub_list)+1):
                return int(user_input)
            else:
                raise ValueError()
        except ValueError:
                print('Invalid input...')
        return None
