import sys

from susu.errors import SusuError
from susu.group import SavingsGroup
from susu.models import CloseResult, GroupReport
from susu.money import format_ghs

MENU = (
    "(1) add member (2) record contribution (3) view report "
    "(4) close week (5) exit"
)


def print_report(report: GroupReport) -> None:
    """Format a group report to stdout."""
    if report.is_complete:
        print("Status: complete")
    else:
        print(f"Week {report.current_week}")
        print(f"Beneficiary: {report.beneficiary_id}")
        print(f"Pot so far: {format_ghs(report.pot)}")
        paid = ", ".join(report.paid_in_full) or "none"
        print(f"Paid in full: {paid}")
        for member_id, amount in report.owing:
            print(f"{member_id} owes {format_ghs(amount)}")
    for payout in report.payouts:
        print(f"Week {payout.week} -> {payout.beneficiary_id} {format_ghs(payout.amount)}")


def print_close_result(result: CloseResult) -> None:
    """Format a close result to stdout."""
    if result.closed and result.payout is not None:
        payout = result.payout
        print(f"Closed week. Paid {payout.beneficiary_id} {format_ghs(payout.amount)}")
        return
    print("Week not closed.")
    for member_id, amount in result.outstanding:
        print(f"{member_id} owes {format_ghs(amount)}")


def run_demo() -> None:
    """Replay the brief's example to stdout."""
    group = SavingsGroup("50.00")
    for name in ("Ama", "Kofi", "Esi"):
        group.add_member(name)
    group.record_contribution("Ama", "50.00")
    group.record_contribution("Kofi", "50.00")
    group.record_contribution("Esi", "30.00")
    print_close_result(group.close_week())
    group.record_contribution("Esi", "20.00")
    print_close_result(group.close_week())
    for _ in range(2):
        for member in group.members:
            group.record_contribution(member.member_id, "50.00")
        print_close_result(group.close_week())
    print_report(group.report())


def _record_contribution(group: SavingsGroup) -> None:
    member_id = input("Member id: ")
    amount = input("Amount: ")
    raw_week = input("Week (blank = current): ").strip()
    if raw_week == "":
        group.record_contribution(member_id, amount)
        return
    try:
        week = int(raw_week)
    except ValueError:
        print(f"Invalid week: {raw_week}")
        return
    group.record_contribution(member_id, amount, week)


def run_menu(group: SavingsGroup) -> None:
    """Interactive loop until the user exits."""
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                member_id = input("Member id: ")
                name = input("Name (blank = same as id): ")
                group.add_member(member_id, name)
            elif choice == "2":
                _record_contribution(group)
            elif choice == "3":
                print_report(group.report())
            elif choice == "4":
                print_close_result(group.close_week())
            elif choice == "5":
                return
            else:
                print("Please choose 1-5.")
        except SusuError as exc:
            print(exc)


def main(argv: list[str] | None = None) -> int:
    """Run the demo with --demo, otherwise create a group and show the menu."""
    args = sys.argv[1:] if argv is None else argv
    if "--demo" in args:
        run_demo()
        return 0
    try:
        while True:
            try:
                group = SavingsGroup(input("Weekly amount (GHS): "))
                break
            except SusuError as exc:
                print(exc)
        run_menu(group)
    except (EOFError, KeyboardInterrupt):
        print()
    return 0
