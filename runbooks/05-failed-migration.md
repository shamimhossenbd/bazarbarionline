# 05 Failed migration

Recover when `php artisan migrate --force` errors during a deploy, or the site breaks right after a migration.

| | |
| --- | --- |
| Who | Owner |
| Needs | The database dump taken immediately before migrating (spec 15.2 makes this mandatory), the previous release folder |
| Target | 1 hour |

## 1. Stop and look

1. Keep the site in maintenance mode (deploys should already run `artisan down` before migrating): `<php> artisan down --retry=60 --secret="<random>"`.
2. Read the error. Copy the full message and the migration file name into the incident log.
3. See where it stopped:
   ```bash
   <php> artisan migrate:status
   ```
   Migrations marked `Ran` in the last batch finished; the first `Pending` one is the one that failed.

MySQL does not roll back DDL (`CREATE`, `ALTER`, `DROP`) inside a transaction, so a migration can fail **half-way**: some columns or indexes added, the row in `migrations` not written.

## 2. Choose a path

| Situation | Path |
| --- | --- |
| Failed migration only adds things (new table, column, index) and no data changed | **A. Fix forward** |
| Migration changed or deleted data, or several migrations ran and the app is broken | **B. Restore** |
| Unsure | **B. Restore** |

### A. Fix forward

1. Undo the half-applied part by hand, matching what the migration's `up()` did before it failed, e.g. `ALTER TABLE products DROP COLUMN vendor_id;`. Check with `SHOW CREATE TABLE <table>;`.
2. Fix the migration in code (local), test it on a copy of production data on staging, commit, and redeploy the fixed release.
3. If earlier migrations in the same batch succeeded and the new code needs them, keep them. If the code cannot run with them, roll them back: `<php> artisan migrate:rollback --step=<n>` — only if each has a working `down()` (spec 9 requires this or an "irreversible" header).

### B. Restore

1. Put the previous release back (swap folders as in [03 § 5](03-full-redeploy.md#5-roll-back)).
2. Restore the pre-migration dump into a new empty database and switch `.env` to it ([01 § 3](01-database-restore.md#3-full-restore), steps 3–5). Keep the broken database for inspection.
3. Any order placed between the dump and maintenance mode: recover it as in [01 § 3 step 6](01-database-restore.md#3-full-restore).

## 3. Bring the site back

```bash
<php> artisan config:cache
<php> artisan route:cache
<php> artisan queue:restart
<php> artisan up
```

Check: admin login, product list, a customer cart, and `storage/logs` free of new errors for 10 minutes.

## 4. Prevent the next one

- Every migration runs on staging against an anonymized copy of production first (spec 15.1).
- Large-table changes (adding `vendor_id` to `products`, `orders`) are split: add nullable column → backfill in chunks → add constraint, each in its own deploy.
- Incident log entry with the root cause and which rule above would have caught it.
