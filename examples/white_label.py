"""
Example: White-label flow with coin selection.
"""

import os
from wolvpay import WolvPayClient
from wolvpay.exceptions import ApiError

client = WolvPayClient(os.environ.get("WOLVPAY_API_KEY", "your_api_key_here"))

# ─────────────────────────────────────────────
# Step 1: Create invoice without a coin.
# Customer will choose the cryptocurrency.
# ─────────────────────────────────────────────
try:
    invoice = client.create_invoice(
        amount=100.0,
        currency="EUR",
        description="Deposit for user #42",
        white_label=True,
    )

    print("Invoice created (awaiting coin selection)")
    print(f"Invoice ID     : {invoice.invoice_id}")
    print(f"Status         : {invoice.status}")  # AWAITING_SELECTION
    print(f"Available coins: {', '.join(invoice.available_coins)}")

except ApiError as e:
    print(f"API error [{e.status_code}]: {e}")
    raise SystemExit(1)

print()

# ─────────────────────────────────────────────
# Step 2: Customer picks "ltc".
# Update the invoice with the selected coin.
# ─────────────────────────────────────────────
try:
    updated = client.update_invoice(invoice.invoice_id, "ltc")

    print("Coin selected!")
    print(f"Status      : {updated.status}")  # AWAITING_PAYMENT
    print(f"Send        : {updated.coin_amount} {(updated.coin or '').upper()}")
    print(f"To address  : {updated.coin_address}")

except ApiError as e:
    print(f"API error [{e.status_code}]: {e}")
