import uuid
from datetime import datetime

from pydantic import Field

from app.models import SessionStatus
from app.schemas.base import CamelModel
from app.schemas.item import ItemOut


class SessionOut(CamelModel):
    id: uuid.UUID
    partner_id: str
    status: SessionStatus
    company_name: str | None
    account_id: str | None
    # api_key is intentionally omitted: never echoed back once submitted.
    last_error: str | None
    warnings: list[str]
    items: list[ItemOut]
    created_at: datetime
    updated_at: datetime


class DetailsIn(CamelModel):
    company_name: str = Field(min_length=1, max_length=200)
    account_id: str = Field(min_length=1, max_length=200)
    api_key: str = Field(min_length=1, max_length=200)
