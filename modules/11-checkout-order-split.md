# Checkout and order split

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Cart, inventory | Partial |

## Purpose

Turn one cart into one parent order and one vendor order per vendor (BD-02), safely.

## What exists today

`POST /api/orders` creates one order from the cart in a transaction with item snapshots. Stock rows are now locked, checked and decremented, and cancellation restores stock (audit H5 partly fixed). Still missing: current-price check (uses the cart price), idempotency key, payment record, vendor split. Frontend checkout files are empty. Admin order list and status update work (H3/H4 fixed) but any status can be set; the spec 7.2 state machine is not enforced. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Steps and transaction boundary as in spec 7.1.
- `Idempotency-Key` header required.
- Item snapshots: name, SKU, unit price, discount, commission rate.
- Delivery charge per vendor order by zone (BD-08).
- Vendor order state machine as in spec 7.2; parent status is derived.
- Every transition writes `order_status_history`.

## Permissions

Customer: owner of record. Vendor: `order.view`, `order.accept`, `order.cancel`. Platform: `order.view_all`, `order.cancel_any`.

## Tables

`orders`, `vendor_orders`, `order_items`, `order_addresses`, `order_status_history`.

## Endpoints

`POST /account/checkout`, `GET /account/orders`, `POST /account/orders/{ulid}/cancel`, `GET /vendor/orders`, `POST /vendor/orders/{ulid}/accept|ready|cancel`, `GET /platform/orders`.

## UI and states

Checkout (address, delivery zone, COD), order confirmation, customer order list, vendor order queue, platform order view.

## Audit events

`order.placed`, `order.cancelled_by_staff`, `order.status_changed`.

## Required tests

- Two-vendor cart creates two vendor orders; each vendor sees only its part and address.
- Same idempotency key twice creates one order.
- Delivered order cannot be cancelled (409).

Done only when the Definition of Done in spec section 16.4 is met.
