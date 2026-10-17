# Susu Group Tracker

A command-line rotating savings (susu) tracker for one group. Members pay a
fixed weekly amount in GHS; when everyone has paid in full the week closes and
the whole pot goes to the next member in join order, until every member has
been paid once. Python 3.10+, standard library only, in-memory.

## Run

```
python -m susu          # interactive: enter the weekly amount, then use the menu
python -m susu --demo   # replay the example: Ama, Kofi and Esi over three weeks
```

Menu: `(1) add member (2) record contribution (3) view report (4) close week (5) exit`.

## Test

```
python -m unittest
```

14 tests, including partial payments (test 03) and a week that cannot close
(test 06). Requires Python 3.10+; no packages to install.

## Assumptions (my decisions, beyond the brief)

- Membership is locked once the first contribution is recorded.
- Contributions are accepted for the current week only.
- The group is complete after every member has been paid once.
- State is in memory only; nothing is saved when the program exits.

The full list, with the brief's requirements mapped to the code, is in
[NOTES.md](NOTES.md).

## Money rules

Amounts are `Decimal`, never floats. An amount must match
`[0-9]{1,12}(\.[0-9]{1,2})?` and be greater than zero. Extra decimal places are
rejected, not rounded. Amounts display as `GHS 50.00`.

See [NOTES.md](NOTES.md) for decisions, limitations and possible improvements.