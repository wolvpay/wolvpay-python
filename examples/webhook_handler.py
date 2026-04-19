"""
Example: Webhook handler for Flask.

Install Flask: pip install flask
Run with: flask --app webhook_handler run
"""

import os
from flask import Flask, request, abort
from wolvpay.webhook import extract_signature, verify
from wolvpay.exceptions import WebhookError

app = Flask(__name__)

WOLVPAY_WEBHOOK_SECRET = os.environ.get("WOLVPAY_WEBHOOK_SECRET", "your_webhook_secret_here")


@app.route("/webhooks/wolvpay", methods=["POST"])
def wolvpay_webhook():
    # Read the raw body BEFORE any framework parsing.
    raw_body = request.get_data()
    headers = dict(request.headers)
    signature = extract_signature(headers)

    try:
        event = verify(raw_body, signature, WOLVPAY_WEBHOOK_SECRET)
    except WebhookError as e:
        app.logger.warning(f"[WolvPay] Webhook verification failed: {e}")
        abort(401)

    invoice_id = event.invoice_id
    status = event.status

    app.logger.info(f"[WolvPay] Event: {status} — {invoice_id}")

    if status == "PAID":
        fulfill_order(invoice_id)
    elif status == "CONFIRMING_PAYMENT":
        app.logger.info(f"[WolvPay] Payment confirming for {invoice_id}")
    elif status == "UNDERPAID":
        app.logger.warning(f"[WolvPay] Underpaid invoice: {invoice_id}")
        mark_underpaid(invoice_id)
    elif status == "EXPIRED":
        mark_expired(invoice_id)
    else:
        app.logger.warning(f"[WolvPay] Unhandled status '{status}' for {invoice_id}")

    return "OK", 200


# ─────────────────────────────────────────────
# Stub handlers — replace with your own logic.
# ─────────────────────────────────────────────

def fulfill_order(invoice_id: str) -> None:
    app.logger.info(f"[WolvPay] Fulfilling order: {invoice_id}")
    # Update database, send email, etc.


def mark_underpaid(invoice_id: str) -> None:
    app.logger.info(f"[WolvPay] Marking underpaid: {invoice_id}")


def mark_expired(invoice_id: str) -> None:
    app.logger.info(f"[WolvPay] Marking expired: {invoice_id}")


# ─────────────────────────────────────────────
# Django example (in views.py):
# ─────────────────────────────────────────────
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wolvpay.webhook import extract_signature, verify
from wolvpay.exceptions import WebhookError

@csrf_exempt
def wolvpay_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    raw_body = request.body
    signature = extract_signature(dict(request.headers))

    try:
        event = verify(raw_body, signature, settings.WOLVPAY_WEBHOOK_SECRET)
    except WebhookError:
        return HttpResponse(status=401)

    if event.status == 'PAID':
        fulfill_order(event.invoice_id)

    return HttpResponse('OK')
"""
