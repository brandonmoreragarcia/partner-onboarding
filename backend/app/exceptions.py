class AppError(Exception):
    """Base for errors that should surface as {code, message} JSON, not a raw 500."""

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TransitionError(AppError):
    def __init__(self, message: str, code: str = "INVALID_STATE"):
        super().__init__(code=code, message=message, status_code=409)


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(code="RESOURCE_NOT_FOUND", message=message, status_code=404)
