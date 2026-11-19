# Module specifications

One page per MVP module (spec section 18). Status values come from the [Phase 0 audit](../audit/phase-0.md), updated after the Steadfast integration was merged (19 Nov 2026).

| Module | Phase | Depends on | Status |
| --- | --- | --- | --- |
| [Identity and authentication](01-identity-auth.md) | 1 | — | Partial |
| [Tenancy (memberships, TenantContext)](02-tenancy.md) | 1 | Identity | Missing |
| [Roles and permissions (Spatie teams)](03-roles-permissions.md) | 1 | Tenancy | Partial |
| [Audit log](04-audit-log.md) | 1 | Identity | Partial |
| [Design system, shell, theme, i18n](05-design-system.md) | 1 | — | Partial |
| [Vendor onboarding and lifecycle](06-vendor-lifecycle.md) | 2 | Tenancy, roles | Missing |
| [Catalogue (categories, brands, products, variants, media)](07-catalogue.md) | 2 | Vendors | Partial |
| [Product approval](08-product-approval.md) | 2 | Catalogue | Missing |
| [Inventory and reservations](09-inventory.md) | 2 | Catalogue | Partial |
| [Customer account, cart, wishlist](10-customer-cart.md) | 2 | Catalogue | Partial |
| [Checkout and order split](11-checkout-order-split.md) | 2 | Cart, inventory | Partial |
| [Payments (COD; online after launch)](12-payments.md) | 3 | Checkout | Missing |
| [Steadfast courier and shipments](13-steadfast-courier.md) | 3 | Orders | Partial |
| [Returns and refunds](14-returns-refunds.md) | 3 | Payments, shipments | Missing |
| [Commission, ledger, settlement, payouts](15-finance.md) | 3 | Orders, refunds | Missing |
| [Reports, notifications, storefront SEO](16-reports-notifications-seo.md) | 3 | All above | Partial |
