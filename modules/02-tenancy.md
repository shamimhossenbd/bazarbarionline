# Tenancy (memberships, TenantContext)

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 1 | Identity | Missing |

## Purpose

Make every vendor's data invisible to every other vendor, enforced on the server (ADR-02, ADR-03).

## What exists today

No vendor concept: no `vendors`, `vendor_user` or `vendor_id` anywhere. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Vendor context comes only from an active membership; `X-Vendor` header only selects among the user's own memberships.
- Membership is re-checked on every request.
- `vendor_id` in a request body is ignored.
- Another vendor's record returns 404.
- Vendor-owned models use `BelongsToVendor` (global scope + auto-fill).

## Permissions

Membership itself grants nothing; permissions come from the team role (module 03).

## Tables

`vendor_user` (`user_id`, `vendor_id`, `status`, `joined_at`; unique pair), `team_invitations`.

## Endpoints

`GET /auth/me` lists memberships; vendor group middleware `tenant`.

## UI and states

Vendor switcher in the dashboard top bar; "no vendor access" state.

## Audit events

`membership.created`, `membership.suspended`, `membership.removed`, `tenant.cross_access_denied`.

## Required tests

- `assertTenantIsolated()` helper for every vendor endpoint (spec 16.2).
- Suspended membership loses access on next request.
- Header with a vendor the user does not belong to returns 404/403 and is audited.

Done only when the Definition of Done in spec section 16.4 is met.
