# Catalogue (categories, brands, products, variants, media)

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Vendors | Partial |

## Purpose

Platform-owned taxonomy; vendor-owned products.

## What exists today

Category tree, brands, products, variants with attribute values, images, features, specifications and questions exist with admin CRUD. No `vendor_id`, no ulid, no bilingual fields, no FULLTEXT. The lowercase `product` namespace bug is fixed (audit H2). `GET /admin/reviews` still returns an empty list (H3 remainder). See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Categories and brands are global (BD-10); vendors may request new ones.
- Products carry `vendor_id`; SKU unique per vendor.
- Public URLs use ulid or slug, never numeric IDs.
- Images converted to WebP in three sizes (ADR-10).
- Soft deletes on catalogue rows.

## Permissions

`catalog.category.manage`, `catalog.brand.manage` (platform); `product.view`, `product.create`, `product.update`, `product.delete` (vendor).

## Tables

`categories`, `brands`, `attributes`, `attribute_values`, `products`, `product_variants`, `product_variant_values`, `product_images`, `product_features`, `product_specifications`.

## Endpoints

`GET /public/products`, `/public/products/{ulid}`, `/public/categories`, `/public/search`; `/vendor/products` CRUD; `/platform/categories`, `/platform/brands`.

## UI and states

Storefront listing, filters and product page; vendor product form with variants and images.

## Audit events

`product.created`, `product.updated`, `product.deleted`, `category.*`, `brand.*`.

## Required tests

- Vendor A cannot edit vendor B's product (404).
- Inactive or unapproved product is not public.
- SKU uniqueness is per vendor.

Done only when the Definition of Done in spec section 16.4 is met.
