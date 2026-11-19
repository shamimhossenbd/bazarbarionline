# Audit log

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 1 | Identity | Partial |

## Purpose

An append-only record of who did what, for security and dispute handling (spec 12.2).

## What exists today

Built with the Steadfast integration (19 Nov 2026): `audit_logs` table with every spec 12.2 column, append-only `AuditLog` model (update/delete throw), `App\Services\AuditLogger`, and read-only `GET /api/admin/audit-logs` (filter by event, `shipment.*` prefix, target). Only courier events are logged so far (`shipment.*`). Missing: auth, role, settings and order events; vendor-scoped view; `X-Request-Id` middleware (the logger stores the header only if the client sends one); DB-level `DELETE` restriction. See [module 13](13-steadfast-courier.md).

## Rules

- Append-only; no update or delete routes; no `updated_at`.
- Every row carries `request_id`, actor, `vendor_id` (nullable), event code, target, result, redacted before/after, reason, IP, user agent.
- Vendors see only their own events; platform auditors see all.
- Nothing is purged until the owner sets retention with legal advice.

## Permissions

`audit.view` (platform), `audit.view_own` (vendor).

## Tables

`audit_logs`.

## Endpoints

`GET /platform/audit-logs`, `GET /vendor/audit-logs`; export is itself audited.

## UI and states

Filterable table (date, actor, event, result) with a detail drawer showing the diff.

## Audit events

—

## Required tests

- Secrets are redacted in `changes`.
- Vendor A cannot read vendor B's events.
- No route can modify a row.

Done only when the Definition of Done in spec section 16.4 is met.
