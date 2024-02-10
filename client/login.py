import os
import re
from datetime import datetime, timedelta
from getpass import getpass
from Validation import AcountValidation
from utils import create_request
from tcp_client import TCPClient

tcp=TCPClient()

class LoginAcount:
    def __init__(self):
        self.acount = AcountValidation("", "", "", "")

    def login(self):
        def getpassword():
                while True:
                    self.acount.password = getpass(prompt="Password:")
                    if self.acount.is_valid_password(self.acount.password):
                        break
                    else:
                        print("\033[91mThe password is not correct. Please try again.\033[0m")

        print("\n---Login---")

        while True:
            acount_input = input("Enter username or email:")
            self.acount.username = self.acount.email = acount_input
            username_format = self.acount.is_valid_username()
            email_format = self.acount.is_valid_email()

            if username_format:
                getpassword()
                data_to_send = {"username": self.acount.username, "password": self.acount.password}
                request_signup= create_request("login",data=data_to_send)
                tcp.send(request_signup)

                return tcp.recive()

            if email_format:
                getpassword()
                data_to_send = {"email": self.acount.email, "password": self.acount.password}
                request_signup= create_request("login",data=data_to_send)
                tcp.send(request_signup)

                return tcp.recive()
    
            else:
                print("\033[91mUsername or email format is not correct.\033[0m")
                
            


        
  
    

if __name__ == "__main__":
    user_creator = LoginAcount()
    user_creator.login()



