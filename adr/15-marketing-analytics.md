# ADR-15: Marketing & Analytics integration (GA4/GTM, Meta Pixel + Conversions API, Marketing API reports)

- **Status:** **Accepted** by the owner on 2026-11-28 (answers MQ1–MQ6). Not built yet.
- **Date:** 2026-11-28
- **Order of work:** after the sidebar redesign (done, web `22e015f`) and AC5 part 2 (migration `000019`). Then M1–M5 (section 9), one commit each. The first migration here is `000020` or later.
- **Sources:** the owner's Marketing & Analytics brief (points 1–8), the plan of 2026-11-28 and the owner's answers MQ1–MQ6 (2026-11-28).
- **Depends on:** ADR-05/dynamic RBAC (permission registry, fail-closed admin routes), ADR-06 (cron-driven queue and scheduler), ADR-08 (money), ADR-09 (time: Asia/Dhaka day boundaries), ADR-14 (ledger: account 5106).
- **Open item:** the owner's Bangla spec was referred to twice but never reached the conversation. Before M1 starts, the owner pastes it and any difference from this ADR is written in as an amendment.

## Context

The shop needs Google Analytics 4 (directly or through Google Tag Manager), Search Console verification, Meta Pixel with the Conversions API (CAPI), and reports that combine GA4 traffic, Meta ad results and our own order data. Secrets (GA4 service account key, Meta tokens) must never reach the browser or any API response. Reports must load fast and still work when Google or Meta is down. Ad spend must not be confused with accounting: the ledger records only what was actually paid.

Facts checked in the code on 2026-11-28:
- The root layout (`app/layout.tsx`) wraps the storefront **and** `/admin` and `/vendor`.
- `/contact` has no backend form (no contact route exists).
- Every order-line delivery path (admin fulfilment, vendor orders, courier sync) calls `VendorEarningsService::markDelivered`.
- Secrets already use Laravel `encrypted` casts and `App\Support\Secret::mask()` (Steadfast keys).
- The spec's role catalogue (section 6) already names a "Marketing Manager" (coupons, campaigns, pixels). This ADR seeds it with reports only (MQ6); more grants are the owner's choice later.

## Decisions

"Brief" is the owner's brief, "Plan" is the 2026-11-28 plan, and MQ1–MQ6 are the owner's answers.

### 1. Placement, permissions, audit (Brief, MQ6)

- **Settings → Marketing & Analytics** in the sidebar's bottom block.
- New sidebar group **"Marketing"**: Analytics overview (`/admin/marketing`), Google reports (`/admin/marketing/google`), Meta Pixel events (`/admin/marketing/pixel-events`), Facebook Ads (`/admin/marketing/facebook-ads`).
- Permissions in `PermissionRegistry` with route-map entries (module `marketing` in `PermissionModules`):
  - `marketing.settings.manage`: Super Admin only (super admin holds every permission). No template role gets it.
  - `marketing.reports.view`: added to the **administrator** template, and to a new seeded, editable role **"Marketing Manager"** that holds only this permission (MQ6).
- Every settings change, test, manual sync and export is written to the audit log with module `marketing`. Secret fields are logged as "changed", never as values.

### 2. Settings (Brief, Plan)

Stored in a new single-row table `marketing_settings`, kept apart from `settings` so secrets never sit near the public `SettingResource`.

| Field | Rule |
| --- | --- |
| `google_method` | `none`, `gtm` or `gtag`. **Never both.** With `gtm`, GA4 is configured inside GTM, `ga4_measurement_id` is ignored and is never sent to the browser. |
| `gtm_container_id` | `GTM-` format |
| `ga4_measurement_id` | `G-` format, used only with `gtag` |
| `ga4_property_id` | numeric |
| `ga4_service_account_json` | upload only, **encrypted**, never returned. The `client_email` is extracted and shown so the owner can add it as Viewer in GA4. |
| `search_console_token` | accepts the token or the whole pasted `<meta>` tag (the `content` is extracted) |
| `meta_pixel_id` | public |
| `meta_capi_token` | **encrypted**, never returned |
| `meta_capi_test_event_code` | optional, used only by the Test button |
| `meta_ad_account_id` | must match `^act_\d+$` |
| `meta_business_id` | numeric |
| `meta_token_expires_at` | from Meta's `debug_token`; null = never expires (system user token). Warning from 14 days before expiry. |
| `events` | on/off per tracking event (section 4) |
| `ga4_timezone`, `meta_account_timezone`, `meta_account_currency` | filled by the Test buttons; a warning shows if either timezone is not Asia/Dhaka |

- The API returns secrets only as `Secret::mask()` plus a set/not-set flag; the model lists them in `$hidden`.
- **The Meta Pixel is always loaded directly, never through GTM** (Plan): the browser and server events must share one `event_id`, which only our own `fbq` calls guarantee. The settings page warns: "Do not add a Meta Pixel tag inside GTM."
- **Test connection** buttons:
  - GA4 Data API: a 1-day `runReport` plus a property lookup (timezone).
  - Meta Conversions API: a test event with the test event code.
  - Meta Marketing API: `GET act_…?fields=name,currency,timezone_name,account_status`.
  - Errors show inline and go to admins with `marketing.settings.manage` as admin notifications (`MarketplaceNotifier::admins`), with secrets stripped.

### 3. Storefront injection (Brief, Plan, MQ3, MQ4)

- **Trackers are rendered in `app/(shop)/layout.tsx`, not the root layout** (Plan). The root layout also wraps admin and vendor pages, which must never be tracked. The Search Console meta tag goes in the shop layout's `generateMetadata`.
- Public IDs only, through `GET /api/marketing/public-config`: method, the one active Google ID, Pixel ID, the events map and the verification token. Cached on the API under a tag cleared on save; the shop layout fetches it with `next: { revalidate, tags }`. Tokens and keys never reach the client bundle.
- One `<Trackers>` component: `next/script` with fixed ids (`bbo-gtm`, `bbo-gtag`, `bbo-pixel`), `strategy="afterInteractive"`, plus a `window.__bboTrackers` guard against loading twice. It renders GTM **or** gtag, never both.
- Page views: GA4's own history-change page views are used (no manual send, so no doubles). The Pixel `PageView` fires on each App Router route change.

**Consent (MQ3, Plan):**
- A cookie notice with Accept and Decline, saved in a `bbo_consent` cookie. It is always shown when Google or Meta is configured (there is no switch to hide it, because without it there is no consent to rely on).
- Until the visitor accepts, and after a decline, **no Google or Meta script loads**. For Google this is my default (MQ3 named only Meta); the owner may relax it later to Consent Mode "denied" pings.
- **Declined → nothing is sent to Meta for that visitor's orders: no browser events, no server events, no Purchase, no Delivered** (MQ3).
- The choice is stored on the order at checkout in `orders.tracking_consent` (`granted` / `denied` / `none` = never chose). Server events go only when it is `granted`.

**Privacy page (Brief, MQ4):** the `/privacy` page (Bangla and English) gets a section on Google Analytics/Tag Manager and Meta Pixel/Conversions API. It covers what is collected, that phone and email are hashed before sending, that **with consent the client IP address and browser user agent are sent to Meta**, and how to decline.

### 4. Events (Brief, Plan, MQ1, MQ5)

Each event can be switched off in Tracking Settings. Server-side `event_id`s are fixed in advance so retries and browser/server pairs deduplicate.

| Event | Trigger | GA4 | Meta browser | Meta server (CAPI) |
| --- | --- | --- | --- | --- |
| Page view | route change | built-in history page views | `PageView` | — |
| View item | product page | `view_item` | `ViewContent` | — |
| Search | search submit | `search` | `Search` | — |
| Add to cart | successful add response | `add_to_cart` | `AddToCart` | — |
| Initiate checkout | checkout page opens | `begin_checkout` | `InitiateCheckout` | — |
| **Purchase** | order placed; fired on the confirmation page, guarded in sessionStorage so a reload does not repeat it | `purchase` (transaction_id = order number) | `Purchase`, eventID `purchase_{order_number}` | `Purchase`, same event_id, queued after commit |
| **Delivered** | see below | — | — | custom `Delivered`, event_id `delivered_{order_number}` |
| Lead | `/contact` form saved (MQ1) | `generate_lead` | `Lead`, eventID `lead_{lead_id}` | `Lead`, same event_id |
| Complete registration | sign-up success | `sign_up` | `CompleteRegistration` | — |
| WhatsApp click | `wa.me` links | `whatsapp_click` | `Contact` + custom `WhatsAppClick` | — |
| Phone click | `tel:` links | `phone_click` | `Contact` + custom `PhoneClick` | — |
| Form submission | contact and newsletter forms | `form_submit` | custom `FormSubmit` | — |

With GTM, the same events are pushed to `dataLayer` in GA4 ecommerce format; GTM forwards them.

**Delivered (MQ5):**
- **One event per order**, sent when every line of the order is delivered or otherwise closed (cancelled, returned, refunded).
- Value = the total of the **delivered** lines only. If no line was delivered, nothing is sent.
- `event_id` = `delivered_{order_number}`, unique per order.
- An `OrderClosureCheck` runs after every line status change (it is called from `VendorEarningsService::markDelivered` and from the cancel/return paths). It dispatches the event once; the unique `event_id` in `capi_events` stops courier re-syncs from sending it again.
- Sent only when `orders.tracking_consent = granted`.

**CAPI user data (Brief, MQ4):** `App\Support\MetaUserData` builds it.
- Phone is normalised to `8801XXXXXXXXX`, email trimmed and lower-cased, and `external_id` is the customer id. City, district and `country=bd` are lower-cased. **All of these are SHA-256 hashed**; no raw phone or email is sent or logged.
- Sent unhashed, as Meta requires, and only with consent: `client_ip_address`, `client_user_agent`, `fbp`, `fbc`.
- Captured at checkout into `orders.marketing_context` (encrypted JSON): fbp, fbc, GA client_id, user agent, IP and UTM tags.

### 5. Data model (Plan)

| Table | Contents | Key |
| --- | --- | --- |
| `marketing_settings` | section 2 | one row |
| `analytics_daily` | GA4 per day and dimension (`total`, `channel_group`, `source_medium`, `device`, `new_vs_returning`): sessions, total_users, new_users, screen_page_views, engaged_sessions, add_to_carts, ecommerce_purchases, purchase_revenue_poisha, synced_at | unique (`date`, `dimension`, `dimension_value`) |
| `analytics_period_totals` | de-duplicated users and sessions for the preset ranges (users cannot be summed across days) | unique (`range_key`, `start`, `end`) |
| `ad_campaign_daily` | Meta per day and campaign: ad_account_id, campaign_name, objective, effective_status, spend_minor + `currency` (the account's own; never converted), impressions, reach, clicks, link_clicks, ctr, leads, purchases, purchase_value_minor, synced_at | unique (`date`, `campaign_id`) |
| `ad_account_period_totals` | account-level de-duplicated reach for the preset ranges | unique (`range_key`, `start`, `end`) |
| `marketing_sync_runs` | source, range, mode, status, rows written, attempt, error (secrets stripped), started_at, finished_at; drives "last synced at" | — |
| `capi_events` | event_id, event_name, order_id, lead_id, status (`pending`/`sent`/`failed`), attempts, http_status, events_received, sent_at. **No user data, not even hashes.** | unique `event_id` |
| `leads` | `/contact` form submissions (MQ1): name, phone (encrypted), email (encrypted), message, source page, UTM, consent, created_at | — |
| `cart_add_events` | append-only, written by `CartService` on add: cart_id, product_id, variant_id, qty, created_at; pruned after 400 days | — |
| `orders` (new columns) | `tracking_consent`, `marketing_context` (encrypted JSON) | — |

The `/contact` form is new: throttled, honeypot field, validated BD phone. Newsletter sign-ups stay in `newsletter_subscribers` and are reported as **Subscribers**, never as leads (MQ1).

### 6. Sync (Brief, Plan)

Artisan commands on the existing scheduler (`withoutOverlapping()->onOneServer()`), run as queued jobs by the existing every-minute `queue:work`.

| Command | When (Asia/Dhaka) | Pulls |
| --- | --- | --- |
| `marketing:sync-ga4 --mode=daily` | 03:10 | yesterday, plus a re-pull of D-2 and D-3 (GA4 data settles within about 48 h); rebuilds period totals |
| `marketing:sync-ga4 --mode=intraday` | every 3 h, 09:00–24:00 | today, `total` and `channel_group` only |
| `marketing:sync-meta --mode=daily` | 03:30 | last 7 days per campaign with `time_increment=1` (Meta attribution keeps changing); rebuilds period reach |
| `marketing:check-meta-token` | 09:00 | `debug_token`; admin notification at 14, 7, 3 and 1 days before expiry and when expired |
| `--date` / `--from --to` | manual | backfill, at most 90 days |

- **Idempotent:** each (source, date) is replaced in one transaction (delete that date's rows, insert the new ones). Running a day again replaces it, never duplicates it.
- **Retries:** 3 attempts, backoff 60 s, 5 min, 15 min.
- **Quotas:** Meta error codes 4, 17, 613 and the `X-Business-Use-Case-Usage` header are respected; above 75 % usage the job stops and reschedules. GA4 requests `returnPropertyQuota` and stops below 10 % of the remaining tokens.
- **On final failure:** the run is marked failed and admins get a notification. Reports keep showing the last good data with "last synced at …" in amber.
- **Custom date ranges** query GA4 live for de-duplicated users (cached 1 h). If that fails, the summed daily figure is shown and labelled "approx."
- **Clients:** GA4 signs its JWT with `openssl_sign` (RS256) and caches the token for 55 min (no `google/apiclient`). Meta uses plain `Http::` calls to a Graph API version pinned in config.

### 7. Where each dashboard number comes from (Brief, MQ1)

Each card shows its source (Our database / GA4 / Meta) and "last synced at".

| Card | Source | Definition |
| --- | --- | --- |
| Visitors, unique, new vs returning | GA4 | `totalUsers`, `newUsers`, `newVsReturning`; de-duplicated period totals |
| Sessions, page views | GA4 | `sessions`, `screenPageViews` |
| Traffic sources | GA4 | `sessionDefaultChannelGroup`, `sessionSourceMedium` |
| **Orders** | **Our DB** | online orders placed in the period. POS and admin-created orders are excluded; orders cancelled before confirmation are shown separately. |
| **Revenue** | **Our DB** | item subtotal after discounts, without shipping; shown as "placed" and "delivered" |
| **Add to cart** | **Our DB** | rows in `cart_add_events` |
| GA4 / Pixel purchases and add-to-cart | GA4, Meta | shown in a grey "for comparison" row, never as the main figure |
| Conversion rate | Our DB ÷ GA4 | our orders ÷ GA4 sessions for the period; the formula and both numbers show on hover |
| **Leads** | **Our DB** | rows in `leads` (`/contact` submissions) (MQ1) |
| **Subscribers** | **Our DB** | new `newsletter_subscribers` rows in the period (MQ1) |
| Spend, impressions, reach, clicks, CTR | Meta | `ad_campaign_daily`; reach from period totals |
| CPL | Meta (+ blended) | spend ÷ Meta-attributed leads; blended = spend ÷ our leads |
| Cost per purchase | Meta (+ blended) | spend ÷ Meta-attributed purchases; blended = spend ÷ our orders |

Blended figures show only when the ad account's currency is BDT; otherwise they read "currency differs".

### 8. Accounting, filters, export (Brief)

- **Meta ad spend is reporting only. It never posts to the ledger.** Actual ad payments are entered as Expenses under **5106 Marketing / ads** (ADR-14). The Facebook Ads page says so.
- Filters: Today, Yesterday, Last 7 days, Last 30 days, This month, Last month, Custom. Day boundaries are Asia/Dhaka (ADR-09, `ReportPeriod`).
- CSV export through `CsvWriter`; PDF through a print view.

### 9. Build order

| Step | Scope |
| --- | --- |
| M1 | migration `0000NN_marketing_analytics` (tables in section 5), settings API and page, permissions, Marketing Manager role, `public-config`, Test buttons, token-expiry notification |
| M2 | `<Trackers>` in the shop layout, cookie notice and `tracking_consent`, browser events, Search Console tag, privacy page (bn and en), `/contact` form and `leads` |
| M3 | CAPI: Purchase, Lead, Delivered (`OrderClosureCheck`), `capi_events`, `MetaUserData` hashing |
| M4 | GA4 and Meta sync commands, period totals, sync runs, retries and quotas |
| M5 | four report pages, source chips, last-synced, filters, CSV and print view; QA screenshots |

### 10. Tests (Brief)

- No duplicate script injection: render `<Trackers>` twice and find one script of each.
- GTM and gtag are exclusive: with `gtm`, `public-config` has no measurement id and only the GTM loader renders.
- Tokens never appear in any API response (including validation errors and audit entries), nor in `.next/static` after a build (the test greps for fake seeded tokens).
- `event_id` deduplication: the browser payload and the CAPI job share the id; a second dispatch is skipped.
- Hashing: fixed vectors for phone and email normalisation; logged payloads hold no raw phone or email.
- Consent: a `denied` or `none` order sends no Purchase and no Delivered; the shop renders no tracker before Accept.
- Delivered: sent once, only when every line is closed, valued at delivered lines only, not repeated on courier re-sync; not sent when no line was delivered.
- Sync idempotency: re-running a day keeps the row counts; 429-then-200 succeeds (`Http::sequence()`); the quota header stops the job.
- Permissions: 403 without the permission on settings and reports; Marketing Manager sees reports but not settings.
- Ledger: the ad sync writes no journal lines.
- Asia/Dhaka day buckets around midnight.

## Consequences

- Reports depend on our own tables, so they load fast and survive API outages, at the cost of figures that are up to 3 hours (GA4 today) or a day old. Every report says when it was synced.
- Visitors who decline cookies are invisible to GA4 and Meta, so platform figures will be lower than our own order counts. That is why our DB is the source of truth and the others are labelled "for comparison".
- Only the Meta Pixel and Google tags are supported. A third-party tag needs a new decision.
- Ad spend and ledger expenses will differ (timing, currency, VAT). That is expected: the ledger shows what was paid, the report shows what Meta charged.
