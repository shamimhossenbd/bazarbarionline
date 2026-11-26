# Permission catalogue

The single list of permissions for BazarBariOnline (spec section 6.4). `config/permissions.php` in the backend is generated from this page in Phase 1; until then this page is the source of truth. A permission that is not listed here does not exist (deny by default, spec rule 6).

**Status (19 Nov 2026):** target catalogue, not yet seeded. Today's database holds the old CRUD-style permissions listed in [section 5](#5-what-exists-today-and-how-it-maps); no route checks any permission yet (audit §2.8).

## 1. Rules

- Name format `module.action`, lower case, `snake_case` inside a part (`finance.commission.manage` is the one allowed three-part name, kept from the spec).
- **Scope** tag: `platform` (only platform roles, `team_id = NULL`), `vendor` (only vendor roles, `team_id = vendor_id`) or `both` (same name in either context; the context decides what records it covers).
- A vendor role may hold only `vendor` or `both` permissions. The seeder and the role editor both reject anything else.
- Nobody grants a permission they do not hold, and nobody changes their own roles.
- **Re-confirm** = password re-entry within 15 minutes (spec 12.1). **2nd approver** = another user with the same permission must approve (maker-checker).
- Roles change only through Spatie APIs (`syncPermissions`, `assignRole`) so the permission cache resets.
- Adding, renaming or removing a permission: change this page and `config/permissions.php` in the same pull request, plus a migration or seeder step that moves existing grants.

## 2. Catalogue

### Access and team

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `role.manage` | both | Create, edit, delete roles and their permissions in the current context | Re-confirm | [03](modules/03-roles-permissions.md) |
| `team.manage` | both | Invite, suspend, remove members; change a member's role (platform: staff; vendor: own team) | Re-confirm for role change | [03](modules/03-roles-permissions.md), [02](modules/02-tenancy.md) |
| `audit.view` | platform | Read all audit events | — | [04](modules/04-audit-log.md) |
| `audit.view_own` | vendor | Read audit events of the current vendor only | — | [04](modules/04-audit-log.md) |
| `settings.manage` | platform | Site settings, logo, SEO defaults, delivery zones and charges | Re-confirm for gateway/courier keys | [16](modules/16-reports-notifications-seo.md) |
| `customer.view` | platform | Read customer accounts and their orders (support) | — | [10](modules/10-customer-cart.md) |
| `customer.manage` | platform | Block or unblock a customer account | Re-confirm | [10](modules/10-customer-cart.md) |

### Vendors

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `vendor.view` | platform | List and read vendor applications and profiles | — | [06](modules/06-vendor-lifecycle.md) |
| `vendor.documents.view` | platform | Open private vendor documents (trade licence, NID) through signed URLs; every view is audited | — | [06](modules/06-vendor-lifecycle.md) |
| `vendor.manage_status` | platform | Approve, reject, restrict, suspend, reactivate, close a vendor | Re-confirm + written reason | [06](modules/06-vendor-lifecycle.md) |
| `store.manage` | vendor | Edit own store profile, logo, banner, policies, pickup address | — | [06](modules/06-vendor-lifecycle.md) |

### Catalogue and inventory

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `catalog.category.manage` | platform | Create, edit, reorder, delete categories | — | [07](modules/07-catalogue.md) |
| `catalog.brand.manage` | platform | Create, edit, delete brands | — | [07](modules/07-catalogue.md) |
| `catalog.attribute.manage` | platform | Create, edit, delete attributes and attribute values | — | [07](modules/07-catalogue.md) |
| `product.view` | both | List and read products (platform: all vendors; vendor: own) | — | [07](modules/07-catalogue.md) |
| `product.create` | vendor | Create draft products and variants | — | [07](modules/07-catalogue.md) |
| `product.update` | both | Edit products (vendor edits create a pending revision; platform edits are limited to taxonomy and SEO fields) | — | [07](modules/07-catalogue.md), [08](modules/08-product-approval.md) |
| `product.delete` | vendor | Soft-delete own products that have no open orders | — | [07](modules/07-catalogue.md) |
| `product.submit` | vendor | Submit a draft or revision for approval | — | [08](modules/08-product-approval.md) |
| `product.approve` | platform | Approve or reject products and revisions | Written reason on reject | [08](modules/08-product-approval.md) |
| `review.moderate` | platform | Approve, hide or delete customer reviews | — | [07](modules/07-catalogue.md) |
| `inventory.view` | vendor | Read own stock levels and movements | — | [09](modules/09-inventory.md) |
| `inventory.adjust` | vendor | Post stock adjustments (each one is a movement row with a reason) | — | [09](modules/09-inventory.md) |

### Orders, delivery, returns

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `order.view` | vendor | List and read own vendor orders (only own items and the delivery address) | — | [11](modules/11-checkout-order-split.md) |
| `order.view_all` | platform | Read every parent and vendor order | — | [11](modules/11-checkout-order-split.md) |
| `order.accept` | vendor | Accept a confirmed vendor order; mark it ready to ship | — | [11](modules/11-checkout-order-split.md) |
| `order.cancel` | vendor | Cancel own vendor order before handover to the courier | Written reason | [11](modules/11-checkout-order-split.md) |
| `order.cancel_any` | platform | Cancel any vendor order before handover (support, suspended vendor) | Re-confirm + written reason | [11](modules/11-checkout-order-split.md) |
| `shipment.book` | vendor | Book, re-book or cancel a Steadfast parcel for own vendor order | — | [13](modules/13-steadfast-courier.md) |
| `courier.reconcile` | platform | Import Steadfast remittance statements and resolve mismatches | — | [13](modules/13-steadfast-courier.md) |
| `return.decide` | vendor | Accept or reject return requests on own orders | Written reason on reject | [14](modules/14-returns-refunds.md) |
| `return.decide_any` | platform | Decide disputed or overdue (48 h) returns for any vendor | Written reason | [14](modules/14-returns-refunds.md) |
| `refund.approve` | platform | Approve a refund; above the configured amount a 2nd approver is required | Re-confirm; 2nd approver above threshold | [14](modules/14-returns-refunds.md) |
| `payment.view` | platform | Read payment records and COD collection status | — | [12](modules/12-payments.md) |

### Finance

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `finance.view` | both | Read ledger, balances and statements (platform: all; vendor: own) | — | [15](modules/15-finance.md) |
| `finance.commission.manage` | platform | Create and end commission rules | Re-confirm | [15](modules/15-finance.md) |
| `finance.adjust` | platform | Post a manual ledger adjustment with reason; above threshold needs a 2nd approver | Re-confirm; 2nd approver above threshold | [15](modules/15-finance.md) |
| `payout.request` | vendor | Request a payout up to the available balance (min BDT 1,000) | — | [15](modules/15-finance.md) |
| `payout.approve` | platform | Approve or reject payout requests; never one's own request | Re-confirm; 2nd approver above threshold | [15](modules/15-finance.md) |
| `payout.record` | platform | Record the bank/bKash/Nagad transfer reference, which posts the payout entries | Re-confirm | [15](modules/15-finance.md) |

### Reports and marketing

| Permission | Scope | Allows | Extra step | Module |
| --- | --- | --- | --- | --- |
| `report.view` | platform | Platform dashboards and reports (spec 14) | — | [16](modules/16-reports-notifications-seo.md) |
| `report.view_own` | vendor | Own vendor dashboard and reports | — | [16](modules/16-reports-notifications-seo.md) |
| `report.export` | both | Queue a CSV export of a report with the same scope as the screen; audited | — | [16](modules/16-reports-notifications-seo.md) |
| `content.manage` | platform | Pages, banners, FAQs (Bangla and English) | — | [16](modules/16-reports-notifications-seo.md) |
| `marketing.manage` | platform | Coupons, campaigns, pixels — **Phase 4**, seeded but granted to nobody until then | — | — |

Totals: 45 permissions — 25 platform, 14 vendor, 6 both.

## 3. Platform roles (`team_id = NULL`)

✓ = granted by the seeder. Super Admin is not listed: it holds every platform and `both` permission through a `Gate::before` check limited to platform context, and it is the only role that can manage the Super Admin role itself.

| Permission | Platform Admin | Catalog Manager | Order & Support | Finance Manager | Marketing Manager |
| --- | --- | --- | --- | --- | --- |
| `role.manage` | ✓ | | | | |
| `team.manage` | ✓ | | | | |
| `audit.view` | ✓ | | | ✓ | |
| `settings.manage` | ✓ | | | | |
| `customer.view` | ✓ | | ✓ | ✓ | |
| `customer.manage` | ✓ | | ✓ | | |
| `vendor.view` | ✓ | ✓ | ✓ | ✓ | |
| `vendor.documents.view` | ✓ | | | ✓ | |
| `vendor.manage_status` | ✓ | | | | |
| `catalog.category.manage` | ✓ | ✓ | | | |
| `catalog.brand.manage` | ✓ | ✓ | | | |
| `catalog.attribute.manage` | ✓ | ✓ | | | |
| `product.view` | ✓ | ✓ | ✓ | | ✓ |
| `product.update` | ✓ | ✓ | | | |
| `product.approve` | ✓ | ✓ | | | |
| `review.moderate` | ✓ | ✓ | ✓ | | |
| `order.view_all` | ✓ | | ✓ | ✓ | |
| `order.cancel_any` | ✓ | | ✓ | | |
| `courier.reconcile` | | | ✓ | ✓ | |
| `return.decide_any` | ✓ | | ✓ | | |
| `refund.approve` | | | ✓ | ✓ | |
| `payment.view` | ✓ | | ✓ | ✓ | |
| `finance.view` | ✓ | | | ✓ | |
| `finance.commission.manage` | | | | ✓ | |
| `finance.adjust` | | | | ✓ | |
| `payout.approve` | | | | ✓ | |
| `payout.record` | | | | ✓ | |
| `report.view` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `report.export` | ✓ | | | ✓ | ✓ |
| `content.manage` | ✓ | ✓ | | | ✓ |
| `marketing.manage` | | | | | (Phase 4) |

Platform Admin deliberately has no finance write permissions, so money moves only through the Finance Manager role and its second-approver rule.

## 4. Vendor roles (`team_id = vendor_id`)

| Permission | Vendor Owner | Store Manager | Inventory Staff | Order Staff | Accountant |
| --- | --- | --- | --- | --- | --- |
| `role.manage` | ✓ | | | | |
| `team.manage` | ✓ | | | | |
| `audit.view_own` | ✓ | ✓ | | | |
| `store.manage` | ✓ | ✓ | | | |
| `product.view` | ✓ | ✓ | ✓ | ✓ | |
| `product.create` | ✓ | ✓ | ✓ | | |
| `product.update` | ✓ | ✓ | ✓ | | |
| `product.delete` | ✓ | ✓ | | | |
| `product.submit` | ✓ | ✓ | ✓ | | |
| `inventory.view` | ✓ | ✓ | ✓ | ✓ | |
| `inventory.adjust` | ✓ | ✓ | ✓ | | |
| `order.view` | ✓ | ✓ | | ✓ | ✓ |
| `order.accept` | ✓ | ✓ | | ✓ | |
| `order.cancel` | ✓ | ✓ | | ✓ | |
| `shipment.book` | ✓ | ✓ | | ✓ | |
| `return.decide` | ✓ | ✓ | | ✓ | |
| `finance.view` | ✓ | | | | ✓ |
| `payout.request` | ✓ | | | | ✓ |
| `report.view_own` | ✓ | ✓ | | | ✓ |
| `report.export` | ✓ | | | | ✓ |

These match the acceptance scenarios in spec 16.3: Inventory Staff has no finance permission, and Accountant has no product permission.

## 5. What exists today and how it maps

`RolePermissionUserSeeder` seeds 24 CRUD-style permissions and three roles (`admin`, `manager`, `user`) on the `web` guard. The live local database has 20 of them (`invoice.*` is in the seeder but not in the database, so the seeder changed after it last ran). Phase 1 replaces them as follows:

| Seeded today | Becomes | Note |
| --- | --- | --- |
| `role.view`, `role.create`, `role.update`, `role.delete` | `role.manage` | Spatie roles admin page |
| `user.view`, `user.create`, `user.update`, `user.delete` | `team.manage` (staff), `customer.view` / `customer.manage` (customers) | `/api/admin/users` serves both today |
| `category.view`, `category.create`, `category.update`, `category.delete` | `catalog.category.manage` | Reading categories is public; no view permission needed |
| `product.view`, `product.create`, `product.update`, `product.delete` | Same names | Scope becomes vendor/both; platform loses create and delete |
| `invoice.view`, `invoice.create`, `invoice.update`, `invoice.delete` | Removed | No invoice module in the MVP |
| `report.view`, `report.create`, `report.update`, `report.delete` | `report.view`, `report.view_own`, `report.export` | Reports are read-only |
| Role `admin` | Super Admin | `admin@example.com` (local only) |
| Role `manager` | Platform Admin or Catalog Manager, decided per person | |
| Role `user` | No role (customers need none) | Customer access comes from owning the record |

`users.role` (string column) duplicates the Spatie role and is dropped once `AdminMiddleware` checks permissions instead (module 03).

## 6. Shape of `config/permissions.php`

```php
<?php

return [
    // name => [scope, description]
    'role.manage' => ['both', 'Manage roles and their permissions'],
    'team.manage' => ['both', 'Invite and manage members'],
    'vendor.manage_status' => ['platform', 'Change vendor status'],
    // … every row of section 2
];
```

The seeder reads this file, creates missing permissions, and fails loudly if a role definition references a permission that is missing or has the wrong scope. Role grants live in `config/roles.php` with the matrices from sections 3 and 4.

## 7. Implemented route permissions: ADR-12 phase 2, slice 1 (2026-11-25)

The backend enforces permissions through `App\Support\PermissionRegistry`, not through a `config/permissions.php` file. Admin routes fail closed: a route with no registry entry is refused. Vendor routes use the shop's own `VendorPermissionRegistry`, and the shop comes from the caller's membership. The routes below were added or changed in this slice. They reuse permissions that already exist. No new permission was created.

| Route | Checks today | Target name (section 2) | Audit event |
| --- | --- | --- | --- |
| `POST /api/admin/products/{product}/suspend` | `products.approve` | `product.approve` | `product.suspended` |
| `POST /api/admin/products/{product}/reactivate` | `products.approve` | `product.approve` | `product.reactivated` |
| `GET /api/admin/products/{product}/history` | `products.view` **or** `products.approve` | `product.view` | — |
| `GET /api/vendor/products/{product}/history` | vendor `products.manage`, own shop only (another shop: 404); admin identities hidden | `product.view` (vendor) | — |
| `GET /api/admin/commission` | `commission.view` (Phase 3) | `finance.view` | — |
| `GET /api/admin/commission/vendors` | `commission.view` (Phase 3) | `finance.view` | — |
| `PUT /api/admin/commission/default` (reason required) | `commission.manage` (Phase 3) | `finance.commission.manage` | `commission.default_changed` |
| `PUT /api/admin/vendors/{vendor}/commission` (needs the `commission_rate` key and a reason; `null` = use default, `0` = no commission) | `commission.manage` (Phase 3) | `finance.commission.manage` | `vendor.commission_changed` |

Vendors and vendor staff can never reach the commission routes. Those routes sit in the admin group behind `AdminMiddleware`, and a vendor cannot hold platform permissions.

**Removed (ADR-12):** the four `saas.*` permissions (`saas.plans.view`, `saas.plans.manage`, `saas.subscriptions.view`, `saas.subscriptions.manage`) and their `/api/admin/saas/*` routes. They were never seeded on any database, because migration `2026_11_25_000004` never ran, so no grants needed moving.

**Phase 3 (2026-11-25): dedicated commission permissions.** Two new admin permissions, in the registry group `commission` ("Vendor commission"):

| Permission | Scope | Allows | Replaces |
| --- | --- | --- | --- |
| `commission.view` | platform | Open Vendor Commission; read the default, every vendor's own and effective rate, and the change history | `vendors.view` on these routes |
| `commission.manage` | platform | Change the default rate and any vendor's own rate. A reason of at least 3 characters is always required. | `vendors.update` on these routes |

Migration `2026_11_25_000007_commission_permissions` copied every role grant, direct grant and explicit deny from `vendors.view` to `commission.view`, and from `vendors.update` to `commission.manage`. Nobody gained or lost access. On local data: `administrator`, `manager` and `super_admin` got both, and `support` got `commission.view`. Templates: `manager` picks up `commission.*`, `support` has `commission.view`, and `administrator` has everything. `vendors.update` no longer covers commission. Password re-confirmation was not added; it is still a later item (spec 12.1). The spec name `finance.commission.manage` stays the target for a future finance-permission rename.

**Phase 4 (2026-11-25): sales report permissions.** Registry group `sales-reports` ("Sales reports"):

| Permission | Scope | Allows | Granted by migration `000008` to |
| --- | --- | --- | --- |
| `reports.sales.view` | platform | Vendor Sales & Performance: `GET /api/admin/reports/vendor-sales`, `…/products`, `…/rankings`, `…/{vendor}` | administrator, manager, super_admin |
| `reports.sales.export` | platform | CSV exports (`GET /api/admin/reports/vendor-sales/export/{type}`: vendor-sales, product-sales, commission, earnings, payouts). Needs `reports.sales.view` too. Each export is audited as `report.exported`. | administrator, manager, super_admin |

`support` gets neither. The manager template picks up `reports.*`.

**Phase 5b (2026-11-25): admin inventory reports.** These use the existing `inventory.view` permission, so no new permission and no migration.

| Route | Checks today |
| --- | --- |
| `GET /api/admin/inventory/summary`, `/stock`, `/movements` | `inventory.view` |

- These routes are read-only; there is no admin route that writes stock.
- Platform admins change platform stock through the product forms. Those forms show a vendor product's stock as read-only and leave it out of the request. The backend still refuses any admin change to vendor stock with `403 STOCK_OWNERSHIP_DENIED`.
- Vendors see the history of their own products only: `GET /api/vendor/products/{product}/stock-movements`, with `products.manage`. Another shop's product returns 404.


**Phase 6a (2026-11-25): Platform POS permissions.** Registry group `platform-pos` ("Platform POS"). Migration `2026_11_25_000009_platform_pos` creates these permissions. It grants all ten to `administrator` and `super_admin`, and all except `platform_pos.settings.manage` to `manager`. `support` and `editor` get none. Vendor roles can never hold them: `VendorPermissionRegistry` is separate, and a test checks this.

| Permission | Allows |
| --- | --- |
| `platform_pos.access` | Open the module: `GET /api/admin/pos/bootstrap`, `/registers`, `/settings`. Every other POS route requires it as well. |
| `platform_pos.sales.create` | Product lookup (`/pos/products?code=` or `?search=`; platform-owned, active, approved only), customer lookup by exact phone (masked), `POST /pos/sales` |
| `platform_pos.sales.view` | See every sale (`GET /pos/sales`, `/pos/sales/{id or number}`). Without it, a cashier sees only their own sales; others return 404. |
| `platform_pos.sales.cancel` | `POST /pos/sales/{sale}/void`. Allowed only while the sale's own session is open and the sale has no returns. |
| `platform_pos.sales.return` | `POST /pos/sales/{sale}/returns`, within the return window, refunded from the returning cashier's open session. Can find any sale. |
| `platform_pos.discount.apply` | Line and sale discounts. A reason is required, and the total discount is capped at `max_discount_percent` (default 10) of the subtotal. |
| `platform_pos.register.open` | `POST /pos/registers/{register}/open`. Each register and each cashier can have only one open session. |
| `platform_pos.register.close` | `POST /pos/sessions/{session}/close` with a cash count. Closing someone else's session also needs `settings.manage`. |
| `platform_pos.reports.view` | `GET /pos/sessions`, `/pos/sessions/{session}` (session summary by method) |
| `platform_pos.settings.manage` | `POST`/`PATCH /pos/registers`, `PUT /pos/settings` |

Audit events: `pos.session.opened`, `pos.session.closed`, `pos.sale.created`, `pos.discount.applied`, `pos.sale.voided`, `pos.sale.returned`, `pos.register.created`, `pos.register.updated`, `pos.settings.updated`.

**POS Sales Management (2026-11-25).** Migration `2026_11_25_000010_pos_sales_management` adds four permissions and copies the existing grants, so nobody gained or lost access on the day:

| Permission | Grants copied from | Allows |
| --- | --- | --- |
| `platform_pos.sales.view_own` | `platform_pos.sales.create` | List and open your own POS sales (`/pos/sales`, `/pos/sales/{sale}`, `/pos/sales/{sale}/history`) |
| `platform_pos.refunds.process` | `platform_pos.sales.return` | Pay refunds. `POST /pos/sales/{sale}/returns` now needs `sales.return` **and** `refunds.process` |
| `platform_pos.registers.manage` | `platform_pos.settings.manage` | Create, edit and activate/deactivate registers; close another cashier's session (it was `settings.manage`) |
| `platform_pos.reports.export` | none; granted to administrator and super_admin | CSV export: `/pos/sales/export` (also needs `sales.view`) and `/pos/reports/export/{type}` (also needs `reports.view`) |

New routes:
- `GET /pos/returns`: needs `sales.view` or `sales.return`.
- `GET /pos/registers/{register}`: needs `registers.manage` or `reports.view`.
- `GET /pos/reports/{type}`: needs `reports.view`. The types are summary, daily, weekly, monthly, payments, cashiers, registers, cash-reconciliation and inventory-reconciliation.

Every route also needs `platform_pos.access`.

New audit events: `pos.sales.exported` and `pos.report.exported`. `pos.register.updated` now records the values before and after the change.

**Central purchasing, phase 1 (2026-11-25).** Migration `2026_11_25_000011_central_purchasing`.

Admin permissions, in the registry group `purchasing` plus two other groups:

| Permission | Allows | Granted to |
| --- | --- | --- |
| `suppliers.view` / `suppliers.manage` | Platform suppliers: list and view / create and edit | admin, super; manager gets view |
| `purchases.view` | Purchase orders, receipts (and, from phase 2, invoices, payments and returns) | admin, super, manager |
| `purchases.create` | Create, edit (draft only), place and cancel purchase orders | admin, super |
| `purchases.receive` | Receive goods into platform stock. This is the only purchase step that adds stock | admin, super, manager |
| `purchases.return`, `purchases.invoice`, `purchases.pay`, `purchases.export` | Phase 2 and 3 | admin, super |
| `purchases.reports.view` | Purchase reports and supplier balances (phase 3) | admin, super, manager |
| `inventory.adjust` | `POST /api/admin/inventory/adjustments`: counted level or signed change (adjustment or damage), with a required reason; audited as `inventory.adjusted`. Platform stock only | admin, super, manager |
| `sales.combined.view` | Combined POS + online sales report (phase 3) | admin, super, manager |

**Platform stock is read-only in the product forms (D3).** A product or variant form that would change platform stock is refused with `422 PLATFORM_STOCK_READ_ONLY`. Platform stock changes only through:
- purchase receiving;
- POS and online sales, voids, cancellations and returns;
- an audited adjustment.

The `editor` template no longer changes platform stock.

**Vendor team permissions** (`VendorPermissionRegistry`, group `purchasing`):
- `purchases.manage`: suppliers, orders, receiving and returns for the shop's own stock. Added to existing shop roles that had `products.manage`.
- `purchases.pay`: invoices and payments. Added to roles that had `finance.view`.
- Templates: manager has both; staff, editor and inventory have `purchases.manage`; accountant has `purchases.pay`.

**Routes:**
- Shop side: `/api/vendor/suppliers`, `/purchase-orders` and `/purchase-receipts` (needs `vendor:active,purchases.manage`).
- Platform side: `/api/admin/…`, the same paths.
- The owner always comes from the caller (`PurchaseScope`), never from request input. Another owner's record returns 404, and another owner's product is refused with `PRODUCT_NOT_OWNED`.

**ADR-13 first-party retail (2026-11-26, planned):**
- ADR-13 adds **no new permissions**.
- `sales.combined.view` now means the **platform-owned** Combined view: POS plus platform online lines. Vendor marketplace sales are never added in (spec 14.2a).
- **Vendor purchasing is switched off (BD-16, phase P5):**
  - `purchases.manage` and `purchases.pay` are removed from `VendorPermissionRegistry`;
  - `routes/vendor-purchasing.php` is unregistered.
  
  Existing grants stay in the database but give no access, because the registry fails closed. The platform-side purchasing permissions above are unchanged.
