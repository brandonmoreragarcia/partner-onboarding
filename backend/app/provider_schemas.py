"""Typed result of a Provider validation call. Internal contract between
provider_client.py and state_machine.py — never serialized directly to the frontend."""

from typing import Literal

from pydantic import BaseModel


class ProviderItem(BaseModel):
    id: str
    name: str


class ProviderValid(BaseModel):
    kind: Literal["valid"] = "valid"
    items: list[ProviderItem]


class ProviderPartial(BaseModel):
    kind: Literal["partial"] = "partial"
    items: list[ProviderItem]
    warnings: list[str]


class ProviderInvalid(BaseModel):
    kind: Literal["invalid"] = "invalid"
    reason: str


class ProviderUnavailable(BaseModel):
    kind: Literal["unavailable"] = "unavailable"
    detail: str


ProviderResult = ProviderValid | ProviderPartial | ProviderInvalid | ProviderUnavailable
