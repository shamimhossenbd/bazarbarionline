# BazarBariOnline — Multi-Vendor Marketplace Specification v2

Nov 19, 2026 · @Md Shamim Hossen

## 0. Document control

This is v2 of the BazarBariOnline specification. It replaces v1 (Parts 1–40) with one roadmap, explicit decisions, Bangladesh-specific commerce rules and a defined MVP. Status: **draft for owner review**. Nothing here authorizes production code, schema or infrastructure changes until Phase 0 is approved.

**How to read it**

- Sections 1–5 are the foundation: facts, business model, glossary, rules and architecture decisions. Read these first.
- Sections 6–14 describe each domain once. Each topic that v1 repeated in several Parts now lives in one place.
- Sections 15–21 cover operations, testing, the roadmap, the module register and the Phase 0 audit.
- Lines marked **Assumption** are not yet confirmed by the owner. Replace each with a decision before building on it.

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| v2.12 | 2026-11-28 | **ADR-15 (marketing and analytics)** accepted with answers MQ1–MQ6: Settings → Marketing & Analytics and a "Marketing" sidebar group; GTM or direct GA4, never both; Meta Pixel loaded directly with the Conversions API sharing `event_id`s; trackers on shop pages only; nothing sent to Meta without cookie consent (stored on the order); one "Delivered" event per order; reports read our own synced tables; ad spend never posts to the ledger (5106 via expenses). Leads = `/contact` submissions; newsletter sign-ups are "Subscribers". Section 5 updated. Not built yet. |
| v2.11 | 2026-11-26 | **ADR-14 (partnership accounting)** drafted for owner review: platform double-entry ledger in poisha, monthly periods that never reopen, and maker-checker. Partners are now a variable number with **equal** shares, stored as membership periods (no percentages). A month's result is spread evenly over its days; the rounding remainder goes to the lowest id. Leaving partners settle after month close, and a negative balance is collected. No migration before review. Sections 5 and 18 updated. |
| v2.10 | 2026-11-26 | Admin navigation reorganised into seven sections: Online Sales, POS Sales, Purchase & Inventory, Marketplace, Website, Accounts and Settings & Access. One audit log with a `module` per event, and one permission system with a module map (stored names unchanged). Each section has its own Audit log and Roles & permissions pages. Eight starter roles. Dashboard cards for Online, POS and Vendor sales, plus "Total GMV". The admin Orders page is built (it fixes the old 404). See permissions.md. |
| v2.9 | 2026-11-26 | Owner addendum A–H adopted as **ADR-13 (first-party retail)**:<br>• The platform sells its own stock through POS and online. Platform-owned stays `vendor_id NULL`, shown as the house seller "BazarBari Official".<br>• One stock ledger with reservations (available = on hand − reserved); weighted average cost; one location, with `location_id` ready.<br>• `sales_channel` on headers, payments and returns.<br>• Platform and marketplace reports are never added together.<br>• No vendor purchasing in this phase.<br>BD-01 and BD-11 amended, BD-15 and BD-16 added; sections 5, 9, 14, 17 and 18 updated; module 09 rewritten. |
| v2.8 | 2026-11-25 | Master task adopted (ADR-12, supersedes ADR-11): vendors online-only, Platform Admin POS for platform products, no subscriptions, admin-managed per-vendor commission with a DB-stored default. BD-01/11/13/14 updated. |
| v2.7 | 2026-11-25 | BD-14 decided (paid plans with limits and optional trial, manual activation, no gateway; no POS commission) and BD-01 amended accordingly. ADR-11 updated. |
| v2.6 | 2026-11-25 | Retail SaaS direction: BD-11 reversed (POS in scope), BD-13 added (Vendor = tenant, storefronts later), BD-14 opened (plans vs BD-01, POS commission). ADR-11 written. |
| v2.5 | 2026-11-19 | Source control: three private GitHub repositories (`bazarbari-api`, `bazarbari-web`, `bazarbarionline` for docs); section 1, 15.2, 19.3 Q10, audit §7.2, runbooks 03 and README updated. Project READMEs written; `runbooks/incident-log.md` created. |
| v2.4 | 2026-11-19 | Steadfast courier integration merged (`laravel-ecommerce` master `dace94a`, 13 commits, 148 tests): modules 04 and 13 now Partial, module 16 note updated; `openapi.yaml` regenerated (105 routes; first `/api/v1` route is the Steadfast webhook); section 1 source control updated (both projects in Git); audit §7 adds the `CACHE_DRIVER` finding. |
| v2.3 | 2026-11-19 | Documentation completed: permission catalogue (`permissions.md`), OpenAPI file (`openapi.yaml`, 98 implemented routes + planned v1), six runbooks (`runbooks/`). Audit §7 records fixes since Phase 0 (H1, H2, H4 fixed; H3, H5 partly). |
| v2.2 | 2026-11-19 | Phase 0 audit done (`audit/phase-0.md`). Section 1 facts verified; flow diagrams in 7 and 17 written out; webhook row in 10.3 fixed; module register (18) and checklist (19.1) filled from evidence; ADR files (`adr/`) and module specs (`modules/`) created. |
| v2.1 | 2026-11-19 | Owner decisions applied: commission only, COD only at launch, Steadfast courier, 7-day return window, manual payouts, delivery fee per vendor order, approval for every product, POS removed. Sections 2, 6, 7, 10, 16, 17, 19 and 20 updated. |
| v2.0 | 2026-11-19 | Restructured v1 into 22 sections; fixed backend path; added business model, Bangladesh payments/courier/COD, Next.js hosting decision, MVP scope, ADRs, glossary and learning path; merged duplicate Parts (audit 9+34, notifications 21+35, analytics 18+28+33, vendor control 27+30, security 8+20) |
| v1.0 | — | Consolidated Parts 1–40 (architecture, security and implementation spec) |

**Where v1 Parts went**

| v1 Part(s) | v2 section |
| --- | --- |
| 1, 13, 14, 17, 19, 23 | 11. Frontend |
| 2–8, 11 | 6. Identity, tenancy and access control |
| 9, 20, 34, 38 | 12. Security baseline |
| 10, 12, 39 | 5. ADRs and 10. API |
| 15, 16, 40.3 | 16. Testing and definition of done |
| 18, 28, 33 | 14. Reporting |
| 21, 35 | 13. Notifications and jobs |
| 22, 36, 37 | 15. Operations |
| 24, 25.8 | 17. Roadmap (one ordering instead of two) |
| 25, 26 | 9. Data model and 18. Module register |
| 27, 29, 30, 32 | 6.6 Vendor lifecycle controls and 8. Finance |
| 31 | 8. Finance |
| 40.1, 40.2 | 19. Phase 0 audit |

## 1. Project facts and environment

BazarBariOnline is a Laravel 13 API with a Next.js storefront and dashboards, hosted on cPanel shared hosting. Code facts below were verified in the Phase 0 audit (19 Nov 2026); items still marked *verify* need the production server.

| Item | Value |
| --- | --- |
| Project root | `D:\bazarbarionline\` |
| Backend path | `D:\bazarbarionline\laravel-ecommerce` (v1 said `laravel-ecommers`; corrected) |
| Frontend path | `D:\bazarbarionline\next-ecommerce` |
| Docs path | `D:\bazarbarionline\documentation` |
| Backend | Laravel 13.24.0 REST API, PHP ^8.3 (local CLI 8.4.12), Sanctum 4, Spatie Permission 8, Pest 4, MySQL (*verify* production MySQL and PHP versions) |
| Frontend | Next.js 16.3.0 App Router, React 19.2.8, TypeScript 5, Bootstrap ^5.3.8, axios, Zustand, react-hook-form + Zod |
| Source control | Git, one private GitHub repository per folder: `laravel-ecommerce` → `shamimhossenbd/bazarbari-api` (`master`), `next-ecommerce` → `shamimhossenbd/bazarbari-web` (`master`), `documentation` → `shamimhossenbd/bazarbarionline` (`main`). No CI yet (spec 15.2). The root `D:\bazarbarionline` is **not** a repository and must never be `git init`-ed; `backups\` holds database dumps and is never committed. |
| API and admin domain | `https://api.bazarbarionline.com` |
| Storefront domain | `https://bazarbarionline.com` |
| Hosting | cPanel shared hosting (*verify* Node.js app support, PHP CLI path, cron, SSH) |
| Queue | `QUEUE_CONNECTION=database` locally (no scheduler or cron yet); production value *verify*; target in ADR-06 |
| Market | Bangladesh; currency BDT; languages Bangla and English |
| Display time zone | Asia/Dhaka (UTC+6); storage in UTC |
| Team | One developer-owner (Shamim Web Solutions) |

**Assumption:** the production brand domain will move from `shamimwebsolutions.com` to a BazarBariOnline domain before public launch. All domain values must come from `.env`, never hard-coded, so this move needs no code change.

## 2. Business model and decision register

BazarBariOnline is a marketplace and a first-party retailer.

- **Vendors** list for free. The platform takes a commission per delivered item, collects Cash on Delivery through Steadfast Courier, and pays vendors manually 7 days after delivery.
- **The platform** also buys its own stock and sells it through its POS and online (BD-15, ADR-13).

The owner first confirmed these decisions on 19 Nov 2026, with amendments since. Only the legal basis (BD-12) is still open.

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| BD-01 | How does the platform earn? | Two ways, kept apart in reports (ADR-13):<br>1. **Commission** per delivered **marketplace vendor** order item. The rate is set per vendor by an authorized admin, with an admin-editable platform default stored in the database as the fallback. 0% is a valid rate. The rate is snapshotted at checkout.<br>2. **First-party sales** of the platform's own purchased stock, through POS and online (BD-15). This is platform sales revenue, never commission.<br>**No subscriptions** (ADR-12). | Confirmed (amended 2026-11-26) |
| BD-02 | Can one cart hold items from several vendors? | Yes. Checkout creates one **parent order** for the customer and one **vendor order** per vendor. Each vendor order ships, cancels and settles on its own. | Confirmed |
| BD-03 | Who ships? | Vendor packs; the platform books **Steadfast Courier** through its API. A second courier may be added after launch. | Confirmed |
| BD-04 | Payment methods at launch | **Cash on Delivery only.** Online payment (SSLCommerz or direct bKash/Nagad) is added after launch. | Confirmed |
| BD-05 | Who holds customer money? | The platform. Steadfast collects COD cash and remits it to the platform's account. | Confirmed (follows from BD-03 and BD-04) |
| BD-06 | When is vendor money payable? | 7 days after delivery, when the return window closes with no open return. | Confirmed |
| BD-07 | How are vendors paid? | Manual: vendor requests a payout, finance sends it by bank or bKash/Nagad and records the reference in the ledger. | Confirmed |
| BD-08 | Who pays delivery charge? | Customer, per vendor order, by zone (inside Dhaka, Dhaka suburbs, outside Dhaka). | Confirmed |
| BD-09 | Product approval | **Every** new or edited product from **every** vendor needs platform approval before it is visible. No auto-approve. | Confirmed |
| BD-10 | Categories and brands | Global, owned by the platform. Vendors pick from them and can request new ones. | Confirmed |
| BD-11 | POS for physical shops | **POS is required for the platform's own (first-party) sales** (ADR-12, extended by ADR-13 on 2026-11-26).<br>• It sells platform-owned products only and has its own sales, registers, sessions, returns and reports.<br>• It shares the one stock ledger with online sales.<br>• It creates no vendor earnings or commission.<br>• Vendors have no POS. | Confirmed (amended 2026-11-26) |
| BD-15 | Platform-owned stock | **First-party retail** (ADR-13):<br>• The platform buys stock through central purchasing and sells it through POS and through the online storefront, next to vendor products.<br>• Platform-owned means `products.vendor_id IS NULL`, with the same product, variant, stock and movement tables as vendors. There is no parallel system and no "house vendor" row.<br>• Customers see the house seller identity "BazarBari Official".<br>• One stock ledger: available = on hand − reserved. POS takes stock at once. Online checkout reserves it, and the reservation converts when the order is confirmed.<br>• Weighted average cost; the unit cost is stored on every sale line.<br>• One stock location for now. | Confirmed (2026-11-26) |
| BD-16 | Vendor purchasing | **Not offered in this phase** (ADR-13). The vendor purchasing routes, UI and permissions are switched off, and the code is kept for later. Vendors record stock with audited adjustments. Replaces decision D1 of 2026-11-25 for now. | Confirmed (2026-11-26) |
| BD-13 | Tenant model | Each Vendor is a marketplace tenant (isolated data, own staff RBAC), online sales only. The vendor Retail SaaS of ADR-11 is withdrawn (ADR-12). | Confirmed (amended 2026-11-25) |
| BD-14 | Vendor subscription plans and POS commission | **Closed: no subscription plans, fees or trials** (ADR-12). Platform POS carries no vendor commission. | Confirmed (2026-11-25) |
| BD-12 | Legal basis | Platform operates under Bangladesh's Digital Commerce Operation Guidelines (2021) and related rules. A qualified adviser must confirm obligations on delivery time limits, refunds and trade licence/e-TIN/VAT. | Open |

**Rule:** when an assumption changes, update this table first, then the affected sections, then the change log in section 0.

## 3. Glossary

Each term has one meaning across code, API, UI and this document.

| Term | Meaning |
| --- | --- |
| Platform | BazarBariOnline as operator: its staff, settings, revenue and ledger accounts |
| Vendor | A seller business on the platform. In this system **vendor = tenant**. |
| Store | The public-facing profile and settings of one vendor (one store per vendor in MVP) |
| Membership | A row linking a user to a vendor with a role; the only source of tenant context |
| Platform user | A user with a platform role; may also hold vendor memberships |
| Customer | A buyer account; may check out as guest with phone OTP |
| Parent order | What the customer placed at checkout; groups vendor orders and payments |
| Vendor order | The part of a parent order belonging to one vendor; the unit of fulfilment and settlement |
| Shipment | One courier consignment for a vendor order |
| COD | Cash on Delivery: courier collects cash and remits it to the platform |
| Commission | Platform's share of a delivered order item, calculated from a commission rule |
| Ledger entry | An append-only financial record; balances are sums of entries |
| Settlement | Moving a vendor's earnings from pending to available after the return window |
| Payout | Money actually sent from the platform to a vendor |
| Return window | Days after delivery during which a customer may request a return |
| Audit event | An append-only record of a security- or business-relevant action |
| ADR | Architecture Decision Record: a short note of one decision, its reason and alternatives |

## 4. Non-negotiable engineering rules

These twelve rules apply to every change, by a human or an AI coding agent.

1. **Audit before change.** Read the related code, tables and routes first; never assume a model or table is missing.
2. **Reuse, never duplicate.** One system each for permissions, notifications, media, jobs, settings, audit and theme.
3. **Preserve working behaviour.** No rewrites of working modules without a written reason and approval.
4. **Backend enforces everything.** Every protected request is authenticated, authorized and tenant-scoped in Laravel. UI checks are convenience only.
5. **Tenant context comes from the server.** It is derived from the authenticated user's membership, never from a `vendor_id` sent by the browser.
6. **Deny by default.** A missing rule means no access.
7. **Real data only.** No mock, seeded or invented values in production dashboards, reports or financial screens. Show "not available" instead.
8. **Money is append-only.** Balances are computed from ledger entries; corrections are reversal entries.
9. **Approval gates.** Production migrations, destructive operations, package additions and deployment changes need a backup and explicit owner approval.
10. **Honest status.** Every report separates Implemented, Planned, Blocked and Untested.
11. **Modular monolith.** One Laravel app, one MySQL database, one Next.js app. No microservices without a written business and operational reason.
12. **Done means tested.** A feature is done only when the Definition of Done in section 16 is met.

## 5. Architecture decisions (ADRs)

Ten decisions fix the shape of the system; each is proposed, to be confirmed against Phase 0 evidence. If the audit contradicts one, write a new ADR rather than silently changing course.

| ADR | Decision | Why | Alternative rejected |
| --- | --- | --- | --- |
| 01 Architecture | Laravel modular monolith with domain folders (`app/Domain/<Name>`); Next.js app with route groups | One developer, shared hosting, one database | Microservices; separate vendor app |
| 02 Tenancy | Single database, shared tables. Vendor-owned tables carry `vendor_id`. A `BelongsToVendor` trait adds a global scope from the current tenant context. | Simplest model that isolates data on shared hosting | Database-per-tenant (needs many DBs, hard on cPanel) |
| 03 Tenant context | A `TenantContext` service is set by middleware from the user's active membership (`X-Vendor` header only *selects* among the user's own memberships and is re-checked every request) | Prevents trusting browser IDs | Reading `vendor_id` from request body |
| 04 Authentication | Laravel Sanctum SPA cookie auth for the storefront and dashboards (same parent domain). `SESSION_DOMAIN=.<parent-domain>`, `SANCTUM_STATEFUL_DOMAINS` set to the frontend host, CORS `supports_credentials=true`. Personal access tokens only for a future mobile app. | HttpOnly cookies keep tokens out of JavaScript | Bearer tokens in localStorage |
| 05 Roles and permissions | Spatie Laravel Permission with **teams enabled**, `team_id` = `vendor_id`. Platform roles are global (`team_id` NULL). Permissions named `module.action`. | One permission system for both domains; native per-vendor roles | Two separate role systems. Re-decide only if the audit shows Spatie is absent or already used differently. |
| 06 Queue | `QUEUE_CONNECTION=database`. cPanel cron every minute runs `schedule:run`; the scheduler runs `queue:work --stop-when-empty --max-time=50`. Mail, notifications and exports go through the queue. | Gets work out of the request without a daemon | `sync` (slows checkout); Redis/Horizon (not available on shared hosting) |
| 07 Frontend hosting | Run Next.js as a Node.js app via cPanel "Setup Node.js App" with `output: 'standalone'` **if the host supports it**. Otherwise host the frontend on Vercel or a small VPS. Static export is not acceptable: storefront SEO needs server rendering. | App Router needs a Node runtime for SSR and middleware | Static export only |
| 08 Money | Store amounts as `DECIMAL(12,2)` in BDT; all arithmetic in PHP via integer paisa or `brick/money`; never floats. Single currency in MVP. | Avoid rounding errors in commission and payouts | `FLOAT` columns |
| 09 Time | Store UTC (`APP_TIMEZONE=UTC`); show Asia/Dhaka. Reports define day boundaries in Asia/Dhaka. | Correct daily sales totals | Storing local time |
| 10 Search and media | MySQL FULLTEXT search on product name and tags for MVP. Images converted to WebP in 3 sizes on upload, stored on the public disk outside the code folder. | Fits shared hosting; revisit Meilisearch/CDN when catalogue grows | External search service at launch |
| 11 Retail SaaS | Superseded by ADR-12 (only the shared inventory slice was kept) | — | — |
| 12 Platform POS, no subscriptions | Vendors sell online only. POS is a Platform Admin module for platform-owned products. No subscription plans. Commission is set per vendor. | Owner master task, 2026-11-25 | Vendor POS; paid plans |
| 13 First-party retail | Platform stock is `vendor_id NULL` with a house seller identity. One stock ledger with reservations. Weighted average cost. `location_id` ready for more locations. `sales_channel` everywhere. Reports never sum the platform and marketplace sections. No vendor purchasing for now. | Owner addendum A–H, 2026-11-26 | A "house vendor" row in `vendors`: it would make commission, ledger and payouts fail open |
| 14 Partnership accounting | Platform double-entry ledger in BIGINT poisha, monthly periods never reopened, maker-checker on manual entries. Partners are membership periods with equal shares; a month's result is spread over its days and split among the partners active each day. | Owner, 2026-11-26 (AQ1–AQ10, amendment, AM1–AM6) | Stored percentages or share versions; actual daily profit |
| 15 Marketing & analytics | GA4 through GTM or gtag (never both) and Meta Pixel + Conversions API, on shop pages only and only after cookie consent. Secrets encrypted and never returned. Reports read daily-synced tables (`analytics_daily`, `ad_campaign_daily`); our own orders are the source of truth. Ad spend is reporting only. | Owner, 2026-11-28 | Live API calls per report view; tracking through GTM for the Pixel; posting ad spend to the ledger |

Each ADR gets its own short file in `documentation/adr/NN-title.md` with Context, Decision, Consequences and Date.

## 6. Identity, tenancy and access control

One `users` table holds everyone; what a user may do comes from platform roles plus vendor memberships, checked on every request in the order of 6.2.

### 6.1 Identity model

- `users`: one row per person (platform staff, vendor staff, customer). Login by email or Bangladeshi mobile number plus password; customers may use phone OTP.
- `vendor_user` (membership): `user_id`, `vendor_id`, `status` (invited, active, suspended), `joined_at`. A user can belong to several vendors and switch between them.
- Vendor roles are Spatie roles with `team_id = vendor_id`; platform roles have `team_id = NULL`.

### 6.2 Authorization order (every protected request)

1. Authenticated and session valid (else 401).
2. Account active, not locked.
3. Context resolved: platform route group or vendor route group. Vendor context from an active membership (ADR-03).
4. Permission for the action in that context (Spatie, team set to current vendor).
5. Resource belongs to the context (policy + global scope). Another vendor's record returns 404, not 403, so its existence is not leaked.
6. Record state allows the action (e.g. a delivered order cannot be cancelled).
7. Extra step if required: password re-confirmation or a second approver.

### 6.3 Roles

| Domain | Role | Scope | Notes |
| --- | --- | --- | --- |
| Platform | Super Admin | All | System role; cannot be deleted; at least one active holder at all times |
| Platform | Platform Admin | All except role management of Super Admin | No implicit Super Admin powers |
| Platform | Catalog Manager | Products, categories, brands, approvals | Replaces v1 "Product Manager" + "Content" overlap |
| Platform | Order and Support Manager | Orders, returns, tickets |  |
| Platform | Finance Manager | Ledger, settlements, payouts, commission rules | Cannot approve own payout batch |
| Platform | Marketing Manager | Coupons, campaigns, pixels |  |
| Vendor | Vendor Owner | Own vendor | Created at vendor onboarding; cannot be removed by staff |
| Vendor | Store Manager | Own vendor, all operations except finance settings and team roles |  |
| Vendor | Inventory Staff | Own vendor products and stock |  |
| Vendor | Order Staff | Own vendor orders and shipments |  |
| Vendor | Accountant | Own vendor statements and payout requests (read + request) |  |

Vendor POS does not exist. Platform POS and cashier roles are Platform Admin permissions only (BD-11, ADR-12).

### 6.4 Permission catalogue rules

- Format `module.action`, for example `product.create`, `order.cancel`, `payout.approve`, `role.manage`.
- Each permission is tagged `platform`, `vendor` or `both`. A vendor role can only hold `vendor` or `both` permissions.
- A user can only grant permissions they themselves hold (no escalation). Nobody can change their own roles.
- Permissions are seeded from one PHP file (`config/permissions.php`) so they are versioned in Git. The full catalogue and role matrices are in [permissions.md](permissions.md).
- Change roles only through Spatie APIs so its cache resets; never write pivot tables directly.

### 6.5 Team invitations

Invite creates a 64-byte random token, stores only its SHA-256 hash, expires in 72 hours, and is single-use. Invite and accept endpoints are rate-limited (5 per minute per user/IP) and return the same response whether the email exists or not. Create, resend, accept, expire and revoke are audit events.

### 6.6 Vendor lifecycle controls

States: `pending` → `active` ↔ `restricted` ↔ `suspended` → `closed`.

| State | Storefront | New orders | Existing orders | Payouts |
| --- | --- | --- | --- | --- |
| Active | Visible | Accepted | Normal | Normal |
| Restricted | Visible | Blocked or limited per restriction | Must be fulfilled | Normal unless frozen |
| Suspended | Hidden | Blocked | Platform support completes or cancels with refund | Frozen pending review |
| Closed | Hidden | Blocked | Must all be closed first | Final settlement then stop |

Every state change needs `vendor.manage_status`, a written reason, confirmation, and an audit event. Suspension never deletes data. Risk indicators (high cancellation rate, unusual refunds, many failed logins) are shown to platform reviewers with the formula used; they never trigger automatic suspension in MVP.

## 7. Orders, checkout, payments and delivery

Checkout splits one customer order into one vendor order per vendor; each vendor order moves through its own states, ships through a courier, and is settled to the vendor only after delivery and the return window.

```
1. Cart (items from one or more vendors)
        │  checkout, one DB transaction
        ▼
2. Parent order ──► one vendor order per vendor (status: confirmed, COD)
        │
        ▼
3. Vendor accepts and packs ──► Steadfast parcel booked (ready_to_ship)
        │
        ▼
4. Steadfast picks up (shipped) ──► delivers and collects COD cash (delivered)
        │                                   │
        │                                   ▼
        │                    Ledger: vendor earnings (pending) + platform commission
        ▼
5. Steadfast remits cash to the platform ──► reconciled against shipments
        │
        ▼
6. 7-day return window closes, no open return ──► earnings move pending → available
        │
        ▼
7. Vendor requests payout ──► finance approves and sends ──► ledger: available → paid
```

Each vendor order follows this path on its own; a two-vendor checkout runs it twice.

### 7.1 Checkout steps (one database transaction where marked)

1. Validate cart: every item active, vendor active, price unchanged since cart (else show the change).
2. **\[tx\]** Lock stock rows (`SELECT … FOR UPDATE`), create stock reservations, create parent order, vendor orders, order items with snapshots (name, SKU, unit price, discount, commission rate), and the delivery address snapshot.
3. COD (the only method at launch): confirm order immediately (status `confirmed`). After launch, online orders get status `awaiting_payment` and redirect to the gateway.
4. Gateway callback/IPN: verify signature and amount **server-to-server** with the gateway's validation API, then mark paid. The browser redirect alone never marks an order paid.
5. Reservations for unpaid online orders expire after 30 minutes and release stock (scheduled job).
6. Send confirmations through the queue (SMS + email + in-app).

Idempotency: checkout requests carry an `Idempotency-Key` header; IPN handlers store the gateway transaction ID with a unique index so a repeated callback changes nothing.

### 7.2 Vendor order states

| From | To | Who | Condition |
| --- | --- | --- | --- |
| awaiting\_payment | confirmed | System | Payment validated |
| awaiting\_payment | cancelled | System | Reservation expired |
| confirmed | processing | Vendor | Vendor accepts |
| confirmed / processing | cancelled | Customer, vendor or platform | Before handover to courier; refund if prepaid |
| processing | ready\_to\_ship | Vendor | Packed; courier booking created |
| ready\_to\_ship | shipped | Courier webhook / vendor | Picked up |
| shipped | delivered | Courier webhook | COD collected or prepaid delivered |
| shipped | delivery\_failed | Courier webhook | Returned to vendor |
| delivered | return\_requested | Customer | Within return window |
| return\_requested | returned / return\_rejected | Vendor, then platform on dispute | Item received or reason given |
| delivered | completed | System | Return window closed, no open return |

The parent order status is derived from its vendor orders (for example "partly delivered"); it is never edited directly. Every transition writes an `order_status_history` row with actor and reason.

### 7.3 Payments (Bangladesh)

| Method | MVP | Integration notes |
| --- | --- | --- |
| Cash on Delivery | Yes | Only method at launch. Steadfast collects; remittance reconciled against Steadfast payout statements |
| SSLCommerz | After launch | One integration covers cards, bKash, Nagad, Rocket, net banking; validate each IPN through the validation API |
| bKash direct (tokenized checkout) | Later | Lower fees at volume; needs merchant agreement |
| Nagad direct | Later | Same |

Gateway credentials live only in `.env` or encrypted settings; the UI shows them masked. Refunds of online payments go back through the same gateway where it supports refunds, otherwise by recorded manual transfer.

### 7.4 Delivery and courier

- Courier adapter interface `CourierGateway` with `quote`, `book`, `track`, `cancel`; first implementation for Steadfast Courier; a second courier can be added later behind the same interface.
- Delivery charge by zone: inside Dhaka, Dhaka suburbs, outside Dhaka. Zones and charges are platform settings.
- Courier webhooks are verified (signature or secret), idempotent, and update shipment and vendor-order states.
- COD remittance: each courier payout batch is imported and matched to shipments; differences appear in a reconciliation report.

### 7.5 Returns and refunds

Customer requests a return per item with reason and photo. Vendor accepts or rejects within 48 hours; unresolved or disputed cases go to platform support. An accepted return creates a refund record and reversal ledger entries (section 8). Refund approval above a configurable amount needs a second platform approver.

## 8. Finance: commission, ledger, settlement, payouts

A vendor's balance is never stored as an editable number; it is the sum of append-only ledger entries, and every entry points back to the order, refund or payout that caused it.

### 8.1 Commission

- `commission_rules`: scope (`category`, `vendor`, `vendor+category`), rate %, optional fixed fee, `valid_from`, `valid_to`. The most specific active rule wins: vendor+category → vendor → category → platform default.
- The rate is copied onto each order item at checkout; later rule changes never alter existing orders.
- Commission base = item price × qty − vendor-funded discount. Delivery charge is not commissioned (**Assumption**).
- Only `finance.commission.manage` can change rules; vendors can view their own rates.

### 8.2 Ledger design

One table `ledger_entries`: `id`, `account_type` (`vendor`, `platform_revenue`, `platform_cash`, `courier_receivable`, `customer_refund`), `account_id`, `amount` (signed DECIMAL), `entry_type`, `reference_type`, `reference_id`, `bucket` (`pending`, `available`, `paid`), `created_by`, `created_at`, `reversal_of_id`. No `updated_at`; the application never updates or deletes rows, and the DB user for the app has no `DELETE` on this table where hosting allows it.

| Event | Entries |
| --- | --- |
| Vendor order delivered | Vendor +net earnings (pending); Platform revenue +commission |
| COD remitted by courier | Courier receivable −amount; Platform cash +amount |
| Return window closes | Vendor pending −X, Vendor available +X |
| Refund after delivery | Reversal of the matching earnings and commission lines |
| Payout sent | Vendor available −X, Vendor paid +X, Platform cash −X |
| Manual adjustment | Entry with reason and approver; above threshold needs maker-checker |

This is a single-entry ledger with references, which is enough for MVP. Call it double-entry only if every event is later posted as balanced debit/credit pairs and tested.

### 8.3 Balances

- Pending = sum of vendor entries in `pending`.
- Available = sum in `available` minus open payout requests.
- Paid = sum in `paid`.
- A nightly job recomputes balances and compares them with a cached summary; any difference raises a finance alert.

### 8.4 Payouts

1. Vendor Accountant or Owner requests a payout up to the available balance (minimum BDT 1,000, a platform setting).
2. Finance Manager reviews; approval above a threshold needs a second approver; nobody approves their own request.
3. Money is sent outside the system (bank or mobile-financial-service transfer); the finance user records the transfer reference.
4. Recording the reference posts the payout entries and notifies the vendor.
5. Payout state changes are idempotent and run inside a transaction with a row lock on the vendor's balance summary.

Vendor statements (monthly PDF/CSV) list every entry with its order or payout reference.

## 9. Core data model

The MVP needs about 35 tables beyond Laravel and Spatie defaults; this is a target list to compare against the existing schema in Phase 0, not a migration checklist. Existing tables with the same purpose are reused and renamed only with approval.

| Group | Tables | Owner | Key rules |
| --- | --- | --- | --- |
| Identity | `users`, `vendor_user`, Spatie `roles`/`permissions`/pivots, `team_invitations`, `personal_access_tokens`, `sessions` | Platform | Unique email and phone; membership unique per (user, vendor) |
| Vendors | `vendors`, `vendor_documents`, `vendor_settings`, `vendor_status_history` | Platform | `status` enum; trade licence and NID stored as private files |
| Catalogue | `categories`, `brands`, `attributes`, `attribute_values`, `products`, `product_variants`, `product_images`, `product_attribute_values` | Platform (taxonomy), vendor (products) | `products.vendor_id`; SKU unique per vendor; FULLTEXT(name, tags) |
| Inventory | Balance on `products.stock` / `product_variants.stock` (on hand) and `reserved_stock` (planned, `000012`)<br>`stock_movements` (built)<br>`stock_reservations` and `stock_locations` (planned, `000012`) | Vendor or platform (`vendor_id NULL`) | Every on-hand change is a movement row in the same transaction, with the row locked `FOR UPDATE`.<br>Available = on hand − reserved.<br>One location (`MAIN`) for now; `location_id` is on movements, reservations, receipts and registers.<br>`stock_levels` comes only when a second location arrives (ADR-13). |
| Purchasing | `suppliers` (+ `opening_balance`), `purchase_orders`(+items), `purchase_receipts`(+items), `purchase_invoices` (`kind`: supplier or opening), `purchase_invoice_receipts`, `purchase_invoice_cost_allocations`, `purchase_payments`, `purchase_returns`(+items) | Platform (the vendor side is off, BD-16) | Purchase order status is **stored** as `draft`, `ordered`, `partial`, `received`, `cancelled`. The UI shows `partial` as "Partly received" / "আংশিক গৃহীত".<br>Weighted average cost lives on `products.average_cost` and `product_variants.average_cost`. It changes on receipts, landed cost (invoice shipping + tax by `purchasing.tax_in_cost` − discount) and purchase returns.<br>The opening balance is one opening invoice. Payments are append-only. |
| Platform POS | `pos_settings`, `pos_registers`, `pos_sessions`, `pos_sales`(+items), `pos_returns`(+items), `pos_payments` | Platform | Platform-owned products only. `sales_channel = pos`. No vendor earnings or commission. |
| Customers | `customer_addresses`, `wishlists`, `carts`, `cart_items` | Customer | Address has division, district, area, phone |
| Orders | `orders` (parent), `vendor_orders`, `order_items`, `order_addresses`, `order_status_history` | Customer + vendor | Snapshots on items; `vendor_orders.vendor_id` indexed with status and date |
| Delivery | `shipping_zones`, `shipments`, `courier_events`, `courier_remittances` | Platform + vendor | Unique (courier, consignment\_id) |
| Payments | `payments`, `payment_events` (raw IPN, redacted) | Platform | Unique gateway transaction ID |
| Returns | `return_requests`, `return_items`, `refunds` | Customer + vendor | Linked to order items |
| Promotions | `coupons`, `coupon_redemptions` | Platform or vendor | `funded_by` field decides who bears the discount |
| Finance | `commission_rules`, `ledger_entries`, `vendor_balance_summaries`, `payout_requests`, `payouts` | Platform | Ledger append-only (section 8) |
| Content | `pages`, `banners`, `faqs` | Platform | Bangla and English fields |
| System | `settings`, `audit_logs`, `notifications`, `jobs`, `failed_jobs`, `media` (if a media library already exists) | Platform | Settings secrets encrypted |

**Schema conventions**

- `id` BIGINT auto-increment internally; public URLs and APIs use a `ulid` column for orders, products and vendors so IDs are not guessable.
- Foreign keys with explicit `ON DELETE RESTRICT` for anything financial or order-related; soft deletes only on catalogue and content.
- Every vendor-owned table: `vendor_id` NOT NULL, indexed, first column of composite indexes used in vendor lists.
- Bilingual text: `name_en`, `name_bn` columns for small taxonomy tables; a translations JSON column only if the existing code already uses one.
- Every migration has a working `down()` or is marked irreversible in its file header and reviewed.

## 10. API conventions and endpoint inventory

All endpoints live under `/api/v1`, split into four route groups whose middleware decides the context before any controller runs.

### 10.1 Route groups

| Prefix | Middleware | Who |
| --- | --- | --- |
| `/api/v1/public/*` | throttle | Anyone (catalogue, vendor stores, CMS) |
| `/api/v1/account/*` | auth:sanctum, verified | Logged-in customer |
| `/api/v1/vendor/*` | auth:sanctum, tenant (sets TenantContext), permission | Vendor members |
| `/api/v1/platform/*` | auth:sanctum, platform, permission | Platform staff |
| `/api/v1/webhooks/*` | signature check, idempotency | Gateways and couriers (no session) |

### 10.2 Conventions

- Validation in Form Requests; responses through API Resources. Never return a model directly.
- Success: `{ "data": …, "meta": { pagination } }`. Error: `{ "message": "…", "code": "ORDER_NOT_CANCELLABLE", "errors": { field: […] } }` with stable `code` values the frontend translates.
- Status codes: 401 unauthenticated, 403 forbidden in own context, 404 for other tenants' records, 409 state conflict, 422 validation, 429 rate limit.
- Pagination default 20, max 100. Filters and sorts from an allowlist per endpoint.
- `Idempotency-Key` on checkout, payout and refund POSTs.
- Every response carries `X-Request-Id`; the same ID goes into logs and audit events.
- Rate limits: login 5/min, OTP 3/10 min per phone, checkout 10/min, general API 120/min per user.

### 10.3 MVP endpoint inventory

| Area | Endpoints | Permission |
| --- | --- | --- |
| Auth | `POST /auth/login`, `/auth/logout`, `/auth/register`, `/auth/otp/send`, `/auth/otp/verify`, `GET /auth/me` (returns roles, memberships, permissions for UI) | — |
| Catalogue (public) | `GET /public/products`, `/public/products/{ulid}`, `/public/categories`, `/public/vendors/{slug}`, `/public/search` | — |
| Cart and checkout | `GET/POST/PATCH/DELETE /account/cart/items`, `POST /account/checkout`, `GET /account/orders`, `POST /account/orders/{ulid}/cancel`, `POST /account/returns` | owner of record |
| Vendor catalogue | `/vendor/products` CRUD, `/vendor/products/{id}/stock` | `product.*`, `inventory.adjust` |
| Vendor orders | `GET /vendor/orders`, `POST /vendor/orders/{ulid}/accept`, `/ready`, `/cancel`, `GET /vendor/shipments` | `order.*` |
| Vendor finance | `GET /vendor/ledger`, `/vendor/balance`, `POST /vendor/payout-requests` | `finance.view`, `payout.request` |
| Vendor team | `/vendor/members`, `/vendor/invitations`, `/vendor/roles` | `team.manage`, `role.manage` |
| Platform vendors | `/platform/vendors`, `POST /platform/vendors/{id}/status` | `vendor.view`, `vendor.manage_status` |
| Platform catalogue | `/platform/categories`, `/platform/brands`, `/platform/product-approvals` | `catalog.*`, `product.approve` |
| Platform finance | `/platform/commission-rules`, `/platform/payout-requests/{id}/approve`, `/platform/payouts`, `/platform/reconciliation` | `finance.*`, `payout.approve` |
| Platform access | `/platform/roles`, `/platform/members`, `/platform/audit-logs` | `role.manage`, `audit.view` |
| Webhooks | `POST /webhooks/courier/steadfast` (**built**: bearer token, see [security/steadfast.md](security/steadfast.md)); payment gateway IPN added after launch | signature / bearer token |

Each endpoint is documented in an OpenAPI file ([`documentation/openapi.yaml`](openapi.yaml), generated from the route list by `tools/gen_openapi.py`) with method, request, response, permission, tenant scope, rate limit, audit event and tests.

## 11. Frontend: design system, theme, i18n, accessibility, SEO

One Next.js app serves four areas from route groups, shares one Bootstrap-based design system, and treats permissions in the UI as hints only.

### 11.1 Structure

```
next-ecommerce/
  app/(storefront)/   public pages, server-rendered for SEO
  app/(account)/      customer area
  app/(vendor)/       vendor dashboard
  app/(platform)/     platform admin
  components/ui/      buttons, inputs, tables, modals, states
  components/layout/  shells, sidebar, topbar, breadcrumbs
  features/<domain>/  orders, catalog, finance, access-control ...
  lib/api/            one fetch client: credentials, X-Request-Id, error codes
  lib/auth/           session from GET /auth/me
  lib/permissions/    can('product.create') helper + <Can> component
  lib/i18n/           bn and en dictionaries
```

Adapt to the existing layout found in Phase 0; move working code only with a reason.

### 11.2 Design system

- Bootstrap 5.3 is the base. Brand tokens are CSS variables layered over Bootstrap's (`--bs-primary`, radius, spacing); no second UI library.
- Shared components with every state: loading skeleton, empty, error with retry, access denied, success toast.
- Dashboard shell: collapsible sidebar, top bar (profile, notifications, language, theme), breadcrumbs, page header with primary action.
- Tables: server-side pagination, sort and filter; on phones they collapse to cards.
- Icons: one set (Lucide) only.
- Optionally document tokens and components in a Design System reference before Phase 1 UI work.

### 11.3 Theme

Light (default), Dark and System modes using Bootstrap's `data-bs-theme`. An inline script in `<head>` reads the saved choice before paint to avoid a flash; the choice is saved per user via `PATCH /account/preferences` and in a cookie for guests. Dark surfaces use dark grey, not pure black, and every component is checked for contrast.

### 11.4 Bangla and English

- Locale in the URL for storefront pages (`/bn/...`, `/en/...`) so search engines index both; dashboards keep locale in user preference.
- Default locale: Bangla for storefront (**Assumption**), English for dashboards.
- All UI strings in dictionaries; API error `code` values translated on the client.
- Numbers and prices formatted with `Intl.NumberFormat('bn-BD')` or `'en-BD'`; currency shown as ৳.
- Bangla font loaded with `next/font` (e.g. Hind Siliguri or Noto Sans Bengali), subset to Bengali + Latin.

### 11.5 Accessibility

Keyboard access for all actions, visible focus rings, labels on every input, 4.5:1 text contrast, confirmation dialogs only for destructive actions, and a mobile-friendly permission editor (accordion by module instead of a wide matrix).

### 11.6 Storefront SEO and performance

- Server-render product, category and vendor pages; `generateMetadata` for title, description, canonical and Open Graph tags per locale.
- `sitemap.xml` and `robots.txt` generated from the API; `Product` and `BreadcrumbList` structured data.
- `next/image` with the WebP sizes from ADR-10; lazy-load below the fold.
- Targets on a mid-range Android phone over 4G: Largest Contentful Paint under 2.5 s, Cumulative Layout Shift under 0.1.
- Caching: catalogue pages revalidate every few minutes; cart, account and dashboards never cached.

## 12. Security baseline and audit logging

The MVP ships with the controls in 12.1 and 12.2; the extras in 12.3 follow in Phase 3 of the roadmap.

### 12.1 MVP security controls

| Area | Control |
| --- | --- |
| Passwords | bcrypt/argon via Laravel; minimum 8 characters; checked against breached-password list (`Password::uncompromised()`) |
| Login | Throttled; generic error messages; session regenerated on login; HttpOnly, Secure, SameSite=Lax cookies |
| CSRF | Sanctum CSRF cookie flow for all state-changing SPA requests |
| 2FA | Required for every platform role and for Vendor Owners (TOTP via Laravel Fortify or an equivalent maintained package) |
| Re-confirm | Password re-entry within 15 minutes for role changes, payout approval, gateway settings, vendor suspension |
| Super Admin | Cannot delete or demote the last active Super Admin; no self-promotion; break-glass account stored offline with its use alerted |
| Mass assignment | `$fillable` on every model; `vendor_id`, `status`, money fields never fillable from requests |
| Files | Uploads checked by MIME and extension, renamed, stored outside the web root for private documents, served through signed URLs |
| Secrets | Only in `.env` or encrypted `settings`; masked in UI; never in logs, API responses or the Next.js client bundle |
| Headers | HSTS, `X-Content-Type-Options`, `Referrer-Policy`, a Content Security Policy on the storefront |
| Dependencies | `composer audit` and `npm audit` on every release |
| Production | `APP_DEBUG=false`; `.env`, `storage` and `vendor` not reachable over HTTP |

### 12.2 Audit log

One `audit_logs` table (or the existing activity log if Phase 0 finds one): `id`, `occurred_at` (UTC), `request_id`, `actor_type`, `actor_id`, `vendor_id` (nullable), `event` (stable code such as `role.permission_granted`), `target_type`, `target_id`, `result` (success, denied, failed), `changes` (before/after, secrets redacted), `reason`, `ip`, `user_agent`.

Events logged at minimum: login success/failure, 2FA changes, role and permission changes, membership changes, invitation lifecycle, vendor status changes, product approvals, order cancellations by staff, refunds, commission rule changes, payout requests/approvals/recordings, settings changes, exports of customer or financial data, and denied cross-tenant attempts.

Every event also stores its `module` (online_sales, pos, purchase, inventory, marketplace, website, accounts, access; `App\Support\PermissionModules`). Each admin section shows only its own module's events, and Settings & Access shows them all. Rules: append-only in the application; no update or delete routes; vendors see only their own vendor's events; platform auditors see all. Retention period is decided by the owner with legal advice and written into this section; until then nothing is purged.

### 12.3 Later additions

Active session list with revoke, new-device login alerts by email/SMS, optional IP allowlist for platform roles, and tamper evidence (daily hash of the day's audit rows copied off the server).

## 13. Notifications and background jobs on cPanel

Notifications run through Laravel's notification system on the database queue, processed by a cron-driven worker each minute; nothing is described as real-time or background until that cron is verified on the host.

### 13.1 Job execution on shared hosting

1. cPanel cron, every minute: `/usr/local/bin/php /home/<user>/laravel-ecommerce/artisan schedule:run >> /dev/null 2>&1` (exact PHP path confirmed in Phase 0).
2. In `routes/console.php`: `Schedule::command('queue:work --stop-when-empty --max-time=50 --tries=3')->everyMinute()->withoutOverlapping();`
3. Jobs must finish in under 50 seconds; long work (large exports) is split into chunks.
4. A `scheduler_heartbeat` setting is updated each run; the platform dashboard shows a warning if it is older than 5 minutes.
5. If volume or duration outgrows this, move the API to a VPS with Supervisor (an infrastructure change needing approval).

### 13.2 Channels

| Channel | MVP | Use |
| --- | --- | --- |
| In-app (database) | Yes | All events for dashboards and customer account |
| SMS | Yes | OTP, order confirmed, shipped, delivered; through one Bangladeshi SMS gateway chosen by the owner |
| Email | Yes | Invitations, receipts, payout notices, password reset; SMTP or a transactional email provider |
| Browser push, WhatsApp | Later | Only with an approved provider and user consent |

OTP SMS is sent synchronously (the user is waiting); everything else is queued.

### 13.3 Events and recipients

| Event | Recipients |
| --- | --- |
| Order placed | Customer; each vendor in the order (their part only) |
| Order status change | Customer |
| Product approved / rejected | Vendor staff with `product.*` |
| Vendor status change | Vendor Owner |
| Return requested | Vendor order staff; platform support after 48 h |
| Payout requested / approved / sent | Finance managers; Vendor Owner and Accountant |
| Low stock | Vendor inventory staff |
| Security events (new 2FA, role change) | The affected user |
| Scheduler stale, failed jobs > 0, finance mismatch | Super Admin |

Recipients are resolved on the server from roles and memberships. Each notification has a dedup key (`event:target_id:recipient`) so retries never send twice. Users can turn off marketing and non-critical messages; security and transactional messages cannot be turned off.

## 14. Reporting and analytics

Every number on a dashboard has a written formula, time zone and source table; the MVP ships the eight metrics below and nothing invented.

### 14.1 Metric definitions

| Metric | Formula | Source | Seen by |
| --- | --- | --- | --- |
| Gross merchandise value (GMV) | Sum of item price × qty for vendor orders placed in the period, excluding cancelled before shipment | `order_items`, `vendor_orders` | Platform; vendor (own) |
| Net sales | GMV − discounts − refunds issued in the period | `order_items`, `refunds` | Platform; vendor (own) |
| Platform revenue | Sum of commission ledger entries in the period, net of reversals | `ledger_entries` | Platform only |
| Orders by status | Count of vendor orders by current status | `vendor_orders` | Platform; vendor (own) |
| Delivery success rate | Delivered ÷ (delivered + delivery\_failed) for orders shipped in the period | `vendor_orders` | Platform; vendor (own) |
| Cancellation rate | Cancelled ÷ placed, per vendor | `vendor_orders` | Platform; vendor (own) |
| Pending payouts | Sum of vendor available balances + open payout requests | `ledger_entries`, `payout_requests` | Platform finance |
| Pending approvals | Count of products and vendors awaiting review | `products`, `vendors` | Platform |

Day, week and month boundaries are Asia/Dhaka. Rates always show numerator and denominator on hover.

### 14.2 Reports (MVP)

- Sales by day/month, filterable by vendor, category, status.
- Vendor statement (ledger lines with references).
- COD reconciliation (courier remittances vs delivered COD shipments).
- Commission report (by vendor and category).

Exports: CSV in MVP, generated by a queued job, stored privately, downloadable for 24 hours through a signed link, logged as an audit event. Exports apply exactly the same scope as the screen.

### 14.2a Platform-owned and marketplace sales (ADR-13)

The admin sales reports have two sections. Their totals are **never added together**:

1. **Platform-owned sales:**
   - POS (`pos_sales`);
   - Online (`order_items` with `vendor_id IS NULL`);
   - Combined = POS + platform Online.
   
   Each shows revenue, discounts, returns, cost and margin. Cost comes from the unit cost stored on each sale line.
2. **Marketplace vendor sales:** GMV, commission and vendor earnings for `order_items` with `vendor_id IS NOT NULL`.

More rules:
- Every header, payment and return carries `sales_channel` (`pos` or `online`). Vendor orders are always `online` and never appear in POS reports.
- Platform POS sales create no vendor earnings or commission ledger rows.

### 14.3 Performance

Start with direct queries on indexed columns. Add a `daily_vendor_stats` summary table, filled nightly, only when a report takes more than 2 seconds on production data. Cached results are keyed by vendor, filters and locale.

## 15. Operations: environments, deployment, backup and recovery, monitoring

Three environments, a repeatable deployment checklist, daily off-site backups and a tested restore are required before public launch.

### 15.1 Environments

| Environment | Where | Data | Purpose |
| --- | --- | --- | --- |
| Local | Developer PC (`D:\bazarbarionline`) | Seeded fake data | Build and test |
| Staging | Subdomain on the same cPanel (e.g. `staging-api.`) with its own database | Anonymized copy or seeded data | Try migrations and releases before production |
| Production | `api.` and storefront domains | Real | Live |

Staging and production never share a database, `APP_KEY` or gateway credentials (staging uses gateway sandbox keys).

### 15.2 Source control and deployment

- Git repository with `main` (production) and `develop` (staging); feature branches merged through pull requests. Today the two code repositories use `master` as their only branch; rename it to `main` and add `develop` before the first staging deploy.
- CI (GitHub Actions): `composer install`, `php artisan test`, `npm ci`, `npm run lint`, `npm run build`, dependency audits. A red build is not deployed.
- Deploy to cPanel with Git Version Control (`.cpanel.yml`) or a scripted upload; then `composer install --no-dev --optimize-autoloader`, `php artisan migrate --force` (after backup), `config:cache`, `route:cache`, `view:cache`, `queue:restart`.
- Laravel `public/` is the only web-exposed folder; the rest sits outside `public_html`.
- Rollback: keep the previous release folder and a database backup taken immediately before migrating.

### 15.3 Backups and recovery

| Item | Frequency | Kept | Where |
| --- | --- | --- | --- |
| MySQL dump | Daily, plus before every migration | 14 daily, 8 weekly | cPanel backup + encrypted off-site copy (e.g. Google Drive or S3-compatible storage) |
| Uploaded files | Daily incremental | 14 days | Off-site |
| Code | Every commit | Forever | Git remote |
| `.env` and keys | On change | Latest + previous | Password manager, never in backups |

These numbers are a starting proposal; the owner sets the final RPO (data loss acceptable, proposed 24 hours) and RTO (time to recover, proposed 8 hours). A restore into staging is tested monthly and recorded (date, duration, result). Runbooks are written for: database restore, file restore, full redeploy, leaked credential rotation, failed migration, hosting outage — see [runbooks/](runbooks/README.md). A single vendor's data is never restored by overwriting the shared production database.

### 15.4 Monitoring

- Uptime check on storefront and `/api/v1/public/health` from an external free monitor, alerting by email.
- Laravel log to daily files; errors above a threshold emailed to Super Admin (or an error tracker such as Sentry free tier, if approved).
- Platform health page: database connectivity, queue size, failed jobs, scheduler heartbeat age, disk usage of `storage/`. Server CPU and memory are shown as "not available from hosting provider" unless cPanel exposes them.
- Health endpoints never return secrets, stack traces or versions to the public.

## 16. Testing and definition of done

Pest feature tests guard every permission and tenant boundary, and a feature counts as done only when all nine checks below pass.

### 16.1 Tools

| Layer | Tool | Runs |
| --- | --- | --- |
| Backend unit and feature | Pest (on PHPUnit), SQLite in memory or a MySQL test database | Every push (CI) |
| Frontend components | Vitest + Testing Library | Every push |
| End-to-end | Playwright against staging: COD checkout, product approval, vendor order flow, Steadfast booking (sandbox), payout request | Before each production release |
| Static checks | Larastan (level 5+), ESLint, TypeScript strict | Every push |

### 16.2 Required security tests (backend)

For every vendor endpoint, one test each that:

- a guest gets 401;
- a member of vendor A gets 404 for vendor B's record (read, update, delete);
- a member without the permission gets 403;
- a `vendor_id` in the request body is ignored;
- a bulk action with one foreign ID changes nothing.

Plus: last Super Admin cannot be removed; a vendor cannot assign a platform role; a user cannot grant a permission they lack; a revoked permission fails on the next request; a repeated IPN or courier webhook creates no second payment or status change; checkout under concurrent requests never oversells stock; ledger balances equal the sum of entries after refund and payout scenarios.

A reusable Pest helper (`assertTenantIsolated($route)`) keeps these tests short.

### 16.3 Business scenarios (acceptance)

1. A customer buys from two vendors in one checkout; each vendor sees only their own items and customer address.
2. COD order delivered; return window closes; vendor balance moves from pending to available with correct commission.
3. A Steadfast delivery webhook arrives twice; the order is marked delivered once and earnings are posted once.
4. Vendor suspended with open orders; orders stay visible to platform support; payouts frozen.
5. Refund after delivery reverses commission and vendor earnings.
6. Inventory Staff cannot see vendor finance; Accountant cannot edit products.
7. Finance Manager cannot approve a payout they requested.

### 16.4 Definition of done

- [ ] Business rule for the feature approved in section 2 or the module page
- [ ] Backend authorization and tenant scope enforced and tested (16.2)
- [ ] Validation, error codes and audit events in place
- [ ] Frontend uses the real API and shows loading, empty, error and denied states
- [ ] Bangla and English strings present; works on phone width
- [ ] Migrations reviewed, reversible or flagged, run on staging
- [ ] CI green; Playwright flow green on staging where relevant
- [ ] Docs updated: module register, OpenAPI, permission catalogue
- [ ] Known limitations written in the release notes

## 17. Roadmap: MVP and later phases

Public launch happens after Phase 3, with a marketplace that takes Cash on Delivery through Steadfast, splits orders by vendor, pays vendors manually from a ledger, and passes the security tests in section 16. This one ordering replaces both orderings in v1 (Part 24 and Part 25.8): tenancy and access come before visual polish.

```
Phase 0  Audit (read-only)                 ──G0──►
Phase 1  Foundation: Git, fix audit H1–H4, auth hardening, tenancy,
         Spatie teams, audit log, design system/theme/i18n  ──G1──►
Phase 2  Marketplace core: vendors, catalogue + approval, inventory,
         cart, checkout with order split                    ──G2──►
Phase 3  Money and delivery: COD, Steadfast, returns, ledger, payouts,
         reports, notifications, SEO, ops                   ──G3──►  PUBLIC LAUNCH
Phase 4  Growth (on demand): coupons, campaigns, online payment, 2nd courier
Phase 5  Scale (on demand): tickets, risk scoring, multi-warehouse, mobile API
```

Phases are not to scale in time; the gate table below gives each gate's exact condition.

**In the MVP (Phases 0–3)**

- Vendor registration, document upload, platform approval, vendor team and roles
- Catalogue with variants, images, platform categories/brands, approval of every product
- Cart, checkout with order split, Cash on Delivery, Steadfast courier, delivery zones
- Vendor order processing, returns and refunds
- Commission rules, ledger, settlement, manual payouts, vendor statement
- Platform admin: vendors, approvals, orders, finance, roles, audit log
- Bangla/English, light/dark theme, storefront SEO
- Backups, staging, CI, monitoring basics

**After launch (Phases 4–5), only when the business asks for them**

- Coupons funded by vendors, campaigns, Meta Pixel and Conversions API
- Online payment (SSLCommerz or direct bKash/Nagad), second courier
- Purchases and suppliers for vendor stock records (built in part, then switched off by BD-16)

**First-party retail track (ADR-13; runs alongside the phases above, local and QA only until launch)**

```
Done   Platform POS (sales, registers, sessions, returns, reports)
Done   Central purchasing phase 1–2 (suppliers, PO, receiving, WAC, invoices, payments, returns)
Done   P1 docs (ADR-13), P2 migration 000012, P3 reservations in InventoryService (2026-11-26)
P4     Movement source names  ─►  P5 vendor purchasing off  ─►  P6 two-section reports
P7     UI (on hand / reserved / available, house seller)  ─►  P8 browser QA
Then   Partnership Accounting (ADR-14): AC0 docs ─► AC1 ledger core ─► … ─► AC8 QA
```
- Support tickets and announcements
- Saved filters, command palette, dashboard personalization
- Risk scoring, approval workflow engine, multi-warehouse, loyalty, mobile app API

**Phase gates**: a phase starts only when the previous gate is met.

| Gate | Condition |
| --- | --- |
| G0 | Phase 0 audit report reviewed; section 2 assumptions confirmed by owner |
| G1 | Tenant isolation tests pass for every existing endpoint; Spatie teams and TenantContext live on staging |
| G2 | A two-vendor COD order runs end to end on staging |
| G3 | Launch checklist: Steadfast live account and API keys, backups restored once, security tests green, legal pages published |

## 18. Module register

The register tracks every MVP module; set each Status from Phase 0 evidence, and mark Done only when the Definition of Done (16.4) is met. Each module also gets its own one-page spec in `documentation/modules/` covering purpose, rules, permissions, tables, endpoints, UI states, audit events and tests.

| Module | Phase | Depends on | Status | Evidence / notes |
| --- | --- | --- | --- | --- |
| [Identity and auth (Sanctum, 2FA)](modules/01-identity-auth.md) | 1 | — | Partial | Sanctum SPA cookie login works; admin login throttled with idle timeout. Customer login not throttled and reveals unknown emails; no OTP, no 2FA |
| [Tenancy (memberships, TenantContext)](modules/02-tenancy.md) | 1 | Identity | Missing | No `vendors`, `vendor_user` or `vendor_id` anywhere |
| [Roles and permissions (Spatie teams)](modules/03-roles-permissions.md) | 1 | Tenancy | Partial | Spatie v8 with CRUD UI; `teams` off; permissions not enforced on any route; `users.role` duplicates admin flag |
| [Audit log](modules/04-audit-log.md) | 1 | Identity | Partial | Append-only `audit_logs` + read API built with Steadfast; only `shipment.*` events logged so far |
| [Design system, shell, theme, i18n](modules/05-design-system.md) | 1 | — | Partial | Bootstrap shells exist; `components/ui/*` empty; light/English only; hard-coded home products |
| [Vendor onboarding and lifecycle](modules/06-vendor-lifecycle.md) | 2 | Tenancy, roles | Missing | — |
| [Catalogue (categories, brands, products, variants, media)](modules/07-catalogue.md) | 2 | Vendors | Partial | Full single-shop catalogue with admin CRUD; no `vendor_id`, ulid, bilingual fields; namespace bug H2 fixed; admin review list still empty (H3 remainder) |
| [Product approval](modules/08-product-approval.md) | 2 | Catalogue | Missing | Only `is_active` flag |
| [Inventory and reservations](modules/09-inventory.md) | 2 | Catalogue | Partial | (2026-11-26) Built:<br>• one balance (`inventories` dropped);<br>• `stock_movements` written only through `InventoryService`, with ownership guards;<br>• admin and vendor stock reports;<br>• audited adjustments;<br>• platform stock read-only in product forms.<br>(2026-11-26, ADR-13 P2–P3) Reservations: checkout reserves, the first status change out of pending converts, cancel releases or restores once (`orders.stock_mode`). POS, cart, adjustments and purchase returns use available = on hand − reserved. One location `MAIN`. MySQL race check in qa-evidence/phase-p3-reservations-2026-11-26/. UI for on hand / reserved / available is P7. |
| [Customer account, cart, wishlist](modules/10-customer-cart.md) | 2 | Catalogue | Partial | APIs and UI work; cart item IDOR fixed (H1) |
| [Checkout and order split](modules/11-checkout-order-split.md) | 2 | Cart, inventory | Partial | Single-order checkout API with stock lock (H5 partly fixed: cart price trusted, no idempotency); no split; frontend checkout files empty; admin order list fixed (H4) |
| [Payments (COD; online after launch)](modules/12-payments.md) | 3 | Checkout | Missing | `payments` table and unrouted controller only |
| [Steadfast courier and shipments](modules/13-steadfast-courier.md) | 3 | Orders | Partial | Booking, secured webhook, idempotency, delivered re-check, COD reconciliation and alerts, audit (master `dace94a`); still per order, not per vendor order; no zones or remittance import |
| [Returns and refunds](modules/14-returns-refunds.md) | 3 | Payments, shipments | Missing | — |
| [Commission, ledger, payouts](modules/15-finance.md) | 3 | Orders, refunds | Missing | — |
| [Reports, notifications, storefront SEO](modules/16-reports-notifications-seo.md) | 3 | All above | Partial | Site and product SEO meta; COD reconciliation report and COD mismatch notification only |
| Platform POS (ADR-12/13) | First-party | Inventory | Partial | Built 2026-11-25 (`000009`, `000010`): terminal, sales, voids, returns, registers, sessions, settings, POS reports. Browser QA passed on QA. Missing: `sales_channel` on payments and returns, and selling against available stock (ADR-13 P2–P3). |
| Central purchasing (ADR-13) | First-party | Inventory | Partial | Built 2026-11-25/26 (`000011`): suppliers, purchase orders, receiving with WAC, invoices, payments, returns, stock adjustment page. No supplier-finance UI. The vendor side is to be switched off (BD-16, P5). |
| First-party sales reports (ADR-13) | First-party | POS, checkout | Missing | Two sections (14.2a) planned in P6. |
| [Partnership accounting (ADR-14)](adr/14-partnership-accounting.md) | First-party | All money modules | Missing | Plan approved 2026-11-26; variable partners with equal shares (amendment, AM1–AM6). ADR-14 approved 2026-11-26 (owner changes C1–C3). Code starts after ADR-13 P3. |

Status values come from the [Phase 0 audit](audit/phase-0.md) of 19 Nov 2026, with notes updated from its §7 re-check. The Inventory row and the first-party rows were updated on 2026-11-26 from code evidence. The other rows have not been re-checked since Phase 0, and many are out of date (for example tenancy, roles, approval and finance were built from 20 to 25 Nov). A full refresh of the register is a separate task. No module is Done.

## 19. Phase 0 audit checklist and open questions

Phase 0 is read-only: it produces one audit report in `documentation/audit/phase-0.md` and changes no code, schema or server setting.

**Result (19 Nov 2026):** local code audit complete — see [audit/phase-0.md](audit/phase-0.md). The code is a single-vendor shop with five high-risk findings (H1–H5) to fix in Phase 1. Server-side items below remain **Blocked** until the owner checks cPanel and production. Gate G0 is not met until the owner reviews the report.

### 19.1 Evidence to collect

- [x] Repository tree of `laravel-ecommerce` and `next-ecommerce`; entry points; Git status — no Git (audit §2.1)
- [x] `composer.json` / `composer.lock`: Laravel 13.24.0, Sanctum 4, Spatie Permission 8 (`teams` off, guards `web`/`admin`) (audit §2.2)
- [x] `package.json`: Next.js 16.3.0, React 19.2.8, Bootstrap 5.3.8; no i18n or theme library (audit §2.3)
- [x] Auth: guards, Sanctum mode (cookie), CORS and session config (audit §2.4)
- [x] Users and vendors: no vendor link and no `vendor_id` columns (audit §2.5)
- [x] All migrations (33) reviewed (audit §2.6) — live row counts and production indexes **Blocked**
- [x] `php artisan route:list`: 106 API routes in public, customer and admin groups (audit §2.7)
- [x] Policies, gates, middleware: none except `AdminMiddleware` role shortcut (audit §2.8)
- [x] Existing audit/activity log, notifications, settings, media handling (audit §2.9)
- [x] Orders, payments and balances: no order split; no money balance stored (audit §2.10)
- [x] Frontend: route groups, API client, permissions, theme, translations; empty checkout files (audit §2.11)
- [x] Tests: `php artisan test` 4 passed; no frontend test runner (audit §2.12)
- [ ] Hosting: PHP version and CLI path, cron access, SSH, Node.js app support, MySQL version, disk quota, backup options, remote storage — **Blocked (owner)**
- [ ] Queue, cache and session drivers in production — **Blocked (owner)**; local values are all `database`

### 19.2 Report format

For each item: what exists (with file paths), what is missing, risk (high/medium/low), and the smallest change proposed. End with a list of ADRs confirmed or contradicted and a revised module register.

### 19.3 Open questions for the owner

1. Business decisions BD-01 to BD-11 are confirmed (19 Nov 2026); only BD-12, the legal review, remains open.
2. Steadfast API keys: owner confirmed they will be available (19 Nov 2026); store them only in .env, never in Git
3. Which SMS gateway and which email sending service?
4. Does the hosting plan offer "Setup Node.js App"? If not, may the frontend move to Vercel or a VPS?
5. Final brand domain and launch date target.
6. Minimum payout: confirmed at BDT 1,000; return window confirmed at 7 days.
7. Who will give legal advice on the Digital Commerce Guidelines, VAT and data retention?
8. Is there real production data today, or can the schema still change freely?
9. Which stock column does the shop actually rely on today: `products.stock`, `product_variants.stock` or `inventories.quantity`? (audit §2.6)
10. ~~May both projects be put under Git now?~~ **Answered (19 Nov 2026):** yes — three separate private GitHub repositories (section 1).

## 20. Learning path for the developer

Learn each topic just before the phase that needs it; each row ends with a small exercise to build in the real project on staging.

| Order | Topic | Needed for | Practice exercise |
| --- | --- | --- | --- |
| 1 | Laravel authorization: Policies, Gates, Form Requests, API Resources | Phase 1 | Write a `ProductPolicy` and a Form Request for product create |
| 2 | Sanctum SPA authentication across subdomains, CORS, CSRF | Phase 1 | Log in from Next.js to the API with cookies on staging |
| 3 | Spatie Permission with teams and its cache | Phase 1 | Seed `config/permissions.php`; give one user different roles in two vendors |
| 4 | Multi-tenancy with global scopes and a context service | Phase 1 | `BelongsToVendor` trait + `assertTenantIsolated` Pest helper |
| 5 | Pest feature testing and factories | Phase 1 onward | 401/403/404 tests for one vendor endpoint |
| 6 | Database transactions, `lockForUpdate`, idempotency keys | Phase 2 | Checkout that never oversells under 20 parallel requests |
| 7 | State machines for orders (enum + transition map) | Phase 2 | Vendor order transitions table from 7.2 as code |
| 8 | Courier API and webhooks (Steadfast) | Phase 3 | Book a parcel and process its status webhook once, even if sent twice |
| 9 | Ledger and settlement design | Phase 3 | Post entries for deliver → settle → refund → payout; balances match |
| 10 | Laravel queues and scheduler on cPanel cron | Phase 3 | Queued order email processed by cron worker on staging |
| 11 | Next.js App Router: server components, metadata, middleware, i18n routing | Phases 1–3 | Bangla/English product page with correct metadata |
| 12 | Web security basics: OWASP Top 10, multi-tenant and authorization cheat sheets | Throughout | Review one module against the cheat sheet |

Free primary sources: the Laravel 13 docs, Spatie docs, Next.js docs and OWASP cheat sheets listed in section 21.

## 21. References

These references are carried over from v1. Always read the version that matches the installed packages found in Phase 0. Sanctum, SSLCommerz, the chosen courier's API and the Digital Commerce Guidelines are added here once they are reviewed.

1. [Laravel 13 — Authorization](https://laravel.com/docs/13.x/authorization)
2. [Laravel 13 — Queues](https://laravel.com/docs/13.x/queues)
3. [Laravel 13 — Database and transactions](https://laravel.com/docs/13.x/database)
4. [Laravel 13 — Task scheduling](https://laravel.com/docs/13.x/scheduling)
5. [Laravel 13 — Encryption](https://laravel.com/docs/13.x/encryption)
6. [Spatie Laravel Permission — Teams](https://spatie.be/docs/laravel-permission/v8/basic-usage/teams-permissions)
7. [Spatie Laravel Permission — Cache](https://spatie.be/docs/laravel-permission/v8/advanced-usage/cache)
8. [Next.js — Authentication guide](https://nextjs.org/docs/app/guides/authentication)
9. [OWASP — Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
10. [OWASP — Multi-Tenant Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html)
11. [OWASP — Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
