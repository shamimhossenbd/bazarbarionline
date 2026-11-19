# 04 Leaked credential rotation

Replace any secret that may have been seen by someone who should not have it: pasted in a chat, committed to Git, shown in a screenshot or log, on a lost laptop, or held by a person who left.

| | |
| --- | --- |
| Who | Owner |
| Needs | cPanel access, provider dashboards (Steadfast, SMS, mail, payment gateway), password manager |
| Target | Start within 1 hour of discovery; finish the same day |

## 1. Contain first

1. Write down which secret, where it was exposed, when, and who could see it.
2. If it is in Git: do **not** just delete the line; the secret is in history. Rotate it (below) — rotation is what makes it safe, rewriting history is optional.
3. If an attacker may already be using it, put the API in maintenance mode while you rotate: `<php> artisan down --retry=60 --secret="<random>"`.

## 2. Rotate by secret type

| Secret | Where to change it | Then on the server | Side effects |
| --- | --- | --- | --- |
| Database password | cPanel → MySQL Databases → change user password | Update `DB_PASSWORD` in `.env`; `config:cache` | None if done quickly |
| `APP_KEY` | `<php> artisan key:generate --show` (copy) | Set `APP_KEY`, and put the **old** key in `APP_PREVIOUS_KEYS` so existing encrypted data still decrypts; `config:cache` | All users are logged out. Re-encrypt settings secrets, then remove the old key from `APP_PREVIOUS_KEYS` |
| Steadfast API key and secret | Steadfast merchant portal → API: generate new keys, revoke the old ones | Update `STEADFAST_API_KEY` / `STEADFAST_SECRET_KEY` in `.env`; `config:cache`; then `php artisan steadfast:check` must print "Steadfast keys work" (it shows keys masked only). Copy the new **API key fingerprint** it prints into staging's `STEADFAST_PRODUCTION_KEY_FINGERPRINT` | None; the next request uses the new key |
| Steadfast webhook token | Generate a new one: `php -r "echo bin2hex(random_bytes(32));"` | Set `STEADFAST_WEBHOOK_TOKEN` in `.env` and `config:cache`, **then immediately** enter the same token in the Steadfast portal webhook settings | Callbacks sent between the two steps get 401; re-sync those shipments' status afterwards |
| Payment gateway (after launch) | Gateway merchant panel | Same as above; test with one sandbox/low-value payment | — |
| SMS gateway key | SMS provider panel | Update `.env`; `config:cache`; `queue:restart` | — |
| Mail / SMTP password | Mail provider or cPanel → Email Accounts | Update `MAIL_PASSWORD`; `config:cache`; `queue:restart` | — |
| cPanel or hosting account password | Hosting client area | Enable 2FA on cPanel if available | Check cPanel → Cron Jobs, FTP accounts and SSH keys for anything unknown |
| SSH key | cPanel → SSH Access → Manage keys | Delete the leaked key, add a new one | — |
| An admin or staff user password | Admin panel or `artisan tinker` | Force a new password; delete their sessions: `DELETE FROM sessions WHERE user_id = <id>` | User must log in again |
| Git remote token | Git host settings | Revoke and create a new token | Update CI secrets |

After any `.env` change: `<php> artisan config:cache && <php> artisan queue:restart`.

## 3. Look for misuse

- Laravel log and (once built) audit log for the exposure window: logins from new IPs, role changes, payout records, settings changes.
- Provider dashboards: unexpected Steadfast bookings, SMS volume spikes, gateway refunds.
- Database: new users with admin role (`SELECT * FROM model_has_roles` joined to `users`, created after the exposure).

## 4. Confirm and record

- The old secret no longer works (try it once).
- The site works: admin login, a test cart, a Steadfast sandbox call, a test email.
- Update the password manager entry, mark the old value as revoked with the date.
- Incident log entry, and an audit event `security.secret_rotated` (no secret values) once the audit log exists.
