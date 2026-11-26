# Architecture Decision Records

One file per decision (spec section 5). To change a decision, add a new ADR that supersedes the old one; never edit history.

| ADR | Title | Status |
| --- | --- | --- |
| [01](01-architecture.md) | Modular monolith | Proposed — partly confirmed by Phase 0 (audit §3) |
| [02](02-tenancy.md) | Single database, shared tables | Proposed — not started (no `vendor_id` exists today) |
| [03](03-tenant-context.md) | Tenant context from the server | Proposed |
| [04](04-authentication.md) | Sanctum SPA cookie authentication | **Confirmed** by Phase 0 (already in use) |
| [05](05-roles-permissions.md) | Spatie Permission with teams | Proposed — Spatie confirmed installed (v8, teams off) |
| [06](06-queue.md) | Database queue driven by cron | Proposed — partly in place (`QUEUE_CONNECTION=database` locally) |
| [07](07-frontend-hosting.md) | Next.js with a Node runtime | Proposed — **blocked** on cPanel Node.js support |
| [08](08-money.md) | Decimal storage, exact arithmetic | **Confirmed** for storage; arithmetic not yet |
| [09](09-time.md) | Store UTC, show Asia/Dhaka | **Confirmed** for storage (`config/app.php` timezone is `UTC`) |
| [10](10-search-media.md) | MySQL FULLTEXT and WebP media | Proposed — not started |
| [11](11-retail-saas-on-vendor-tenant.md) | Retail SaaS (POS, inventory, accounts) on the Vendor tenant | **Superseded** by ADR-12 (2026-11-25); slice 1a inventory kept |
| [12](12-platform-pos-no-subscriptions.md) | Marketplace-only vendors, Platform Admin POS, no subscriptions | **Accepted** 2026-11-25; POS scope and platform stock extended by ADR-13 |
| [13](13-first-party-retail.md) | First-party retail: platform-owned stock through POS and online, reservations, WAC, locations, sales channel | **Accepted** 2026-11-26 |
| [14](14-partnership-accounting.md) | Partnership accounting: platform ledger, variable partners with equal shares | **Accepted** 2026-11-26 (with owner changes C1–C3) |
