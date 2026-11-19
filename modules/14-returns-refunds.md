# Returns and refunds

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 3 | Payments, shipments | Missing |

## Purpose

Let customers return items within 7 days of delivery (BD-06) and reverse money correctly.

## What exists today

Nothing; order status has a `refunded` value only. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Request per item with reason and photo, within the return window.
- Vendor accepts or rejects within 48 h; then platform support decides.
- Accepted return creates a refund and reversal ledger entries.
- Refund above a configurable amount needs a second platform approver.
- COD refunds are paid by recorded manual transfer.

## Permissions

Customer: owner. Vendor: `return.decide`. Platform: `return.decide_any`, `refund.approve`.

## Tables

`return_requests`, `return_items`, `refunds`.

## Endpoints

`POST /account/returns`, `GET /vendor/returns`, `POST /vendor/returns/{id}/accept|reject`, `/platform/returns`, `/platform/refunds/{id}/approve`.

## UI and states

Return form, vendor return queue, platform dispute view.

## Audit events

`return.requested`, `return.accepted`, `return.rejected`, `refund.approved`, `refund.paid`.

## Required tests

- Return after 7 days is refused.
- Refund after delivery reverses commission and vendor earnings.

Done only when the Definition of Done in spec section 16.4 is met.
