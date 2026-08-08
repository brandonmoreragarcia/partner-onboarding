"""Dev/test-only utilities. Not part of the partner-facing API contract -- tagged
separately in OpenAPI so it's visually distinct from the real /sessions endpoints,
and the frontend only ever renders a control for this in non-production builds."""

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.database import get_db
from app.models import SessionRow

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/reset", status_code=204)
def reset_session(db: DBSession = Depends(get_db)) -> None:
    db.execute(delete(SessionRow).where(SessionRow.partner_id == settings.partner_id))
    db.commit()
