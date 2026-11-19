# Commission, ledger, settlement, payouts

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 3 | Orders, refunds | Missing |

## Purpose

Calculate commission, hold vendor earnings for the return window, and pay vendors manually from an append-only ledger (spec 8).

## What exists today

Nothing. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Commission rule precedence: vendor+category → vendor → category → platform default; rate snapshotted on each order item.
- Ledger is append-only; corrections are reversals.
- Earnings move pending → available when the return window closes with no open return.
- Payout minimum BDT 1,000; maker-checker above threshold; no self-approval.
- Nightly balance recomputation; mismatch raises an alert.
- Money arithmetic per ADR-08.

## Permissions

`finance.view` and `payout.request` (vendor); `finance.commission.manage`, `payout.approve`, `payout.record` (platform).

## Tables

`commission_rules`, `ledger_entries`, `vendor_balance_summaries`, `payout_requests`, `payouts`.

## Endpoints

`GET /vendor/ledger`, `/vendor/balance`, `POST /vendor/payout-requests`; `/platform/commission-rules`, `/platform/payout-requests/{id}/approve`, `/platform/payouts`.

## UI and states

Vendor balance cards (pending, available, paid) and statement; platform payout queue and commission rule editor.

## Audit events

`commission_rule.changed`, `payout.requested`, `payout.approved`, `payout.recorded`, `ledger.adjusted`.

## Required tests

- Deliver → settle → refund → payout: balances equal sum of entries.
- Finance Manager cannot approve own request.
- Rule change does not alter existing order items.

Done only when the Definition of Done in spec section 16.4 is met.
