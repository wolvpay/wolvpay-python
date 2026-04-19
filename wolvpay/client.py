from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .exceptions import ApiError, WolvPayError
from .models import Coin, Invoice, InvoiceList

_BASE_URL = "https://wolvpay.com/api/v1"


class WolvPayClient:
    """
    Official WolvPay API client.

    Args:
        api_key: Your WolvPay API key from the dashboard.
        timeout: Request timeout in seconds (default: 30).

    Example::

        import os
        from wolvpay import WolvPayClient

        client = WolvPayClient(os.environ["WOLVPAY_API_KEY"])
        invoice = client.create_invoice(amount=50.0, currency="USD")
    """

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("WolvPay API key cannot be empty.")

        self._api_key = api_key
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # =========================================================================
    # Coins
    # =========================================================================

    def get_coins(self) -> List[Coin]:
        """
        Retrieve all supported cryptocurrencies and their current exchange rates.

        Returns:
            A list of :class:`~wolvpay.models.Coin` objects.

        Raises:
            ApiError: On API error.
            WolvPayError: On network or parse error.
        """
        data = self._request("GET", "/coins")
        return [Coin.from_dict(c) for c in data]

    # =========================================================================
    # Invoices
    # =========================================================================

    def create_invoice(
        self,
        amount: float,
        currency: str = "USD",
        coin: Optional[str] = None,
        description: Optional[str] = None,
        white_label: bool = True,
        redirect_url: Optional[str] = None,
    ) -> Invoice:
        """
        Create a new payment invoice.

        Pass ``white_label=False`` for a hosted invoice (returns a payment URL).
        Omit ``coin`` to let the customer select the cryptocurrency themselves
        (invoice status will be ``AWAITING_SELECTION``).

        Args:
            amount:       Payment amount in the specified fiat currency.
            currency:     Fiat currency code (e.g. ``"USD"``, ``"EUR"``). Defaults to ``"USD"``.
            coin:         Cryptocurrency code (e.g. ``"btc"``, ``"ltc"``). Optional.
            description:  Invoice description. Optional.
            white_label:  ``True`` = white-label flow, ``False`` = hosted page. Defaults to ``True``.
            redirect_url: URL to redirect the customer after payment. Optional.

        Returns:
            An :class:`~wolvpay.models.Invoice` object.

        Raises:
            ApiError: On API error.
            WolvPayError: On network or parse error.
        """
        payload: Dict[str, Any] = {
            "amount": amount,
            "currency": currency.upper(),
            "white_label": white_label,
        }

        if coin is not None:
            payload["coin"] = coin.lower()
        if description is not None:
            payload["description"] = description
        if redirect_url is not None:
            payload["redirect_url"] = redirect_url

        data = self._request("POST", "/invoices", json=payload)
        return Invoice.from_dict(data)

    def get_invoice(self, invoice_id: str) -> Invoice:
        """
        Retrieve a specific invoice by ID.

        Args:
            invoice_id: The invoice ID (e.g. ``"INVabc123def456"``).

        Returns:
            An :class:`~wolvpay.models.Invoice` object.

        Raises:
            ApiError: On API error (404 if not found).
            WolvPayError: On network or parse error.
        """
        from urllib.parse import quote

        data = self._request("GET", f"/invoices/{quote(invoice_id, safe='')}")
        return Invoice.from_dict(data)

    def update_invoice(self, invoice_id: str, coin: str) -> Invoice:
        """
        Update a white-label invoice by selecting a cryptocurrency.

        Only available for invoices in ``AWAITING_SELECTION`` status.

        Args:
            invoice_id: The invoice ID.
            coin:       Cryptocurrency code (e.g. ``"btc"``, ``"erc20_usdt"``).

        Returns:
            The updated :class:`~wolvpay.models.Invoice`.

        Raises:
            ApiError: On API error.
            WolvPayError: On network or parse error.
        """
        from urllib.parse import quote

        data = self._request(
            "POST",
            f"/invoices/{quote(invoice_id, safe='')}",
            json={"coin": coin.lower()},
        )
        return Invoice.from_dict(data)

    def list_invoices(self, page: int = 1, limit: int = 3) -> InvoiceList:
        """
        List all invoices with optional pagination.

        Args:
            page:  Page number (default: 1).
            limit: Invoices per page (default: 3, max: 3).

        Returns:
            An :class:`~wolvpay.models.InvoiceList` object containing invoices and pagination info.

        Raises:
            ApiError: On API error.
            WolvPayError: On network or parse error.
        """
        data = self._request("GET", "/invoices", params={"page": page, "limit": limit})
        return InvoiceList.from_dict(data)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "WolvPayClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # =========================================================================
    # Internal HTTP transport
    # =========================================================================

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = _BASE_URL + path

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                timeout=self._timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise WolvPayError(f"HTTP request failed: {exc}") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise WolvPayError(f"Failed to parse WolvPay API response: {exc}") from exc

        if response.status_code >= 400:
            error = body.get("error") if isinstance(body, dict) else {}
            if isinstance(error, dict):
                message = error.get("message") or body.get("message") or "WolvPay API error."
            else:
                message = str(error) or body.get("message") or "WolvPay API error."
            raise ApiError(str(message), response.status_code, error if isinstance(error, dict) else {})

        if isinstance(body, dict) and "data" in body:
            return body["data"]

        return body
