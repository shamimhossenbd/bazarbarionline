# ADR-08: Decimal storage, exact arithmetic

- **Status:** **Confirmed** for storage; arithmetic not yet
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

All money columns are already `DECIMAL(12,2)`. Phase 0 found float arithmetic in checkout (`$item->price * $item->quantity`).

## Decision

Store BDT amounts as `DECIMAL(12,2)`. Do all arithmetic in integer paisa or with `brick/money` (adding the package needs approval). Commission is rounded half-up to the paisa, per order item. Single currency (BDT) in MVP.

## Consequences

- Ledger sums and commission are exact.
- A small `Money` value object or Eloquent cast is needed before Phase 3.

## Alternatives rejected

- `FLOAT`/`DOUBLE` columns or float arithmetic.
