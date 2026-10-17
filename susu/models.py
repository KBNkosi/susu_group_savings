from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Member:
    member_id: str
    name: str


@dataclass(frozen=True)
class Contribution:
    member_id: str
    week: int
    amount: Decimal


@dataclass(frozen=True)
class Payout:
    week: int
    beneficiary_id: str
    amount: Decimal


@dataclass(frozen=True)
class CloseResult:
    closed: bool
    payout: Payout | None
    outstanding: tuple[tuple[str, Decimal], ...]


@dataclass(frozen=True)
class GroupReport:
    is_complete: bool
    current_week: int | None
    beneficiary_id: str | None
    pot: Decimal
    paid_in_full: tuple[str, ...]
    owing: tuple[tuple[str, Decimal], ...]
    payouts: tuple[Payout, ...]
