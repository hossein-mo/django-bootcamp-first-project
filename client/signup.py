import os
import re
from datetime import datetime, timedelta
from getpass import getpass
from Validation import AcountValidation
from utils import create_request
from tcp_client import TCPClient

tcp=TCPClient()
class CreateAccount:
    
   
    
    def __init__(self):
        self.user = AcountValidation("", "", "", "")

    def signup(self):
        print("\n---Create Account---")

        # Username
        while True:
            self.user.username = input("Username:")
            if self.user.is_valid_username():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe username format is incorrect, please try again (Format: A-Z a-z 0-9).\033[0m")

        # Email
        while True:
            self.user.email = input("Email:")
            if self.user.is_valid_email():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe email format is incorrect, please try again\033[0m")

        # PhoneNumber
        while True:
            self.user.phone = input("Contact Number (Optional):")
            if self.user.is_valid_phone():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe PhoneNumber is invalid. please try again.\033[0m")

        # Password
        while True:
            self.user.password = getpass(prompt="Password (Password must be at least 8 characters long and contain at least two @#$& characters): ")
            if self.user.is_valid_password(self.user.password):
                print("\033[92mOK!\033[0m")
                break
            else:
                print("\033[91mThe password is invalid, please try again.\033[0m")

        # Birthdate
        while True:
            self.user.birthdate = input("Enter your birthdate (Year-Month-Day): ")
            if self.user.validate_date_format() is not False:
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mInvalid date format. please try again.\033[0m")

        self.user.registration_date = datetime.now()
        self.user.update_last_login_date()
        print("secsesful!")
        
        data_to_send = {"username": self.user.username, "password": self.user.password,\
            "email": self.user.email, "phone_number":self.user.phone, "birth_date": self.user.birthdate}
        
        request_signup= create_request("signup",data=data_to_send)
        tcp.send(request_signup)
        
        
        print( tcp.recive())
        
    

if __name__ == "__main__":
    user_creator = CreateAccount()
    user_creator.signup()
