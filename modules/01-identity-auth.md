# Identity and authentication

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 1 | — | Partial |

## Purpose

Let every person (customer, vendor staff, platform staff) sign in once with one account, safely.

## What exists today

Sanctum SPA cookie login for customers (`/api/account/login`) and admins (`/api/admin/login`, throttled, 15-min idle timeout). Customer login leaks whether an email exists and is not throttled; register issues an unused API token. No OTP, no 2FA. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- One `users` row per person; unique email and unique phone.
- Login by email or BD mobile + password; customers may use phone OTP (3 sends per 10 min per phone).
- Generic error on failed login; 5 attempts/min per account+IP.
- Session regenerated on login; HttpOnly, Secure, SameSite=Lax cookies.
- 2FA (TOTP) required for platform roles and Vendor Owners.
- Password re-confirmation within 15 min for sensitive actions (spec 12.1).

## Permissions

None (public auth endpoints); `GET /auth/me` for any signed-in user.

## Tables

`users`, `sessions`, `password_reset_tokens`, `personal_access_tokens` (mobile later), 2FA columns or table.

## Endpoints

`POST /auth/login`, `/auth/logout`, `/auth/register`, `/auth/otp/send`, `/auth/otp/verify`, `GET /auth/me` (roles, memberships, permissions).

## UI and states

Login, register, OTP, forgot/reset password, 2FA setup and challenge; loading, error and locked-out states.

## Audit events

`auth.login_succeeded`, `auth.login_failed`, `auth.logout`, `auth.2fa_enabled`, `auth.2fa_disabled`, `auth.password_changed`.

## Required tests

- Same response for unknown email and wrong password.
- 6th attempt in a minute returns 429.
- Platform user without 2FA cannot reach platform routes.
- `/auth/me` never returns password or tokens.

Done only when the Definition of Done in spec section 16.4 is met.
