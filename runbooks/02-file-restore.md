# 02 File restore

Restore uploaded files (product images, category and brand images, logo, vendor documents) after they are deleted or damaged.

| | |
| --- | --- |
| Who | Owner (Super Admin) |
| Needs | Off-site copy of `storage/app`; cPanel File Manager or SSH |
| Target | RPO 24 h, RTO 8 h |
| Status | **Blocked** until daily off-site file backups exist |

## Where files live

| Files | Path on server | Web access |
| --- | --- | --- |
| Public images (products, categories, brands, logo, description images) | `laravel-ecommerce/storage/app/public/…` | Through the `public/storage` symlink (`php artisan storage:link`) |
| Private vendor documents (Phase 2) | `laravel-ecommerce/storage/app/private/…` | Only through signed URLs |

The database stores paths, not files, so a restored file must keep its exact path and name.

## 1. Find what is missing

1. Note one broken image URL and convert it to a path: `https://api.…/storage/products/abc.webp` → `storage/app/public/products/abc.webp`.
2. Check whether the symlink is the problem rather than the files: `ls -la public/storage`. If the link is missing or points to an old release folder:
   ```bash
   rm public/storage   # only if it is a broken link, never a real folder
   <php> artisan storage:link
   ```
   If images now load, stop here.
3. List what the database expects but the disk lacks (run in `laravel-ecommerce`):
   ```bash
   <php> artisan tinker --execute 'foreach (App\Models\ProductImage::pluck("image") as $p) { if (! Storage::disk("public")->exists($p)) echo $p.PHP_EOL; }'
   ```
   Adjust the model and column to the table that is affected.

## 2. Restore

1. Download the newest file backup taken before the loss into `~/restore/`, not over the live folder.
2. Copy back only missing files, never overwriting newer ones:
   ```bash
   rsync -av --ignore-existing ~/restore/storage/app/public/ /home/<user>/laravel-ecommerce/storage/app/public/
   rsync -av --ignore-existing ~/restore/storage/app/private/ /home/<user>/laravel-ecommerce/storage/app/private/
   ```
   Without SSH: upload the zip in cPanel File Manager to `~/restore/` and extract there, then move the missing folders.
3. Fix permissions: folders `755`, files `644`.

## 3. Confirm healthy

- Re-run the check in 1.3: no missing paths.
- Open the storefront home page, a product page and the admin product list.
- Files uploaded after the backup cannot come back from it: list them (from step 1.3) and ask the vendor or admin to upload them again.

## 4. Afterwards

Incident log entry with the number of files restored and the number lost.
