# 01 Database restore

Restore the MySQL database from a backup after data loss or corruption, or into staging for the monthly test.

| | |
| --- | --- |
| Who | Owner (Super Admin) |
| Needs | cPanel or SSH access; latest good dump; the dump's decryption key from the password manager |
| Target | RPO 24 h (data since the last dump is lost unless rebuilt), RTO 8 h |
| Status | **Blocked** until daily dumps exist (runbooks README) |

## 1. Decide

1. Confirm the damage: which tables, since when, and whether new orders are still arriving. Write it in the incident log.
2. Choose the scope:
   - **Whole database** wrong or missing → full restore (section 3).
   - **One vendor or a few rows** wrong → partial restore (section 4). Never a full restore for this.
3. Pick the backup: the newest dump taken **before** the damage. Note its file name and time.

## 2. Protect what is there now

```bash
cd /home/<user>/laravel-ecommerce
<php> artisan down --retry=60 --secret="<random>"
mysqldump --single-transaction --routines --triggers -u <db_user> -p <db_name> | gzip > ~/backups/pre-restore-$(date +%Y%m%d-%H%M).sql.gz
```

This copy of the damaged database is kept until the incident is closed: orders placed after the backup are recovered from it.

## 3. Full restore

1. Download the chosen dump from off-site storage to `~/backups/` and decrypt it (`gpg -d file.sql.gz.gpg > file.sql.gz` or the tool the backup uses).
2. Check it is complete: `gunzip -t file.sql.gz` and `zcat file.sql.gz | tail -n 3` should end with `-- Dump completed`.
3. Restore into an **empty new database** first (cPanel → MySQL Databases → create `<user>_restore`, grant the app user):
   ```bash
   zcat file.sql.gz | mysql -u <db_user> -p <user>_restore
   ```
4. Spot-check the restored copy: row counts of `users`, `products`, `orders`, `order_items` and (Phase 3) `ledger_entries`; the newest `orders.created_at`.
5. Switch the app to it: in `.env` set `DB_DATABASE=<user>_restore`, then
   ```bash
   <php> artisan config:cache
   <php> artisan queue:restart
   ```
   Keeping the old database untouched means you can switch back in one step.
6. Recover orders placed after the backup time from the pre-restore copy (section 2): list them with `SELECT id, order_number, created_at FROM orders WHERE created_at > '<backup time UTC>'` on the pre-restore copy and re-enter them, or contact those customers. Never copy finance rows by hand; post corrections as ledger reversals (spec 8.2).
7. `<php> artisan up`.

## 4. Partial restore (one vendor or a few rows)

1. Restore the dump into a separate database `<user>_restore` (steps 3.1–3.3), **not** the live one.
2. Export only the needed rows, for example one vendor's products:
   ```sql
   SELECT * FROM <user>_restore.products WHERE vendor_id = 42;
   ```
3. Compare with live rows and write an `INSERT … ON DUPLICATE KEY UPDATE` script for the affected rows only. Review it with a second person if possible.
4. Run it inside a transaction on live, check the result, commit. Finance and order tables are never fixed this way: use reversal entries.
5. Write an audit event (`system.data_restored`) with the row IDs and reason once the audit log exists.

## 5. Confirm healthy

- Log in as admin; open products, orders, and one customer account.
- Place a test COD order on staging (or production with a test product, then cancel it).
- `<php> artisan queue:failed` is empty or understood; the scheduler heartbeat is under 5 minutes old.
- Drop `<user>_restore` / the pre-restore copy only after 14 days and the owner's OK.

## 6. Afterwards

Fill in the incident log: backup used, data lost (time window), orders re-entered, root cause, prevention.
