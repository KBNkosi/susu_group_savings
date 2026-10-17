import unittest
from decimal import Decimal

from susu.errors import (
    DuplicateMember,
    EmptyGroup,
    GroupComplete,
    InvalidAmount,
    MembershipLocked,
    Overpayment,
    SusuError,
    UnknownMember,
    WeekNotOpen,
)
from susu.group import SavingsGroup
from susu.models import Member, Payout
from susu.money import parse_amount


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

    def test_05_exact_money_and_rejected_precision(self):
        group = SavingsGroup("50.00")
        group.add_member("ama")
        group.record_contribution("ama", "33.33")
        group.record_contribution("ama", "16.67")
        result = group.close_week()
        self.assertTrue(result.closed)
        self.assertEqual(result.payout.amount, Decimal("50.00"))
        with self.assertRaises(InvalidAmount):
            parse_amount("10.005")
        with self.assertRaises(InvalidAmount):
            parse_amount("NaN")

    def test_06_week_cannot_close_lists_outstanding(self):
        group = SavingsGroup("50.00")
        group.add_member("ama")
        group.add_member("kofi")
        group.record_contribution("ama", "50.00")
        result = group.close_week()
        self.assertFalse(result.closed)
        self.assertIsNone(result.payout)
        self.assertEqual(result.outstanding, (("kofi", Decimal("50.00")),))
        self.assertEqual(group.current_week, 1)
        self.assertEqual(group.current_beneficiary.member_id, "ama")
        self.assertEqual(group.payouts, ())

    def test_07_successful_close_pays_pot_to_first_member(self):
        group = SavingsGroup("50.00")
        group.add_member("ama")
        group.add_member("kofi")
        group.record_contribution("ama", "50.00")
        group.record_contribution("kofi", "50.00")
        result = group.close_week()
        self.assertEqual(result.payout, Payout(1, "ama", Decimal("100.00")))
        self.assertEqual(group.payouts, (result.payout,))
        self.assertEqual(group.current_week, 2)
        self.assertEqual(group.current_beneficiary.member_id, "kofi")

    def test_08_rotation_and_second_close_does_not_double_pay(self):
        group = SavingsGroup("50.00")
        for ident in ("ama", "kofi"):
            group.add_member(ident)
        for ident in ("ama", "kofi"):
            group.record_contribution(ident, "50.00")
        group.close_week()
        failed = group.close_week()
        self.assertFalse(failed.closed)
        self.assertEqual(len(group.payouts), 1)
        self.assertEqual(failed.outstanding, (
            ("ama", Decimal("50.00")),
            ("kofi", Decimal("50.00")),
        ))
        group.record_contribution("ama", "50.00")
        with self.assertRaises(WeekNotOpen):
            group.record_contribution("kofi", "50.00", week=1)
        group.record_contribution("kofi", "50.00", week=2)
        result = group.close_week()
        self.assertEqual(result.payout, Payout(2, "kofi", Decimal("100.00")))
        self.assertEqual(len(group.payouts), 2)

    def test_09_membership_locked_and_empty_close_rejected(self):
        empty = SavingsGroup("50.00")
        with self.assertRaises(EmptyGroup):
            empty.close_week()
        group = SavingsGroup("50.00")
        group.add_member("ama")
        group.record_contribution("ama", "10.00")
        with self.assertRaises(MembershipLocked):
            group.add_member("kofi")
        self.assertEqual(len(group.members), 1)

    def test_10_cycle_completion_and_brief_example(self):
        group = SavingsGroup("50.00")
        for ident in ("Ama", "Kofi", "Esi"):
            group.add_member(ident)
        expected = ("Ama", "Kofi", "Esi")
        for week, beneficiary in enumerate(expected, start=1):
            for ident in expected:
                group.record_contribution(ident, "50.00")
            result = group.close_week()
            self.assertTrue(result.closed)
            self.assertEqual(result.payout.beneficiary_id, beneficiary)
            self.assertEqual(result.payout.amount, Decimal("150.00"))
            self.assertEqual(result.payout.week, week)
        self.assertTrue(group.is_complete)
        self.assertIsNone(group.current_beneficiary)
        with self.assertRaises(GroupComplete):
            group.add_member("Yaw")
        with self.assertRaises(GroupComplete):
            group.record_contribution("Ama", "50.00")
        with self.assertRaises(GroupComplete):
            group.close_week()


if __name__ == "__main__":
    unittest.main()
