"""
wolvpay.exceptions
~~~~~~~~~~~~~~~~~~
Custom exception types raised by the WolvPay Python SDK.

All exceptions inherit from :class:`WolvPayError` so you can catch everything
with a single ``except WolvPayError`` if needed.
"""
from __future__ import annotations


class WolvPayError(Exception):
    """Base exception for all WolvPay SDK errors."""


class ApiError(WolvPayError):
    """Raised when the WolvPay API returns a 4xx or 5xx HTTP response."""

    def __init__(self, message: str, status_code: int, error_data: dict | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_data: dict = error_data or {}

    def __repr__(self) -> str:
        return f"ApiError(status_code={self.status_code}, message={str(self)!r})"


class WebhookError(WolvPayError):
    """Raised when webhook signature verification fails or the payload is malformed."""
