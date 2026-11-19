# ADR-05: Spatie Permission with teams

- **Status:** Proposed — Spatie confirmed installed (v8, teams off)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Spatie Laravel Permission v8 is installed and roles/permissions have CRUD screens. Phase 0 found that permissions are **not enforced** (no `permission:` middleware, policies or gates) and that admin access also depends on a separate `users.role` enum.

## Decision

Enable Spatie `teams` with `team_id = vendor_id`; platform roles have `team_id = NULL`. Permissions are named `module.action`, tagged platform/vendor/both, and seeded from `config/permissions.php`. Every protected route uses `permission:` middleware or a Policy. The `users.role` column is retired once the admin check uses platform roles. Roles change only through Spatie APIs so its cache resets.

## Consequences

- One permission system for platform and vendors.
- Enabling teams changes unique keys on `roles` and the pivots; the migration needs a backup and owner approval (rule 9). The existing migration already creates team columns conditionally.
- Guard names (`web`, `admin`) must be unified so one role works for the user's session.

## Alternatives rejected

- Two separate role systems for platform and vendors.
- Keeping `users.role` as a second source of truth.
