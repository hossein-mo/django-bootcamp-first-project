class Response:
    def __init__(
        self, status: bool, type: str, message: str, data: dict | list
    ) -> None:
        self.status = status
        self.type = type
        self.message = message
        self.data = data
