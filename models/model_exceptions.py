class DuplicatedEntry(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class WrongCredentials(Exception):
    def __init__(self):
        self.message = "Wrong User Credentials"
        super().__init__(self.message)
