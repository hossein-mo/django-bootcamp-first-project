import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from home import HomePage
from utils import CinemaReservationApp

def main():
    client_app = CinemaReservationApp()
    client_app.start(HomePage(client_app))
     

if __name__ == "__main__":
    main()
    
