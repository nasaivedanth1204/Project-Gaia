from typing import List, Optional


class ValidationError(Exception):
    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors or [message]


class SampleNotFoundError(Exception):
    pass


class StageNotCompletedError(Exception):
    pass
