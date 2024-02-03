class NotEnoughBalance(Exception):

    def __init__(self):
        super().__init__("Not enough balance.")
