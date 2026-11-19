# Inventory and reservations

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Catalogue | Partial |

## Purpose

Accurate stock that never oversells.

## What exists today

Three stock sources: `products.stock`, `product_variants.stock`, `inventories.quantity/reserved_quantity`. Admin can list and update `inventories` (the broken store/show/destroy routes were removed). Checkout now decrements `products.stock` / `product_variants.stock` under a row lock, but `inventories` is not updated, so the three sources can drift. No movements, no reservations. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- One source of truth: `stock_levels` per variant, a cached sum of `stock_movements`.
- Every change (adjust, reserve, release, sale, return) is a movement row with reason and actor.
- Checkout locks stock rows (`FOR UPDATE`) and creates reservations; unpaid reservations expire after 30 min.
- Low-stock alert per variant threshold.

## Permissions

`inventory.view`, `inventory.adjust` (vendor).

## Tables

`stock_levels`, `stock_movements`, `stock_reservations` (replace or migrate `inventories`).

## Endpoints

`GET /vendor/products/{ulid}/stock`, `POST /vendor/products/{ulid}/stock/adjust`.

## UI and states

Stock table with low-stock filter; adjustment form with mandatory reason; movement history.

## Audit events

`inventory.adjusted`.

## Required tests

- 20 parallel checkouts for the last unit: exactly one succeeds.
- Expired reservation releases stock.
- Stock level equals sum of movements.

Done only when the Definition of Done in spec section 16.4 is met.
