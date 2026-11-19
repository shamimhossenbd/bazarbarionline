# Customer account, cart, wishlist

| Phase | Depends on | Status (Phase 0) |
| --- | --- | --- |
| 2 | Catalogue | Partial |

## Purpose

Let customers keep a cart and wishlist across devices and manage addresses.

## What exists today

Register/login, account pages, cart and wishlist APIs and UI exist. Cart item ownership is now enforced (another user's item returns 404; audit H1 fixed, `CartItemOwnershipTest`). Cart stores price at add time; add-to-cart checks stock. See [Phase 0 audit](../audit/phase-0.md).

## Rules

- Every cart, wishlist and address query is scoped to the signed-in user; other users' rows return 404.
- Cart shows current price; checkout re-validates price and availability.
- Addresses have division, district, area and phone.

## Permissions

Owner of record.

## Tables

`carts`, `cart_items`, `wishlists`, `wishlist_items`, `customer_addresses`.

## Endpoints

`GET/POST/PATCH/DELETE /account/cart/items`, `/account/wishlist`, `/account/addresses`.

## UI and states

Cart page and mini-cart, wishlist, address book; empty states.

## Audit events

—

## Required tests

- User B cannot update or delete user A's cart item (404).
- Price change between add and checkout is shown to the customer.

Done only when the Definition of Done in spec section 16.4 is met.
