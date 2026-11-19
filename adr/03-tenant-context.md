# ADR-03: Tenant context from the server

- **Status:** Proposed
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

A browser can send any `vendor_id`. Trusting it is the most common multi-tenant data leak (OWASP Multi-Tenant Security Cheat Sheet).

## Decision

A request-scoped `TenantContext` service is set by `tenant` middleware on the `/api/v1/vendor/*` group. It reads the optional `X-Vendor` header (a vendor ULID), checks that the user has an **active** membership in that vendor (re-checked on every request, never cached in the session), and sets the context plus Spatie's team ID. With no header and exactly one membership, that one is used; otherwise the request fails with 409 `VENDOR_CONTEXT_REQUIRED`. Any `vendor_id` in a request body is ignored.

## Consequences

- A user can belong to several vendors and switch in the UI.
- Suspended memberships lose access on their next request.
- Queued jobs and commands set the context explicitly from the record they process.

## Alternatives rejected

- Reading `vendor_id` from the request body or URL.
- Storing the chosen vendor only in the session without re-checking membership.
