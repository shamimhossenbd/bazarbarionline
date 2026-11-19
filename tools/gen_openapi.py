"""Generate documentation/openapi.yaml from `artisan route:list --json` plus hand-written metadata."""
import json
import re
import sys

import yaml

routes = json.load(open(sys.argv[1], encoding="utf-8"))
out_path = sys.argv[2]
BS = chr(92)

# ---------------------------------------------------------------- schemas
def s(t, **kw):
    d = {"type": t}
    d.update(kw)
    return d

STR = s("string")
INT = s("integer")
BOOL = s("boolean")
NUM = s("number")

def obj(props, required=()):
    d = {"type": "object", "properties": props}
    if required:
        d["required"] = list(required)
    return d

def arr(items):
    return {"type": "array", "items": items}

schemas = {
    "Message": obj({"success": BOOL, "message": STR}),
    "ValidationError": obj({
        "message": STR,
        "errors": {"type": "object", "additionalProperties": arr(STR)},
    }),
    "CodedError": obj({"message": STR, "code": s("string", example="INSUFFICIENT_STOCK")}),
    "AdminSession": obj({
        "success": BOOL,
        "message": s("string", nullable=True),
        "user": obj({"id": INT, "name": STR, "email": STR, "status": INT}),
        "roles": arr(STR),
        "permissions": arr(STR),
    }),
    "Paginated": obj({
        "current_page": INT, "data": arr(s("object")), "per_page": INT,
        "total": INT, "last_page": INT, "next_page_url": s("string", nullable=True),
    }),
    "LoginRequest": obj({"email": s("string", format="email", maxLength=255),
                         "password": STR}, ["email", "password"]),
    "RegisterRequest": obj({
        "name": s("string", maxLength=255),
        "email": s("string", format="email", maxLength=255),
        "password": s("string", minLength=8),
        "password_confirmation": STR,
    }, ["name", "email", "password", "password_confirmation"]),
    "CartItemCreate": obj({"product_id": INT, "product_variant_id": s("integer", nullable=True),
                           "quantity": s("integer", minimum=1)}, ["product_id", "quantity"]),
    "CartItemUpdate": obj({"quantity": s("integer", minimum=1)}, ["quantity"]),
    "CheckoutRequest": obj({
        "shipping_address": obj({"name": STR, "phone": STR, "address": STR, "city": STR,
                                 "postal_code": s("string", nullable=True)},
                                ["name", "phone", "address", "city"]),
    }, ["shipping_address"]),
    "OrderStatusUpdate": obj({"status": s("string", enum=[
        "pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"])},
        ["status"]),
    "CouponValidate": obj({"code": STR, "subtotal": s("number", minimum=0)}, ["code", "subtotal"]),
    "ReviewCreate": obj({"rating": s("integer", minimum=1, maximum=5),
                         "comment": s("string", maxLength=1000, nullable=True),
                         "order_id": s("integer", nullable=True)}, ["rating"]),
    "WishlistItemCreate": obj({"product_id": INT}, ["product_id"]),
    "CategoryWrite": obj({
        "parent_id": s("integer", nullable=True), "name": s("string", maxLength=255),
        "slug": s("string", maxLength=255), "image": s("string", format="binary"),
        "image_alt": STR, "icon": STR, "short_description": s("string", maxLength=500),
        "description": STR, "status": BOOL, "sort_order": INT,
    }, ["name"]),
    "BrandWrite": obj({"name": STR, "slug": STR, "logo": s("string", format="binary"),
                       "description": STR, "status": BOOL}, ["name"]),
    "AttributeWrite": obj({"name": s("string", maxLength=255), "slug": STR}, ["name"]),
    "AttributeValueWrite": obj({"value": s("string", maxLength=255), "slug": STR}, ["value"]),
    "ProductWrite": obj({
        "category_id": INT, "brand_id": s("integer", nullable=True), "name": STR, "slug": STR,
        "sku": STR, "short_description": STR, "description": STR, "price": NUM,
        "compare_price": NUM, "cost_price": NUM, "stock": INT, "low_stock_threshold": INT,
        "thumbnail": s("string", format="binary"), "images": arr(s("string", format="binary")),
        "delete_images": s("array", items=INT, description="Update only"),
        "primary_image_id": s("integer", description="Update only"),
        "is_featured": BOOL, "is_active": BOOL, "sort_order": INT,
        "meta_title": STR, "meta_description": STR,
    }, ["category_id", "name", "price"]),
    "DescriptionImageUpload": obj({"upload": s("string", format="binary")}, ["upload"]),
    "VariantWrite": obj({"sku": STR, "price": NUM, "compare_price": NUM, "stock": INT,
                         "image": s("string", format="binary"), "status": BOOL,
                         "attribute_value_ids": arr(INT)}),
    "FeatureWrite": obj({"feature": STR, "sort_order": INT, "status": BOOL}, ["feature"]),
    "SpecificationWrite": obj({"group_name": STR, "name": STR, "value": STR,
                               "sort_order": INT, "status": BOOL}, ["name", "value"]),
    "InventoryUpdate": obj({"quantity": s("integer", minimum=0), "reserved_quantity": INT,
                            "low_stock_threshold": INT}, ["quantity"]),
    "PermissionWrite": obj({"name": s("string", maxLength=255)}, ["name"]),
    "RoleWrite": obj({"name": s("string", maxLength=255), "permissions": arr(STR)}, ["name"]),
    "AssignRoles": obj({"roles": arr(STR)}, ["roles"]),
    "UserWrite": obj({"name": STR, "email": s("string", format="email"),
                      "phone": s("string", maxLength=20, nullable=True),
                      "password": s("string", minLength=8), "status": BOOL,
                      "role": s("string", description="Store only")}, ["name", "email"]),
    "LogoUpload": obj({"logo": s("string", format="binary")}, ["logo"]),
    "SeoUpdate": obj({"meta_title": STR, "meta_description": STR, "meta_keywords": STR}),
    # Steadfast courier
    "SteadfastBookRequest": obj({"note": s("string", maxLength=255, nullable=True)}),
    "SteadfastBookResponse": obj({"message": STR, "shipment": obj({
        "id": INT, "order_id": INT, "courier": s("string", example="steadfast"),
        "consignment_id": STR, "tracking_number": s("string", nullable=True), "invoice": STR,
        "cod_amount": s("string", example="1560.00"), "status": s("string", example="processing"),
        "courier_status": s("string", example="in_review"), "booked_at": s("string", format="date-time")})}),
    "SteadfastWebhook": obj({
        "consignment_id": s("string", description="Integer or string"),
        "status": s("string", enum=[
            "in_review", "pending", "hold", "unknown", "delivered_approval_pending",
            "partial_delivered_approval_pending", "cancelled_approval_pending",
            "unknown_approval_pending", "delivered", "partial_delivered", "cancelled"]),
        "invoice": s("string", nullable=True), "cod_amount": s("number", nullable=True, minimum=0),
        "updated_at": s("string", nullable=True)}, ["consignment_id", "status"]),
    "SteadfastWebhookResult": obj({"status": s("string", enum=[
        "processed", "duplicate", "unknown_consignment", "delivery_not_confirmed"])}),
    "CourierSettings": obj({
        "courier": STR, "configured": BOOL, "base_url": STR,
        "api_key": s("string", example="********7890"), "secret_key": s("string", example="********ghij"),
        "environment": STR, "api_key_fingerprint": s("string", nullable=True),
        "production_key_guard": BOOL, "production_key_refused": BOOL,
        "webhook_url": STR, "webhook_token": s("string", example="********6789")}),
    "CodReconciliationReport": obj({
        "courier": STR, "from": s("string", nullable=True), "to": s("string", nullable=True),
        "totals": obj({"shipments": INT, "expected": STR, "collected": STR, "difference": STR,
                       "mismatches": INT, "not_reported": INT}),
        "data": arr(obj({
            "shipment_id": INT, "order_id": INT, "order_number": STR, "consignment_id": STR,
            "courier_status": STR, "delivered_at": s("string", nullable=True), "expected": STR,
            "collected": s("string", nullable=True), "difference": s("string", nullable=True),
            "result": s("string", enum=["matched", "mismatch", "not_reported"])}))}),
}

def ref(name):
    return {"$ref": f"#/components/schemas/{name}"}

# --------------------------------------------- per-controller metadata
# controller -> (tag, request schema for POST/PUT, target permission(s), audit event prefix)
CTRL = {
    "AttributeController": ("Admin catalogue", "AttributeWrite", "catalog.attribute.manage", "attribute"),
    "AttributeValueController": ("Admin catalogue", "AttributeValueWrite", "catalog.attribute.manage", "attribute_value"),
    "BrandController": ("Admin catalogue", "BrandWrite", "catalog.brand.manage", "brand"),
    "CategoryController": ("Admin catalogue", "CategoryWrite", "catalog.category.manage", "category"),
    "ProductController": ("Admin catalogue", "ProductWrite", "product.view / product.update", "product"),
    "ProductFeatureController": ("Admin catalogue", "FeatureWrite", "product.update", "product"),
    "ProductSpecificationController": ("Admin catalogue", "SpecificationWrite", "product.update", "product"),
    "ProductVariantController": ("Admin catalogue", "VariantWrite", "product.update", "product"),
    "InventoryController": ("Admin inventory", "InventoryUpdate", "inventory.adjust", "inventory"),
    "OrderController": ("Admin orders", "OrderStatusUpdate", "order.view_all / order.cancel_any", "order"),
    "PermissionController": ("Admin access", "PermissionWrite", "role.manage", "permission"),
    "RoleController": ("Admin access", "RoleWrite", "role.manage", "role"),
    "UserController": ("Admin access", "UserWrite", "team.manage / customer.manage", "user"),
    "ReviewController": ("Admin catalogue", None, "review.moderate", "review"),
    "SettingController": ("Admin settings", None, "settings.manage", "settings"),
}

# exact overrides: (METHOD, uri) -> dict
O = {}
def o(method, uri, **kw):
    O[(method, uri)] = kw

# Auth
o("POST", "api/account/login", tag="Customer auth", summary="Customer login (Sanctum session cookie)",
  body="LoginRequest", rate="none (spec: 5/min — missing)",
  issues=["Not throttled.", "Returns 'User not found.' vs 'Password is incorrect.' (account enumeration, spec 12.1)."],
  target="— (public)", audit="auth.login_succeeded / auth.login_failed (not yet logged)")
o("POST", "api/account/register", tag="Customer auth", summary="Register a customer account", body="RegisterRequest",
  issues=["Returns an unused personal access token although the SPA uses cookies.",
          "No Password::uncompromised() check."], target="— (public)")
o("POST", "api/account/logout", tag="Customer auth", summary="Log out the customer session")
o("GET", "api/account/user", tag="Customer auth", summary="Current customer")
o("POST", "api/admin/login", tag="Admin auth", summary="Admin login (Sanctum session cookie, `admin` guard)",
  body="LoginRequest", resp="AdminSession", rate="5 failed attempts per email+IP, 60 s lockout",
  target="— (public)", audit="auth.login_succeeded / auth.login_failed (not yet logged)",
  notes="Must be called from the SPA origin (SANCTUM_STATEFUL_DOMAINS) after GET /sanctum/csrf-cookie. "
        "A direct call without an Origin/Referer header fails with 500 'Session store not set on request.' "
        "Local seed account: admin@example.com / password.",
  extra_resp={"403": "Account inactive or lacks the admin role", "429": "Too many attempts"})
o("POST", "api/admin/logout", tag="Admin auth", summary="Admin logout; invalidates the session")
o("GET", "api/admin/user", tag="Admin auth", summary="Current admin with roles and permissions", resp="AdminSession")

# Storefront public
for u, sm in [("api/products", "List active products (filters, pagination)"),
              ("api/products/{product}", "Product detail by slug"),
              ("api/products/{product}/variants", "Variants of a product"),
              ("api/products/{product}/reviews", "Approved reviews of a product"),
              ("api/categories", "Category tree for the storefront"),
              ("api/categories/{category}", "Category by slug with products"),
              ("api/brands", "Active brands"), ("api/attributes", "Attributes and values"),
              ("api/settings", "Public site settings (logo, SEO defaults)")]:
    o("GET", u, tag="Storefront", summary=sm, target="— (public)")

o("POST", "api/products/{product}/reviews", tag="Customer account", summary="Submit a review (held for approval)",
  body="ReviewCreate", target="owner of record")

# Cart / wishlist / orders
o("GET", "api/cart", tag="Customer cart", summary="Current user's cart with items and totals", target="owner of record")
o("DELETE", "api/cart", tag="Customer cart", summary="Empty the cart", target="owner of record")
o("POST", "api/cart/items", tag="Customer cart", summary="Add a product or variant to the cart", body="CartItemCreate",
  target="owner of record", extra_resp={"422": "INSUFFICIENT_STOCK or validation error"})
o("PUT", "api/cart/items/{cartItem}", tag="Customer cart", summary="Change quantity of a cart item", body="CartItemUpdate",
  target="owner of record", notes="Another user's item returns 404 (audit H1 fixed; CartItemOwnershipTest).",
  extra_resp={"404": "Item not in the current user's cart"})
o("DELETE", "api/cart/items/{cartItem}", tag="Customer cart", summary="Remove a cart item", target="owner of record",
  notes="Another user's item returns 404 (audit H1 fixed).", extra_resp={"404": "Item not in the current user's cart"})
o("GET", "api/wishlist", tag="Customer account", summary="Wishlist items", target="owner of record")
o("POST", "api/wishlist/items", tag="Customer account", summary="Add to wishlist", body="WishlistItemCreate", target="owner of record")
o("DELETE", "api/wishlist/items/{productId}", tag="Customer account", summary="Remove from wishlist", target="owner of record")
o("POST", "api/coupon/validate", tag="Customer cart", summary="Check a coupon code against a subtotal", body="CouponValidate",
  target="— (any signed-in user)")
o("GET", "api/orders", tag="Customer orders", summary="Own orders", target="owner of record")
o("POST", "api/orders", tag="Customer orders", summary="Checkout: create one order from the cart (COD)", body="CheckoutRequest",
  target="owner of record", rate="none (spec: 10/min)", audit="order.placed (not yet logged)",
  notes="Locks product/variant rows, checks and decrements stock in one transaction (audit H5 partly fixed; CheckoutStockTest).",
  issues=["Uses the price stored on the cart item, not the current product price.",
          "No payment record created; no Idempotency-Key.", "No order split by vendor (Phase 2)."],
  extra_resp={"422": "Cart empty, INSUFFICIENT_STOCK or validation error"})
o("GET", "api/orders/{order}", tag="Customer orders", summary="Own order detail", target="owner of record",
  issues=["Another user's order returns 403; spec 6.2 wants 404."])
o("POST", "api/orders/{order}/cancel", tag="Customer orders", summary="Cancel own order before shipping; restores stock",
  target="owner of record", audit="order.status_changed (not yet logged)",
  issues=["Another user's order returns 403; spec 6.2 wants 404."], extra_resp={"409": "Order cannot be cancelled"})

# Admin specifics
o("GET", "api/admin/orders", tag="Admin orders", summary="All orders (admin list)", target="order.view_all",
  notes="Lists every customer's orders (audit H4 fixed; AdminOrderListTest).")
o("GET", "api/admin/orders/{order}", tag="Admin orders", summary="Any order detail", target="order.view_all")
o("PUT", "api/admin/orders/{order}", tag="Admin orders", summary="Change order status; cancelling restores stock",
  body="OrderStatusUpdate", target="order.cancel_any (cancel) / order.view_all",
  audit="order.cancelled_by_staff / order.status_changed (not yet logged)",
  issues=["Any status may be set; the state machine in spec 7.2 is not enforced."])
o("GET", "api/admin/reviews", tag="Admin catalogue", summary="Reviews for moderation", target="review.moderate",
  issues=["Calls ReviewController::index(Product) with no product: always returns an empty list, and only approved reviews (audit H3, still open)."])
o("DELETE", "api/admin/reviews/{review}", tag="Admin catalogue", summary="Delete a review", target="review.moderate")
o("POST", "api/admin/products/description-image", tag="Admin catalogue", summary="Upload an image for the rich-text description editor",
  body="DescriptionImageUpload", target="product.update")
o("PUT", "api/admin/users/{user}/roles", tag="Admin access", summary="Replace a user's roles", body="AssignRoles",
  target="role.manage", audit="member.role_changed (not yet logged)",
  issues=["No check that the actor holds the granted permissions; users can change their own roles; last Super Admin not protected (spec 6.4, 12.1)."])
o("POST", "api/admin/settings/logo", tag="Admin settings", summary="Upload site logo", body="LogoUpload", target="settings.manage")
o("DELETE", "api/admin/settings/logo", tag="Admin settings", summary="Remove site logo", target="settings.manage")
o("PUT", "api/admin/settings/seo", tag="Admin settings", summary="Update default SEO meta", body="SeoUpdate", target="settings.manage")

# Steadfast courier (documentation/security/steadfast.md)
o("POST", "api/admin/orders/{order}/shipment/steadfast", tag="Admin courier",
  summary="Book a Steadfast parcel for an order (server-side call to /create_order)",
  body="SteadfastBookRequest", resp="SteadfastBookResponse", target="shipment.book",
  audit="shipment.booked / shipment.booking_failed",
  notes="COD amount = order total unless the order has a paid payment. Moves a pending/confirmed order to processing. "
        "Courier keys never appear in the response.",
  extra_resp={"409": "ORDER_NOT_BOOKABLE or SHIPMENT_ALREADY_BOOKED", "422": "SHIPPING_ADDRESS_MISSING",
              "502": "COURIER_BOOKING_FAILED (Steadfast error, not configured, or production key outside production)"},
  issues=["Books per order; Phase 2 moves this to one shipment per vendor order (module 13)."])
o("GET", "api/admin/courier/steadfast", tag="Admin courier", summary="Steadfast connection status with masked keys",
  resp="CourierSettings", target="settings.manage",
  notes="Keys and webhook token are shown masked only (last 4 chars). api_key_fingerprint is a 16-char SHA-256 prefix "
        "to copy into staging's STEADFAST_PRODUCTION_KEY_FINGERPRINT.")
o("GET", "api/admin/courier/steadfast/reconciliation", tag="Admin courier",
  summary="COD reconciliation: expected vs collected cash per delivered shipment",
  resp="CodReconciliationReport", target="courier.reconcile",
  notes="Query: from, to (Y-m-d, Asia/Dhaka days), only_problems (bool). Amounts are decimal strings computed in paisa.",
  issues=["Steadfast /payments remittance batches are not imported yet; matching uses the cod_amount reported in the delivered webhook."])
o("GET", "api/admin/notifications", tag="Admin notifications", summary="Signed-in admin's notifications (COD mismatch alerts)",
  target="— (own notifications)", notes="Query: unread=1. Paginated, unread first.")
o("POST", "api/admin/notifications/{notification}/read", tag="Admin notifications", summary="Mark one of your notifications read",
  target="— (own notifications)", extra_resp={"404": "Not one of your notifications"})
o("GET", "api/admin/audit-logs", tag="Admin access", summary="Read the append-only audit log",
  target="audit.view", notes="Query: event (exact or prefix like shipment.*), target_type, target_id, per_page (max 100). "
  "There are no update or delete routes (spec 12.2).")
o("POST", "api/v1/webhooks/courier/steadfast", tag="Webhooks", summary="Steadfast parcel status callback",
  body="SteadfastWebhook", resp="SteadfastWebhookResult", target="signature (bearer token)",
  security=[{"steadfastBearer": []}],
  rate="STEADFAST_WEBHOOK_RATE_LIMIT per minute per IP (default 120), counted before the token check",
  audit="shipment.status_changed / shipment.delivered / shipment.cancelled",
  scope="consignments booked by the platform",
  notes="Order of checks: HTTPS (403 HTTPS_REQUIRED) -> rate limit (429 RATE_LIMITED) -> Authorization: Bearer "
        "STEADFAST_WEBHOOK_TOKEN (401 WEBHOOK_TOKEN_INVALID; 503 WEBHOOK_NOT_CONFIGURED if unset) -> validation (422) -> "
        "duplicate check (unique courier+consignment_id+status) -> delivered/partial_delivered re-checked with "
        "GET /status_by_cid (409 DELIVERY_NOT_CONFIRMED, 503 COURIER_UNAVAILABLE). Header format taken from the "
        "steadfast-laravel-package source; confirm on the first live callback.",
  extra_resp={"401": "WEBHOOK_TOKEN_INVALID", "403": "HTTPS_REQUIRED", "409": "DELIVERY_NOT_CONFIRMED",
              "429": "RATE_LIMITED", "503": "WEBHOOK_NOT_CONFIGURED or COURIER_UNAVAILABLE"})

# ---------------------------------------------------------------- build
ACTION_SUMMARY = {"index": "List {r}", "store": "Create {r}", "show": "Show {r}", "update": "Update {r}",
                  "destroy": "Delete {r}"}

def resource_name(uri):
    parts = [p for p in uri.split("/") if p and not p.startswith("{")]
    return parts[-1].replace("-", " ")

def path_params(uri):
    return re.findall(r"\{([^}:]+)(?::[^}]+)?\}", uri)

paths = {}
count = 0
for r in routes:
    uri = r["uri"]
    clean_uri = re.sub(r"\{([^}:]+):[^}]+\}", r"{\1}", uri)
    ctrl_action = (r["action"] or "").split(BS)[-1]
    ctrl, _, action = ctrl_action.partition("@")
    mws = [m.split(BS)[-1] for m in (r["middleware"] or [])]
    auth = "Authenticate:sanctum" in mws
    admin = "AdminMiddleware" in mws
    methods = [m for m in r["method"].split("|") if m != "HEAD"]
    if methods == ["PUT", "PATCH"]:
        methods = ["PUT"]  # documented once; PATCH is an alias
    for method in methods:
        count += 1
        meta = dict(O.get((method, clean_uri), {}))
        cmeta = CTRL.get(ctrl, (None, None, None, None))
        tag = meta.get("tag") or (cmeta[0] if admin else "Storefront")
        summary = meta.get("summary") or ACTION_SUMMARY.get(action, action).format(r=resource_name(clean_uri))
        op = {"tags": [tag], "summary": summary,
              "operationId": re.sub(r"[^a-zA-Z0-9]+", "_", f"{method.lower()}_{clean_uri[4:]}").strip("_")}
        desc = [f"Controller: `{ctrl_action}`. Middleware: `{', '.join(mws)}`."]
        if "PATCH" in r["method"]:
            desc.append("`PATCH` is accepted as an alias of `PUT`.")
        if meta.get("notes"):
            desc.append(meta["notes"])
        op["description"] = "\n\n".join(desc)
        params = [{"name": p, "in": "path", "required": True, "schema": STR if p in ("product", "category") and method == "GET" and not admin else INT}
                  for p in path_params(clean_uri)]
        if params:
            op["parameters"] = params
        body = meta.get("body")
        if body is None and method in ("POST", "PUT") and admin and cmeta[1] and action in ("store", "update"):
            body = cmeta[1]
        if body:
            binary = any(v.get("format") == "binary" or v.get("items", {}).get("format") == "binary"
                         for v in schemas[body]["properties"].values())
            ctype = "multipart/form-data" if binary else "application/json"
            op["requestBody"] = {"required": True, "content": {ctype: {"schema": ref(body)}}}
        ok = "201" if action == "store" or (method == "POST" and clean_uri in ("api/orders", "api/account/register", "api/cart/items")) else "200"
        responses = {ok: {"description": "Success",
                          "content": {"application/json": {"schema": ref(meta.get("resp", "Message")) if meta.get("resp") or method != "GET" else ({"$ref": "#/components/schemas/Paginated"} if action in ("index", "adminIndex") else {"type": "object"})}}}}
        if auth:
            responses["401"] = {"$ref": "#/components/responses/Unauthenticated"}
        if admin:
            responses["403"] = {"$ref": "#/components/responses/NotAdmin"}
            responses["419"] = {"$ref": "#/components/responses/SessionExpired"}
        if body:
            responses.setdefault("422", {"$ref": "#/components/responses/Validation"})
        for code, d in (meta.get("extra_resp") or {}).items():
            responses[code] = {"description": d}
        op["responses"] = dict(sorted(responses.items()))
        webhook_token = "VerifySteadfastWebhookToken" in mws
        if "security" in meta:
            op["security"] = meta["security"]
        elif auth:
            op["security"] = [{"sanctumSession": [], "xsrf": []}]
        else:
            op["security"] = [] if method == "GET" else [{"xsrf": []}]
        op["x-status"] = "implemented"
        op["x-permission"] = "admin role (AdminMiddleware); no permission check" if admin else (
            "signed-in user" if auth else ("HTTPS + bearer token (VerifySteadfastWebhookToken)" if webhook_token else "public"))
        op["x-target-permission"] = meta.get("target") or (cmeta[2] if admin else ("owner of record" if auth else "— (public)"))
        op["x-tenant-scope"] = meta.get("scope") or ("none yet (single shop); vendor scope added in Phase 2" if admin else (
            "current user's own records" if auth else "none"))
        op["x-rate-limit"] = meta.get("rate", "none (spec: 120/min per user)")
        op["x-audit-event"] = meta.get("audit") or (f"{cmeta[3]}.{ {'store':'created','update':'updated','destroy':'deleted'}.get(action, '')} (not yet logged)".replace(". (", " (") if admin and cmeta[3] and action in ("store", "update", "destroy") else "—")
        if meta.get("issues"):
            op["x-known-issues"] = meta["issues"]
        paths.setdefault("/" + clean_uri, {})[method.lower()] = op

# Sanctum CSRF route (outside /api)
paths["/sanctum/csrf-cookie"] = {"get": {
    "tags": ["Admin auth"], "summary": "Get the XSRF-TOKEN cookie before any state-changing request",
    "operationId": "sanctum.csrfCookie", "security": [],
    "description": "Sets `XSRF-TOKEN` and the session cookie. The SPA sends the token back as `X-XSRF-TOKEN`.",
    "responses": {"204": {"description": "Cookies set"}}, "x-status": "implemented",
    "x-permission": "public", "x-target-permission": "— (public)", "x-tenant-scope": "none",
    "x-rate-limit": "none", "x-audit-event": "—"}}

# ---------------------------------------------------- planned v1 (spec 10.3)
planned = [
    ("Auth", "post", "/auth/login", "Login by email or BD mobile + password", "—", "5/min per account+IP", "auth.login_succeeded / auth.login_failed"),
    ("Auth", "post", "/auth/logout", "Log out", "—", "120/min", "auth.logout"),
    ("Auth", "post", "/auth/register", "Register a customer", "—", "5/min per IP", "—"),
    ("Auth", "post", "/auth/otp/send", "Send a phone OTP", "—", "3 per 10 min per phone", "—"),
    ("Auth", "post", "/auth/otp/verify", "Verify a phone OTP and sign in", "—", "5/min per phone", "auth.login_succeeded"),
    ("Auth", "get", "/auth/me", "Current user with roles, memberships and permissions", "—", "120/min", "—"),
    ("Public catalogue", "get", "/public/products", "Approved products of active vendors", "—", "120/min per IP", "—"),
    ("Public catalogue", "get", "/public/products/{ulid}", "Product detail", "—", "120/min per IP", "—"),
    ("Public catalogue", "get", "/public/categories", "Category tree", "—", "120/min per IP", "—"),
    ("Public catalogue", "get", "/public/vendors/{slug}", "Vendor store page", "—", "120/min per IP", "—"),
    ("Public catalogue", "get", "/public/search", "FULLTEXT product search (ADR-10)", "—", "60/min per IP", "—"),
    ("Public catalogue", "get", "/public/health", "Health check for the uptime monitor (no secrets or versions)", "—", "60/min per IP", "—"),
    ("Account", "get", "/account/cart/items", "Cart items", "owner of record", "120/min", "—"),
    ("Account", "post", "/account/cart/items", "Add cart item", "owner of record", "120/min", "—"),
    ("Account", "patch", "/account/cart/items/{id}", "Change quantity", "owner of record", "120/min", "—"),
    ("Account", "delete", "/account/cart/items/{id}", "Remove cart item", "owner of record", "120/min", "—"),
    ("Account", "post", "/account/checkout", "Checkout with order split; requires Idempotency-Key", "owner of record", "10/min", "order.placed"),
    ("Account", "get", "/account/orders", "Own parent orders", "owner of record", "120/min", "—"),
    ("Account", "post", "/account/orders/{ulid}/cancel", "Cancel before handover", "owner of record", "120/min", "order.status_changed"),
    ("Account", "post", "/account/returns", "Request a return per item", "owner of record", "120/min", "return.requested"),
    ("Account", "patch", "/account/preferences", "Theme and language preference", "owner of record", "120/min", "—"),
    ("Vendor", "get", "/vendor/products", "Own products", "product.view", "120/min", "—"),
    ("Vendor", "post", "/vendor/products", "Create draft product", "product.create", "120/min", "product.created"),
    ("Vendor", "patch", "/vendor/products/{id}", "Edit product (creates a pending revision when approved)", "product.update", "120/min", "product.updated"),
    ("Vendor", "delete", "/vendor/products/{id}", "Soft-delete product", "product.delete", "120/min", "product.deleted"),
    ("Vendor", "post", "/vendor/products/{id}/submit", "Submit for approval", "product.submit", "120/min", "product.submitted"),
    ("Vendor", "post", "/vendor/products/{id}/stock", "Post a stock adjustment", "inventory.adjust", "120/min", "inventory.adjusted"),
    ("Vendor", "get", "/vendor/orders", "Own vendor orders", "order.view", "120/min", "—"),
    ("Vendor", "post", "/vendor/orders/{ulid}/accept", "Accept order", "order.accept", "120/min", "order.status_changed"),
    ("Vendor", "post", "/vendor/orders/{ulid}/ready", "Packed; book Steadfast parcel", "order.accept + shipment.book", "120/min", "shipment.booked"),
    ("Vendor", "post", "/vendor/orders/{ulid}/cancel", "Cancel before handover", "order.cancel", "120/min", "order.status_changed"),
    ("Vendor", "get", "/vendor/shipments", "Own shipments", "order.view", "120/min", "—"),
    ("Vendor", "get", "/vendor/ledger", "Own ledger entries", "finance.view", "120/min", "—"),
    ("Vendor", "get", "/vendor/balance", "Pending / available / paid", "finance.view", "120/min", "—"),
    ("Vendor", "post", "/vendor/payout-requests", "Request payout; requires Idempotency-Key", "payout.request", "120/min", "payout.requested"),
    ("Vendor", "get", "/vendor/members", "Team members", "team.manage", "120/min", "—"),
    ("Vendor", "post", "/vendor/invitations", "Invite a member", "team.manage", "5/min per user", "invitation.created"),
    ("Vendor", "get", "/vendor/roles", "Vendor roles", "role.manage", "120/min", "—"),
    ("Platform", "get", "/platform/vendors", "Vendors and applications", "vendor.view", "120/min", "—"),
    ("Platform", "post", "/platform/vendors/{id}/status", "Change vendor status with reason (re-confirm)", "vendor.manage_status", "120/min", "vendor.status_changed"),
    ("Platform", "get", "/platform/categories", "Categories", "catalog.category.manage", "120/min", "—"),
    ("Platform", "get", "/platform/brands", "Brands", "catalog.brand.manage", "120/min", "—"),
    ("Platform", "get", "/platform/product-approvals", "Approval queue", "product.approve", "120/min", "—"),
    ("Platform", "post", "/platform/product-approvals/{id}", "Approve or reject", "product.approve", "120/min", "product.approved / product.rejected"),
    ("Platform", "get", "/platform/commission-rules", "Commission rules", "finance.view", "120/min", "—"),
    ("Platform", "post", "/platform/commission-rules", "Create commission rule (re-confirm)", "finance.commission.manage", "120/min", "commission_rule.changed"),
    ("Platform", "post", "/platform/payout-requests/{id}/approve", "Approve payout (re-confirm, not own)", "payout.approve", "120/min", "payout.approved"),
    ("Platform", "post", "/platform/payouts", "Record transfer reference; requires Idempotency-Key", "payout.record", "120/min", "payout.recorded"),
    ("Platform", "get", "/platform/reconciliation", "COD remittance vs delivered shipments", "courier.reconcile", "120/min", "—"),
    ("Platform", "get", "/platform/roles", "Platform roles", "role.manage", "120/min", "—"),
    ("Platform", "get", "/platform/members", "Platform staff", "team.manage", "120/min", "—"),
    ("Platform", "get", "/platform/audit-logs", "Audit events", "audit.view", "120/min", "—"),
]
# POST /api/v1/webhooks/courier/steadfast is implemented (generated from the route list above).
for tag, method, p, summary, perm, rate, audit in planned:
    full = "/api/v1" + p
    scope = ("current vendor (TenantContext); other vendors' records return 404" if p.startswith("/vendor")
             else "all vendors" if p.startswith("/platform")
             else "current user's own records" if p.startswith("/account")
             else "none")
    sec = ([] if p.startswith(("/public", "/webhooks")) or p in ("/auth/login", "/auth/register", "/auth/otp/send", "/auth/otp/verify")
           else [{"sanctumSession": [], "xsrf": []}])
    op = {"tags": [f"v1 — {tag}"], "summary": summary,
          "operationId": "v1." + re.sub(r"[^a-zA-Z0-9]+", "_", f"{method}{p}").strip("_"),
          "security": sec,
          "responses": {"200": {"description": "Planned — see the module page"}},
          "x-status": "planned", "x-permission": perm, "x-target-permission": perm,
          "x-tenant-scope": scope, "x-rate-limit": rate, "x-audit-event": audit,
          "x-tests": "spec 16.2 for vendor endpoints (401 guest, 404 other vendor, 403 no permission, body vendor_id ignored)"
                     if p.startswith("/vendor") else "module page 'Required tests'"}
    for pp in path_params(p):
        op.setdefault("parameters", []).append({"name": pp, "in": "path", "required": True, "schema": STR})
    paths.setdefault(full, {})[method] = op

impl_tags = sorted({op["tags"][0] for pth in paths.values() for op in pth.values() if op.get("x-status") == "implemented"})
v1_tags = []
for t in [p[0] for p in planned]:
    if f"v1 — {t}" not in v1_tags:
        v1_tags.append(f"v1 — {t}")

spec = {
    "openapi": "3.1.0",
    "info": {
        "title": "BazarBariOnline API",
        "version": "0.2.0-steadfast",
        "description": (
            "Generated from `php artisan route:list --json` on 2026-11-19 plus the endpoint inventory in spec section 10.3.\n\n"
            "Two sets of paths live in this file:\n\n"
            "* `/api/...` — **implemented today** (`x-status: implemented`): "
            f"{count} operations from {len(routes)} routes in the single-shop code.\n"
            "* `/api/v1/...` — **planned MVP API** (`x-status: planned`), the target from spec 10.3. Each one moves to implemented "
            "as it is built (Definition of Done, spec 16.4). The first one already built is the Steadfast webhook "
            "`POST /api/v1/webhooks/courier/steadfast` (`x-status: implemented`).\n\n"
            "Extension fields on every operation: `x-permission` (what the code checks now), `x-target-permission` "
            "(from `documentation/permissions.md`), `x-tenant-scope`, `x-rate-limit`, `x-audit-event`, `x-known-issues`.\n\n"
            "**Authentication:** Sanctum SPA cookies (ADR-04). Call `GET /sanctum/csrf-cookie` first, then send "
            "`X-XSRF-TOKEN` and cookies from an origin listed in `SANCTUM_STATEFUL_DOMAINS` (`localhost:3000` locally). "
            "In the browser, Next.js rewrites `/api/*` and `/sanctum/*` to Laravel, so requests are same-origin.\n\n"
            "**Responses today** do not yet follow the `{data, meta}` envelope of spec 10.2: most return `{success, message, ...}`, "
            "Laravel paginator JSON or a bare model. The v1 API adopts the envelope and stable `code` values."
        ),
    },
    "servers": [
        {"url": "http://localhost:8000", "description": "Local Laravel (`php artisan serve`)"},
        {"url": "https://api.shamimwebsolutions.com", "description": "Production API (domain may change, spec section 1)"},
    ],
    "tags": [{"name": t} for t in impl_tags] + [{"name": t, "description": "Planned (spec 10.3)"} for t in v1_tags],
    "paths": dict(sorted(paths.items(), key=lambda kv: (kv[0].startswith("/api/v1"), kv[0]))),
    "components": {
        "securitySchemes": {
            "sanctumSession": {"type": "apiKey", "in": "cookie", "name": "laravel_session",
                               "description": "Session cookie set by login (cookie name follows SESSION_COOKIE / APP_NAME)."},
            "xsrf": {"type": "apiKey", "in": "header", "name": "X-XSRF-TOKEN",
                     "description": "URL-decoded value of the XSRF-TOKEN cookie from /sanctum/csrf-cookie."},
            "steadfastBearer": {"type": "http", "scheme": "bearer",
                                "description": "STEADFAST_WEBHOOK_TOKEN, the same value entered in the Steadfast portal "
                                               "(documentation/security/steadfast.md)."},
        },
        "responses": {
            "Unauthenticated": {"description": "Not signed in", "content": {"application/json": {"schema": ref("Message")}}},
            "NotAdmin": {"description": "Signed in but not an admin ('Unauthorized. Admin access required.')",
                         "content": {"application/json": {"schema": ref("Message")}}},
            "SessionExpired": {"description": "Admin idle for more than ADMIN_IDLE_TIMEOUT_MINUTES (15), or CSRF token mismatch",
                               "content": {"application/json": {"schema": ref("Message")}}},
            "Validation": {"description": "Validation failed", "content": {"application/json": {"schema": ref("ValidationError")}}},
        },
        "schemas": schemas,
    },
}

class D(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("# BazarBariOnline OpenAPI — generated; regenerate after route changes (see documentation/README.md)\n")
    yaml.dump(spec, f, Dumper=D, sort_keys=False, allow_unicode=True, width=120)

print("operations implemented:", count, "routes:", len(routes), "planned:", len(planned), "paths:", len(paths))
