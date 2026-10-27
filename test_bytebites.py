import unittest
from decimal import Decimal

from bytebites import Customer, CustomerRegistry, Menu, MenuItem, Transaction


class MenuItemTests(unittest.TestCase):
    def test_normalizes_price_to_decimal(self) -> None:
        item = MenuItem("Spicy Burger", 8.25, "Meals", 4.5)

        self.assertEqual(item.price, Decimal("8.25"))

    def test_rejects_invalid_item_values(self) -> None:
        invalid_items = [
            {"name": "", "price": 1, "category": "Drinks", "popularity": 3},
            {"name": "Soda", "price": -1, "category": "Drinks", "popularity": 3},
            {"name": "Soda", "price": 1, "category": " ", "popularity": 3},
            {"name": "Soda", "price": 1, "category": "Drinks", "popularity": 6},
        ]

        for values in invalid_items:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    MenuItem(**values)


class MenuTests(unittest.TestCase):
    def test_filters_items_by_exact_category(self) -> None:
        burger = MenuItem("Spicy Burger", "8.25", "Meals", 4.5)
        soda = MenuItem("Large Soda", "2.10", "Drinks", 4)
        menu = Menu([burger, soda])

        self.assertEqual(menu.filter_by_category("Drinks"), [soda])
        self.assertEqual(menu.filter_by_category("Desserts"), [])


class CustomerRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.customer = Customer("student-1", "Casey")
        self.registry = CustomerRegistry()
        self.registry.add_customer(self.customer)

    def test_verifies_registered_customer(self) -> None:
        self.assertTrue(self.registry.verify_customer("student-1"))
        self.assertFalse(self.registry.verify_customer("unknown"))

    def test_rejects_duplicate_customer_id(self) -> None:
        with self.assertRaises(ValueError):
            self.registry.add_customer(Customer("student-1", "Another Casey"))

    def test_rejects_transaction_for_unknown_customer(self) -> None:
        item = MenuItem("Large Soda", "2.10", "Drinks", 4)

        with self.assertRaisesRegex(KeyError, "Unknown customer ID"):
            self.registry.create_transaction("unknown", [item])

    def test_creates_transaction_and_records_purchase_history(self) -> None:
        burger = MenuItem("Spicy Burger", "8.25", "Meals", 4.5)
        soda = MenuItem("Large Soda", "2.10", "Drinks", 4)

        transaction = self.registry.create_transaction(
            "student-1", [burger, soda]
        )

        self.assertEqual(transaction.items, (burger, soda))
        self.assertEqual(transaction.total_cost, Decimal("10.35"))
        self.assertEqual(self.customer.purchase_history, [transaction])
        self.assertIs(transaction.customer, self.customer)

    def test_rejects_empty_transaction_without_recording_it(self) -> None:
        with self.assertRaises(ValueError):
            self.registry.create_transaction("student-1", [])

        self.assertEqual(self.customer.purchase_history, [])


if __name__ == "__main__":
    unittest.main()