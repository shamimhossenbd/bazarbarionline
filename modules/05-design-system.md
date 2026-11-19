# Design system, shell, theme, i18n

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 1 | — | Partial |

## Purpose

One consistent UI for storefront and dashboards in Bangla and English, light and dark (spec 11).

## What exists today

Bootstrap 5.3 storefront and admin shell exist. `components/ui/{Button,Loader,Modal,Pagination}.tsx` are empty; two icon sets (bootstrap-icons and lucide-react) and two alert libraries; light theme only; English only; home page uses hard-coded products in `data/homeSections.ts`. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Bootstrap 5.3 base with CSS-variable brand tokens; no second UI library.
- One icon set (Lucide).
- Every data view has loading, empty, error-with-retry and access-denied states.
- Theme via `data-bs-theme`, set before paint.
- Storefront locale in URL (`/bn`, `/en`); dashboards use user preference.
- No hard-coded or mock business data (rule 7).

## Permissions

—

## Tables

User preference columns (locale, theme).

## Endpoints

`PATCH /account/preferences`.

## UI and states

Dashboard shell (sidebar, top bar, breadcrumbs), shared components, theme and language switchers.

## Audit events

—

## Required tests

- Component tests for each state (Vitest).
- Contrast check in both themes.
- Bangla price formatting with `Intl.NumberFormat('bn-BD')`.

Done only when the Definition of Done in spec section 16.4 is met.
