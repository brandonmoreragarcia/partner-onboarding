import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Text, func, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.item import ItemRow
    from app.models.validation_log import ValidationLogRow


class SessionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    DETAILS_OK = "DETAILS_OK"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"
    LIVE = "LIVE"


class SessionRow(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(
            SessionStatus,
            name="session_status",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda cls: [member.value for member in cls],
        ),
        nullable=False,
        default=SessionStatus.DRAFT,
        server_default=SessionStatus.DRAFT.value,
    )
    company_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["ItemRow"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ItemRow.created_at"
    )
    validation_logs: Mapped[list["ValidationLogRow"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
