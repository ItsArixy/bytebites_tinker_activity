from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class MenuItem:
    name: str
    price: Decimal
    category: str
    popularity: int | float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Item name must be a non-empty string")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("Item category must be a non-empty string")

        try:
            normalized_price = Decimal(str(self.price))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError("Item price must be a valid number") from error

        if not normalized_price.is_finite() or normalized_price < 0:
            raise ValueError("Item price must be a finite, nonnegative number")
        object.__setattr__(self, "price", normalized_price)

        if isinstance(self.popularity, bool) or not isinstance(
            self.popularity, (int, float)
        ):
            raise ValueError("Popularity must be a number from 0 to 5")
        if not isfinite(self.popularity) or not 0 <= self.popularity <= 5:
            raise ValueError("Popularity must be a number from 0 to 5")


class Menu:
    def __init__(self, items: Iterable[MenuItem] = ()) -> None:
        self.items: list[MenuItem] = []
        for item in items:
            self.add_item(item)

    def add_item(self, item: MenuItem) -> None:
        if not isinstance(item, MenuItem):
            raise TypeError("Menu can only contain MenuItem objects")
        self.items.append(item)

    def filter_by_category(self, category: str) -> list[MenuItem]:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category must be a non-empty string")
        return [item for item in self.items if item.category == category]


class Customer:
    def __init__(self, customer_id: str, name: str) -> None:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("Customer ID must be a non-empty string")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Customer name must be a non-empty string")

        self.customer_id = customer_id
        self.name = name
        self.purchase_history: list[Transaction] = []


class Transaction:
    def __init__(self, customer: Customer, items: Iterable[MenuItem]) -> None:
        if not isinstance(customer, Customer):
            raise TypeError("Transaction requires a Customer")

        selected_items = tuple(items)
        if not selected_items:
            raise ValueError("Transaction must contain at least one item")
        if any(not isinstance(item, MenuItem) for item in selected_items):
            raise TypeError("Transaction items must be MenuItem objects")

        self.customer = customer
        self.items = selected_items

    @property
    def total_cost(self) -> Decimal:
        return sum((item.price for item in self.items), Decimal("0"))


class CustomerRegistry:
    def __init__(self) -> None:
        self._customers: dict[str, Customer] = {}

    def add_customer(self, customer: Customer) -> None:
        if not isinstance(customer, Customer):
            raise TypeError("Registry can only contain Customer objects")
        if customer.customer_id in self._customers:
            raise ValueError(f"Customer ID already registered: {customer.customer_id}")
        self._customers[customer.customer_id] = customer

    def verify_customer(self, customer_id: str) -> bool:
        return customer_id in self._customers

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self._customers[customer_id]
        except KeyError:
            raise KeyError(f"Unknown customer ID: {customer_id}") from None

    def create_transaction(
        self, customer_id: str, items: Iterable[MenuItem]
    ) -> Transaction:
        customer = self.get_customer(customer_id)
        transaction = Transaction(customer, items)
        customer.purchase_history.append(transaction)
        return transaction