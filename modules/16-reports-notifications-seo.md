# Reports, notifications, storefront SEO

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 3 | All above | Partial |

## Purpose

Trustworthy numbers, timely messages, and search-friendly storefront pages (spec 11.6, 13, 14).

## What exists today

Site-wide SEO meta in `settings` and per-product meta fields exist. The `notifications` table and one notification exist since the Steadfast work (`CodMismatchDetected`, database channel, read via `GET /api/admin/notifications`), plus the COD reconciliation report (`GET /api/admin/courier/steadfast/reconciliation`). No other reports or notifications; mail driver `log`; no scheduler cron yet, so queued notifications need a worker. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Only the eight metrics in spec 14.1, each with formula and Asia/Dhaka boundaries.
- Exports are queued CSV, private, 24-hour signed link, audited.
- Notifications via database queue; OTP SMS synchronous; dedup key per event/target/recipient.
- Server-rendered product, category and vendor pages with metadata, sitemap and structured data.

## Permissions

`report.view` (platform), `report.view_own` (vendor), `report.export`.

## Tables

`notifications`, optional `daily_vendor_stats`.

## Endpoints

`/platform/reports/*`, `/vendor/reports/*`, `/account/notifications`, `GET /public/sitemap`.

## UI and states

Dashboard metric tiles, report tables with export, notification bell.

## Audit events

`report.exported`.

## Required tests

- Vendor report shows only own data.
- Retried notification is sent once.
- Sale at 23:30 Dhaka counts on the Dhaka date.

Done only when the Definition of Done in spec section 16.4 is met.
