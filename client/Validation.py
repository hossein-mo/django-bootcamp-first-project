
import re
from datetime import datetime


class AcountValidation:
    def __init__(self, user_id=None, username="", email="", phone=None, password=None, birthdate=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password
        self.registration_date = datetime.now()
        self.last_login_date = None
        self.birthdate = birthdate

    
    # Username must be unique and less than 100 characters and contain 1-9, A-Z, and a-z.
    def is_valid_username(self):
        username_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{1,100}$'
        return bool(re.match(username_pattern, self.username))
          

    #The password must have at least 8 characters and at least two @#$& characters and contain upper and lower case English letters and numbers.
    def is_valid_password(self, password):
        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=(.*[@$&#]){2})[A-Za-z\d@$&#]{8,}$'
        return bool(re.match(password_pattern, password))
        
                  
    
    #The email must be entered in the correct format 
    def is_valid_email(self):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_pattern, self.email))
          
    
    #The Phonr number must be entered in the correct format or none 
    def is_valid_phone(self):
        if not self.phone:
            return True
        phone_pattern = r'^\d{11}$'
        return bool(re.match(phone_pattern, self.phone))
    
    #The birthdate must be entered in the correct format y-m-d 
    def validate_date_format(self):
        try:
            date = datetime.strptime(self.birthdate, '%Y-%m-%d')  
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return False
    
    #When the user exits, his last login must be saved 
    def update_last_login_date(self):
        self.last_login_date = datetime.now()

