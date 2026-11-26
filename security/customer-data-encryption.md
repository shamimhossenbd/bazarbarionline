# Customer data encryption at rest

Customer contact details are stored encrypted with Laravel encrypted casts
(AES-256, key = `APP_KEY`). The application reads and writes them as plain
text; the database, backups and anyone with SQL access see only ciphertext.

| Table | Encrypted | Plain (on purpose) |
|---|---|---|
| `users` | `phone` | `name`, `email` (login identifier, must be searchable) |
| `order_addresses` | `phone`, `address` | `name`, `city`, `state`, `postal_code`, `country` (delivery zones, courier) |

Not encrypted: `vendors.phone` and `settings.support_phone` (public business
contact numbers).

## Encrypted columns cannot be searched in the database

Every encryption produces a different ciphertext, so MySQL cannot compare,
search, sort, group or enforce uniqueness on these columns:

- `where('phone', '017...')`, `like '%017%'`, `orderBy('phone')` and unique
  indexes **do not work** on encrypted columns.
- Exact phone lookups and the unique rule use `users.phone_hash`, a keyed
  HMAC of the normalized number (`App\Support\BlindIndex`,
  `App\Rules\UniquePhone`). `01712345678`, `+8801712345678` and
  `8801712345678` are the same number.
- Partial matches are impossible on encrypted data. Load the rows, then
  filter in PHP (fine for an admin page; not for large tables).
- New encrypted columns must be `TEXT`: ciphertext is several times longer
  than the plain value.

## Keys: losing APP_KEY loses the data

- Back up `APP_KEY` with the database backups, stored separately from them.
  A database backup without its `APP_KEY` cannot be read.
- Never run `php artisan key:generate` on a server that holds data.
- Rotating `APP_KEY`: put the old key in `APP_PREVIOUS_KEYS` (comma
  separated), deploy the new key; old values still decrypt and are
  re-encrypted with the new key when saved. Then run
  `php artisan users:reindex-phone-hashes` (the phone hash is derived from
  `APP_KEY` unless `BLIND_INDEX_KEY` is set).
- `BLIND_INDEX_KEY` (optional) separates the search-hash key from
  `APP_KEY`; changing it also requires `php artisan users:reindex-phone-hashes`.

## Deploying the encryption migration

Migration `2026_11_21_000002_encrypt_customer_contact_details`:

1. Back up the database and `APP_KEY` (runbook 01).
2. `php artisan down`, then `php artisan migrate --force`.
3. The migration stops before changing anything if two users have the same
   phone number in different formats; resolve those accounts and re-run.
4. It is safe to re-run after a partial failure (already encrypted values
   are skipped, schema steps check the current state).
5. Verify: sign in to the admin panel, open Users and an order; phones and
   addresses must display normally. `php artisan up`.

Rollback: `php artisan migrate:rollback --step=1` decrypts every value and
restores the original columns and the unique index on `users.phone`.
Rehearsed on a copy of the local database (MySQL 8.4): encrypt, decrypt and
rollback all reproduced the original values exactly.

## Audit log

`App\Services\AuditLogger` redacts values under sensitive keys (password,
token, secret, API key, email, phone, address, account details) at any
depth. Record field names, not values, when personal data changes.
