# ADR-04: Sanctum SPA cookie authentication

- **Status:** **Confirmed** by Phase 0 (already in use)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Phase 0 found `statefulApi()` enabled, axios with `withCredentials` and XSRF, and Next.js rewrites proxying `/api/*` and `/sanctum/*` to Laravel, so the browser sees one origin. Customer register still creates a personal access token that the SPA never uses.

## Decision

Storefront and dashboards authenticate with Sanctum SPA cookies (HttpOnly session + XSRF token). Production: `SESSION_DOMAIN=.<parent-domain>`, `SANCTUM_STATEFUL_DOMAINS=<storefront host>`, CORS `supports_credentials=true`, cookies Secure and SameSite=Lax. Personal access tokens are reserved for a future mobile app. Token creation is removed from `AuthController::register`.

## Consequences

- No token ever reaches JavaScript or localStorage.
- Two session guards (`web`, `admin`) exist today; Phase 1 decides whether to keep both or use one guard with platform roles (ADR-05).
- The domain move (spec §1) needs only `.env` changes.

## Alternatives rejected

- Bearer tokens in localStorage: readable by any XSS.
