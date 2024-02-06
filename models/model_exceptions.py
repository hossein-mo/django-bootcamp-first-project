class NotEnoughBalance(Exception):

    def __init__(self) -> None:
        """Exception to raise when balance is not enough"""
        super().__init__("Not enough balance.")


class DuplicatedEntry(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class WrongCredentials(Exception):
    def __init__(self):
        self.message = "Wrong User Credentials"
        super().__init__(self.message)
