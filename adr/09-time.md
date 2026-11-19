# ADR-09: Store UTC, show Asia/Dhaka

- **Status:** **Confirmed** for storage (`config/app.php` timezone is `UTC`)
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Bangladesh is UTC+6. Daily sales reports must cut days at Dhaka midnight, not UTC midnight.

## Decision

Database and application time are UTC. The API returns ISO-8601 timestamps with offset; the frontend formats them in Asia/Dhaka. Report queries convert period boundaries from Asia/Dhaka to UTC before filtering. Return-window and settlement jobs count days in Asia/Dhaka.

## Consequences

- One conversion helper is used by every report.
- Tests include a sale at 23:30 Dhaka time.

## Alternatives rejected

- Storing local time: complicates integrations and breaks if hosting time zone changes.
