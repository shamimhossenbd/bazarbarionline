# ADR-13: First-party retail (platform-owned stock sold through POS and online)

- **Status:** Accepted by the owner on 2026-11-26 (owner addendum A–H; plan approved 2026-11-26)
- **Date:** 2026-11-26
- **Amends:** ADR-12 (the scope of POS and of the platform's own stock), BD-01, BD-11
- **Keeps:** ADR-02/03 (single database, Vendor = marketplace tenant), ADR-08 (money), ADR-09 (time), ADR-12 rules 1, 3, 4 and 5 (no vendor POS, no subscriptions, commission per vendor, one ownership-aware stock balance)

## Context

The platform now buys its own stock and sells it, alongside the commission marketplace. Platform stock is sold:
- in person, through the Platform POS;
- online, through the same storefront and checkout as vendor products.

Vendor sales stay commission-only (BD-01). Most of the machinery already exists:
- the Platform POS (ADR-12, phase 6);
- central purchasing with weighted average cost (migration `000011`);
- the `stock_movements` ledger;
- `sales_channel` on `orders` and `pos_sales`.

This ADR records the decisions and the gaps that remain.

## Decisions

### 1. Who owns platform stock (addendum B)

The owner asked for a "house vendor" (a row in `vendors`). The audit found that `products.vendor_id IS NULL` already means "platform-owned" in 24 backend files:
- inventory ownership guards;
- POS catalogue;
- purchasing scope;
- commission snapshot and vendor ledger;
- marketplace reports;
- shipments;
- product approval.

A house vendor row would turn every one of those checks into an `is_house` exception. If a single check were forgotten, the platform's own sales would create commission, vendor earnings and a payable balance. That is the outcome addendum G forbids.

**Decision:**
- `vendor_id IS NULL` stays the internal meaning of platform-owned. There is no row in `vendors`.
- Platform products use the same products, variants, stock and movement tables as vendor products. There is no parallel product or stock system, which was the purpose of addendum B.
- The storefront, cart, order and invoice pages show a **house seller identity**, "BazarBari Official": a name in English and Bangla plus a logo, stored in platform settings. It is shown wherever a vendor name would appear for a platform product.
- POS sells platform-owned products only. This is already enforced in `InventoryService` and `PosCatalog`.

### 2. One stock ledger with reservations (addendum C)

- **On hand** is `products.stock` (a product without variants) or `product_variants.stock` (a variant). It always equals the sum of that item's `stock_movements.quantity`.
- **Reserved** is a new column `reserved_stock` on the same row. It always equals the sum of that item's `active` rows in `stock_reservations`.
- **Available = on hand − reserved.** Every sale, adjustment and purchase return that takes stock out checks available, not on hand.
- Every change runs in a DB transaction and locks the stock row with `lockForUpdate`. Rows are always locked in the same order (variants, then products, by id), which prevents deadlocks.

**Flows**

| Event | On hand | Reserved | Movement written |
| --- | --- | --- | --- |
| POS sale | − qty, at once | — | `pos_sale` |
| POS void | + qty | — | `pos_void` |
| POS return, restocked | + qty | — | `pos_return` |
| Online checkout | — | + qty | none (the reservation row is created) |
| Order **converted** (see below) | − qty | − qty | `online_order` |
| Order cancelled **before** conversion | — | − qty | none (the reservation is released) |
| Order cancelled **after** conversion, before delivery | + qty | — | `online_cancellation` |
| Online return, restocked (future item-level returns) | + qty | — | `online_return` |
| Purchase receipt | + qty | — | `purchase_receipt` |
| Purchase return | − qty (only up to available) | — | `purchase_return` |
| Stock count or adjustment | ± | — | `adjustment` (also `damage` and `opening`) |

**Conversion trigger:** the order's first status change from `pending` to any status other than cancelled (`confirmed`, `processing`, `shipped` or `delivered`). It runs in the same transaction as the status change, whichever path makes it (admin, customer or courier webhook). All of the order's active reservations convert together.

**No automatic expiry.** COD orders keep their reservation until they are confirmed or cancelled. The admin inventory and order pages list pending orders older than 48 hours so staff can follow up. Reservations expiring after a time limit can come later with online payment.

**Order stock state (`orders.stock_mode`, owner request 2026-11-26).** Each order records where its stock stands. Every change of `stock_mode` runs in the same transaction as the stock change, with the order row locked `FOR UPDATE`. That is what makes each action happen at most once.

| `stock_mode` | Meaning | Confirm / convert | Cancel |
| --- | --- | --- | --- |
| `legacy_deducted` | Order placed before `000012`. Its stock was taken at checkout (`sale`, channel `online`), and it has no reservation. | **No stock change.** The mode stays `legacy_deducted`. | Stock goes back once through `InventoryService::apply` (stock in, `online_cancellation`). The mode becomes `restored`. Reservations are never touched. |
| `reserved` | New order holding active reservations | Reservations convert, on hand goes down (`online_order`), mode becomes `deducted` | Reservations are released, no movement is written, mode becomes `released` |
| `deducted` | Converted; the stock has left | No stock change | Stock goes back once (`online_cancellation`), mode becomes `restored` |
| `released` | Cancelled before conversion | — (cancelled orders can't be reopened) | No-op |
| `restored` | Cancelled after its stock left; stock is back | — | No-op |

- The migration sets every existing order to `legacy_deducted`. New orders start as `reserved`.
- A second cancel, a repeated webhook or a double click finds a mode that is already `restored` or `released` and changes nothing.
- Cancelled orders already return stock today. The current check (`status = cancelled`) stays, and `stock_mode` becomes the authority for stock.
- `stock_mode` is never accepted from a request.

**Movement source names (addendum C).** The names are still derived from `type` + `channel`, with no extra column. The display names change to the owner's list:

| Type : channel | Source name |
| --- | --- |
| `purchase:*` | `purchase_receipt` |
| `purchase_return:*` | `purchase_return` |
| `sale:pos` | `pos_sale` |
| `sale_cancel:pos` | `pos_void` |
| `return:pos` | `pos_return` |
| `sale:online` | `online_order` |
| `sale_cancel:online` | `online_cancellation` |
| `return:online` | `online_return` |
| `adjustment:admin` / `:vendor` / `:system` | `adjustment` (the channel is still shown separately) |
| `damage:*` | `damage` |
| `opening:*` | `opening_stock` |

The `?source=` filter still accepts the old names for one release, so saved links keep working.

### 3. Costing (addendum D)

- Weighted average cost per product (no variants) or per variant. It is updated by each purchase receipt (already built in `PurchaseService`).
- Every sale line stores its unit cost:
  - `pos_sale_items.unit_cost` when the POS sale is made;
  - `order_items.unit_cost` **when the order converts**, which is when the stock leaves. Today it is taken at checkout, which is too early.
- Cost columns are widened to 4 decimals so they match the average cost.
- Purchase-return valuation and landed cost belong to accounting (ADR-14, phase AC4), not to this ADR.

### 4. One stock location for now (addendum E)

- New table `stock_locations` with a single row, `MAIN`.
- The tables where a location matters get a nullable `location_id`: `stock_movements`, `stock_reservations`, `purchase_receipts`, `pos_registers`. Existing rows are backfilled with `MAIN`. `InventoryService` fills it in for every new row.
- The stock balance itself stays on `products` and `product_variants`. When a second location arrives, the balance moves into a `stock_levels (product, variant, location)` table. Because every stock change already goes through `InventoryService`, that change stays inside that one class plus the read queries.

### 5. Sales channel on every header, payment and return (addendum F)

- `sales_channel` is `pos` or `online`. It is stored as `string(10)` (the convention since `000011`) and validated by a PHP backed enum `App\Enums\SalesChannel`.
- It already exists on `orders` (default `online`) and `pos_sales` (default `pos`).
- It is added to `payments` (default `online`), `pos_payments` (default `pos`) and `pos_returns` (default `pos`). Future online return and refund tables carry it too.
- Vendor marketplace orders are always `online` and never appear in POS reports.

### 6. Reports: two sections that are never added together (addendum G)

1. **Platform-owned sales:** POS, Online (order lines with `vendor_id IS NULL`), and Combined (POS + platform online).
2. **Marketplace vendor sales:** GMV and commission for lines with `vendor_id IS NOT NULL` (the existing `MarketplaceSalesReport`).

There is no grand total across the two sections. The "all sales" total planned in purchasing phase 3 is dropped. `sales.combined.view` now means the platform-owned Combined view only.

Platform POS sales and platform online lines create no vendor earnings and no commission ledger rows. This is already true, and a test will guard it.

### 7. No vendor purchasing in this phase (addendum H)

- The vendor purchasing routes (`routes/vendor-purchasing.php`) are unregistered.
- The vendor purchasing UI is hidden.
- The vendor permissions `purchases.manage` and `purchases.pay` are removed from `VendorPermissionRegistry`. Existing grants stay in the database but give no access, because the registry fails closed.
- The code and the nullable `vendor_id` columns on the purchasing tables stay, so the module can return later. This replaces decision D1 of 2026-11-25 for now.
- Vendors keep changing their own stock with audited adjustments (channel `vendor`).

## Schema for migration `2026_11_26_000012_first_party_retail` (for owner approval; not written yet)

| Table | Change |
| --- | --- |
| `stock_locations` (new) | `id`; `code` string(20) unique; `name` string(100); `is_default` bool; `is_active` bool; timestamps. Seeded with one row: `MAIN` / "Main store", default, active. |
| `products` | + `reserved_stock` unsigned int, default 0 |
| `product_variants` | + `reserved_stock` unsigned int, default 0 |
| `stock_reservations` (new) | `id`<br>`location_id` FK nullable, restrict<br>`order_id` FK, restrict<br>`order_item_id` FK, restrict, **unique**<br>`product_id` FK, restrict<br>`product_variant_id` FK nullable, restrict<br>`vendor_id` FK nullable (copy of the owner, for filtering)<br>`quantity` unsigned int<br>`status` string(10): `active`, `converted` or `released`<br>`stock_movement_id` FK nullable (the conversion movement)<br>`converted_at`, `released_at` nullable<br>`release_reason` string(255) nullable<br>timestamps<br>Indexes: (`status`, `product_id`, `product_variant_id`), (`order_id`) |
| `stock_movements` | + `location_id` FK nullable (backfilled `MAIN`). `unit_cost` widened from decimal(12,2) to decimal(14,4). |
| `purchase_receipts` | + `location_id` FK nullable (backfilled `MAIN`) |
| `pos_registers` | + `location_id` FK nullable (backfilled `MAIN`) |
| `pos_sale_items` | `unit_cost` widened from decimal(12,2) to decimal(14,4) |
| `orders` | + `stock_mode` string(20), NOT NULL, default `reserved`. Allowed values: `legacy_deducted`, `reserved`, `deducted`, `released`, `restored` (PHP backed enum `App\Enums\OrderStockMode`). Every existing row is set to `legacy_deducted` in the same migration. |
| `payments` | + `sales_channel` string(10), default `online` |
| `pos_payments` | + `sales_channel` string(10), default `pos` |
| `pos_returns` | + `sales_channel` string(10), default `pos` |

- No permissions change, and no data changes apart from the backfills.
- `down()` reverses every step. Shrinking the cost columns back to 2 decimals rounds them.
- Run only on `api-backend` and `bazarbari_cart_qa`, after verified backups. Never on production.

## Consequences

- Checkout no longer takes stock. POS and admins see available stock, and an order holds its units until it is confirmed or cancelled.
- Pending COD orders that nobody follows up hold stock. The 48-hour list is the control for that.
- The vendor product pages show on hand, reserved and available, because reservations apply to vendor products too. Ownership rules are unchanged.
- Accounting (ADR-14) relies on this: stock leaving at conversion moves cost into "inventory awaiting delivery", and delivery recognises revenue and COGS.

## Delivery

The addendum plan's phases, each reported to the owner before the next starts:

- **P1:** documents (this ADR).
- **P2:** migration `000012`.
- **P3:** reservations in `InventoryService`, checkout, conversion and cancellation; POS, adjustments and purchase returns use available stock; tests and a MySQL race test.
- **P4:** source names.
- **P5:** vendor purchasing switched off.
- **P6:** reports split into two sections.
- **P7:** UI.
- **P8:** browser QA.

After P3 comes Partnership Accounting (ADR-14), from AC0.
