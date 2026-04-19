# wolvpay-python

Official Python SDK for the [WolvPay](https://wolvpay.com) cryptocurrency payment API.

[![PyPI version](https://img.shields.io/pypi/v/wolvpay.svg)](https://pypi.org/project/wolvpay/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.8-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## What is WolvPay?

[WolvPay](https://wolvpay.com) is a secure, low-fee cryptocurrency payment processor built for developers and businesses. It lets you accept payments in Bitcoin, Litecoin, USDT, USDC, and many other cryptocurrencies — either through a **hosted payment page** (zero front-end work) or a fully **white-label flow** where you control the entire UI.

This is the **official Python SDK**. It wraps the WolvPay REST API so you can create and manage invoices, verify webhook signatures, and handle payment events — compatible with any Python web framework including Flask, Django, and FastAPI.

> **API docs:** [wolvpay.com/docs](https://wolvpay.com/docs)  
> **Dashboard:** [wolvpay.com/home](https://wolvpay.com/home)  
> **Discord:** [wolvpay.com/discord](https://wolvpay.com/discord)

---

## Requirements

- Python 3.8 or higher
- [`requests`](https://docs.python-requests.org) >= 2.28

---

## Installation

```bash
pip install wolvpay
```

---

## Quick Start

```python
import os
from wolvpay import WolvPayClient

client = WolvPayClient(os.environ["WOLVPAY_API_KEY"])

# Create a hosted invoice
invoice = client.create_invoice(
    amount=50.0,
    currency="USD",
    white_label=False,
    redirect_url="https://example.com/thank-you",
)

print(invoice.url)  # https://invoices.wolvpay.com/INV...
# Redirect user to invoice.url
```

---

## Configuration

```python
from wolvpay import WolvPayClient

client = WolvPayClient(api_key="your_api_key", timeout=30)
```

The client also supports use as a **context manager** to auto-close the HTTP session:

```python
with WolvPayClient(os.environ["WOLVPAY_API_KEY"]) as client:
    coins = client.get_coins()
```

> **Security:** Never hard-code your API key. Use environment variables.

---

## API Reference

### Coins

#### `client.get_coins()`

Retrieve all supported cryptocurrencies and their current exchange rates.

```python
coins = client.get_coins()

for coin in coins:
    print(f"{coin.name}: ${coin.prices.get('USD')}")
```

**Returns:** `List[Coin]`

---

### Invoices

#### `client.create_invoice(...)`

Create a new payment invoice.

```python
# Hosted invoice — customer pays on WolvPay's page
invoice = client.create_invoice(
    amount=100.0,
    currency="USD",
    description="Order #1234",
    white_label=False,
    redirect_url="https://example.com/thank-you",
)
# → invoice.url is the hosted payment page

# White-label — show payment details in your own UI
invoice = client.create_invoice(
    amount=100.0,
    currency="EUR",
    coin="ltc",
    white_label=True,
)
# → invoice.coin_address and invoice.coin_amount

# Let the customer choose the coin
invoice = client.create_invoice(amount=100.0)
# → invoice.status == 'AWAITING_SELECTION'
# → invoice.available_coins lists supported options
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `amount` | `float` | — | Payment amount (required). |
| `currency` | `str` | `"USD"` | Fiat currency code. |
| `coin` | `str` | `None` | Crypto code (e.g. `"btc"`). Omit for AWAITING_SELECTION. |
| `description` | `str` | `None` | Invoice description. |
| `white_label` | `bool` | `True` | `True` = white-label, `False` = hosted. |
| `redirect_url` | `str` | `None` | Post-payment redirect URL. |

**Returns:** `Invoice`

---

#### `client.get_invoice(invoice_id)`

Retrieve a specific invoice by ID.

```python
invoice = client.get_invoice("INVabc123def456")

if invoice.status == "AWAITING_PAYMENT":
    print(f"Send {invoice.coin_amount} {invoice.coin.upper()}")
    print(f"To: {invoice.coin_address}")
```

**Returns:** `Invoice`

---

#### `client.update_invoice(invoice_id, coin)`

Select a cryptocurrency for a white-label invoice in `AWAITING_SELECTION` status.

```python
updated = client.update_invoice("INVabc123def456", "ltc")
print(updated.coin_address)  # LTC payment address
```

**Returns:** `Invoice`

---

#### `client.list_invoices(page=1, limit=3)`

List all invoices with pagination.

```python
result = client.list_invoices(page=1, limit=3)

for invoice in result.invoices:
    print(invoice.invoice_id, invoice.status)

print(f"Page {result.pagination.current_page} of {result.pagination.total_pages}")
```

**Returns:** `InvoiceList`

---

## Webhooks

WolvPay sends POST requests to your endpoint when invoice status changes.
All requests come from IP **128.140.76.192**.

### Flask

```python
from flask import Flask, request, abort
from wolvpay.webhook import extract_signature, verify
from wolvpay.exceptions import WebhookError

app = Flask(__name__)

@app.route("/webhooks/wolvpay", methods=["POST"])
def wolvpay_webhook():
    raw_body = request.get_data()           # MUST get raw bytes before parsing
    signature = extract_signature(dict(request.headers))

    try:
        event = verify(raw_body, signature, os.environ["WOLVPAY_WEBHOOK_SECRET"])
    except WebhookError:
        abort(401)

    if event.status == "PAID":
        fulfill_order(event.invoice_id)

    return "OK", 200
```

### Django

```python
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wolvpay.webhook import extract_signature, verify
from wolvpay.exceptions import WebhookError

@csrf_exempt
def wolvpay_webhook(request):
    raw_body = request.body
    signature = extract_signature(dict(request.headers))

    try:
        event = verify(raw_body, signature, settings.WOLVPAY_WEBHOOK_SECRET)
    except WebhookError:
        return HttpResponse(status=401)

    if event.status == "PAID":
        fulfill_order(event.invoice_id)

    return HttpResponse("OK")
```

### Webhook Payload (`WebhookPayload`)

| Field | Type | Description |
|---|---|---|
| `invoice_id` | `str` | Invoice ID. |
| `amount` | `float` | Fiat amount. |
| `status` | `str` | Invoice status. |
| `coin` | `str` | Cryptocurrency used. |
| `coin_amount` | `float` | Expected crypto amount. |
| `coin_received` | `float` | Actual crypto received. |
| `coin_address` | `str` | Payment address. |
| `description` | `str \| None` | Invoice description. |
| `redirect_url` | `str \| None` | Post-payment redirect URL. |
| `created_at` | `str` | Creation timestamp. |

---

## Error Handling

```python
from wolvpay.exceptions import ApiError, WolvPayError

try:
    invoice = client.create_invoice(amount=50.0)
except ApiError as e:
    print(e.status_code)   # HTTP status code (400, 401, 404, 429, etc.)
    print(str(e))          # Human-readable message
    print(e.error_data)    # Raw error dict from the API
except WolvPayError as e:
    print(str(e))          # Network or parse error
```

| Exception | When |
|---|---|
| `WolvPayError` | Base — network failures, JSON parse errors |
| `ApiError` | API returned 4xx or 5xx |
| `WebhookError` | Signature verification failed |

---

## Invoice Status Reference

| Status | Description |
|---|---|
| `AWAITING_SELECTION` | Customer has not selected a cryptocurrency. |
| `AWAITING_PAYMENT` | Crypto selected, waiting for payment. |
| `CONFIRMING_PAYMENT` | Payment detected, waiting for confirmations. |
| `PAID` | Payment confirmed and complete. |
| `UNDERPAID` | Payment received but below required amount. |
| `EXPIRED` | Invoice expired without payment. |

---

## Examples

See the [`examples/`](examples/) directory:

- [`create_invoice.py`](examples/create_invoice.py) — Hosted invoice creation
- [`white_label.py`](examples/white_label.py) — White-label flow with coin selection
- [`webhook_handler.py`](examples/webhook_handler.py) — Flask + Django webhook handlers

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## Links

- [WolvPay Website](https://wolvpay.com)
- [API Documentation](https://wolvpay.com/docs)
- [Dashboard](https://wolvpay.com/home)
- [Discord Community](https://wolvpay.com/discord)
- [Report an Issue](https://github.com/wolvpay/wolvpay-python/issues)

---

## License

MIT — see [LICENSE](LICENSE).
