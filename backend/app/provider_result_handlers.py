"""One handler per ProviderResult variant, dispatched by apply_validation_result in
state_machine.py. Adding a 5th outcome later means one new function + one dict entry."""

from app.models import SessionStatus, ValidationOutcome
from app.provider_schemas import ProviderInvalid, ProviderPartial, ProviderUnavailable, ProviderValid


def handle_valid(result: ProviderValid):
    return SessionStatus.VALIDATED, [], ValidationOutcome.VALID, None, result.items


def handle_partial(result: ProviderPartial):
    return SessionStatus.VALIDATED, result.warnings, ValidationOutcome.PARTIAL, None, result.items


def handle_invalid(result: ProviderInvalid):
    return SessionStatus.INVALID, [], ValidationOutcome.INVALID, result.reason, None


def handle_unavailable(result: ProviderUnavailable):
    return SessionStatus.UNAVAILABLE, [], ValidationOutcome.UNAVAILABLE, result.detail, None


RESULT_HANDLERS = {
    ProviderValid: handle_valid,
    ProviderPartial: handle_partial,
    ProviderInvalid: handle_invalid,
    ProviderUnavailable: handle_unavailable,
}
