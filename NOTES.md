# Susu Group Tracker — Notes

## Overview
A command-line program managing one rotating savings group (susu). Members pay
a fixed weekly amount in GHS. A week closes only when every member has paid in
full; the whole pot then goes to the next member in join order.

## Requirements from the brief (and where they are met)
These come from the brief; they are not my decisions.

| Brief requirement | How it is met |
|---|---|
| Create a group with a fixed weekly contribution in GHS | `SavingsGroup("50.00")`; the CLI prompts for the weekly amount first |
| Add members with a unique name or ID | `add_member`; duplicates are rejected |
| Record a contribution for a member for a given week; partial payments allowed | `record_contribution(member, amount, week)`; payments accumulate (test 03) |
| Close a week: pay the pot to the next member in order if everyone paid in full; otherwise pay nothing and report who owes how much | `close_week` returns a `CloseResult` with the outstanding list (tests 06-08) |
| Report: current week, who has paid in full, who owes what, payout history | `report()` and the CLI's "view report" (test 12) |
| Reject unknown members, duplicates, zero or negative amounts, and payments above what is owed for the week | `UnknownMember`, `DuplicateMember`, `InvalidAmount`, `Overpayment` (tests 02, 04) |
| Money handled exactly, no rounding errors | `Decimal` from strings; extra decimal places are rejected, never rounded (money tests, test 05) |
| Anything not covered is my decision, enforced and written down | see the next section |
| Example: Ama, Kofi, Esi at 50.00; Esi pays 30 then 20; Ama receives 150.00; week 2, Kofi next | test 11 and `python -m susu --demo` |
| At least 6 automated tests, including partial payment and "week cannot close" | 14 tests, including those cases (03 and 06) |

## My assumptions and decisions
The brief leaves these open. Each is my own choice, enforced in the code.
Where the brief says "for a given week" or "unique name or ID", my reading is
stated here.
1. **Members are identified by a unique identifier** (trimmed, case-insensitive).
   The display name is optional and defaults to the identifier.
2. **Membership freezes when the first contribution is recorded.** Members can
   be added freely before week 1 starts; afterwards adding is rejected. This
   keeps the pot constant (members × weekly amount) and the payout order fixed.
4. **Contributions are accepted for the current week only.** Closed weeks are
   final; future weeks are rejected.
5. **The group completes after every member has been paid once.** After that,
   adding members, contributions and closing are rejected, and the report shows
   the group as complete.
6. **Closing an empty group is rejected.**
7. **Overpayment** is measured cumulatively: total paid for the week may never
   exceed the weekly amount.
8. **A week is a numbered cycle, not a calendar period.** No deadlines,
   penalties, reminders or disputes. An unpaid week stays open and the report
   shows who owes what.
9. **State is in memory.** Data is lost when the program exits.
10. **A contribution's week must be the current week.** The brief says "for a
    given week"; the week argument exists and defaults to the current week, but
    closed or future weeks are rejected (`WeekNotOpen`).
11. **Money is limited to 12 integer digits and 2 decimal places.** This keeps
    amounts realistic and the display exact.
12. **A closed week is never reopened.** A week that cannot close simply stays
    open until everyone has paid.

## Money
Amounts use `Decimal`, parsed from strings, never floats. An amount must match
`[0-9]{1,12}(\.[0-9]{1,2})?` and be greater than zero, so non-finite values,
scientific notation, signs, more than 2 decimal places and more than 12 integer
digits are rejected (never rounded). Amounts are displayed as `GHS 50.00`.

## Design
- `group.py` holds all rules; `cli.py` only handles input and output.
- Only facts are stored (members, contribution records, payouts). Current week,
  beneficiary, amounts paid or owed, and the pot are calculated from them,
  so they cannot disagree.
- Invalid operations raise `SusuError` subclasses and change nothing. A week that
  cannot close is a normal outcome, returned as a result object listing who owes.
- Operations validate fully before modifying state.

## Testing
`python -m unittest` from the repository root. Tests cover partial payments,
validation, exact money, a week that cannot close, payouts, rotation, membership
locking, cycle completion, the report, and the example from the brief.

## Known limitations
- No persistence.
- Balances are calculated by scanning the contribution list, which is fine for
  small groups.
- No late joiners after week 1 starts.
- No prepaying future weeks or reversing mistaken contributions.
- No CLI-level tests.

## What I would improve with more time
- Persist state (JSON file, then a database).
- Allow late joiners from the following week, with a documented rule for pot
  size and payout position.
- Keep running totals per (week, member) so balance lookups don't scan history.
- Support prepaying future weeks, and reversing mistaken contributions through
  an audited correction record.
- Add due dates and overdue reporting.
- Add an API layer and CLI-level tests.

## References
Python `decimal` module documentation; `unittest` documentation.
