"""
Example: Creating invoices with wolvpay-python.
"""

import os
from wolvpay import WolvPayClient
from wolvpay.exceptions import ApiError, WolvPayError

client = WolvPayClient(os.environ.get("WOLVPAY_API_KEY", "your_api_key_here"))

# ─────────────────────────────────────────────
# Example 1: Hosted invoice
# ─────────────────────────────────────────────
try:
    invoice = client.create_invoice(
        amount=50.0,
        currency="USD",
        description="Order #1001",
        white_label=False,
        redirect_url="https://example.com/thank-you",
    )

    print("Hosted invoice created!")
    print(f"Invoice ID : {invoice.invoice_id}")
    print(f"Pay URL    : {invoice.url}")
    print(f"Status     : {invoice.status}")

except ApiError as e:
    print(f"API error [{e.status_code}]: {e}")
except WolvPayError as e:
    print(f"SDK error: {e}")

print()

# ─────────────────────────────────────────────
# Example 2: Retrieve an invoice
# ─────────────────────────────────────────────
try:
    invoice = client.get_invoice("INVabc123def456")

    print(f"Status: {invoice.status}")

    if invoice.status == "AWAITING_PAYMENT":
        print(f"Send {invoice.coin_amount} {(invoice.coin or '').upper()}")
        print(f"To:   {invoice.coin_address}")

except ApiError as e:
    print(f"API error [{e.status_code}]: {e}")

print()

# ─────────────────────────────────────────────
# Example 3: List invoices
# ─────────────────────────────────────────────
try:
    result = client.list_invoices(page=1, limit=3)

    print(f"Total invoices: {result.pagination.total_items}")
    for inv in result.invoices:
        print(f"  {inv.invoice_id} | {inv.status} | ${inv.amount}")

except ApiError as e:
    print(f"API error [{e.status_code}]: {e}")

# ─────────────────────────────────────────────
# Context manager usage
# ─────────────────────────────────────────────
with WolvPayClient(os.environ.get("WOLVPAY_API_KEY", "your_api_key_here")) as c:
    coins = c.get_coins()
    for coin in coins:
        print(f"  {coin.coin:<18} {coin.name} — ${coin.prices.get('USD', 'N/A')}")
