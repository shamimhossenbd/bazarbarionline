# Steadfast courier and shipments

| Phase | Depends on | Status |
| --- | --- | --- |
| 3 | Orders | **Partial** — courier integration and security built (19 Nov 2026, `laravel-ecommerce` master `dace94a`); per-vendor-order shipments wait for Phase 2 |

## Purpose

Book parcels with Steadfast, track them, and reconcile COD cash (BD-03, BD-05).

## What exists today

Built from the 13-item checklist in [security/steadfast.md](../security/steadfast.md), one commit each, 80 tests in `tests/Feature/Steadfast/`.

| Part | Where | Notes |
| --- | --- | --- |
| Courier interface | `app/Services/Courier/CourierGateway.php` | `book()`, `status()` only (no `quote`, `track`, `cancel` yet) |
| Steadfast client | `app/Services/Courier/Steadfast/SteadfastClient.php` | Laravel `Http`; `Api-Key` / `Secret-Key` headers from `config('services.steadfast')`; `/create_order`, `/status_by_cid/{id}`, `/get_balance`. No third-party package (decision in security/steadfast.md) |
| Booking | `POST /api/admin/orders/{order}/shipment/steadfast` | Admin only; COD = order total unless paid; 409 if already booked or order closed; 502 on courier error |
| Webhook | `POST /api/v1/webhooks/courier/steadfast` | HTTPS only → rate limit → `Authorization: Bearer STEADFAST_WEBHOOK_TOKEN` → validation → duplicate check → delivered re-check via status API |
| Idempotency | `courier_events` | Unique (courier, consignment_id, status); payload stored |
| Status mapping | `SteadfastStatus` | `in_review` → processing; pending/hold/unknown/*_approval_pending → shipped; delivered/partial_delivered → delivered; cancelled → returned. Final shipment states never change |
| COD reconciliation | `GET /api/admin/courier/steadfast/reconciliation` | Expected `cod_amount` vs `collected_cod_amount` from the verified delivered webhook; paisa arithmetic; Asia/Dhaka date filters |
| Mismatch alert | `CodMismatchDetected` notification | Database channel to active admins; `GET /api/admin/notifications` |
| Audit | `audit_logs` | `shipment.booked`, `shipment.booking_failed`, `shipment.status_changed`, `shipment.delivered`, `shipment.cancelled` |
| Key safety | `Secret`, `steadfast:check`, `GET /api/admin/courier/steadfast` | Masked keys, fingerprint guard for staging, read-only key check |

Configuration (all in `.env`, listed in `.env.example`): `STEADFAST_BASE_URL`, `STEADFAST_API_KEY`, `STEADFAST_SECRET_KEY`, `STEADFAST_TIMEOUT`, `STEADFAST_PRODUCTION_KEY_FINGERPRINT`, `STEADFAST_WEBHOOK_REQUIRE_HTTPS`, `STEADFAST_WEBHOOK_TOKEN`, `STEADFAST_VERIFY_DELIVERED`, `STEADFAST_WEBHOOK_RATE_LIMIT`.

Not built yet: shipping zones and delivery charge by zone, Steadfast `/payments` remittance import (`courier_remittances`), parcel cancel and return requests, tracking page, vendor-facing endpoints. The old unrouted `ShipmentController` is still in the code base and unused.

## Rules

- `CourierGateway` interface (target: `quote`, `book`, `track`, `cancel`); Steadfast is the first implementation.
- One shipment per vendor order; unique (courier, consignment_id).
- Webhooks verified and idempotent; they move vendor-order state.
- Steadfast payout batches imported and matched to shipments; differences shown in reconciliation.
- API keys only in `.env`.

## Phase 2 changes (when `vendor_orders` exists)

Today `shipments.order_id` links to the single-shop `orders` table. One shipment per vendor order needs:

| Area | Today | Change |
| --- | --- | --- |
| Schema | `shipments.order_id` (cascade on delete) | Add `vendor_order_id` (FK, `ON DELETE RESTRICT`) and `vendor_id`; backfill; stop using `order_id` |
| Relations | `Order::shipment()` hasOne | `VendorOrder::shipment()`, `Shipment::vendorOrder()`; parent order reaches shipments through vendor orders |
| Booking | Admin `POST /api/admin/orders/{order}/shipment/steadfast` | Vendor `POST /api/v1/vendor/orders/{ulid}/ready` with `shipment.book`, tenant-scoped |
| Booking data | invoice = `order_number`; COD = `orders.total`; `order_addresses` | Vendor order number (unique at Steadfast); COD = vendor order items + its delivery fee (BD-08); address snapshot per vendor order |
| Webhook effects | Sets `orders.status` | Vendor order state machine (spec 7.2): `ready_to_ship` → `shipped` → `delivered` / `delivery_failed` (map `cancelled` → `delivery_failed`); parent status derived |
| Delivered | Status, COD check, audit | Also post ledger entries (vendor earnings pending + commission, spec 8.2) in the same transaction |
| Reconciliation | Rows by order | Rows by vendor order and vendor; vendor sees own (`finance.view`) |
| Audit | `vendor_id` null | Fill `vendor_id` so vendors see their own events |
| Tests | `createShippableOrder()`, `createBookedShipment()` | Vendor order factories; spec 16.2 tenant tests (other vendor's shipment → 404) |

Unchanged by Phase 2: the client, `CourierGateway`, key masking and staging guard, `steadfast:check`, all webhook security, and `courier_events` (keyed by consignment).

## Permissions

`shipment.book` (vendor order staff), `courier.reconcile` (platform finance). Today the admin routes check only the `admin` role.

## Tables

Built: `shipments` (+ `consignment_id`, `invoice`, `cod_amount`, `collected_cod_amount`, `courier_status`, `booked_at`), `courier_events`. Still to build: `shipping_zones`, `courier_remittances`.

## Endpoints

Built: `POST /api/admin/orders/{order}/shipment/steadfast`, `GET /api/admin/courier/steadfast`, `GET /api/admin/courier/steadfast/reconciliation`, `POST /api/v1/webhooks/courier/steadfast`. Target: `POST /vendor/orders/{ulid}/ready`, `GET /vendor/shipments`, `/platform/reconciliation`. See [openapi.yaml](../openapi.yaml).

## UI and states

Not built: ready-to-ship action, shipment tracking, platform reconciliation report screen, courier settings card (the APIs above exist).

## Audit events

Built: `shipment.booked`, `shipment.booking_failed`, `shipment.status_changed`, `shipment.delivered`, `shipment.cancelled`. Still to add: `courier.remittance_imported`.

## Required tests

- [x] Same delivery webhook twice: delivered once (`SteadfastWebhookIdempotencyTest`, `SteadfastDeliveredVerificationTest`). Earnings posted once — waits for the ledger (module 15).
- [x] Invalid webhook secret rejected and logged (`SteadfastWebhookTokenTest`).

## Before going live

1. Set the `STEADFAST_*` values in production `.env`; run `php artisan config:cache` and `php artisan steadfast:check` (read-only: calls `get_balance`).
2. Register `https://<api-domain>/api/v1/webhooks/courier/steadfast` and the token in the Steadfast portal.
3. On the first real callback, confirm Steadfast sends `Authorization: Bearer <token>` (taken from the community package source; Steadfast's own docs were not readable).
4. If cPanel sits behind a proxy that terminates TLS, configure trusted proxies so `RequireHttps` sees HTTPS.

Done only when the Definition of Done in spec section 16.4 is met.

## Admin panel, auto-booking and status poll (built 2026-11-28)

Owner brief 2026-11-27 and answers 2026-11-28. Code: api `59651fc` and web `ccd31f5`, on branch `feat/accounting-ac2` (also `feat/steadfast-admin-settings`). Migration `2026_11_28_000018_steadfast_admin_settings`. Because of it, AC5 part 2 is now `000019`.

| Part | Rule |
| --- | --- |
| Keys | Saved under **Settings & Access → Courier (Steadfast)**, encrypted with APP_KEY in `settings`. No API ever returns them; the UI shows only the last 4 characters. `.env` keys are the fallback for local and CI. New keys save only after a successful **Test connection** (Check Balance) with exactly those keys, or with an override and a reason. Permission `courier.settings.manage` (super admin only). Audited as `courier.settings_updated` (field names only). |
| Switches | `enabled` (off = no Steadfast call at all) and `auto_book` (default off). No sandbox/live switch, because none is documented. |
| Auto-book | An admin confirming an order (only orders with no vendor lines) or a vendor accepting their lines queues `AutoBookSteadfastShipment`. It is idempotent: invoice = order number, unique, and an existing shipment is reused. 3 retries with 1/5/15-minute backoff. A failure keeps the order confirmed and sets the shipment to `failed` with the error; this shows a red badge, Retry, and the **Courier issues** page. A bad phone or address is not retried. |
| Manual | **Book with Steadfast** on the order page; **Book selected** (Create Bulk Order, max 500). The phone must be `01XXXXXXXXX` and an address is required. |
| Status | `steadfast:poll-statuses` runs every 30 minutes for active shipments (the documented path). The secured webhook stays. Both go through `SteadfastWebhookProcessor`: the same status is never applied twice, and an older status never moves a shipment backwards. |
| Courier history | Fraud Check runs **only on click** ("Check courier history") on COD orders, from the admin (`courier.fraud_check`) or the vendor. It is cached 24 h per phone (HMAC key) and every check is audited (`courier.fraud_checked`, no phone). The storefront `/privacy` page says the phone is shared with the courier for delivery and fraud prevention. |
| Other | Send Pickup Request (saved address_id and police station); Steadfast balance card on the Accounts dashboard; our own call limit (`STEADFAST_RATE_PER_MINUTE`, default 60); 15 s timeout. |

Before going live: the cPanel cron must run `php artisan schedule:run` every minute and a queue worker (`php artisan queue:work --stop-when-empty`), or the poll and auto-booking retries never run.
