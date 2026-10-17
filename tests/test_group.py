import unittest
from decimal import Decimal

from susu.errors import DuplicateMember, InvalidAmount, Overpayment, SusuError, UnknownMember
from susu.group import SavingsGroup
from susu.models import Member


class TestSavingsGroup(unittest.TestCase):
    def test_01_add_member_preserves_join_order(self):
        group = SavingsGroup("50.00")
        ama = group.add_member("ama", "Ama")
        kofi = group.add_member(" kofi ")
        self.assertEqual(ama, Member("ama", "Ama"))
        self.assertEqual(kofi, Member("kofi", "kofi"))
        self.assertEqual([m.member_id for m in group.members], ["ama", "kofi"])
        self.assertEqual(group.current_week, 1)
        self.assertEqual(group.current_beneficiary, ama)
        self.assertFalse(group.is_complete)

    def test_02_duplicate_member_case_insensitive(self):
        group = SavingsGroup("50.00")
        group.add_member("ama", "Ama")
        with self.assertRaises(DuplicateMember):
            group.add_member("Ama")
        with self.assertRaises(SusuError) as ctx:
            group.add_member("  ")
        self.assertEqual(str(ctx.exception), "Member identifier is required")
        self.assertEqual(len(group.members), 1)

    def test_03_partial_payments_accumulate(self):
        group = SavingsGroup("50.00")
        group.add_member("ama")
        group.record_contribution("ama", "20.00")
        group.record_contribution("AMA", "15")
        self.assertEqual(group.paid("ama"), Decimal("35.00"))
        self.assertEqual(group.owed("ama"), Decimal("15.00"))
        self.assertEqual(len(group.contributions), 2)

    def test_04_rejects_invalid_and_overpayment(self):
        group = SavingsGroup("50.00")
        group.add_member("ama")
        with self.assertRaises(UnknownMember):
            group.record_contribution("kofi", "10.00")
        self.assertEqual(len(group.contributions), 0)
        for raw in ("0", "-5"):
            with self.assertRaises(InvalidAmount):
                group.record_contribution("ama", raw)
        group.record_contribution("ama", "40.00")
        with self.assertRaises(Overpayment):
            group.record_contribution("ama", "10.01")
        self.assertEqual(group.paid("ama"), Decimal("40.00"))
        group2 = SavingsGroup("50.00")
        group2.add_member("ama")
        group2.record_contribution("ama", "30.00")
        with self.assertRaises(Overpayment):
            group2.record_contribution("ama", "20.01")
        self.assertEqual(group2.paid("ama"), Decimal("30.00"))


if __name__ == "__main__":
    unittest.main()
