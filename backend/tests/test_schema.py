import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import ItemRow, SessionRow, SessionStatus


def test_session_status_and_warnings_default(db):
    session = SessionRow(partner_id="p-defaults")
    db.add(session)
    db.flush()

    assert session.status == SessionStatus.DRAFT
    assert session.warnings == []
    assert session.api_key is None


def test_status_check_constraint_rejects_invalid_value_at_db_level(db):
    # Bypasses the ORM's Python-side Enum validation on purpose: this proves the CHECK
    # constraint itself rejects bad data, not just SQLAlchemy's client-side type.
    with pytest.raises(IntegrityError):
        db.execute(
            text(
                "INSERT INTO sessions (id, partner_id, status) "
                "VALUES (:id, :partner_id, :status)"
            ),
            {"id": uuid.uuid4(), "partner_id": "p-bad-status", "status": "NOT_A_STATUS"},
        )
        db.flush()


def test_partner_id_unique_constraint(db):
    db.add(SessionRow(partner_id="p-dup"))
    db.flush()
    db.add(SessionRow(partner_id="p-dup"))
    with pytest.raises(IntegrityError):
        db.flush()


def test_items_unique_per_session_and_external_id(db):
    session = SessionRow(partner_id="p-items")
    db.add(session)
    db.flush()

    db.add(ItemRow(session_id=session.id, external_id="itm_1", name="Item One"))
    db.flush()
    db.add(ItemRow(session_id=session.id, external_id="itm_1", name="Item One (dup)"))
    with pytest.raises(IntegrityError):
        db.flush()


def test_items_cascade_delete_with_session(db):
    session = SessionRow(partner_id="p-cascade")
    db.add(session)
    db.flush()
    db.add(ItemRow(session_id=session.id, external_id="itm_1", name="Item One"))
    db.flush()

    db.delete(session)
    db.flush()

    remaining = db.execute(
        text("SELECT count(*) FROM items WHERE session_id = :id"), {"id": session.id}
    ).scalar_one()
    assert remaining == 0


def test_validation_log_outcome_check_constraint(db):
    session = SessionRow(partner_id="p-vlog")
    db.add(session)
    db.flush()

    with pytest.raises(IntegrityError):
        db.execute(
            text(
                "INSERT INTO validation_log (id, session_id, outcome) "
                "VALUES (:id, :session_id, :outcome)"
            ),
            {"id": uuid.uuid4(), "session_id": session.id, "outcome": "not-a-real-outcome"},
        )
        db.flush()
