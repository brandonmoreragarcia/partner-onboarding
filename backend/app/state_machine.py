"""Session state transitions. Routes validate input and delegate here — this is the
only place that decides whether a transition is legal and commits the result."""

import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import selectinload

from app.exceptions import NotFoundError, TransitionError
from app.models import ItemRow, SessionRow, SessionStatus, ValidationLogRow, ValidationOutcome
from app.provider_schemas import (
    ProviderInvalid,
    ProviderPartial,
    ProviderResult,
    ProviderUnavailable,
    ProviderValid,
)
from app.schemas import DetailsIn

_DETAILS_LEGAL_FROM = (SessionStatus.DRAFT, SessionStatus.DETAILS_OK, SessionStatus.INVALID)
_VALIDATE_CLAIMABLE_FROM = (SessionStatus.DETAILS_OK, SessionStatus.UNAVAILABLE)


def _get_or_404(db: DBSession, session_id: uuid.UUID) -> SessionRow:
    # selectinload: this session's items are read after the ORM session that loaded it
    # closes (see routers/sessions.py's validate handler) — without eager loading here,
    # accessing .items on a detached instance would raise DetachedInstanceError.
    #
    # populate_existing: apply_validation_result calls _get_or_404 twice in the same DB
    # session — once before mutating items, once after committing the mutation. Without
    # this, SQLAlchemy's identity map returns the second call's SessionRow with its
    # *already-loaded* items collection from the first call, silently stale even though
    # the scalar columns (status, etc.) do refresh. Caught by curl showing items: [] on
    # POST /validate immediately followed by a GET on the same session showing the real
    # items — same DB row, two different responses.
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
    if session.status not in _DETAILS_LEGAL_FROM:
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
        .where(SessionRow.id == session_id, SessionRow.status.in_(_VALIDATE_CLAIMABLE_FROM))
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

    if isinstance(result, (ProviderValid, ProviderPartial)):
        session.status = SessionStatus.VALIDATED
        session.warnings = result.warnings if isinstance(result, ProviderPartial) else []
        session.last_error = None
        outcome = ValidationOutcome.PARTIAL if isinstance(result, ProviderPartial) else ValidationOutcome.VALID
        detail = None
        db.execute(delete(ItemRow).where(ItemRow.session_id == session_id))
        for item in result.items:
            db.add(ItemRow(session_id=session_id, external_id=item.id, name=item.name))
    elif isinstance(result, ProviderInvalid):
        session.status = SessionStatus.INVALID
        session.warnings = []
        session.last_error = result.reason
        outcome = ValidationOutcome.INVALID
        detail = result.reason
    elif isinstance(result, ProviderUnavailable):
        session.status = SessionStatus.UNAVAILABLE
        session.warnings = []
        session.last_error = result.detail
        outcome = ValidationOutcome.UNAVAILABLE
        detail = result.detail
    else:
        raise AssertionError(f"Unhandled ProviderResult variant: {result!r}")

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
