# ai_errors.py

class AIRetryableError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AINonRetryableError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)