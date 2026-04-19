"""
wolvpay — Official Python SDK for the WolvPay cryptocurrency payment API.

Quick start::

    from wolvpay import WolvPayClient

    client = WolvPayClient("your_api_key")
    invoice = client.create_invoice(amount=50.0, currency="USD")
    print(invoice.url)  # hosted payment URL

Webhook verification::

    from wolvpay.webhook import extract_signature, verify
    from wolvpay.exceptions import WebhookError
"""

from .client import WolvPayClient
from .exceptions import ApiError, WebhookError, WolvPayError
from .models import Coin, Invoice, InvoiceList, Pagination, WebhookPayload
from . import webhook

__all__ = [
    "WolvPayClient",
    "WolvPayError",
    "ApiError",
    "WebhookError",
    "Coin",
    "Invoice",
    "InvoiceList",
    "Pagination",
    "WebhookPayload",
    "webhook",
]

__version__ = "1.0.0"
