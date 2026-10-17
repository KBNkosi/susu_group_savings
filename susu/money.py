import re
from decimal import Decimal

from susu.errors import InvalidAmount

_CENTS = Decimal("0.01")
_AMOUNT_PATTERN = re.compile(r"[0-9]{1,12}(?:\.[0-9]{1,2})?")


def parse_amount(text: str) -> Decimal:
    """Parse a positive amount: up to 12 digits, optional 1-2 decimal places."""
    candidate = text.strip()
    if _AMOUNT_PATTERN.fullmatch(candidate) is None:
        raise InvalidAmount(f"Invalid amount: {text}")
    value = Decimal(candidate)
    if value <= 0:
        raise InvalidAmount(f"Invalid amount: {text}")
    return value


def format_ghs(amount: Decimal) -> str:
    """Format an amount as 'GHS 50.00'."""
    return f"GHS {amount.quantize(_CENTS)}"
