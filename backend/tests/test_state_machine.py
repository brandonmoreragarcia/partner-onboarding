import threading
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app import state_machine
from app.exceptions import NotFoundError, TransitionError
from app.models import SessionRow, SessionStatus, ValidationLogRow, ValidationOutcome
from app.provider_schemas import ProviderInvalid, ProviderItem, ProviderPartial, ProviderUnavailable, ProviderValid
from app.schemas import DetailsIn

ALL_STATUSES = list(SessionStatus)
_DETAILS_PAYLOAD = DetailsIn(companyName="Acme", accountId="acct_1", apiKey="valid-key")


def _make_session(db, status: SessionStatus) -> SessionRow:
    session = SessionRow(partner_id=f"p-{uuid.uuid4()}", status=status)
    db.add(session)
    db.commit()
    return session


# --- submit_details ---


@pytest.mark.parametrize("status", [SessionStatus.DRAFT, SessionStatus.DETAILS_OK, SessionStatus.INVALID])
def test_submit_details_legal_from(db, status):
    session = _make_session(db, status)
    result = state_machine.submit_details(db, session.id, _DETAILS_PAYLOAD)
    assert result.status == SessionStatus.DETAILS_OK
    assert result.company_name == "Acme"


@pytest.mark.parametrize(
    "status",
    [s for s in ALL_STATUSES if s not in (SessionStatus.DRAFT, SessionStatus.DETAILS_OK, SessionStatus.INVALID)],
)
def test_submit_details_illegal_from(db, status):
    session = _make_session(db, status)
    with pytest.raises(TransitionError):
        state_machine.submit_details(db, session.id, _DETAILS_PAYLOAD)


def test_submit_details_unknown_session_404(db):
    with pytest.raises(NotFoundError):
        state_machine.submit_details(db, uuid.uuid4(), _DETAILS_PAYLOAD)


def test_submit_details_clears_previous_error(db):
    session = _make_session(db, SessionStatus.INVALID)
    session.last_error = "bad credentials"
    db.commit()
    result = state_machine.submit_details(db, session.id, _DETAILS_PAYLOAD)
    assert result.last_error is None


def test_submit_details_is_idempotent(db):
    session = _make_session(db, SessionStatus.DRAFT)
    state_machine.submit_details(db, session.id, _DETAILS_PAYLOAD)
    result = state_machine.submit_details(db, session.id, _DETAILS_PAYLOAD)
    assert result.status == SessionStatus.DETAILS_OK


# --- claim_validation ---


@pytest.mark.parametrize("status", [SessionStatus.DETAILS_OK, SessionStatus.UNAVAILABLE])
def test_claim_validation_legal_from(db, status):
    session = _make_session(db, status)
    result, claimed = state_machine.claim_validation(db, session.id)
    assert claimed is True
    assert result.status == SessionStatus.VALIDATING


@pytest.mark.parametrize(
    "status",
    [s for s in ALL_STATUSES if s not in (SessionStatus.DETAILS_OK, SessionStatus.UNAVAILABLE, SessionStatus.VALIDATING)],
)
def test_claim_validation_illegal_from(db, status):
    session = _make_session(db, status)
    with pytest.raises(TransitionError):
        state_machine.claim_validation(db, session.id)


def test_claim_validation_duplicate_while_validating_is_safe_noop(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    state_machine.claim_validation(db, session.id)

    result, claimed = state_machine.claim_validation(db, session.id)
    assert claimed is False
    assert result.status == SessionStatus.VALIDATING


# --- apply_validation_result: all 4 Provider outcomes ---


def test_apply_validation_result_valid(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    state_machine.claim_validation(db, session.id)

    result = state_machine.apply_validation_result(
        db, session.id, ProviderValid(items=[ProviderItem(id="itm_1", name="Item One")])
    )

    assert result.status == SessionStatus.VALIDATED
    assert result.warnings == []
    assert result.last_error is None
    assert [i.external_id for i in result.items] == ["itm_1"]

    log = db.execute(select(ValidationLogRow).where(ValidationLogRow.session_id == session.id)).scalar_one()
    assert log.outcome == ValidationOutcome.VALID


def test_apply_validation_result_partial(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    state_machine.claim_validation(db, session.id)

    result = state_machine.apply_validation_result(
        db,
        session.id,
        ProviderPartial(items=[ProviderItem(id="itm_1", name="Item One")], warnings=["itm_2 unverifiable"]),
    )

    assert result.status == SessionStatus.VALIDATED
    assert result.warnings == ["itm_2 unverifiable"]

    log = db.execute(select(ValidationLogRow).where(ValidationLogRow.session_id == session.id)).scalar_one()
    assert log.outcome == ValidationOutcome.PARTIAL


def test_apply_validation_result_invalid(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    state_machine.claim_validation(db, session.id)

    result = state_machine.apply_validation_result(db, session.id, ProviderInvalid(reason="bad key"))

    assert result.status == SessionStatus.INVALID
    assert result.last_error == "bad key"
    assert result.items == []


def test_apply_validation_result_unavailable_leaves_session_retryable(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    state_machine.claim_validation(db, session.id)

    result = state_machine.apply_validation_result(db, session.id, ProviderUnavailable(detail="503"))
    assert result.status == SessionStatus.UNAVAILABLE
    assert result.last_error == "503"

    retried, claimed = state_machine.claim_validation(db, session.id)
    assert claimed is True
    assert retried.status == SessionStatus.VALIDATING


def test_apply_validation_result_illegal_when_not_validating(db):
    session = _make_session(db, SessionStatus.DETAILS_OK)
    with pytest.raises(TransitionError):
        state_machine.apply_validation_result(db, session.id, ProviderValid(items=[]))


# --- go_live ---


def test_go_live_from_validated(db):
    session = _make_session(db, SessionStatus.VALIDATED)
    result = state_machine.go_live(db, session.id)
    assert result.status == SessionStatus.LIVE


@pytest.mark.parametrize("status", [s for s in ALL_STATUSES if s != SessionStatus.VALIDATED and s != SessionStatus.LIVE])
def test_go_live_illegal_from(db, status):
    session = _make_session(db, status)
    with pytest.raises(TransitionError):
        state_machine.go_live(db, session.id)


def test_go_live_is_idempotent_no_duplicate_write(db):
    session = _make_session(db, SessionStatus.VALIDATED)
    first = state_machine.go_live(db, session.id)
    second = state_machine.go_live(db, session.id)

    assert second.status == SessionStatus.LIVE
    assert first.updated_at == second.updated_at  # proves the 2nd call performed no write


def test_go_live_failed_commit_leaves_no_partial_state(db, monkeypatch):
    """go_live is a single atomic UPDATE -- there's no multi-write sequence to fail
    partway through. This instead proves that if the commit itself fails, nothing gets
    persisted: the session is left at VALIDATED, not some in-between state."""
    session = _make_session(db, SessionStatus.VALIDATED)

    def failing_commit():
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(db, "commit", failing_commit)

    with pytest.raises(RuntimeError):
        state_machine.go_live(db, session.id)

    db.rollback()
    reloaded = state_machine._get_or_404(db, session.id)
    assert reloaded.status == SessionStatus.VALIDATED


# --- true concurrency: two independent DB sessions, not the shared per-test fixture ---


def test_go_live_concurrent_calls_only_one_actually_writes(engine):
    """Reproduces the exact race a naive read-then-write go_live would suffer from,
    against two real, independent DB sessions racing on the same row."""
    SessionForThread = sessionmaker(bind=engine)

    with SessionForThread() as setup_db:
        session = SessionRow(partner_id=f"race-{uuid.uuid4()}", status=SessionStatus.VALIDATED)
        setup_db.add(session)
        setup_db.commit()
        session_id = session.id

    results: list = []
    barrier = threading.Barrier(2)

    def call_go_live():
        barrier.wait()  # maximize the chance both threads hit the UPDATE at the same instant
        with SessionForThread() as thread_db:
            results.append(state_machine.go_live(thread_db, session_id).updated_at)

    threads = [threading.Thread(target=call_go_live) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    try:
        assert len(results) == 2
        assert results[0] == results[1]  # identical timestamp -> only one real write happened
    finally:
        with SessionForThread() as cleanup_db:
            cleanup_db.execute(
                SessionRow.__table__.delete().where(SessionRow.id == session_id)
            )
            cleanup_db.commit()
