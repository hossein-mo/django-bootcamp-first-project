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


class PasswordPolicyNotPassed(Exception):
    def __init__(self, message: str = "Password policy verfication failed."):
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
