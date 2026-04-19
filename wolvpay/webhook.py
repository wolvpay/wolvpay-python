from __future__ import annotations

import hashlib
import hmac
import json
from typing import Dict, Optional

from .exceptions import WebhookError
from .models import WebhookPayload

# All common header-name variants WolvPay may send.
_SIGNATURE_HEADER_VARIANTS = [
    "X-WolvPay-Signature",
    "X-Wolvpay-Signature",
    "x-wolvpay-signature",
    "X-WOLVPAY-SIGNATURE",
]


def extract_signature(headers: Dict[str, str]) -> str:
    """
    Extract the WolvPay webhook signature from a headers dictionary.

    Checks all common casing variants since HTTP servers may normalise headers.

    Args:
        headers: A dict of HTTP headers (e.g. ``request.headers`` in Flask/Django).

    Returns:
        The signature string, or an empty string if not found.
    """
    for variant in _SIGNATURE_HEADER_VARIANTS:
        value = headers.get(variant) or headers.get(variant.lower())
        if value:
            return value
    return ""


def verify(raw_body: str | bytes, signature: str, secret: str) -> WebhookPayload:
    """
    Verify a WolvPay webhook signature and decode the payload.

    **Important:** Pass the raw request body *before* any JSON parsing.
    Re-serialising a parsed object will change whitespace and break the hash.

    Args:
        raw_body:  The raw HTTP request body (bytes or str).
        signature: The value of the ``X-WolvPay-Signature`` header.
        secret:    Your WolvPay webhook secret from the dashboard.

    Returns:
        A :class:`~wolvpay.models.WebhookPayload` instance with the verified event data.

    Raises:
        WebhookError: If the signature is missing, invalid, or the payload is malformed.

    Example (Flask)::

        from flask import Flask, request
        from wolvpay.webhook import extract_signature, verify
        from wolvpay.exceptions import WebhookError

        app = Flask(__name__)

        @app.route('/webhooks/wolvpay', methods=['POST'])
        def wolvpay_webhook():
            raw_body = request.get_data()
            signature = extract_signature(dict(request.headers))
            try:
                event = verify(raw_body, signature, os.environ['WOLVPAY_WEBHOOK_SECRET'])
            except WebhookError:
                return 'Unauthorized', 401

            if event.status == 'PAID':
                fulfill_order(event.invoice_id)

            return 'OK', 200
    """
    if not signature:
        raise WebhookError("Missing X-WolvPay-Signature header.")

    if not secret:
        raise WebhookError("Webhook secret is required.")

    body_bytes = raw_body if isinstance(raw_body, bytes) else raw_body.encode("utf-8")
    secret_bytes = secret.encode("utf-8")

    computed = hmac.new(secret_bytes, body_bytes, hashlib.sha256).hexdigest()

    # Use hmac.compare_digest to prevent timing attacks.
    if not hmac.compare_digest(computed, signature):
        raise WebhookError("Webhook signature verification failed.")

    if not raw_body:
        raise WebhookError("Webhook payload is empty.")

    try:
        data = json.loads(body_bytes)
    except json.JSONDecodeError as exc:
        raise WebhookError(f"Invalid webhook payload: failed to parse JSON — {exc}") from exc

    if not isinstance(data, dict):
        raise WebhookError("Invalid webhook payload: expected a JSON object.")

    return WebhookPayload.from_dict(data)
