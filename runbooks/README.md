# Runbooks

Step-by-step procedures for the incidents named in spec section 15.3. Each runbook is meant to be followed under pressure by one person, so it lists who acts, what to check first, the exact commands, and how to confirm the system is healthy again.

| Runbook | Use when | Target time |
| --- | --- | --- |
| [01 Database restore](01-database-restore.md) | Data lost or corrupted; restore test each month | RTO 8 h |
| [02 File restore](02-file-restore.md) | Uploaded images or vendor documents missing | RTO 8 h |
| [03 Full redeploy](03-full-redeploy.md) | Code folder damaged, new server, or a release must be rebuilt from Git | 2 h |
| [04 Leaked credential rotation](04-credential-rotation.md) | Any secret seen by someone who should not have it | Start within 1 h |
| [05 Failed migration](05-failed-migration.md) | `php artisan migrate --force` errors or leaves the site broken during a deploy | 1 h |
| [06 Hosting outage](06-hosting-outage.md) | API or storefront unreachable, cPanel down, or the host suspends the account | Depends on host |

## Before any of these can work (blockers)

These runbooks assume the operations setup in spec section 15. Until each item below exists, the matching steps are **Blocked** and the runbook says so.

| Prerequisite | Needed by | Status (19 Nov 2026) |
| --- | --- | --- |
| Git repository and remote (spec 15.2) | 03, 05 | Done — private GitHub remotes `bazarbari-api` and `bazarbari-web` (branch `master`); history survives a lost PC once pushed. No CI yet |
| Daily MySQL dump + encrypted off-site copy | 01, 05 | Missing |
| Daily off-site copy of `storage/app` | 02 | Missing |
| Staging subdomain with its own database | 01, 05 | Missing |
| SSH or cPanel Terminal access; PHP CLI path | All | Blocked (owner must check cPanel) |
| Password manager holding `.env` values and keys | 03, 04 | Not confirmed |
| External uptime monitor on storefront and health URL | 06 | Missing (`/api/v1/public/health` not built yet) |

## Conventions used in every runbook

- `<user>` = the cPanel account user name; `<php>` = PHP CLI path confirmed in Phase 0 (often `/usr/local/bin/php` or `/opt/cpanel/ea-php84/root/usr/bin/php`).
- API code lives in `/home/<user>/laravel-ecommerce`; only its `public/` folder is web-exposed (spec 15.2).
- Times are recorded in Asia/Dhaka in the incident log; the database stores UTC.
- **Maintenance mode**: `<php> artisan down --retry=60 --secret="<random>"` lets you browse the site at `https://api.…/<random>` while customers see the 503 page. `<php> artisan up` ends it.
- Every incident gets a short entry in [`incident-log.md`](incident-log.md): date, runbook, who, start/end time, what was lost, what to change.
- Never restore a single vendor's data by overwriting the shared production database (spec 15.3). Use [01 § Partial restore](01-database-restore.md#partial-restore-one-vendor-or-a-few-rows).

## Monthly restore test

Once a month, run [01](01-database-restore.md) and [02](02-file-restore.md) into **staging** using the latest off-site backup. Record in the incident log: date, backup file used, duration, row counts checked, result. A failed test is treated as an incident.
