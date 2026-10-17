import unittest
from decimal import Decimal

from susu.errors import InvalidAmount
from susu.money import format_ghs, parse_amount


class TestMoney(unittest.TestCase):
    def test_parse_and_format(self):
        self.assertEqual(parse_amount("50"), Decimal("50"))
        self.assertEqual(parse_amount(" 50.00 "), Decimal("50.00"))
        self.assertEqual(parse_amount("999999999999"), Decimal("999999999999"))
        self.assertEqual(format_ghs(Decimal("50")), "GHS 50.00")
        self.assertEqual(format_ghs(parse_amount("1.5")), "GHS 1.50")

    def test_reject_invalid_amounts(self):
        for raw in (
            "0", "0.00", "-1", "10.005", "NaN", "Infinity", "-Infinity",
            "1e2", "abc", "", "1000000000000",
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidAmount) as ctx:
                    parse_amount(raw)
                self.assertEqual(str(ctx.exception), f"Invalid amount: {raw}")


if __name__ == "__main__":
    unittest.main()
