# Product approval

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Catalogue | Missing |

## Purpose

Every new or edited product from every vendor is reviewed before it is visible (BD-09).

## What exists today

Products have `is_active` only; no approval state. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- States `draft → pending_review → approved | rejected`.
- Editing an approved product creates a pending revision; the approved version stays live until the revision is approved.
- Rejection needs a reason shown to the vendor.
- No auto-approve.

## Permissions

`product.submit` (vendor), `product.approve` (platform Catalog Manager).

## Tables

`products.approval_status`, `product_revisions` (or a pending JSON snapshot).

## Endpoints

`POST /vendor/products/{ulid}/submit`, `GET /platform/product-approvals`, `POST /platform/product-approvals/{id}/approve|reject`.

## UI and states

Platform review queue with side-by-side diff; vendor sees status badge and rejection reason.

## Audit events

`product.submitted`, `product.approved`, `product.rejected`.

## Required tests

- Unapproved product is invisible publicly.
- Approved product stays live while its edit is pending.
- Vendor cannot approve own product.

Done only when the Definition of Done in spec section 16.4 is met.
