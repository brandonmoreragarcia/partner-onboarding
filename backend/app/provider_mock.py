"""In-process fake Provider. Magic apiKey values select the outcome — see README for the
full table. A plain function call, not a real HTTP round-trip: BRIEF.md explicitly allows
'in-process fake' and this avoids the async/sync transport mismatch a real ASGI-mounted
mock would introduce for no real benefit at this scope."""

from dataclasses import dataclass

from app.provider_schemas import ProviderItem

_ITEMS = [ProviderItem(id="itm_1", name="Item One"), ProviderItem(id="itm_2", name="Item Two")]


@dataclass
class MockResponse:
    status_code: int
    body: dict


def mock_provider_validate(account_id: str, api_key: str) -> MockResponse:
    if api_key == "invalid-key":
        return MockResponse(200, {"status": "invalid", "reason": "The provided API key was rejected"})

    if api_key == "timeout-key":
        # Returns 503 immediately rather than actually blocking, so the app and its tests
        # stay fast and deterministic — the real failure mode being exercised is how the
        # client and state machine handle a 503, not literal wall-clock latency.
        return MockResponse(503, {})

    if api_key == "partial-key":
        return MockResponse(
            200,
            {
                "status": "partial",
                "items": [item.model_dump() for item in _ITEMS],
                "warnings": [f"Item {_ITEMS[1].id} could not be verified"],
            },
        )

    # valid-key, or any other value (documented fallback in the README).
    return MockResponse(200, {"status": "valid", "items": [item.model_dump() for item in _ITEMS]})
