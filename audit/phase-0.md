# Phase 0 Audit Report — BazarBariOnline

Date: 2026-11-19 · Scope: `D:\bazarbarionline\laravel-ecommerce` and `D:\bazarbarionline\next-ecommerce` · Method: read-only (files read, `php artisan route:list`, `php artisan test` on in-memory SQLite). No code, schema or server setting was changed.

Status labels follow rule 10 of the specification: **Implemented**, **Partial**, **Missing**, **Blocked** (cannot be checked from the local machine), **Untested**.

## 1. Summary

The code today is a **single-vendor shop**, not a marketplace. Catalogue, cart, wishlist, a basic order, and an admin panel with Spatie roles exist. There is **no vendor (tenant) concept anywhere**: no `vendors` table, no `vendor_id` column, no membership, no tenant scope. Spatie teams are off. There is no ledger, commission, courier, return or payout code.

Five findings are high risk and should be fixed in Phase 1 before any vendor work, because multi-tenancy would build on top of them:

| # | Finding | Risk |
| --- | --- | --- |
| H1 | `PUT/DELETE /api/cart/items/{cartItem}` has no ownership check: any logged-in user can change or delete another user's cart item by ID (IDOR). `CartItemController.php:52-72` | High |
| H2 | Request classes are imported as `App\Http\Requests\product\…` but the folder is `Product`. Works on Windows, **fails with "class not found" on Linux cPanel**. `ProductController.php:6-8`, `ProductService.php:5-6` | High |
| H3 | Admin routes are registered for methods that do not exist: `PUT /admin/orders/{order}` (`OrderController::update`), `apiResource('coupons')` (only `validateCoupon` exists), `inventory` store/show/destroy, `DELETE /admin/reviews/{review}` (`ReviewController::destroy`). These return 500 errors. `GET /admin/reviews` calls `index(Product $product)` with no product, so it always returns an empty list, and it only lists approved reviews, so admins cannot moderate. | High |
| H4 | `GET /admin/orders` reuses the customer `OrderController::index`, which filters by `user_id = current user`: the admin sees only their own orders, not the shop's. | High |
| H5 | Checkout (`OrderController::store`) does not check or lock stock, does not decrement stock, trusts the price saved in the cart at add time, creates no payment record, and has no idempotency key. Concurrent checkouts can oversell. | High |

## 2. Evidence by checklist item (spec section 19.1)

### 2.1 Repository and Git

| Item | Finding | Status |
| --- | --- | --- |
| Git | Neither project nor the root is a Git repository. No history, no remote, no CI. | Missing (high: rule 9 rollbacks and section 15.2 depend on it) |
| Backend entry points | `routes/api.php` (106 API routes), `routes/web.php` (welcome view), `routes/console.php` (only `inspire`), `bootstrap/app.php` | Implemented |
| Backend layout | Flat `app/Http/Controllers/{Api,Admin}`, `app/Services` (5 services), `app/Http/Requests`, `app/Http/Resources` (7). No `app/Domain`, no Policies. | Partial vs ADR-01 |
| Frontend layout | `app/(shop)`, `app/admin/(protected)`, `app/admin/login`, `components/`, `services/`, `store/` (Zustand), `hooks/`, `schemas/` (Zod), `types/` | Partial vs section 11.1 |

### 2.2 Backend packages (`composer.json` / installed)

| Package | Version | Notes |
| --- | --- | --- |
| PHP | `^8.3` required; local CLI 8.4.12 (Laragon) | Production version: Blocked |
| laravel/framework | 13.24.0 | Matches spec |
| laravel/sanctum | ^4.0 | Used in SPA cookie mode; register still also issues a personal access token |
| spatie/laravel-permission | ^8.3 | `teams => false`; guard names `web`/`admin` |
| pestphp/pest | ^4.7 | Tests present |
| laravel/boost, pint, pail | dev | |
| Not installed | Fortify/2FA, brick/money, Larastan, an activity/audit log, a media library | |

### 2.3 Frontend packages (`package.json`)

Next.js 16.3.0, React 19.2.8, TypeScript 5, Bootstrap ^5.3.8, bootstrap-icons **and** lucide-react (two icon sets; section 11.2 allows one), axios, Zustand, react-hook-form + Zod, react-hot-toast **and** sweetalert2, CKEditor 5, Swiper, react-select. No i18n library, no theme switching, no test runner, no ESLint script.

### 2.4 Authentication, CORS, session

| Item | Finding | Status |
| --- | --- | --- |
| Sanctum mode | SPA cookie: `statefulApi()` in `bootstrap/app.php`; frontend axios uses `withCredentials` + XSRF; Next.js rewrites `/api/*` and `/sanctum/*` to Laravel (same-origin in the browser). | Implemented (matches ADR-04) |
| Guards | `web` and `admin`, both session driver on the same `users` provider; Sanctum checks both. | Implemented |
| Admin login | Rate limited 5 attempts/min per email+IP, session regenerated, 15-minute idle timeout (`ADMIN_IDLE_TIMEOUT_MINUTES`). | Implemented |
| Customer login | No rate limiter; returns "User not found." vs "Password is incorrect." (account enumeration, contradicts 12.1). | Partial (medium) |
| Customer register | Creates a personal access token and returns it in JSON although the SPA uses cookies; no `Password::uncompromised()`. | Partial (medium) |
| Phone / OTP login | Not present (`users.phone` column exists). | Missing |
| 2FA, password re-confirm | Not present. | Missing |
| CORS | `supports_credentials => true`; origins from config. | Implemented |
| Session | `SESSION_DRIVER=database`, `SESSION_DOMAIN=null`, `SESSION_ENCRYPT=false` locally. Production values: Blocked. | Partial |

### 2.5 Users and vendors

- `users.role` is an enum `customer | admin | users` (the third value looks like a typo of `user`; `User::isUser()` checks `'user'`, which the enum cannot store).
- Admin access uses Spatie `hasRole('admin')` **plus** a separate `users.role` column: two sources of truth for the same fact.
- **No `vendors` table, no `vendor_id` column in any migration or model, no membership table.** Products, orders, inventory and coupons all belong to the single shop.

### 2.6 Database schema (33 migrations)

Existing tables and how they map to section 9:

| Section 9 group | Existing | Gap |
| --- | --- | --- |
| Identity | `users`, `password_reset_tokens`, `sessions`, `personal_access_tokens`, Spatie tables (team columns present but disabled) | `vendor_user`, `team_invitations` |
| Vendors | — | All four tables |
| Catalogue | `categories` (self-parent tree), `brands`, `attributes`, `attribute_values`, `products`, `product_variants`, `product_variant_values`, `product_images`, `product_features`, `product_specifications`, `product_questions`, `reviews` | `products.vendor_id`, approval status, `ulid`, bilingual columns, FULLTEXT index |
| Inventory | `inventories` (quantity, reserved_quantity) **and** `products.stock` **and** `product_variants.stock` | Three stock sources; no movements or reservations table |
| Customers | `carts`, `cart_items`, `wishlists`, `wishlist_items` | `customer_addresses` |
| Orders | `orders`, `order_items` (name/SKU/price snapshot), `order_addresses` | `vendor_orders`, `order_status_history`, commission snapshot |
| Delivery | `shipments` (per order) | `shipping_zones`, `courier_events`, `courier_remittances`; shipment must move to vendor order |
| Payments | `payments` (unique `transaction_id`) | `payment_events` |
| Returns | — | All |
| Promotions | `coupons`, `coupon_usages` | `funded_by`, vendor scope |
| Finance | — | All |
| Content / System | `settings` (single row: logo, SEO), `cache`, `jobs`, `job_batches`, `failed_jobs` | `audit_logs`, `notifications`, pages/banners/faqs |

Schema conventions: money is `DECIMAL(12,2)` (matches ADR-08). Several order-related foreign keys use `cascadeOnDelete` (`order_items`, `payments`, `shipments`, `coupon_usages`), which contradicts the `ON DELETE RESTRICT` rule for financial data. No `ulid` columns. Live row counts, indexes and whether production holds real data: **Blocked** (needs the production database).

### 2.7 Routes and middleware

| Group | Middleware | Count (approx.) | Matches section 10? |
| --- | --- | --- | --- |
| Public (`/api/categories`, `/products`, `/brands`, `/settings`, `/attributes`, reviews) | none (no throttle) | 10 | No `/v1`, no `/public` prefix, no throttle |
| Customer (`/api/cart`, `/wishlist`, `/orders`, `/account/*`) | `auth:sanctum` | 15 | No `verified`, no `/account` prefix for cart/orders |
| Admin (`/api/admin/*`) | `auth:sanctum`, `admin` | ~80 | No per-permission middleware |
| Vendor, webhooks | — | 0 | Missing |
| `/up` health | framework | 1 | Exists; spec asks for `/api/v1/public/health` |

### 2.8 Policies, gates, middleware

- No Policies, no Gates, no `authorize()` calls, no `permission:` middleware. The only check on 80 admin routes is "has role `admin`". Permissions are seeded and shown in the UI but **not enforced** anywhere.
- `AdminMiddleware` is the `is_admin`-style shortcut the spec warns about.
- Customer ownership checks: present in `OrderController` (`show`, `cancel` return 403 — spec wants 404), absent in `CartItemController` (H1).

### 2.9 Audit log, notifications, settings, media

| Item | Finding |
| --- | --- |
| Audit / activity log | None |
| Notifications | `Notifiable` trait on `User`; no notification classes, no `notifications` table; `MAIL_MAILER=log` |
| Settings | `settings` table with one row (logo, meta title/description/keywords); `SettingController` |
| Media | Files on the `public` disk (`FILESYSTEM_DISK=public`); product thumbnail, gallery, CKEditor description images; no WebP conversion, no media library |

### 2.10 Orders, payments, balances

- One `orders` row per checkout with status enum `pending, confirmed, processing, shipped, delivered, cancelled, refunded`. **No order split.**
- `payments` and `shipments` tables exist; `PaymentController` and `ShipmentController` (265 and 195 lines) exist but **are not routed**. Same for `OrderAddressController`, `OrderItemController`, `CouponUsageController`, `ProductQuestionController`, `ProductVariantValueController`.
- `coupons.used_count` and `inventories.quantity` are editable counters; no balance of money is stored (there is no finance module at all).
- `.env` contains placeholders for Stripe, SSLCommerz and bKash; no integration code uses them. Stripe is out of scope (section 7.3).

### 2.11 Frontend

| Item | Finding | Status |
| --- | --- | --- |
| Route groups | `(shop)` storefront, `admin/(protected)` with `AdminAuthGuard` (client-side) | Partial; no `(vendor)`, no `(account)` group (account lives under `(shop)/account`) |
| API client | One axios instance (`lib/axios.ts`), XSRF, 401 redirect | Implemented; no `X-Request-Id`, no error-code mapping |
| Permission handling | Admin login returns roles and permissions; no `can()` helper / `<Can>` component | Missing |
| Checkout UI | `components/checkout/*.tsx`, `services/orderService.ts`, `services/paymentService.ts`, `schemas/checkoutSchema.ts`, `types/order.ts` are **empty files** | Missing |
| Other empty files | `components/ui/{Button,Loader,Modal,Pagination}.tsx`, `components/layout/Navbar.tsx`, `lib/constants.ts`, `schemas/{address,product}Schema.ts`, `types/{common,payment}.ts` | Missing |
| Home page data | `data/homeSections.ts` holds hard-coded products (e.g. "AG Computers") | Contradicts rule 7 (real data only) |
| Theme | Light only; no `data-bs-theme` switching | Missing |
| i18n | English only; no dictionaries, no `/bn` routes | Missing |
| Hosting build | No `output: 'standalone'` in `next.config.ts` | Missing (ADR-07) |

### 2.12 Tests

`php artisan test`: **4 passed, 12 assertions** (Pest, in-memory SQLite) — one real feature test (`CategoryApiTest`) plus the two example tests. No authorization, ownership or checkout tests. Frontend: no test runner configured.

### 2.13 Hosting, queue, cache, session in production

| Item | Local value | Production |
| --- | --- | --- |
| Queue | `QUEUE_CONNECTION=database` (spec section 1 said `sync`; corrected) | Blocked |
| Cache | `database` | Blocked |
| Session | `database` | Blocked |
| Scheduler | `routes/console.php` has no schedule; no cron | Missing |
| PHP CLI path, cron, SSH, Node.js app support, MySQL version, disk quota, backups | — | **Blocked: owner must check cPanel** |
| `APP_DEBUG` | `true` locally | Must be `false` in production (verify) |

## 3. ADRs confirmed or contradicted

| ADR | Result | Note |
| --- | --- | --- |
| 01 Architecture | Partial | Monolith yes; no domain folders yet. Introduce `app/Domain` for **new** modules only; move existing code only when touched. |
| 02 Tenancy | Not started | No `vendor_id` anywhere — free to implement as designed if production data is small (open question 8). |
| 03 Tenant context | Not started | |
| 04 Authentication | **Confirmed** | SPA cookie auth already works via Next.js rewrites. Remove token creation from customer register. |
| 05 Roles and permissions | Confirmed with work | Spatie installed and used; enable `teams`, add `permission:` enforcement, retire `users.role` column. Two guards (`web`, `admin`) must be reconciled with team roles. |
| 06 Queue | Partial | `database` queue configured locally; scheduler and cron not set up. |
| 07 Frontend hosting | Blocked | Depends on cPanel Node.js support. |
| 08 Money | **Confirmed** | `DECIMAL(12,2)` used; PHP arithmetic still uses floats (`$item->price * $item->quantity`). |
| 09 Time | **Confirmed** (storage) | `config/app.php` timezone is hard-coded `'UTC'`; Asia/Dhaka display and report boundaries not yet implemented. |
| 10 Search and media | Not started | No FULLTEXT, no WebP conversion. |

## 4. Smallest proposed changes (in order)

1. Put both projects under Git (one repository or two) before anything else.
2. Fix H1–H4 with Pest tests that prove them (each is a few lines).
3. Fix customer login enumeration and add throttling; drop the token from register.
4. Decide one stock source (`inventories` or `products.stock`) — write an ADR.
5. Then start Phase 1 as planned: Spatie teams, `vendors` + `vendor_user`, `TenantContext`, `BelongsToVendor`, audit log.
6. Fix H5 when checkout is rebuilt for the order split in Phase 2 (not before — it will be replaced).

## 5. Revised module register

Copied into section 18 of the specification.

| Module | Status | Evidence |
| --- | --- | --- |
| Identity and auth | Partial | Sanctum SPA, admin throttling and idle timeout; no 2FA, OTP, enumeration fix |
| Tenancy | Missing | No vendor concept |
| Roles and permissions | Partial | Spatie installed, role/permission CRUD UI; teams off; not enforced |
| Audit log | Missing | |
| Design system, shell, theme, i18n | Partial | Bootstrap admin shell and storefront; empty UI components; no theme or i18n |
| Vendor onboarding and lifecycle | Missing | |
| Catalogue | Partial | Categories (tree), brands, products, variants, attributes, images, features, specs; no vendor, no ulid, no bilingual fields |
| Product approval | Missing | |
| Inventory and reservations | Partial | `inventories` table + admin index/update; three stock sources; no reservations |
| Customer account, cart, wishlist | Partial | Cart, wishlist, register/login, account pages; cart IDOR (H1) |
| Checkout and order split | Partial | Single order checkout API; no split, no stock lock; frontend checkout empty |
| Payments | Missing | Table and unrouted controller only |
| Steadfast courier and shipments | Missing | `shipments` table and unrouted controller only |
| Returns and refunds | Missing | |
| Commission, ledger, payouts | Missing | |
| Reports, notifications, SEO | Partial | Settings-level SEO meta and product meta fields; no reports or notifications |

## 6. Questions this audit could not answer

1. cPanel: PHP CLI path, cron, SSH, "Setup Node.js App", MySQL version, disk quota, backup options.
2. Is the production database live with real customers and orders? (Decides whether tenancy migrations need data backfill.)
3. Which of the three stock columns is the one the shop actually uses?
4. Production `.env`: `APP_DEBUG`, `SESSION_DOMAIN`, `SANCTUM_STATEFUL_DOMAINS`, queue driver.

## 7. Re-check after first fixes (19 Nov 2026, later the same day)

Checked again while writing `openapi.yaml` (route list, controllers, `php artisan test`). The findings above stay as recorded; this section only states what has changed in the code since.

| # | Now | Evidence |
| --- | --- | --- |
| H1 | **Fixed.** Another user's cart item returns 404. | `CartItemController` ownership check; `tests/Feature/CartItemOwnershipTest.php` |
| H2 | **Fixed.** No lowercase `Requests\product` imports remain. | `grep` finds none; `ProductFormRequestTest.php` |
| H3 | **Mostly fixed.** Routes to missing methods are gone (98 API routes now, was 106: coupon resource and unused inventory routes removed); `OrderController::update` and `ReviewController::destroy` exist. **Still open:** `GET /admin/reviews` calls `index(Product)` with no product, so it always returns an empty list of approved reviews only. | `AdminBrokenRoutesTest.php` |
| H4 | **Fixed.** `GET /admin/orders` uses `OrderController::adminIndex` and lists all orders. | `AdminOrderListTest.php` |
| H5 | **Partly fixed.** Checkout locks product/variant rows, checks and decrements stock; cancelling restores stock. **Still open:** price comes from the cart item (set when added), no payment record, no `Idempotency-Key`. | `CheckoutStockTest.php`, `CancelRestoresStockTest.php`, `CartStockTest.php` |

Unchanged: customer login is not throttled and still reveals whether an email exists; customer `GET/POST /orders/{order}` returns 403 rather than 404 for another user's order; no route checks a Spatie permission.

Tests: `php artisan test` — 68 passed (197 assertions), was 4.

### 7.1 After the Steadfast merge (19 Nov 2026)

- **Git:** both projects are now Git repositories (`laravel-ecommerce` master at `dace94a`, `next-ecommerce`); still no remote or CI. Audit §2.1 "no Git" no longer holds.
- **Steadfast integration merged** (13 commits, see [module 13](../modules/13-steadfast-courier.md)); migrations ran on the local database after a backup (`D:\bazarbarionline\backups\`). Tests: 148 passed.
- **New finding (medium): cache store ignored.** `config/cache.php` reads `env('CACHE_DRIVER', 'file')`, but `.env` and `.env.example` set `CACHE_STORE`, so the app always uses the file cache (including rate-limit counters). Tests are fixed by `CACHE_DRIVER=array` in `phpunit.xml`; the app config is unchanged because the fix changes production caching. Smallest fix: read `env('CACHE_STORE', env('CACHE_DRIVER', 'database'))` and decide the production store with the owner.

### 7.2 Source control remotes (19 Nov 2026)

- Each folder now has its own private GitHub remote: `laravel-ecommerce` → `bazarbari-api`, `next-ecommerce` → `bazarbari-web`, `documentation` → `bazarbarionline`. Finding §2.1 is closed except for CI.
- **Lesson recorded:** GitHub's "quick setup" snippet run at `D:\bazarbarionline` created a root repository, deleted the projects' `.git` folders and committed a database dump. Never run `git init` at the root; check `git -C <folder> remote -v` in each project folder instead. If a project's `.git` folder goes missing, restore it from the Recycle Bin or re-clone from GitHub before making changes.
- Pushes fail from inside Claude Code (its shell blocks Git Credential Manager sign-in); push from a normal PowerShell window or GitHub Desktop.
