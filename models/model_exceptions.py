class NotEnoughBalance(Exception):

    def __init__(self):
        """Exception to raise when balance is not enough"""
        super().__init__("Not enough balance.")
