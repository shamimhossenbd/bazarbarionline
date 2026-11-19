# ADR-02: Single database, shared tables

- **Status:** Proposed — not started (no `vendor_id` exists today)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Vendor = tenant. Phase 0 found no vendor concept: no `vendors` table and no `vendor_id` column. cPanel makes many databases hard to create and migrate.

## Decision

All tenants share one database. Every vendor-owned table has `vendor_id` BIGINT NOT NULL, indexed and first in composite list indexes. Vendor-owned models use a `BelongsToVendor` trait that (1) adds a global scope `where vendor_id = TenantContext::id()` when a tenant context is set, and (2) fills `vendor_id` from the context on create, never from the request.

## Consequences

- Isolation depends on code, so every vendor endpoint needs the tenant tests in spec §16.2 (`assertTenantIsolated`).
- Platform screens that read across vendors call `withoutGlobalScope` explicitly and are permission-gated.
- Existing single-shop rows (products, inventory) need a backfill to a first "house" vendor if production holds real data (audit §6 Q2).

## Alternatives rejected

- Database per tenant: needs many databases and per-tenant migrations; impractical on cPanel.
- Schema per tenant: MySQL treats schemas as databases, so the same problem.
