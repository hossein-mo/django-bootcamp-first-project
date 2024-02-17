
import re
from datetime import datetime


class AccountValidation:
    
    # Username must be unique and less than 100 characters and contain 1-9, A-Z, and a-z.
    @staticmethod
    def is_valid_username(username):
        # username_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{1,100}$'
        username_pattern = r'^[a-zA-Z\d]{1,100}$'
        return bool(re.match(username_pattern, username))
          

    #The password must have at least 8 characters and at least two @#$& characters and contain upper and lower case English letters and numbers.
    @staticmethod
    def is_valid_password(password):
        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=(.*[@$&#]){2})[A-Za-z\d@$&#]{8,}$'
        return bool(re.match(password_pattern, password))
             
    
    #The email must be entered in the correct format 
    @staticmethod
    def is_valid_email(email):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_pattern, email))
          
    
    #The Phonr number must be entered in the correct format or none 
    @staticmethod
    def is_valid_phone(phone):
        phone_pattern = r'^\d{11}$'
        return bool(re.match(phone_pattern, phone))
    

    #The birthdate must be entered in the correct format y-m-d
    @staticmethod
    def validate_date_format(input_date):
        try:
            date = datetime.strptime(input_date, '%Y-%m-%d')  
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return False
        

    @staticmethod
    def validate_datetime_format(input_datetime):
        try:
            date = datetime.strptime(input_datetime, '%Y-%m-%d %H:%M:%S')  
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return False
