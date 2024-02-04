class InsertFailed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DeleteFailed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UpdateFailed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UserNotExist(Exception):
    def __init__(self):
        self.message = "User Doesn't Exist"
        super().__init__(self.message)


class WrongCredentials(Exception):
    def __init__(self):
        self.message = "Wrong User Credentials"
        super().__init__(self.message)
