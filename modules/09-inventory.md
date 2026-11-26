# Inventory and reservations

| Phase | Depends on | Status (2026-11-26) |
| --- | --- | --- |
| 2 + first-party track (ADR-12, ADR-13) | Catalogue | Partial: ledger built; reservations and locations planned (ADR-13 P2–P3) |

## Purpose

Accurate stock that never oversells. One stock ledger serves vendor products and platform-owned products (`vendor_id IS NULL`). It is shared by online checkout, Platform POS, purchasing and adjustments.

## What exists today (built)

- **Balance.** `products.stock` (a product without variants) or `product_variants.stock` (a variant). The old `inventories` table was dropped in `2026_11_25_000003`.
- **Ledger.** `stock_movements` is append-only. Each item's movements add up to its stock column. Movements are written only by `InventoryService` and by the `RecordsStockMovements` model hook.
- **Concurrency.** Stock rows are locked `FOR UPDATE` in id order (variants, then products). A decrease is a conditional `UPDATE … WHERE stock >= qty`. A MySQL race test (45 processes) showed no oversell.
- **Ownership.** Enforced by channel:
  - `pos` and `admin`: platform stock only;
  - `vendor`: the caller's own shop only;
  - `online` and `system`: any owner.
  
  A wrong owner is refused with `403 STOCK_OWNERSHIP_DENIED`.
- **Platform stock is read-only in product forms** (`422 PLATFORM_STOCK_READ_ONLY`). It changes only through:
  - purchase receiving;
  - sales, voids, cancellations and returns;
  - an audited adjustment (`inventory.adjust`, reason required).
- **Cost.** Weighted average cost (`average_cost`) per product or variant, updated by purchase receipts. Each movement records a unit cost.
- **Reports.** Admin `/api/admin/inventory/summary|stock|movements` (`inventory.view`) and the vendor stock history.
- **Checkout today** takes stock when the order is placed (`sale`, channel `online`). Cancelling puts it back (`sale_cancel`). There are no reservations yet.

## Rules (ADR-13, to build in P2–P3)

- **On hand** = the stock column. **Reserved** = `reserved_stock` = the sum of active `stock_reservations`. **Available = on hand − reserved.**
- Everything that takes stock out (POS sale, adjustment down, purchase return) checks **available**.
- **POS sale:** on hand goes down at once.
- **Online checkout:** creates one reservation per order line and raises `reserved_stock`. On hand does not change.
- **Conversion:** the order's first status change from `pending` to `confirmed`, `processing`, `shipped` or `delivered`. On hand and reserved both go down, an `online_order` movement is written, and `order_items.unit_cost` is set then.
- **Cancel before conversion:** the reservation is released, and no movement is written. **Cancel after conversion:** on hand goes back up (`online_cancellation`).
- Reservations have no automatic expiry while orders are COD. Pending orders older than 48 hours are listed for staff to follow up.
- Every change runs in one DB transaction, with the same lock order as today.
- One location, `MAIN`. `location_id` is stored on movements, reservations, purchase receipts and POS registers, so more locations can be added later (see ADR-13 §4).
- Movement source names: `purchase_receipt`, `purchase_return`, `pos_sale`, `pos_void`, `pos_return`, `online_order`, `online_cancellation`, `online_return`, `adjustment`, `damage`, `opening_stock`. They are derived from `type` + `channel`.

## Permissions

- Platform: `inventory.view` (reports) and `inventory.adjust` (platform adjustments).
- Vendor: `inventory.view` and `inventory.adjust` for their own shop.

See [permissions.md](../permissions.md). ADR-13 adds no new permissions.

## Tables

- Built: `stock_movements`, plus the stock columns on `products` and `product_variants`.
- Planned in `000012`: `reserved_stock` columns, `stock_reservations`, `stock_locations`, `location_id` columns.

The schema is in [ADR-13](../adr/13-first-party-retail.md#schema-for-migration-2026_11_26_000012_first_party_retail-for-owner-approval-not-written-yet).

## Endpoints

- Admin: `GET /api/admin/inventory/summary`, `/stock`, `/movements`; `POST /api/admin/inventory/adjustments`.
- Vendor: product stock history `GET /api/vendor/products/{id}/stock-movements`.

## UI and states

- Admin `/admin/inventory`: platform and vendor cards, current stock, low stock, movements with filters by source, owner, vendor, product and date.
- Admin `/admin/inventory/adjustments`.
- Vendor product "Stock history" tab.
- P7 adds on hand, reserved and available columns and the list of pending orders older than 48 hours.

## Audit events

`inventory.adjusted`, `inventory.counted`.

## Required tests

Existing:
- 20+ parallel checkouts for the last unit: exactly one succeeds.
- Stock level equals the sum of movements.
- The ownership matrix.

Added by ADR-13:
- Reserved equals the sum of active reservations after every flow.
- POS cannot sell reserved units.
- Converting twice changes nothing.
- Cancelling before or after conversion restores the right figure.
- Legacy order (`stock_mode = legacy_deducted`), **confirm:**
  - on hand, reserved and the movement count don't change;
  - no reservation is created or converted;
  - the mode stays `legacy_deducted`.
- Legacy order, **cancel:**
  - stock goes back by exactly the line quantities, through **one** `online_cancellation` stock-in movement per line;
  - no reservation is read or released;
  - the mode becomes `restored`.
- Legacy order, **cancel again** (admin, customer, or a repeated request): no second movement, and stock unchanged.
- Legacy order **confirmed, then cancelled:** stock goes back once.
- Migration test: rows that existed before `000012` get `legacy_deducted`; new checkouts get `reserved`.
- MySQL race between POS and checkout on the last available unit.

Done only when the Definition of Done in spec section 16.4 is met.
