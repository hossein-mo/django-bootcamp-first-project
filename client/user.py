import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, Page, clear_screen, Response, CinemaReservationApp
from user import User
from datetime import datetime
from getpass import getpass
from Validation import AcountValidation
from tcp_client import TCPClient

class User:
    def __init__(self, id, username, email, subscription:str, phone=None, subscription_rest_days=0):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone
        self.subscription = subscription
        self.subscription_rest_days = subscription_rest_days


class ProfilePage(Page):
    user = None
    def __init__(self, app, user:User):
        super().__init__(app)
        ProfilePage.user = user

    def display(self):
        clear_screen()
