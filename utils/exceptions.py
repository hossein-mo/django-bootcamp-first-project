class DatabaseError(Exception):
    def __init__(
        self, message: str = "Something went wrong with the database."
    ) -> None:
        self.message = message
        super().__init__(self.message)


class DuplicatedEntry(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class WrongCredentials(Exception):
    def __init__(self, message: str = "Wrong User Credentials"):
        self.message = message
        super().__init__(self.message)


class PasswordPolicyNotPassed(Exception):
    def __init__(self, message: str = "Invalid password format."):
        self.message = message
        super().__init__(self.message)


class InvalidUserInfo(Exception):
    def __init__(self, message: str = "User info is invalid."):
        self.message = message
        super().__init__(self.message)


class AuthenticationFaild(Exception):
    def __init__(self, message: str = "User authentication faild. Please login."):
        self.message = message
        super().__init__(self.message)


class NotEnoughBalance(Exception):

    def __init__(self, message: str = "Not enough balance.") -> None:
        """Exception to raise when balance is not enough"""
        self.message = message
        super().__init__("Not enough balance.")


class InvalidRequest(Exception):
    def __init__(self, message: str = "Invalid request!") -> None:
        self.message = message
        super().__init__(self.message)


class WrongBankAccCreds(Exception):
    def __init__(
        self, message: str = "Wrong bank account credentials, please try again!"
    ) -> None:
        self.message = message
        super().__init__(message)


class TheaterNotExist(Exception):
    def __init__(self, message: str = "Requested theater doesn't exist!") -> None:
        self.message = message
        super().__init__(message)


class MovieNotExist(Exception):
    def __init__(self, message: str = "Requested movie doesn't exist!") -> None:
        self.message = message
        super().__init__(message)


class ShowTimeError(Exception):
    def __init__(self, message: str = "Show overlaps with existing show!") -> None:
        self.message = message
        super().__init__(message)

class UnvalidRate(Exception):
    def __init__(self, message: str = "Rate must be in the range of 1 to 5 star!") -> None:
        self.message = message
        super().__init__(message)

class NotFound(Exception):
    def __init__(self, message: str = "Not Found!") -> None:
        self.message = message
        super().__init__(message)