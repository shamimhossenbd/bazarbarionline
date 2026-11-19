# Incident and restore-test log

One row per incident or monthly restore test (see [README](README.md#monthly-restore-test)). Times in Asia/Dhaka. Newest first. Never paste secrets, customer personal data or full stack traces here.

| Date | Type | Runbook | Who | Start | End | What was lost / affected | Result | What to change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-19 | Incident (local) | — | Owner | — | — | Running GitHub's "quick setup" at `D:\bazarbarionline` deleted the projects' `.git` folders and committed a DB dump to a new root repo. `.git` folders restored from the Recycle Bin; root repo removed. Nothing pushed publicly from the dump. | Recovered | Never `git init` at the root; remotes already set in each folder (audit §7.2) |

## Restore-test template

```
Date:
Backup file used (name, date taken):
Restored into: staging
Duration (start → site healthy):
Row counts checked (users, orders, products, ledger_entries):
Images checked:
Result: pass / fail
Notes:
```
