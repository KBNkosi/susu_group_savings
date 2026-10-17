from decimal import Decimal

from susu.errors import (
    DuplicateMember,
    GroupComplete,
    MembershipLocked,
    Overpayment,
    SusuError,
    UnknownMember,
    WeekNotOpen,
)
from susu.models import Contribution, Member, Payout
from susu.money import format_ghs, parse_amount


class SavingsGroup:
    def __init__(self, weekly_amount: str) -> None:
        """Create a group; weekly_amount is parsed with parse_amount."""
        self._weekly_amount: Decimal = parse_amount(weekly_amount)
        self._members: list[Member] = []
        self._contributions: list[Contribution] = []
        self._payouts: list[Payout] = []

    def add_member(self, member_id: str, name: str | None = None) -> Member:
        """Append a member in join order; name defaults to the stored identifier."""
        stored_id = member_id.strip()
        if stored_id == "":
            raise SusuError("Member identifier is required")
        if self.is_complete:
            raise GroupComplete("The savings group cycle is complete")
        if self._contributions:
            raise MembershipLocked("Membership is locked after the first contribution")
        if self._find_member(member_id) is not None:
            raise DuplicateMember(f"Duplicate member: {member_id}")
        display = name.strip() if name and name.strip() else stored_id
        member = Member(stored_id, display)
        self._members.append(member)
        return member

    def record_contribution(
        self, member_id: str, amount: str, week: int | None = None
    ) -> Contribution:
        """Record a payment for the current week after all checks pass."""
        if self.is_complete:
            raise GroupComplete("The savings group cycle is complete")
        member = self._require_member(member_id)
        week = self.current_week if week is None else week
        if week != self.current_week:
            raise WeekNotOpen(
                f"Week {week} is not open (current week is {self.current_week})"
            )
        parsed = parse_amount(amount)
        due = self.owed(member.member_id, week)
        if parsed > due:
            raise Overpayment(
                f"Overpayment: {format_ghs(parsed)} exceeds {format_ghs(due)} "
                f"owed by {member.member_id} in week {week}"
            )
        contribution = Contribution(member.member_id, week, parsed)
        self._contributions.append(contribution)
        return contribution

    def paid(self, member_id: str, week: int | None = None) -> Decimal:
        """Sum of contributions for the member in that week (default: current)."""
        member = self._require_member(member_id)
        week = self.current_week if week is None else week
        return sum(
            (
                c.amount
                for c in self._contributions
                if c.member_id == member.member_id and c.week == week
            ),
            Decimal("0"),
        )

    def owed(self, member_id: str, week: int | None = None) -> Decimal:
        """weekly_amount minus paid for that member and week."""
        return self._weekly_amount - self.paid(member_id, week)

    def _require_member(self, member_id: str) -> Member:
        member = self._find_member(member_id)
        if member is None:
            raise UnknownMember(f"Unknown member: {member_id}")
        return member

    def _find_member(self, member_id: str) -> Member | None:
        key = member_id.strip().casefold()
        for member in self._members:
            if member.member_id.casefold() == key:
                return member
        return None

    @property
    def weekly_amount(self) -> Decimal:
        return self._weekly_amount

    @property
    def members(self) -> tuple[Member, ...]:
        return tuple(self._members)

    @property
    def contributions(self) -> tuple[Contribution, ...]:
        return tuple(self._contributions)

    @property
    def payouts(self) -> tuple[Payout, ...]:
        return tuple(self._payouts)

    @property
    def current_week(self) -> int:
        return len(self._payouts) + 1

    @property
    def current_beneficiary(self) -> Member | None:
        if len(self._payouts) < len(self._members):
            return self._members[len(self._payouts)]
        return None

    @property
    def is_complete(self) -> bool:
        return len(self._members) > 0 and len(self._payouts) == len(self._members)
