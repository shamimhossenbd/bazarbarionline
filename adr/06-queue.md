# ADR-06: Database queue driven by cron

- **Status:** Proposed — partly in place (`QUEUE_CONNECTION=database` locally)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Shared hosting has no long-running daemon. Phase 0 found the database queue configured locally but no scheduled tasks and no cron.

## Decision

`QUEUE_CONNECTION=database`. cPanel cron runs `php artisan schedule:run` every minute; `routes/console.php` schedules `queue:work --stop-when-empty --max-time=50 --tries=3` every minute without overlapping, plus the nightly jobs (settlement, balance check, reservation expiry). A `scheduler_heartbeat` setting is written on each run.

## Consequences

- Jobs can run up to about a minute late; nothing is advertised as real-time.
- Jobs must finish in under 50 seconds; exports are chunked.
- If volume outgrows this, move the API to a VPS with Supervisor (needs approval).

## Alternatives rejected

- `sync`: slows checkout and loses work on errors.
- Redis/Horizon: not available on shared hosting.
