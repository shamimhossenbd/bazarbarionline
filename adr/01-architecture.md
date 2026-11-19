# ADR-01: Modular monolith

- **Status:** Proposed — partly confirmed by Phase 0 (audit §3)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

One developer-owner, cPanel shared hosting and one MySQL database. Phase 0 found a flat Laravel app (`app/Http/Controllers/{Api,Admin}`, `app/Services`) and one Next.js app with `(shop)` and `admin` route groups.

## Decision

Keep one Laravel app and one Next.js app. New modules (Tenancy, Vendors, Finance, Courier, Returns, Audit) live in `app/Domain/<Name>` with their own models, actions, policies and events. Existing code moves into a domain folder only when it is changed for another reason. The Next.js app gains `(vendor)`, `(platform)` and `(account)` route groups.

## Consequences

- One deploy, one database, one place to debug.
- Domain boundaries are folder conventions, not services; cross-domain calls go through actions or events.
- Old and new layouts co-exist for a while; the module register (spec §18) records which modules have moved.

## Alternatives rejected

- Microservices: too much operational load for one person on shared hosting.
- A separate vendor frontend app: duplicates the design system and auth.
