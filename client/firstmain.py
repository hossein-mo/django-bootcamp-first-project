import os
from datetime import datetime, timedelta
from signup import CreateAccount
from login import LoginAcount

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    while True:
        clear_screen()
        print("1. Create Account")
        print("2. Login")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            clear_screen()
            CreateAccount().signup()
            clear_screen()
            
            print("\033[92m Account created successfully! \033[0m")
            end_time = datetime.now() + timedelta(seconds=1)
            while datetime.now() < end_time:
                pass
                
        elif user_choice == "2":
            clear_screen()
            LoginAcount().login()
            clear_screen()

            print("\033[92mLogin successfully!\033[0m")
            end_time = datetime.now() + timedelta(seconds=5)
            while datetime.now() < end_time:
                pass 

if __name__ == "__main__":
    main()
    
