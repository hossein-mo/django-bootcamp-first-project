class DuplicatedEntry(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class WrongCredentials(Exception):
    def __init__(self, message: str = "Wrong User Credentials"):
        self.message = message
        super().__init__(self.message)
