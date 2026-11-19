# Payments (COD; online after launch)

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 3 | Checkout | Missing |

## Purpose

Record how each parent order is paid. Launch with Cash on Delivery only (BD-04).

## What exists today

`payments` table and an unrouted `PaymentController`. `.env` has unused Stripe, SSLCommerz and bKash placeholders (Stripe is out of scope). See [Phase 0 audit](../audit/phase-0.md).

## Rules

- COD order is `confirmed` at checkout; payment becomes `collected` when the courier reports delivery.
- Online gateways (after launch): mark paid only after server-to-server validation; unique gateway transaction ID.
- Credentials only in `.env` or encrypted settings.

## Permissions

`payment.view` (platform finance).

## Tables

`payments`, `payment_events` (raw callbacks, redacted).

## Endpoints

Internal for COD; `POST /webhooks/payments/{gateway}` after launch.

## UI and states

Payment status on order pages.

## Audit events

`payment.collected`, `payment.refunded`.

## Required tests

- Repeated IPN creates no second payment.
- Browser redirect alone never marks paid.

Done only when the Definition of Done in spec section 16.4 is met.
