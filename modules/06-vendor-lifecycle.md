# Vendor onboarding and lifecycle

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Tenancy, roles | Missing |

## Purpose

Let a business apply, be reviewed, sell, and be restricted, suspended or closed with controlled effects (spec 6.6).

## What exists today

No vendors. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- States `pending → active ↔ restricted ↔ suspended → closed`.
- Every change needs `vendor.manage_status`, a reason, confirmation and an audit event.
- Suspension hides the store, blocks new orders, freezes payouts, deletes nothing.
- Trade licence and NID stored privately, served by signed URL.
- Risk indicators are shown, never auto-suspend in MVP.

## Permissions

`vendor.view`, `vendor.manage_status`, `vendor.documents.view`; vendor side `store.manage`.

## Tables

`vendors` (ulid, slug, status), `vendor_documents`, `vendor_settings`, `vendor_status_history`.

## Endpoints

`POST /vendor-applications`, `/platform/vendors`, `POST /platform/vendors/{id}/status`, `/vendor/store`.

## UI and states

Application form with document upload; platform review queue; vendor store settings page.

## Audit events

`vendor.applied`, `vendor.approved`, `vendor.rejected`, `vendor.status_changed`, `vendor.document_viewed`.

## Required tests

- Suspended vendor's products vanish from public endpoints.
- Payout request blocked while suspended.
- Status change without reason is rejected.

Done only when the Definition of Done in spec section 16.4 is met.
