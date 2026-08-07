"""Session status groupings shared across state_machine.py and anything else that
needs to know which states a transition is legal from (routes, tests, future scripts)."""

from app.models import SessionStatus

SUBMIT_DETAILS_LEGAL_FROM = (SessionStatus.DRAFT, SessionStatus.DETAILS_OK, SessionStatus.INVALID)
VALIDATE_CLAIMABLE_FROM = (SessionStatus.DETAILS_OK, SessionStatus.UNAVAILABLE)
