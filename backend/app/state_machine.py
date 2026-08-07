"""Session state transitions. Routes validate input and delegate here — this is the
only place that decides whether a transition is legal and commits the result."""

import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import selectinload

from app.constants import SUBMIT_DETAILS_LEGAL_FROM, VALIDATE_CLAIMABLE_FROM
from app.exceptions import NotFoundError, TransitionError
from app.models import ItemRow, SessionRow, SessionStatus, ValidationLogRow
from app.provider_result_handlers import RESULT_HANDLERS
from app.provider_schemas import ProviderResult
from app.schemas import DetailsIn


def _get_or_404(db: DBSession, session_id: uuid.UUID) -> SessionRow:
    # selectinload: caller's DB session may close before serialization (routers/sessions.py's
    # validate handler) — without eager loading, accessing .items would raise DetachedInstanceError.
    # populate_existing: forces a fresh read so a 2nd call in the same session doesn't return
    # items stale from the 1st (bug + repro in ai-log/02-backend.md).
    session = db.execute(
        select(SessionRow)
        .where(SessionRow.id == session_id)
        .options(selectinload(SessionRow.items))
        .execution_options(populate_existing=True)
    ).scalar_one_or_none()
    if session is None:
        raise NotFoundError(f"Session {session_id} not found")
    return session


def submit_details(db: DBSession, session_id: uuid.UUID, payload: DetailsIn) -> SessionRow:
    session = _get_or_404(db, session_id)
    if session.status not in SUBMIT_DETAILS_LEGAL_FROM:
        raise TransitionError(f"Cannot submit details while status is {session.status.value}")

    session.company_name = payload.company_name
    session.account_id = payload.account_id
    session.api_key = payload.api_key
    session.status = SessionStatus.DETAILS_OK
    session.last_error = None
    db.commit()
    return _get_or_404(db, session_id)


def claim_validation(db: DBSession, session_id: uuid.UUID) -> tuple[SessionRow, bool]:
    """Atomically claims the right to call the Provider. Returns (session, claimed).

    claimed=True  -> caller must call the Provider, then call apply_validation_result.
    claimed=False -> caller must NOT call the Provider. Either a concurrent duplicate
                     (session is already VALIDATING — return it as-is, 200) or the
                     session was never in a claimable state (raised as 409 below).
    """
    result = db.execute(
        update(SessionRow)
        .where(SessionRow.id == session_id, SessionRow.status.in_(VALIDATE_CLAIMABLE_FROM))
        .values(status=SessionStatus.VALIDATING, last_error=None)
        .returning(SessionRow.id)
    )
    claimed = result.scalar_one_or_none() is not None
    db.commit()

    session = _get_or_404(db, session_id)
    if claimed or session.status == SessionStatus.VALIDATING:
        return session, claimed
    raise TransitionError(f"Cannot validate while status is {session.status.value}")


def apply_validation_result(db: DBSession, session_id: uuid.UUID, result: ProviderResult) -> SessionRow:
    session = _get_or_404(db, session_id)
    if session.status != SessionStatus.VALIDATING:
        raise TransitionError(f"Cannot apply validation result while status is {session.status.value}")

    handler = RESULT_HANDLERS[type(result)]
    session.status, session.warnings, outcome, detail, items = handler(result)
    session.last_error = detail
    if items is not None:
        db.execute(delete(ItemRow).where(ItemRow.session_id == session_id))
        
        for item in items:
            db.add(ItemRow(session_id=session_id, external_id=item.id, name=item.name))

    db.add(ValidationLogRow(session_id=session_id, outcome=outcome, detail=detail))
    db.commit()
    return _get_or_404(db, session_id)


def go_live(db: DBSession, session_id: uuid.UUID) -> SessionRow:
    result = db.execute(
        update(SessionRow)
        .where(SessionRow.id == session_id, SessionRow.status == SessionStatus.VALIDATED)
        .values(status=SessionStatus.LIVE)
        .returning(SessionRow.id)
    )
    claimed = result.scalar_one_or_none() is not None
    db.commit()

    session = _get_or_404(db, session_id)
    if claimed or session.status == SessionStatus.LIVE:
        return session
    raise TransitionError(f"Cannot go live while status is {session.status.value}")
