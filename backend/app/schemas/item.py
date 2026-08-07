import uuid

from app.schemas.base import CamelModel


class ItemOut(CamelModel):
    id: uuid.UUID
    external_id: str
    name: str
