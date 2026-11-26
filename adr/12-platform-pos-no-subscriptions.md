# ADR-12: Marketplace-only vendors, Platform Admin POS, no subscriptions

- **Status:** Accepted by the owner on 2026-11-25 (master task `documentation/writing-block .md`)
- **Date:** 2026-11-25
- **Supersedes:** ADR-11 (Retail SaaS on the Vendor tenant). Amends BD-01, BD-11, BD-13 and BD-14.
- **Keeps:** ADR-02 and ADR-03 (single database, Vendor = tenant for marketplace data, tenant resolved on the server), ADR-08 (money), ADR-09 (time).

## Decision

1. **Vendors sell online only.** No vendor POS: no vendor POS routes, APIs, pages, permissions, tables or menu items. Vendor staff can never hold POS permissions.
2. **POS is a Platform Admin module.**
   - It sells platform-owned products only (`products.vendor_id IS NULL`), checked on the server for every line.
   - It has its own sales, payments, registers, cashier sessions, returns and reports.
   - It never creates marketplace orders, vendor commission or vendor earnings.
3. **No vendor subscription system.** That means no plans, fees, trials, renewals, expiry or billing, and no product, staff or module limits tied to a plan. Vendor access is controlled only by RBAC (platform registry and vendor registry).
4. **Commission is set per vendor by an admin.**
   - A platform default rate is stored in the database and can be changed by an admin, with an audit record. Before this ADR it was the environment value `MARKETPLACE_COMMISSION_RATE`, which admins could not see or change.
   - A vendor's own rate (0–100) overrides the default. A rate of `0` means "no commission" and is never treated as "not set".
   - Only authorized platform admins can change rates. Every change keeps its history: actor, old rate, new rate, time.
   - The rate is snapshotted onto `order_items` when an order is placed. Historical lines are never recalculated.
5. **One stock balance, ownership-aware.**
   - Keep slice 1a of ADR-11: `InventoryService` and `stock_movements`.
   - Online checkout moves stock for both vendor and platform products. Platform POS moves stock for platform products only.
   - Vendors move stock only for their own products.

## What this means for ADR-11 work already done

| ADR-11 item | Status | Under ADR-12 |
| --- | --- | --- |
| 1a shared inventory (`InventoryService`, `stock_movements`, `RecordsStockMovements`) | Built, migrated locally | **Kept.** POS will later use it with channel `pos`. |
| 1b paid plans and subscriptions (`saas_plans`, `vendor_subscriptions`, `PlanGate`, `EnsurePlanFeature`, `saas.*` permissions, `routes/admin-saas.php`) | Built, uncommitted. Migration `2026_11_25_000004` **never run** | **Removed 2026-11-25** (owner approved). Code, routes, the `plan` middleware and the `saas.*` permissions are gone. `000004` is kept as an empty no-op because it never ran anywhere. `vendors.timezone` and `vendors.currency` were kept as business settings in `2026_11_25_000005_vendor_business_settings`. |
| 1c vendor POS | Not started | **Cancelled.** Rebuilt as the Platform Admin POS (master task phase 6). |

## Consequences

- BD-01 returns to "commission only" with no subscription amendment. BD-11 now reads "POS for the platform's own shop only". BD-13 drops the vendor Retail SaaS. BD-14 is closed as "no plans".
- The commission policy (calculation base, coupons, shipping, refunds) must be written down before phase 3. Today: commission is charged on the full line total because coupons are platform-funded. Shipping is excluded. Cancelled and refunded lines reverse the earning through `vendor_ledger_entries`.

## Inventory ownership (Phase 5a, owner decisions 2026-11-25)

`InventoryService` enforces who may move whose stock, before anything changes:

| Channel | May change |
| --- | --- |
| `pos` (Platform POS) | platform-owned products only |
| `admin` (platform admins) | platform-owned products only. **Vendor stock is never changed by an admin**: the admin product and variant forms refuse a stock change on a vendor product with `403 STOCK_OWNERSHIP_DENIED`. |
| `vendor` | only products of the caller's own shop (`vendor_id` from the membership) |
| `online` (checkout, cancellation, return) and `system` | any owner (marketplace order flows) |

Further rules:
- A variant only ever moves together with its own product.
- The owner is re-read from the database, so a stale model can't pass the check.
- Eloquent stock writes made inside `InventoryService::withContext()` (the admin and vendor product and variant forms) are guarded the same way, by the `RecordsStockMovements` model hook.

**Spec movement names** are derived from type + channel, with no extra column (`StockMovement::SOURCES`):

| Type and channel | Spec name |
| --- | --- |
| opening (any channel) | `opening_stock` |
| sale, online | `online_sale` |
| sale_cancel, online | `online_cancellation` |
| return, online | `online_return` |
| sale, pos | `platform_pos_sale` |
| return, pos | `platform_pos_return` |
| purchase / purchase_return | `purchase` / `purchase_return` |
| adjustment, vendor | `vendor_adjustment` |
| adjustment, admin | `platform_adjustment` |
| damage | `damage` |

**Reserved stock:** not used yet. Cash-on-delivery checkout takes stock when the order is placed. Reservation arrives with online payment.
