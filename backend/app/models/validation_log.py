import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.session import SessionRow


class ValidationOutcome(str, enum.Enum):
    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


class ValidationLogRow(Base):
    """Insert-only audit trail of validate() outcomes. Not part of the API response
    contract today; exists for debugging and a future 'last N attempts' read endpoint."""

    __tablename__ = "validation_log"
    __table_args__ = (Index("ix_validation_log_session_created", "session_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    outcome: Mapped[ValidationOutcome] = mapped_column(
        SAEnum(
            ValidationOutcome,
            name="validation_outcome",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda cls: [member.value for member in cls],
        ),
        nullable=False,
    )
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped["SessionRow"] = relationship(back_populates="validation_logs")
