import os
import re
from datetime import datetime, timedelta
from getpass import getpass
from mysocket import Request


class User:
    def __init__(
        self,
        user_id=None,
        username="",
        email="",
        phone=None,
        password=None,
        birthdate=None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password
        self.registration_date = datetime.now()
        self.last_login_date = None
        self.birthdate = birthdate

    # Username must be unique and less than 100 characters and contain 1-9, A-Z, and a-z.
    def is_valid_username(self, username):
        username_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{1,100}$"
        return bool(re.match(username_pattern, username))

    # The password must have at least 8 characters and at least two @#$& characters and contain upper and lower case English letters and numbers.
    def is_valid_password(self, password):
        password_pattern = (
            r"^(?=.*[A-Za-z])(?=.*\d)(?=(.*[@$&#]){2})[A-Za-z\d@$&#]{8,}$"
        )
        return bool(re.match(password_pattern, password))

    # The email must be entered in the correct format
    def is_valid_email(self, email):
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(email_pattern, email))

    # The Phone number must be entered in the correct format or none
    def is_valid_phone(self):
        if not self.phone:
            return True
        phone_pattern = r"^\d{11}$"
        return bool(re.match(phone_pattern, self.phone))

    # The birthdate must be entered in the correct format y-m-d
    def validate_date_format(self):
        try:
            date = datetime.strptime(self.birthdate, "%Y-%m-%d")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return False

    # When the user exits, his last login must be saved
    def update_last_login_date(self):
        self.last_login_date = datetime.now()


def create_account(request_instance):
    clear_screen()
    user = User("", "", "", "")

    def get_user_input_sign_in():
        print("\n---Create Account---")
        nonlocal user

        # Username
        while True:
            user.username = input("Username:")
            if user.is_valid_username():
                print("\033[92mOK! \033[0m")
                break
            else:
                print(
                    "\033[91mThe username format is incorrect, please try again (Format: A-Z a-z 0-9).\033[0m"
                )

        # Email
        while True:
            user.email = input("Email:")
            if user.is_valid_email():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe email format is incorrect, please try again\033[0m")

        # PhoneNumber
        while True:
            user.phone = input("Contact Number (Optional):")
            if user.is_valid_phone():
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mThe PhoneNumber is invalid. please try again.\033[0m")

        # Password
        while True:
            password = getpass(
                prompt="Password (Password must be at least 8 characters long and contain at least two @#$& characters): "
            )
            if user.is_valid_password(password):
                print("\033[92mOK!\033[0m")
                break
            else:
                print("\033[91mThe password is invalid, please try again.\033[0m")

        # Birthdate
        while True:
            user.birthdate = input("Enter your birthdate (Year-Month-Day): ")
            if user.validate_date_format() is not False:
                print("\033[92mOK! \033[0m")
                break
            else:
                print("\033[91mInvalid date format. please try again.\033[0m")

        user.registration_date = datetime.now()
        user.update_last_login_date()

        request_instance.send_socket_request(
            status=True,
            type="signup",
            message="This is a message from the client",
            data={
                "username": user.username,
                "password": user.password,
                "email": user.email,
                "phone_number": user.phone,
                "birth_date": user.birthdate,
            },
        )

        end_time = datetime.now() + timedelta(seconds=5)
        while datetime.now() < end_time:
            pass

    get_user_input_sign_in()


def login(inq_users):
    clear_screen()
    user_login = User("", "", "", "")

    def get_user_input_login():
        nonlocal user_login
        print("\n---Login---")

        while True:
            user_input = input("Enter username or email: ")
            user_login.username = user_login.email = user_input
            print(user_input)
            username_duplicates = user_login.is_valid_username(user_input)
            email_duplicates = user_login.is_valid_email(user_input)

            if not (username_duplicates or email_duplicates):
                print("\033[91mUsername or email not found\033[0m")
            else:
                while True:
                    password = getpass(prompt="Password:")
                    if user_login.is_valid_password(password, inq_users):
                        print(f"Logged in successfully as {user_login.username}")
                        break
                    else:
                        print(
                            "\033[91mThe password is not correct. Please try again.\033[0m"
                        )

    get_user_input_login()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    request_instance = Request()

    while True:
        clear_screen()
        print("1. Create Account")
        print("2. Login")
        # print("\033[91mPlease note that you can exit anywhere in the program by entering logout\033[0m")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            create_account(request_instance)
            clear_screen()
            print("\033[92m Account created successfully! \033[0m")
            end_time = datetime.now() + timedelta(seconds=1)
            while datetime.now() < end_time:
                pass

        if user_choice == "2":
            login(request_instance)
            clear_screen()
            print("\033[92mLogin successfully!\033[0m")
            end_time = datetime.now() + timedelta(seconds=1)
            while datetime.now() < end_time:
                pass


if __name__ == "__main__":
    main()
