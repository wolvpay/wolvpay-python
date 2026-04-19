"""
wolvpay.models
~~~~~~~~~~~~~~
Data classes that represent the objects returned by the WolvPay API.

All classes expose a ``from_dict`` class method so they can be constructed
directly from the raw JSON decoded from an API response.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CoinPrices:
    """Exchange rates for a coin, keyed by fiat currency code."""
    rates: Dict[str, str]

    def get(self, currency: str) -> Optional[str]:
        return self.rates.get(currency.upper())


@dataclass
class Coin:
    coin: str
    name: str
    logo: str
    minimum_transaction_coin: str
    prices: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coin":
        return cls(
            coin=data["coin"],
            name=data["name"],
            logo=data["logo"],
            minimum_transaction_coin=data["minimum_transaction_coin"],
            prices=data.get("prices", {}),
        )


@dataclass
class Invoice:
    invoice_id: str
    amount: float
    status: str
    description: Optional[str] = None
    coin: Optional[str] = None
    coin_amount: Optional[float] = None
    coin_received: Optional[float] = None
    coin_address: Optional[str] = None
    redirect_url: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Hosted invoices only
    url: Optional[str] = None
    # Present when status is AWAITING_SELECTION
    available_coins: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Invoice":
        return cls(
            invoice_id=data["invoice_id"],
            amount=data.get("amount", 0),
            status=data.get("status", ""),
            description=data.get("description"),
            coin=data.get("coin"),
            coin_amount=data.get("coin_amount"),
            coin_received=data.get("coin_received"),
            coin_address=data.get("coin_address"),
            redirect_url=data.get("redirect_url"),
            created_at=data.get("created_at"),
            expires_at=data.get("expires_at"),
            updated_at=data.get("updated_at"),
            url=data.get("url"),
            available_coins=data.get("available_coins", []),
        )


@dataclass
class Pagination:
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_page: Optional[int]
    previous_page: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pagination":
        return cls(
            current_page=data["current_page"],
            per_page=data["per_page"],
            total_items=data["total_items"],
            total_pages=data["total_pages"],
            has_next=data["has_next"],
            has_previous=data["has_previous"],
            next_page=data.get("next_page"),
            previous_page=data.get("previous_page"),
        )


@dataclass
class InvoiceList:
    invoices: List[Invoice]
    pagination: Pagination

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvoiceList":
        return cls(
            invoices=[Invoice.from_dict(i) for i in data.get("invoices", [])],
            pagination=Pagination.from_dict(data["pagination"]),
        )


@dataclass
class WebhookPayload:
    invoice_id: str
    amount: float
    status: str
    coin: str
    coin_amount: float
    coin_received: float
    coin_address: str
    description: Optional[str] = None
    redirect_url: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookPayload":
        return cls(
            invoice_id=data["invoice_id"],
            amount=data.get("amount", 0),
            status=data.get("status", ""),
            coin=data.get("coin", ""),
            coin_amount=data.get("coin_amount", 0),
            coin_received=data.get("coin_received", 0),
            coin_address=data.get("coin_address", ""),
            description=data.get("description"),
            redirect_url=data.get("redirect_url"),
            created_at=data.get("created_at"),
        )
