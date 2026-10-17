import unittest

from susu.errors import DuplicateMember, SusuError
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


if __name__ == "__main__":
    unittest.main()
