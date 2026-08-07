"""Provider client: explicit timeout, typed result union — never raises raw HTTP
errors into routes. Wraps the in-process mock today; swapping in a real HTTP call
later only touches this file."""

from app.config import settings
from app.provider_mock import mock_provider_validate
from app.provider_schemas import (
    ProviderInvalid,
    ProviderItem,
    ProviderPartial,
    ProviderResult,
    ProviderUnavailable,
    ProviderValid,
)


class ProviderClient:
    def __init__(self, timeout_seconds: float):
        self._timeout_seconds = timeout_seconds

    def validate(self, account_id: str, api_key: str) -> ProviderResult:
        # The mock resolves synchronously and never actually blocks (see provider_mock.py),
        # so there is nothing for self._timeout_seconds to interrupt today. Kept as the
        # explicit seam CLAUDE.md requires — a real HTTP-backed client would apply it as
        # the request timeout without changing this method's signature or callers.
        response = mock_provider_validate(account_id, api_key)

        if response.status_code == 503:
            return ProviderUnavailable(detail="Provider returned 503")

        status = response.body.get("status")
        if status == "valid":
            return ProviderValid(items=[ProviderItem(**item) for item in response.body["items"]])
        if status == "partial":
            return ProviderPartial(
                items=[ProviderItem(**item) for item in response.body["items"]],
                warnings=response.body["warnings"],
            )
        if status == "invalid":
            return ProviderInvalid(reason=response.body["reason"])

        # Not one of the 4 documented outcomes: a real bug in the mock, not a transient
        # condition — surfaces as an unhandled 500 rather than being folded into
        # ProviderUnavailable, which would mask the defect behind a "safe to retry" state.
        raise RuntimeError(f"Unexpected Provider status field: {status!r}")


provider_client = ProviderClient(timeout_seconds=settings.provider_timeout_seconds)
