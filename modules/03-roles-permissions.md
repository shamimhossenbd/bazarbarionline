# Roles and permissions (Spatie teams)

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 1 | Tenancy | Partial |

## Purpose

One permission system for platform and vendor roles (ADR-05).

## What exists today

Spatie v8 installed with role/permission CRUD and an admin roles page. `teams` is off, permissions are not enforced on any route, and `users.role` duplicates the admin flag. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Permission names `module.action`, tagged platform/vendor/both, seeded from `config/permissions.php`.
- Vendor roles hold only vendor/both permissions.
- No one grants a permission they lack; no one changes their own roles.
- Last active Super Admin cannot be removed or demoted.
- Roles change only through Spatie APIs (cache reset).

## Permissions

`role.manage` (vendor or platform scope), `team.manage`.

## Tables

Spatie `roles`, `permissions`, `model_has_roles`, `model_has_permissions`, `role_has_permissions` with `team_id`.

## Endpoints

`/platform/roles`, `/platform/members`, `/vendor/roles`, `/vendor/members`, `/vendor/invitations`.

## UI and states

Role list, permission editor (accordion by module on phones), member list, invite form.

## Audit events

`role.created`, `role.deleted`, `role.permission_granted`, `role.permission_revoked`, `member.role_changed`, `invitation.*`.

## Required tests

- Vendor cannot assign a platform role.
- User cannot grant a permission they lack.
- Revoked permission fails on the next request.
- Last Super Admin protection.

Done only when the Definition of Done in spec section 16.4 is met.
