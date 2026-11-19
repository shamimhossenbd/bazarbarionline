# Steadfast Courier integration — security plan

Nov 19, 2026 · @Md Shamim Hossen

**অবস্থা (19 Nov 2026):** নিচের ১৩টা checklist item-ই বানানো হয়েছে, প্রতিটা আলাদা commit-এ, test সহ (148টা test pass), আর `laravel-ecommerce`-এর `master`-এ merge হয়েছে (`dace94a`)। Local database-এ migration চালানো হয়েছে (আগে backup নেওয়া হয়েছে)। প্রতিটা item-এর পাশে commit লেখা আছে; বিস্তারিত [module 13](../modules/13-steadfast-courier.md)-এ।

**Live করার আগে বাকি:** production `.env`-এ `STEADFAST_*` key ও `STEADFAST_WEBHOOK_TOKEN` বসানো; `php artisan steadfast:check` চালানো (শুধু balance পড়ে, কোনো parcel বানায় না); Steadfast portal-এ webhook URL ও token দেওয়া; প্রথম আসল webhook-এ `Authorization: Bearer` header এসেছে কিনা দেখা।

## এখন পর্যন্ত যা ঠিক হয়েছে

দুটো নিয়ম আগেই Specification v2.1-এ লেখা আছে।

| বিষয় | সিদ্ধান্ত | কোথায় লেখা |
| --- | --- | --- |
| Key কোথায় থাকবে | শুধু `.env` ফাইলে, Git-এ কখনো না | Section 19.3 |
| Webhook | verify করা হবে, আর idempotent হবে (একই খবর দুবার এলেও একবারই কাজ হবে) | Section 7.4 ও 10 |

## API key সুরক্ষা

Steadfast-এর API চলে দুটো key দিয়ে: একটা API key আর একটা Secret key ([উৎস](https://steadfast-python.readthedocs.io/en/latest/_sources/index.md.txt))। দুটোই শুধু server-এ থাকবে।

- [x] Key দুটো `.env`-এ রাখা: `STEADFAST_API_KEY` আর `STEADFAST_SECRET_KEY` — `config/services.php` → `services.steadfast` (commit `9f7b675`)
- [x] Key কখনো Next.js frontend-এ যাবে না; Steadfast-কে শুধু Laravel server থেকে ডাকা হবে — `SteadfastClient`, booking: `POST /api/admin/orders/{order}/shipment/steadfast` (`b6bec03`)
- [x] Log, error message বা admin panel-এ key দেখানো যাবে না; দেখাতে হলে mask করে — `Secret::mask()`, `GET /api/admin/courier/steadfast` (`03ed7d7`)
- [x] Staging-এর জন্য আলাদা key — staging-এর `.env`-এ `STEADFAST_PRODUCTION_KEY_FINGERPRINT` দিলে production key সেখানে চলবে না (`ebd7495`)
- [x] Key ফাঁস হলে Steadfast portal থেকে সাথে সাথে নতুন key বানানো — portal-এর ধাপ [runbook 04](../runbooks/04-credential-rotation.md)-এ; নতুন key যাচাই: `php artisan steadfast:check` (`e52d529`)

## Webhook সুরক্ষা

Steadfast delivery-র খবর পাঠালে কোনো তথ্য যাচাই ছাড়া গ্রহণ করা হবে না।

- [x] Webhook URL চলবে শুধু HTTPS-এ: `POST /api/v1/webhooks/courier/steadfast` — HTTP হলে 403 (`b7e8079`)
- [x] Steadfast portal-এ webhook-এর জন্য token বা secret দেওয়ার ব্যবস্থা আছে কিনা দেখা। থাকলে প্রতিটা request-এ মিলিয়ে দেখা হবে; না মিললে request বাতিল (401) — `Authorization: Bearer <STEADFAST_WEBHOOK_TOKEN>`; token না থাকলে 503 (`b663393`)
- [x] একই consignment-এর একই status দুবার এলে একবারই কাজ হবে; এজন্য database-এ unique index — `courier_events` unique (courier, consignment_id, status) (`d2f1844`)
- [x] "Delivered" খবর এলে দরকার হলে Steadfast-এর status API থেকে আবার যাচাই — না মিললে 409, Steadfast না পেলে 503 (`4a164fa`)
- [x] Webhook endpoint-এ rate limit — IP প্রতি মিনিটে `STEADFAST_WEBHOOK_RATE_LIMIT` (default 120), token check-এর আগে (`77ca07c`)

**উত্তর (19 Nov 2026):** Steadfast webhook-এ কোনো signature নেই; merchant portal-এ নিজের বানানো একটা token দেওয়া হয়, আর Steadfast সেটা `Authorization: Bearer <token>` header-এ পাঠায়। এটা `steadfast-laravel-package`-এর source ও README থেকে নেওয়া; Steadfast-এর নিজের API docs (Postman) পড়া যায়নি, তাই প্রথম live webhook এলে header-টা একবার মিলিয়ে দেখতে হবে।

## COD টাকার হিসাব ও audit

Steadfast যত টাকা জমা দেয়, তা প্রতিটা shipment-এর সাথে মিলিয়ে দেখা হবে, আর প্রতিটা বদল audit log-এ থাকবে।

- [x] Steadfast-এর জমা দেওয়া টাকা প্রতিটা shipment-এর COD amount-এর সাথে মেলানো (reconciliation report) — `GET /api/admin/courier/steadfast/reconciliation` (`02f6604`). Steadfast-এর `/payments` API-তে consignment-ভিত্তিক হিসাব documented নয়, তাই এখন delivered webhook-এর `cod_amount`-এর সাথে মেলানো হয়; payment batch import পরে।
- [x] না মিললে admin-কে সতর্ক করা — `CodMismatchDetected` notification, `GET /api/admin/notifications` (`4c96ad6`)
- [x] Parcel booking, cancel আর delivery status-এর প্রতিটা বদল audit log-এ রাখা — `audit_logs` (append-only), `GET /api/admin/audit-logs` (`dace94a`)

## অফিসিয়াল Laravel package ও উৎস

Steadfast-এর নিজস্ব একটা অফিসিয়াল Laravel package আছে। এর version 2.0.0 বের হয়েছে 10 নভেম্বর 2026-এ, আর Laravel 11 বা তার পুরনো version-এ থাকা project-কে ^1.1-এ থাকতে বলা হয়েছে। BazarBariOnline Laravel 13-এ, তাই 2.x চলার কথা।

Specification-এর Section 4 অনুযায়ী নতুন package যোগ করার আগে owner-এর অনুমতি লাগবে।

**সিদ্ধান্ত (19 Nov 2026):** package install করা হয়নি। এটা শুধু একটা Guzzle HTTP client; webhook verify করার কোনো middleware দেয় না (README-তে একটা উদাহরণ controller আছে মাত্র), আর Packagist-এ এটা Steadfast-এর নিজের প্রকাশিত কিনা নিশ্চিত হওয়া যায়নি। তার বদলে Laravel-এর `Http` দিয়ে ছোট `SteadfastClient` বানানো হয়েছে, `CourierGateway` interface-এর পেছনে; পরে চাইলে package দিয়ে বদলানো যাবে।

**উৎস**

- [Steadfast Courier Python SDK documentation](https://steadfast-python.readthedocs.io/en/latest/_sources/index.md.txt): API key ও Secret key
- [steadfast-courier/steadfast-laravel-package on Packagist](https://packagist.org/packages/steadfast-courier/steadfast-laravel-package): package-এর version ও Laravel সমর্থন
