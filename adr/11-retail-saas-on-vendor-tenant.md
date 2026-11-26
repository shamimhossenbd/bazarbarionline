# ADR-11: Retail SaaS (POS, inventory, accounts) on the Vendor tenant

- **Status:** **Superseded by [ADR-12](12-platform-pos-no-subscriptions.md)** on 2026-11-25. Slice 1a (shared inventory) is kept; 1b (plans) and 1c (vendor POS) are cancelled.
- **Date:** 2026-11-25
- **Builds on:** ADR-02 (single database, Vendor = tenant), ADR-03 (tenant context from the server), ADR-08 (money), ADR-09 (time). Amends module 09 (inventory).

## Decision

**Phase 1:** each existing `Vendor` shop is the SaaS tenant. POS, shared inventory, purchasing, accounts, reports and staff tools are added on top of the vendor system and reuse its isolation, staff RBAC, marketplace order lines, commission and payouts.

**Phase 2 (later, separate project):** independent storefronts (own domain, customers, checkout). Nothing in Phase 1 adds tenant domains, separate customer bases or a tenant checkout.

Platform-owned products (`products.vendor_id IS NULL`) stay admin-managed and outside the tenant modules in Phase 1.

## How the pieces relate (as built today, plus Phase 1 additions)

```
Vendor (tenant)
 ├─ vendor_members (owner + staff; status)        ← membership resolves the tenant, never a request field
 │    └─ vendor_roles / member overrides           ← tenant-scoped RBAC (VendorPermissionRegistry)
 ├─ products / product_variants (vendor_id)        ← ONE stock balance: products.stock / product_variants.stock
 │    └─ stock_movements (Phase 1a, new)           ← every change, signed, with reason, channel, actor; sum = balance
 ├─ order_items (vendor_id)                        ← ONLINE channel: the vendor's lines inside a marketplace order
 │    ├─ total, discount_amount (platform-funded coupon share)
 │    ├─ commission_rate / commission_amount       ← snapshotted at checkout
 │    └─ vendor_earning = total − commission       ← what the platform owes the vendor
 ├─ vendor_ledger_entries                          ← earning (on delivery), reversal (cancel/refund), payout, adjustment
 ├─ vendor_payouts                                 ← requested → approved → paid
 └─ pos_* (Phase 1c, new)                          ← POS channel: shifts, sales, payments, returns (tenant collects the money)
```

### Inventory (one source of truth)

- The balance is the existing `products.stock` (no variant) / `product_variants.stock` (variant). Storefront, cart, checkout and vendor screens already read these, so they stay the balance.
- New `stock_movements` records every change: `opening`, `sale` (channel online|pos), `sale_cancel`, `return`, `adjustment`, `damage`, `purchase`, `purchase_return`. Its rows sum to the balance (a reconciliation test checks it).
- One `InventoryService` is the only code that changes stock. It locks rows `FOR UPDATE` in id order (as checkout already does), refuses to go below zero, writes the movement and the audit event in the same transaction. Checkout, order cancellation, admin/vendor stock edits and POS all call it.
- The old `inventories` table (0 rows, read only by the unused `/api/admin/inventory` endpoints, never by checkout) is retired. This amends module 09: `stock_levels` = the existing stock columns.
- Reservations are not needed now: online checkout is Cash on Delivery and takes stock immediately at order placement (current policy), and POS takes it at sale completion. Reservations come back only if online prepayment is added.
- Because both channels go through the same locked rows, a POS sale and an online checkout racing for the last unit cannot both succeed.

### Online sales (marketplace lines) and the vendor's receivable

The customer pays the **platform** (COD collected by the courier). The vendor is paid later through payouts. So for the tenant:

| Event | Vendor ledger (exists) | Tenant books (Phase 1e, double entry) |
| --- | --- | --- |
| Order placed | none | stock out (movement); no revenue yet |
| Line delivered | `earning` = vendor_earning | Dr Receivable from platform (vendor_earning), Dr Commission expense (commission_amount); Cr Sales — online (line total). Dr COGS, Cr Inventory (cost at sale) |
| Cancelled / refunded after delivery | `reversal` | the reverse entries; stock back in if returned |
| Payout paid | `payout` | Dr Cash/Bank, Cr Receivable from platform |
| Platform adjustment | `adjustment` | Dr/Cr Receivable from platform against Other income/expense |

- The coupon discount is platform-funded: it never appears in the vendor's books (the vendor's revenue is the full line total).
- Receivable from platform = vendor ledger balance; the tenant books are derived from the ledger, not a second calculation.

### POS sales

- Separate `pos_sales` (+ items, payments) records, never `orders`. Each is single-tenant, has a cashier and a shift, and is paid at the till.
- Tenant books: Dr Cash/Bank/Mobile wallet, Cr Sales — POS; Dr COGS, Cr Inventory.
- No platform commission on POS sales in Phase 1 (BD-14, decided 2026-11-25): POS revenue belongs to the tenant. The platform earns from the Retail SaaS through paid subscription plans. The commission policy stays configurable for later.
- Reports add online lines + POS sales. Each sale exists in exactly one place, so nothing is double-counted.

### Cost method

Weighted average cost per product/variant: purchases update the average; every sale/return movement snapshots the unit cost used, so COGS and stock valuation reconcile with the movement history.

## Phase 1 delivery slices

| Slice | Scope |
| --- | --- |
| 1a | `InventoryService`, `stock_movements`, opening balances, all writers routed through it, `inventories` retired, channel on movements — **built 2026-11-25** (uncommitted; migrated locally; 510 tests) |
| 1b | Tenant settings (currency BDT, timezone Asia/Dhaka), plans + subscriptions (manual, no gateway), plan limits enforced server-side, per-tenant SKU/barcode uniqueness, barcode/QR generation and labels, new vendor permission groups |
| 1c | POS: shifts, sales, payments per method, receipts, returns/cancellations with permission, cash reconciliation, keyboard-wedge scanner + camera where the browser supports it |
| 1d | Suppliers, purchase receiving and returns, damage, weighted average cost |
| 1e | Double-entry tenant accounting from POS, purchases, expenses and the vendor ledger |
| 1f | Reports (sales, inventory, accounts, staff) in the tenant time zone, permission-gated export |
| 1g | Staff extras (employee id, department), read-only tenant audit view |

Out of scope for Phase 1: offline POS, payroll/attendance/leave, multi-branch, subscription payment gateway, independent storefronts.

## Consequences

- New tenant tables carry `vendor_id NOT NULL` and are always queried through the caller's membership (ADR-03). The pending `BelongsToVendor` global scope (Option C phase 6B) is held back by Courier Commit 2; new tables can adopt it without touching courier files.
- Stock-changing code outside `InventoryService` is a bug; a test fails if a movement-less stock change appears.
- The vendor ledger stays the source for what the platform owes the vendor; tenant accounting reads it.
