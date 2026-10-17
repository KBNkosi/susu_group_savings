class SusuError(Exception):
    """Base error for invalid susu operations."""


class InvalidAmount(SusuError):
    """Amount is not a positive value matching the allowed money format."""


class UnknownMember(SusuError):
    """No member matches the given identifier."""


class DuplicateMember(SusuError):
    """Identifier already exists (case-insensitive)."""


class Overpayment(SusuError):
    """Payment would exceed the amount owed for the week."""


class MembershipLocked(SusuError):
    """Members cannot be added after the first contribution."""


class WeekNotOpen(SusuError):
    """Contribution week is not the current open week."""


class GroupComplete(SusuError):
    """Every member has already been paid once."""


class EmptyGroup(SusuError):
    """Close was requested with no members."""
