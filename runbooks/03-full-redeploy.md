# 03 Full redeploy

Rebuild the API (and the Next.js app if it runs on the same host) from Git on a clean folder: after a damaged code folder, a move to a new host, or a release that must be rebuilt.

| | |
| --- | --- |
| Who | Owner |
| Needs | Git remote, `.env` values from the password manager, database backup, file backup |
| Target | 2 hours |
| Status | **Blocked** until both projects are in Git (audit §2.1) |

## 1. Prepare

1. Write in the incident log why a full redeploy is needed and which commit or tag to deploy (normally the last tag on `main`).
2. Take a fresh database dump (see [01 § 2](01-database-restore.md#2-protect-what-is-there-now)) if the database is still reachable.
3. Copy `storage/app` aside if the old folder still exists: `cp -a ~/laravel-ecommerce/storage/app ~/storage-app-$(date +%Y%m%d)`.

## 2. Backend (Laravel)

```bash
cd /home/<user>
git clone --branch main <git-remote-url> laravel-ecommerce-new
cd laravel-ecommerce-new
git checkout <tag>
composer install --no-dev --optimize-autoloader
```

1. Create `.env` from the password manager copy (never from Git). Confirm `APP_ENV=production`, `APP_DEBUG=false`, `APP_URL`, `FRONTEND_URL`, `SESSION_DOMAIN=.<parent-domain>`, `SANCTUM_STATEFUL_DOMAINS`, database and mail values. `APP_KEY` must be the **same** as before or encrypted settings and sessions become unreadable.
2. Bring back uploaded files: copy the saved `storage/app` (step 1.3) or restore from backup ([02](02-file-restore.md)).
3. Prepare the app:
   ```bash
   <php> artisan storage:link
   <php> artisan migrate --force        # only after the backup in step 1.2
   <php> artisan config:cache
   <php> artisan route:cache
   <php> artisan view:cache
   ```
   If `route:cache` fails, a route points at a missing controller method (audit H3); fix it in code, do not skip caching.
4. Swap folders so the old one is kept for rollback:
   ```bash
   mv laravel-ecommerce laravel-ecommerce-old-$(date +%Y%m%d)
   mv laravel-ecommerce-new laravel-ecommerce
   ```
5. Point the API domain's document root (cPanel → Domains) at `/home/<user>/laravel-ecommerce/public`. Nothing else is web-exposed.
6. Make sure the cron job exists (cPanel → Cron Jobs, every minute):
   ```
   <php> /home/<user>/laravel-ecommerce/artisan schedule:run >> /dev/null 2>&1
   ```
7. `<php> artisan queue:restart`.

## 3. Frontend (Next.js)

Only if the storefront runs on this host (ADR-07; otherwise redeploy on Vercel/VPS from the same commit).

1. `git clone` `next-ecommerce` to a new folder and check out the same release tag.
2. Create `.env.production` with `NEXT_PUBLIC_API_URL` and the other public values.
3. `npm ci && npm run build` (on the server if Node is available, otherwise build locally and upload `.next/standalone`, `.next/static` and `public`).
4. cPanel → Setup Node.js App: application root = the new folder, startup file = `server.js` (standalone build), restart.

## 4. Confirm healthy

- `https://api.…/up` returns 200; the storefront home page loads.
- Admin login works at `/admin/login` from the storefront domain (it needs the CSRF cookie and a domain listed in `SANCTUM_STATEFUL_DOMAINS`); `GET /api/admin/user` returns the admin.
- Customer flow: log in, add to cart, view cart.
- Images load (storage symlink). No errors in `storage/logs/laravel-*.log` for 10 minutes.
- Scheduler heartbeat updates within 2 minutes (once the heartbeat exists).

## 5. Roll back

If the new release is broken and cannot be fixed fast: swap the folders back (`mv` in step 2.4 in reverse), restore the database dump from step 1.2 if migrations ran ([05](05-failed-migration.md)), `config:cache`, `queue:restart`.

Delete `laravel-ecommerce-old-*` after one week without issues.
