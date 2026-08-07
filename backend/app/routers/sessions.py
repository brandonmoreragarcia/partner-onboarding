import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import selectinload

from app import state_machine
from app.config import settings
from app.database import SessionLocal, get_db
from app.exceptions import NotFoundError
from app.models import SessionRow
from app.provider_client import provider_client
from app.schemas import DetailsIn, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut)
def create_or_resume_session(response: Response, db: DBSession = Depends(get_db)) -> SessionRow:
    created_id = db.execute(
        pg_insert(SessionRow)
        .values(partner_id=settings.partner_id)
        .on_conflict_do_nothing(index_elements=["partner_id"])
        .returning(SessionRow.id)
    ).scalar_one_or_none()
    db.commit()

    response.status_code = 201 if created_id is not None else 200
    return db.execute(
        select(SessionRow)
        .where(SessionRow.partner_id == settings.partner_id)
        .options(selectinload(SessionRow.items))
    ).scalar_one()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: uuid.UUID, db: DBSession = Depends(get_db)) -> SessionRow:
    session = db.execute(
        select(SessionRow).where(SessionRow.id == session_id).options(selectinload(SessionRow.items))
    ).scalar_one_or_none()
    if session is None:
        raise NotFoundError(f"Session {session_id} not found")
    return session


@router.post("/{session_id}/details", response_model=SessionOut)
def submit_details(session_id: uuid.UUID, payload: DetailsIn, db: DBSession = Depends(get_db)) -> SessionRow:
    return state_machine.submit_details(db, session_id, payload)


@router.post("/{session_id}/validate", response_model=SessionOut)
def trigger_validation(session_id: uuid.UUID) -> SessionRow:
    # Deliberately not Depends(get_db): this is the one route that opens two separate,
    # short-lived DB sessions with the Provider call between them holding no DB connection
    # at all. Do not "simplify" this back to a single session — see CLAUDE.md §10.
    with SessionLocal() as db1:
        session, claimed = state_machine.claim_validation(db1, session_id)

    if not claimed:
        return session

    result = provider_client.validate(session.account_id, session.api_key)

    with SessionLocal() as db2:
        return state_machine.apply_validation_result(db2, session_id, result)


@router.post("/{session_id}/go-live", response_model=SessionOut)
def go_live(session_id: uuid.UUID, db: DBSession = Depends(get_db)) -> SessionRow:
    return state_machine.go_live(db, session_id)
