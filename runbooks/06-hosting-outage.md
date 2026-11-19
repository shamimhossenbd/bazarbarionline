# 06 Hosting outage

What to do when the API, storefront or cPanel stops responding, or the host suspends the account.

| | |
| --- | --- |
| Who | Owner |
| Needs | Host's support contact and status page, domain registrar login, latest off-site backups |
| Target | Depends on the host; decide on moving after 4 hours down (proposed, owner confirms) |

## 1. Is it us or the host? (first 10 minutes)

| Check | How | If it fails |
| --- | --- | --- |
| Domain resolves | `nslookup api.<domain>` and `nslookup <domain>` | DNS or registrar problem: check the registrar (expired domain, changed nameservers) |
| Server answers | `curl -I https://api.<domain>/up` | 5xx → step 2; timeout → step 3 |
| cPanel reachable | Open `https://<host>:2083` | Host-wide outage → step 3 |
| SSL valid | Browser padlock / `curl -v` | Expired certificate → cPanel → SSL/TLS Status → Run AutoSSL |
| Host status | Host's status page or support chat | Note the ticket number in the incident log |

## 2. Site returns errors but the host is up

1. Read the newest `storage/logs/laravel-*.log` (cPanel File Manager if no SSH) and the cPanel **Errors** page.
2. Common causes on shared hosting:

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| 500 on every API call after a deploy | Stale caches or missing `vendor/` | `composer install --no-dev`, `config:clear`, then `config:cache`, `route:cache` |
| "Class not found" only on the server | Folder name case (audit H2: `Requests\product` vs `Product`) | Fix the namespace in code and redeploy |
| 503 "Resource limit reached" | CPU/entry-process limit (CloudLinux) | Wait, check for a runaway cron (`queue:work` without `--max-time`), ask the host for the limit hit |
| "Disk quota exceeded" | Logs, old releases or backups filling the account | Delete old `laravel-ecommerce-old-*`, rotate logs, move backups off-site |
| Database connection refused | MySQL down or user password changed | Host ticket, or check `.env` against cPanel MySQL users |
| Storefront down, API fine | Node.js app stopped (ADR-07) | cPanel → Setup Node.js App → Restart; check its log |

3. Fix, then confirm as in [03 § 4](03-full-redeploy.md#4-confirm-healthy).

## 3. Host is down

1. Open a support ticket; record its number and time.
2. Tell customers: a short message on the brand's social pages ("Orders are paused; no data is lost"). Do not promise times you do not control.
3. Steadfast keeps delivering parcels already booked; webhooks sent while the API is down are lost or retried by Steadfast. After recovery, re-sync shipment status from the Steadfast API for every shipment updated during the outage window (module 13).
4. If the host has given no recovery time after **4 hours** (owner may change this), start moving:
   1. Prepare a new host (another cPanel plan or a small VPS).
   2. Redeploy from Git ([03](03-full-redeploy.md)), restore the database ([01](01-database-restore.md)) and files ([02](02-file-restore.md)) from the latest off-site backups.
   3. Lower DNS TTL if still possible, then point `api.` and the storefront domain at the new server.
   4. Update `SANCTUM_STATEFUL_DOMAINS`, `SESSION_DOMAIN` only if domains change.
   5. Update the Steadfast webhook URL if it changes.

Data written after the last off-site backup lives only on the failed host. Recover it from the old host once it returns, using the partial-restore method in [01 § 4](01-database-restore.md#4-partial-restore-one-vendor-or-a-few-rows).

## 4. Afterwards

- Incident log: start and end time, cause, orders affected, data lost.
- Uptime monitor alerted? If not, fix the monitor (spec 15.4).
- If outages repeat, move the API to a VPS (needs owner approval; ADR-06 consequence).
