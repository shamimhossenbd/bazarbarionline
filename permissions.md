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
