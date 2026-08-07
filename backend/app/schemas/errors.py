from app.schemas.base import CamelModel


class ErrorResponse(CamelModel):
    code: str
    message: str
