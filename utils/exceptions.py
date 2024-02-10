class DatabaseError(Exception):
    def __init__(self, message: str = "Something went wrong with the database.") -> None:
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

    def __init__(self) -> None:
        """Exception to raise when balance is not enough"""
        super().__init__("Not enough balance.")


class InvalidRequest(Exception):
    def __init__(self, message: str = "Invalid request please try again!") -> None:
        self.message = message
        super().__init__(self.message)


class WrongBankAccCreds(Exception):
    def __init__(
        self, message: str = "Wrong bank account credentials, please try again!"
    ) -> None:
        super().__init__(message)
