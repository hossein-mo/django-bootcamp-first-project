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
