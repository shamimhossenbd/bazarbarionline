# MASTER TASK: BUILD A PROFESSIONAL MULTI-TENANT MARKETPLACE, RETAIL POS & CENTRALIZED BUSINESS MANAGEMENT SYSTEM

**Project:** BazarBariOnline

**Backend:** Laravel 13, PHP 8.4, MySQL  
**Frontend:** Next.js App Router, TypeScript, Bootstrap 5  
**Architecture:** Multi-Tenant Marketplace with Vendor Online Sales and Platform-Managed POS  
**Market:** Bangladesh  
**Default Currency:** BDT  
**Default Timezone:** Asia/Dhaka

---

# 1. CORE BUSINESS ARCHITECTURE

Build a professional Multi-Tenant Marketplace and Retail Management Platform.

The platform must support:

1. Multi-Tenant Vendor Management
2. Vendor Online Sales Only
3. Vendor Product Submission and Admin Approval
4. Dynamic Vendor-wise Commission Management
5. Platform Admin POS
6. Centralized Admin Business Dashboard
7. Product and Variant Management
8. Platform-owned and Vendor-owned Products
9. Ownership-aware Inventory Management
10. SKU, Barcode and QR Management
11. Purchasing and Supplier Management
12. Centralized Accounts and Financial Management
13. Vendor Staff Management
14. Dynamic Roles and Permissions
15. Audit Logs
16. Marketplace Order Management
17. Vendor-wise Sales Analytics
18. Product-wise Sales Analytics
19. Steadfast Courier API Integration
20. Daily, Weekly, Monthly and Yearly Reports

## Critical Business Decisions

### A. No Vendor Subscription System

The platform must NOT contain a Vendor Subscription System.

Completely exclude:

- Subscription Plans
- Vendor Subscription Fees
- Subscription Trials
- Subscription Renewals
- Subscription Expiry
- Subscription Billing
- Subscription-based Product Limits
- Subscription-based Staff Limits
- Subscription-based Module Access

Do not implement or retain a new subscription workflow.

Inspect any existing subscription implementation and report its current status and dependencies before proposing changes. Do not delete existing data or migrations without explicit approval.

Vendor access and feature permissions must be controlled through the approved authorization system, not subscription plans.

### B. Vendor Sales

- Vendors can sell products ONLY through the online marketplace.
- Vendors must NOT have POS functionality.
- Vendor Dashboard must not contain POS menus, POS sales, registers, cashier sessions or POS reports.
- Vendor Staff must never receive Platform POS permissions.
- Vendor online sales must remain separate from Platform POS sales.
- Vendors can manage their own products, stock, online orders and permitted business operations.

### C. Platform POS

POS is a separate Platform Admin module.

- Only authorized Platform Admin users can access POS.
- POS must never appear in Vendor Dashboard.
- Platform POS may sell only Platform-owned products.
- Platform POS must never sell Vendor-owned products.
- POS must have separate sales, payments, registers, cashier sessions and reports.
- Platform POS sales must not generate Vendor commission or Vendor earnings.
- Platform POS must not create Marketplace Vendor Orders.

Do not create Vendor POS routes, APIs, pages, permissions, database relationships or navigation items.

If existing Vendor POS implementation exists, inspect it and report its status before proposing removal. Do not delete existing data or migrations without explicit approval.

---

# 2. FIRST: INSPECT THE EXISTING PROJECT

Before implementation, inspect:

- Existing Laravel and Next.js architecture.
- Marketplace Vendor and Customer architecture.
- Existing Admin/Vendor/Customer authentication.
- Existing product, variant, SKU, barcode and inventory tables.
- Existing cart, checkout and order functionality.
- Existing POS functionality and ownership scope.
- Existing product approval workflow, if any.
- Existing Vendor commission and earnings logic.
- Existing payout and refund logic.
- Existing dynamic RBAC implementation.
- Existing stock movement service.
- Existing accounting and financial tables.
- Existing courier integration and Steadfast configuration.
- Existing database migrations and automated tests.
- Existing Admin and Vendor navigation/sidebar structure.
- Existing QA and local database setup.

Do not assume a feature is complete merely because a route, page, migration or database table exists.

## Required Initial Report

Before major schema changes, provide:

1. Current architecture summary.
2. Existing Vendor/Tenant relationship.
3. Existing Product Ownership rules.
4. Existing Product Approval workflow.
5. Existing Inventory architecture.
6. Existing POS implementation and ownership.
7. Existing Commission and Vendor Earnings implementation.
8. Existing Accounts and Financial Management implementation.
9. Existing RBAC implementation.
10. Existing subscription implementation and dependencies.
11. Existing Courier integration status.
12. Existing Admin Dashboard structure.
13. Missing functionality.
14. Data migration risks.
15. Proposed implementation phases.

Do not make major schema changes before completing this inspection.

---

# 3. MULTI-TENANT ARCHITECTURE

Each Vendor represents a separate business tenant.

Requirements:

- Each Vendor must have isolated business data.
- Vendor users must only access their own Vendor data.
- Tenant identity must be resolved server-side from authenticated membership.
- Never trust browser-submitted vendor_id or tenant_id.
- Super Admin manages the entire platform.
- Vendor Owner manages their own Vendor business.
- Vendor Staff receive permissions assigned by their Vendor Owner.
- Use the existing shared MySQL database.
- Do not introduce separate physical databases without explicit approval.

## Authorization Domains

Maintain separate authorization domains:

1. Platform Super Admin
2. Platform Admin
3. Vendor Owner
4. Vendor Staff
5. Customer

A Vendor must never grant itself Platform Admin or Super Admin permissions.

Platform Admin and Vendor authorization must remain strictly separated.

---

# 4. PRODUCT OWNERSHIP AND PRODUCT APPROVAL SYSTEM

The platform must distinguish:

- Platform-owned Products
- Vendor-owned Products

Every product must have an explicit and verifiable ownership relationship.

## 4.1 Vendor Product Creation

Vendor can:

- Create products.
- Create product variants.
- Upload product images.
- Set product descriptions.
- Set product pricing.
- Set SKU and barcode.
- Manage product stock.
- Edit their own products according to permissions.
- View their own product approval status.

When a Vendor creates a product:

- The product must be saved with the authenticated Vendor's ownership.
- The initial approval status must be Pending.
- It must not immediately appear on the public Landing Page.
- It must not become publicly purchasable before approval.
- The product must appear in the Admin Product Approval Queue.

## 4.2 Admin Product Approval Dashboard

Create a dedicated Product Approval section in the Platform Admin Dashboard.

Admin must be able to see:

- Product Name
- Product Image
- Product SKU
- Product Category
- Product Price
- Product Stock
- Product Creation Date
- Product Approval Status
- Vendor Name
- Vendor ID
- Vendor Contact Information where authorized
- Product Created By
- Last Updated By

Admin must be able to:

- View submitted products.
- Approve products.
- Reject products with a reason.
- Request product changes where supported.
- Suspend previously approved products.
- Reactivate products where authorized.
- Review product modification history.

Every product approval or rejection must record:

- Admin Actor ID
- Action
- Timestamp
- Previous Status
- New Status
- Rejection or review reason where applicable

## 4.3 Product Publication Rules

Use explicit product statuses, such as:

- draft
- pending
- approved
- rejected
- suspended
- inactive

The exact state machine must be based on the existing project architecture.

Only products that satisfy all publication conditions may appear publicly:

- Approved by authorized Admin.
- Active.
- Valid price.
- Valid ownership.
- Publicly available.
- Not suspended.
- Not otherwise restricted.

Approved Vendor products may appear on:

- Public Landing Page sections where configured.
- Marketplace product listing.
- Category pages.
- Product search.
- Product detail pages.

Pending, rejected, suspended or inactive products must not appear in public product listings or be purchasable.

Backend product queries must enforce approval status. Hiding products only in the frontend is not sufficient.

## 4.4 Product Edit and Re-Approval

Inspect the existing business rules and implement a controlled approval workflow.

At minimum:

- A Vendor must not be able to bypass approval by changing product status.
- Sensitive changes such as ownership, pricing, category, product identity or other Admin-defined restricted fields must follow an explicit approval policy.
- If an approved product requires re-approval after a sensitive edit, its public availability must follow the configured policy.
- Record all product changes and approval history.

Do not silently overwrite approval history.

## 4.5 Platform Products

Platform Admin manages Platform-owned products separately.

Platform-owned products must not be treated as Vendor-owned products.

Always validate product ownership during product lookup, editing, stock changes, sales and reporting.

Duplicate product names are allowed.

SKU/barcode uniqueness must follow the approved ownership scope.

---

# 5. DYNAMIC VENDOR COMMISSION MANAGEMENT

This is a core business requirement.

There must be NO subscription-based commission rates.

Commission must be configured individually and dynamically by Platform Admin.

## 5.1 Admin Commission Management

Create a dedicated Admin module:

**Vendor Commission Management**

Admin must be able to:

1. View all Vendors.
2. Search and filter Vendors.
3. Select a specific Vendor.
4. View the Vendor's current commission percentage.
5. Set a new commission percentage.
6. Increase or decrease the percentage at any time.
7. Activate or deactivate commission collection where authorized.
8. View commission change history.
9. View the Admin who changed the commission.
10. View when the commission was changed.

Example only:

| Vendor | Commission Rate |
|---|---:|
| ABC Electronics | 5% |
| Fashion House | 8% |
| Smart Gadget | 10% |

These are demonstration values only. Do not hardcode them.

The actual rate must be stored in the database and managed dynamically through Admin Dashboard.

## 5.2 Commission Rules

- Each Vendor may have a different commission percentage.
- Admin chooses which Vendor receives which commission rate.
- Changing one Vendor's rate must not affect other Vendors.
- Commission must not be automatically inherited from a subscription plan.
- Vendor must not be allowed to change its own commission.
- Only authorized Platform Admin users can change commission.
- Commission changes must be audited.
- Validate the commission percentage on the backend.
- Define an explicit permitted range, normally 0–100%.
- A zero rate must be handled as an intentional zero commission, not as a missing configuration.

## 5.3 Commission Snapshot

This is mandatory for accounting accuracy.

When a qualifying Marketplace sale is finalized:

- Read the Vendor's effective commission rate.
- Calculate the commission amount.
- Store the effective commission percentage on the relevant order item or Vendor order financial record.
- Store the commission amount.
- Store the gross eligible sale amount.
- Store the applicable discount/refund adjustments.
- Store the Vendor net earnings.
- Store the commission calculation timestamp.

Historical sales must never be recalculated using the Vendor's latest commission rate.

Example:

A Vendor has a 5% commission rate when an order is finalized.

Later, Admin changes the rate to 8%.

The historical order must continue using 5%.

Only qualifying new sales after the new rate becomes effective should use 8%.

## 5.4 Commission Calculation Policy

Implement a clearly documented calculation policy.

The policy must define:

- Commission calculation base.
- Treatment of item discounts.
- Treatment of platform-funded coupons.
- Treatment of Vendor-funded discounts.
- Treatment of shipping charges.
- Treatment of taxes where applicable.
- Treatment of refunds and returns.
- Treatment of partial refunds.
- Treatment of cancelled orders.
- Treatment of failed payments.

Do not calculate commission on shipping charges unless the approved business policy explicitly requires it.

Commission should normally be calculated on the eligible net merchandise value after applicable item-level discounts.

Do not treat an unpaid or failed order as earned Vendor revenue.

Use the existing payment and order lifecycle. Define the exact qualifying financial event before implementation.

## 5.5 Commission Reversal and Refunds

- Cancelled orders must not create earned commission.
- Refunds must reverse or adjust the corresponding Vendor earnings and commission according to the actual refunded amount.
- Partial refunds must be calculated proportionally or according to the refunded order items.
- Prevent duplicate commission reversals.
- Preserve the original commission snapshot.
- Record all adjustments in the financial ledger.

## 5.6 Vendor Commission Visibility

Vendor Dashboard must display:

- Current Commission Rate.
- Gross Eligible Sales.
- Total Commission Deducted.
- Refund/Commission Adjustments.
- Net Vendor Earnings.
- Pending Earnings where applicable.
- Paid Out Amount.
- Remaining Payable Amount.

Vendor must not be allowed to modify the commission rate.

---

# 6. VENDOR ONLINE SALES

Vendor Sales are ONLINE ONLY.

Vendor Dashboard must include:

- Dashboard
- Products
- Product Approval Status
- Online Orders
- Order Details
- Order Status Management
- Online Sales Overview
- Product-wise Sales Reports
- Gross Online Revenue
- Commission Details
- Vendor Earnings
- Payouts
- Returns and Refunds
- Customer Information related to Vendor Orders
- Inventory
- Stock Movement
- Staff
- Roles and Permissions
- Settings

Vendor Dashboard must NOT include:

- POS Terminal
- POS Sales
- POS Register
- Cashier Session
- POS Payment Management
- POS Sales Reports
- POS Returns
- POS Settings
- POS Permissions
- Platform-wide Courier API Settings

Do not expose POS APIs to Vendor users.

Do not mix Platform POS sales into Vendor Online Sales.

## Online Order Rules

- Use the existing Marketplace checkout.
- Every order item must be associated with its actual Vendor.
- Vendor must only access their own order items and permitted order information.
- Existing order status and cancellation rules must be preserved.
- Stock changes must use the centralized inventory service.
- Commission must follow the Vendor-specific commission snapshot.
- Vendor earnings and payout calculations must remain consistent.
- Only eligible finalized sales should appear as recognized Vendor sales.
- Pending, unpaid, cancelled and failed orders must not be incorrectly counted as completed sales.

---

# 7. CENTRALIZED PLATFORM ADMIN DASHBOARD

This is a major requirement.

The Platform Admin Dashboard must provide a centralized business management experience.

Online Sales, Platform POS Sales, Inventory Management and Accounts Management must be accessible from one integrated Admin Dashboard.

Do not build these as disconnected systems with unrelated financial calculations.

They must use consistent data, reporting periods, ownership scopes and accounting rules.

## 7.1 Admin Dashboard Overview

Create a professional responsive Admin Dashboard with the following summary cards:

### Marketplace Online Sales

- Total Online Orders
- Total Online Products Sold
- Gross Online Sales
- Net Online Sales
- Total Vendor Commission
- Total Vendor Earnings
- Pending Vendor Earnings
- Completed Online Orders
- Cancelled Orders
- Refunded Orders

### Platform POS Sales

- Total POS Transactions
- Total POS Products Sold
- Gross POS Sales
- Net POS Sales
- POS Discounts
- POS Refunds
- POS Cash Sales
- POS Digital Payments
- Cash Register Status

### Inventory Overview

- Total Platform Products
- Total Vendor Products
- Total Stock Quantity
- Platform Stock Value
- Vendor Stock Overview
- Low Stock Products
- Out of Stock Products
- Pending Purchase Receipts
- Recent Stock Movements

### Accounts Overview

- Total Income
- Total Expenses
- Net Operating Result
- Cash Balance
- Bank Balance
- Vendor Payables
- Supplier Payables
- Pending Payouts
- Recent Financial Transactions

### Vendor Overview

- Total Vendors
- Active Vendors
- Inactive Vendors
- Pending Vendor Approvals
- Pending Product Approvals
- Top Selling Vendors
- Vendors with Highest Commission

All figures must come from actual database records.

Do not use hardcoded demonstration values in production components.

## 7.2 Centralized Admin Navigation

Organize the Admin Sidebar into logical sections.

### Main Dashboard

- Business Overview
- Sales Analytics

### Marketplace Management

- Online Orders
- Order Details
- Product Approvals
- Products
- Categories
- Vendors
- Customers

### Sales Management

- Marketplace Online Sales
- Platform POS Sales
- Vendor-wise Sales
- Product-wise Sales
- Commission Management
- Vendor Earnings
- Payout Management
- Returns and Refunds

### Platform POS

- POS Dashboard
- POS Terminal
- POS Sales
- POS Products
- POS Payments
- Cash Registers
- Cashier Sessions
- POS Returns
- POS Reports
- POS Settings

### Inventory Management

- Inventory Overview
- Platform Inventory
- Vendor Inventory Overview
- Stock Movements
- Low Stock Alerts
- Purchase Management
- Suppliers
- Purchase Receiving
- Purchase Returns
- Stock Adjustments
- Inventory Valuation

### Accounts Management

- Accounts Dashboard
- Chart of Accounts
- Income
- Expenses
- Cash Accounts
- Bank Accounts
- Financial Transactions
- Vendor Commission Ledger
- Vendor Payables
- Vendor Payouts
- Supplier Payables
- Payment Records
- Refund Records
- Profit and Loss
- Cash Flow
- Financial Reconciliation

### Courier Management

- Steadfast Courier
- Shipments
- Tracking
- Delivery Reports
- Failed Deliveries
- Return Shipments
- API Settings
- Webhook Logs
- API Activity Logs

### User and Security Management

- Platform Admin Users
- Vendor Staff Overview
- Roles and Permissions
- Login Activity
- Audit Logs

### Reports

- Online Sales Reports
- POS Sales Reports
- Vendor Sales Reports
- Product Sales Reports
- Commission Reports
- Inventory Reports
- Accounts Reports
- Courier Reports
- Staff Activity Reports

All navigation items must be permission-aware.

Backend authorization remains mandatory.

## 7.3 Unified Dashboard, Separate Business Ledgers

The Admin Dashboard must combine the overview of business operations without mixing the underlying transactions.

Use clearly separated channels:

- marketplace_online
- platform_pos

Admin may see a combined high-level business overview, but each figure must also be traceable to its original channel.

Never double-count an order, sale, refund, commission or stock movement.

Marketplace Online Sales and Platform POS Sales must remain distinguishable in all reports.

---

# 8. VENDOR-WISE SALES ANALYTICS

Create a dedicated Admin module:

**Vendor Sales & Performance**

Admin must be able to see exactly how much each Vendor sells.

## 8.1 Vendor Sales List

Provide a searchable, filterable table.

Required columns:

- Vendor Name
- Vendor ID
- Total Orders
- Total Products Sold
- Gross Sales
- Discounts
- Refunds
- Net Sales
- Commission Rate
- Commission Amount
- Vendor Net Earnings
- Pending Earnings
- Paid Out
- Remaining Payable
- Last Sale Date
- Vendor Status

Admin must be able to search and filter by:

- Vendor
- Date Range
- Sales Status
- Product Category
- Product
- Commission Rate
- Payment Status

## 8.2 Vendor Detail Sales Report

When Admin clicks a Vendor, open a detailed Vendor Sales page.

Display:

- Vendor Profile
- Current Commission Rate
- Commission History
- Total Online Orders
- Total Products Sold
- Gross Sales
- Net Sales
- Total Commission
- Refund Adjustments
- Vendor Earnings
- Payout History
- Outstanding Payable
- Top Selling Products
- Recent Orders
- Daily Sales Chart
- Monthly Sales Chart
- Product-wise Sales Table

## 8.3 Product-wise Vendor Sales

For every Vendor product, Admin must see:

- Product Name
- Product Image
- SKU
- Total Quantity Sold
- Gross Sales
- Discounts
- Refund Quantity
- Refund Amount
- Net Sales
- Applicable Commission Percentage
- Commission Amount
- Vendor Net Earnings

A product must be attributed to the Vendor that owns it at the time of sale.

Never calculate Vendor sales based only on the product's current name or category.

Use immutable product ownership references on the relevant sale/order item records where required.

## 8.4 Vendor Sales Ranking

Provide reports such as:

- Top Selling Vendors
- Highest Revenue Vendors
- Highest Product Quantity Vendors
- Highest Commission Generating Vendors
- Vendors with Pending Payouts

All rankings must use server-side calculations and accurate date boundaries.

## 8.5 Date Filters

Support:

- Today
- Yesterday
- This Week
- This Month
- Last Month
- This Year
- Custom Date Range

Use Asia/Dhaka for business reporting boundaries.

## 8.6 Export

Allow authorized Admin users to export:

- Vendor-wise Sales
- Product-wise Sales
- Commission Reports
- Vendor Earnings
- Payout Reports

Exports must respect date filters and authorization scope.

---

# 9. PLATFORM ADMIN POS MODULE

POS is a Platform Admin-only module.

## Platform POS Product Rules

- Platform POS can sell only Platform-owned products.
- Vendor-owned products must never appear in POS search.
- Product lookup must validate Platform ownership on the backend.
- POS sales must use Platform-owned stock.
- POS sales must not create Marketplace Vendor Orders.
- POS sales must not generate Vendor commission or earnings.

## POS Features

- Barcode scanner input.
- Manual product search.
- Product and variant selection.
- Cart management.
- Quantity adjustment.
- Stock validation.
- Customer selection or walk-in customer.
- Authorized discounts.
- Payment methods.
- Receipt printing.
- Sale cancellation and returns.
- Cash register opening and closing.
- Cash reconciliation.
- Sales by cashier.
- POS reports.

Use hardware barcode scanners through keyboard-wedge input where appropriate.

Camera-based barcode scanning may be implemented only where supported and permission is granted.

## POS Permissions

Suggested permission keys:

- platform_pos.access
- platform_pos.sales.view
- platform_pos.sales.create
- platform_pos.sales.cancel
- platform_pos.sales.return
- platform_pos.discount.apply
- platform_pos.register.open
- platform_pos.register.close
- platform_pos.reports.view
- platform_pos.settings.manage

Never add these permissions to Vendor Staff roles.

---

# 10. PRODUCT, SKU, BARCODE AND QR MANAGEMENT

Products and variants should support:

- SKU
- Barcode
- QR Code
- Product Name
- Description
- Category
- Brand
- Cost Price
- Selling Price
- Optional Wholesale Price
- Stock Quantity
- Reorder Threshold
- Unit of Measure
- Product Images
- Active/Inactive Status
- Ownership Type
- Approval Status

Requirements:

- Generate unique SKU/barcode values according to the approved ownership scope.
- Generate QR codes containing safe product identifiers or product URLs.
- Never encode sensitive customer, tenant or financial information into QR codes.
- Allow authorized users to print labels.
- Search by SKU, barcode, QR identifier and product name.
- Validate ownership during every lookup.
- Ensure Vendor barcode lookup returns only Vendor-owned products.
- Ensure Platform POS lookup returns only Platform-owned products.

Do not introduce an additional QR library without explicit approval if the existing project does not already support it.

---

# 11. SHARED INVENTORY ARCHITECTURE

Use one authoritative stock source per product/variant and ownership scope.

Platform-owned inventory and Vendor-owned inventory must remain separate.

## Inventory Rules

- Vendor Online Sales reduce the corresponding Vendor product stock.
- Platform POS Sales reduce only Platform-owned product stock.
- Vendor stock must never be reduced by Platform POS.
- Platform stock must never be reduced by Vendor Online Sales.
- Every stock-changing operation must use the centralized inventory service.
- Prevent negative stock.
- Use transactions and row-level locking.
- Handle concurrent sales safely.
- Record stock movement history.
- Support opening stock, purchases, sales, returns, damages and adjustments.
- Maintain available, reserved and sold stock where checkout requires reservation.

## Stock Movement Channels

Use clear movement source types:

- online_sale
- online_cancellation
- online_return
- platform_pos_sale
- platform_pos_return
- purchase
- purchase_return
- vendor_adjustment
- platform_adjustment
- damage
- opening_stock

Every stock movement must record the correct product owner and actor.

---

# 12. STEADFAST COURIER API INTEGRATION

Integrate Steadfast Courier with the existing Marketplace Order Management System.

This is a Platform Admin-managed courier integration.

Create a dedicated Admin Sidebar section:

**Steadfast Courier**

Suggested submenu:

- Courier Dashboard
- Shipments
- Create Shipment
- Tracking
- Delivery Reports
- Failed Deliveries
- Return Shipments
- API Settings
- Webhook Logs
- API Activity Logs

## API Security

Provide secure configuration for:

- Steadfast API Key
- Steadfast Secret Key
- Webhook Authentication Token
- API Environment/Endpoint
- Integration Enabled/Disabled status

Rules:

- Never expose credentials to frontend JavaScript.
- Never return secret values through API responses.
- Never store secrets in normal audit logs.
- Never expose credentials to Vendor users.
- Prefer secure environment/configuration management.
- If Admin UI credential management is required, encrypt secrets at rest and mask values.
- Show whether credentials are configured without revealing them.
- Do not hardcode credentials.
- Do not ask the user to paste production secrets into source code or chat.

## Shipment Creation

Authorized Admin users can:

- View eligible Marketplace orders.
- Inspect shipping/customer details.
- Select an eligible order.
- Create a Steadfast shipment.
- Store the courier consignment/tracking identifier.
- Track shipment status.
- Retry failed operations safely.

Before creating a shipment:

- Verify the order exists.
- Verify the order is eligible for dispatch.
- Verify shipping details.
- Verify payment/COD information.
- Prevent duplicate shipment creation.
- Use idempotency or safe duplicate prevention.
- Record Admin actor and timestamp.

Do not create shipments for cancelled, refunded or otherwise ineligible orders.

## Tracking and Webhooks

Inspect official Steadfast API documentation before implementation.

- Use only documented endpoints and request fields.
- Map actual API response statuses.
- Validate webhook authentication/signature where supported.
- Reject invalid webhook requests.
- Prevent duplicate event processing.
- Store safe webhook logs.
- Never trust unverified webhook payloads.
- Use controlled polling only where necessary and documented.

Never call the real production courier API from automated tests.

---

# 13. CENTRALIZED ACCOUNTS AND FINANCIAL MANAGEMENT

Accounts Management must be a first-class module in the Platform Admin Dashboard.

It must integrate with:

- Marketplace Online Sales
- Vendor Commission
- Vendor Earnings
- Vendor Payouts
- Platform POS Sales
- POS Payments
- Inventory Purchases
- Supplier Payments
- Refunds
- Courier Delivery Charges
- COD Reconciliation where supported by actual data
- Platform Income and Expenses

Do not implement accounting as unrelated manual income/expense entries.

## 13.1 Accounts Dashboard

Display:

- Total Marketplace Online Sales
- Total Platform POS Sales
- Total Vendor Commission
- Total Vendor Payables
- Total Vendor Payouts
- Total Platform POS Income
- Total Purchase Expenses
- Total Operating Expenses
- Cash Balance
- Bank Balance
- Supplier Payables
- Refund Liabilities
- Net Operating Result
- Recent Transactions

The Dashboard may combine operational summaries but must preserve the original transaction channel and ownership.

## 13.2 Accounting Features

- Chart of Accounts
- Income Accounts
- Expense Accounts
- Cash Accounts
- Bank Accounts
- Online Sales Ledger
- Platform POS Sales Ledger
- Marketplace Commission Ledger
- Vendor Earnings Ledger
- Vendor Payout Ledger
- Purchase Ledger
- Supplier Payables
- Payment Records
- Refund Records
- Courier Charges
- COD Reconciliation where supported
- Financial Transaction Ledger
- Profit and Loss
- Cash Flow
- Balance Sheet only if a complete double-entry accounting model exists

## 13.3 Financial Integrity

Prefer double-entry accounting for a professional financial ledger.

- Every posted transaction must balance.
- Posted transactions must not be silently edited or deleted.
- Use reversal or adjustment entries.
- Maintain source transaction references.
- Use idempotency to prevent duplicate financial postings.
- Keep financial records auditable.
- Do not calculate profit using selling price alone.
- Account for cost, discounts, returns, expenses and applicable fees.

## 13.4 Vendor Financial Separation

Vendor Online Sales must create the correct Vendor financial records.

Platform POS Sales belong to the Platform.

Platform POS must not create Vendor commission or Vendor earnings.

Vendor payables must reconcile with commission, refunds and payouts.

---

# 14. PURCHASING AND SUPPLIER MANAGEMENT

Provide centralized Purchasing and Supplier Management.

Features:

- Supplier List
- Supplier Details
- Purchase Orders
- Purchase Receiving
- Purchase Payments
- Purchase Returns
- Supplier Payables
- Purchase History
- Purchase Reports

Every purchase must be linked to the correct inventory ownership scope.

Do not allow a Vendor purchase to modify Platform-owned stock.

Do not allow Platform purchases to modify Vendor-owned stock.

Use the centralized inventory service for stock receiving and purchase returns.

---

# 15. STAFF AND PERSONNEL MANAGEMENT

Each Vendor Owner can manage staff belonging to their own Vendor.

Platform Admin manages Platform Admin users separately.

Features:

- Staff List
- Create Staff Account
- Assign Roles
- Activate/Deactivate Staff
- Staff Profile
- Contact Information
- Optional Employee ID and Department
- Staff Activity
- Login History

Attendance, payroll, leave and HR functionality remain out of scope unless separately approved.

Vendor Staff must not receive:

- Platform Admin access
- Super Admin access
- Platform POS access
- Platform POS sales permissions
- Platform-wide Steadfast API configuration access

---

# 16. DYNAMIC ROLE AND PERMISSION SYSTEM

Maintain separate authorization domains:

- Platform Super Admin
- Platform Admin
- Vendor Owner
- Vendor Staff
- Customer

Vendor Owner must be able to:

- Create custom staff roles.
- Assign permissions to roles.
- Assign roles to staff.
- Grant individual permissions where supported.
- Deny selected permissions if existing RBAC supports explicit deny.
- View effective permissions.

A Vendor must never grant Platform Admin or Super Admin permissions.

Platform Admin permissions must include separately controlled access to:

- Product Approvals
- Vendor Commission Management
- Marketplace Online Sales
- Vendor Sales Reports
- Platform POS
- Inventory Management
- Accounts Management
- Vendor Payouts
- Purchasing
- Supplier Management
- Steadfast Courier
- Financial Reports
- Audit Logs

Do not expose Platform POS or platform-wide courier permissions in Vendor RBAC.

All protected operations must be authorized by the backend.

---

# 17. AUDIT LOGS

Maintain comprehensive audit logs for:

- Login/logout
- Product creation
- Product approval/rejection
- Product updates
- Stock changes
- Online orders
- Platform POS sales
- Returns and cancellations
- Commission rate changes
- Commission calculations
- Vendor earnings adjustments
- Vendor payouts
- Purchase transactions
- Supplier payments
- Account transactions
- Staff creation
- Permission changes
- Courier shipment creation
- Courier API success/failure
- Tracking updates
- Webhook processing
- Courier configuration changes

Each audit record should include where appropriate:

- Tenant ID or Platform Scope
- Actor User ID
- Action
- Entity Type and ID
- Timestamp
- Before/After values or safe change summary
- Request/Correlation Identifier
- IP Address and User-Agent where safely available

Never store passwords, session tokens, API secrets or other sensitive credentials in audit logs.

Ordinary users must not be able to edit or delete audit history.

---

# 18. REPORTING AND ANALYTICS

Provide Daily, Weekly, Monthly and Yearly reports.

Use Asia/Dhaka for reporting boundaries.

## Marketplace Online Sales

- Total Online Sales
- Vendor-wise Sales
- Product-wise Sales
- Category-wise Sales
- Total Products Sold
- Gross Sales
- Discounts
- Refunds
- Net Sales
- Commission
- Vendor Earnings
- Vendor Payouts

## Platform POS

- Platform POS Sales
- POS Sales by Product
- POS Sales by Category
- POS Sales by Cashier
- POS Sales by Payment Method
- POS Discounts
- POS Refunds

## Vendor Commission

- Current Vendor Commission Rate
- Historical Commission Rate
- Commission Amount
- Commission Adjustments
- Vendor Net Earnings
- Commission by Date Range
- Commission by Vendor
- Commission by Product

## Inventory

- Current Stock
- Low Stock
- Stock Movement
- Stock Valuation
- Purchase and Return Reports
- Platform vs Vendor Inventory

## Accounts

- Income and Expenses
- Cash and Bank Balances
- Profit and Loss
- Cash Flow
- Vendor Payables
- Supplier Payables
- Refunds and Adjustments

## Courier

- Shipment Count
- Pending Shipments
- Delivered Shipments
- Returned Shipments
- Failed Shipments
- Delivery Charges
- COD Summary where actual data is available

## Report Rules

- Reports must be scope-aware.
- Vendor reports must contain only Vendor data.
- Vendor Online Sales must never include Platform POS.
- Platform POS reports must never include Vendor Online Sales as POS sales.
- Admin combined reports may combine totals only with clearly identified channels.
- Avoid double-counting.
- Use server-side calculations.
- Support date filters.
- Support authorized exports.
- Distinguish gross sales, discounts, refunds, net sales, commission, earnings and profit.

---

# 19. VENDOR SIDEBAR AND ADMIN SIDEBAR

## Vendor Sidebar

Include only Vendor business features:

- Dashboard
- Products
- Product Approval Status
- Inventory
- Online Orders
- Online Sales Reports
- Product-wise Sales
- Customers related to Vendor orders
- Vendor Earnings
- Commission Details
- Payouts
- Returns and Refunds
- Staff
- Roles and Permissions
- Settings

Never show:

- POS
- POS Terminal
- POS Sales
- Cash Register
- Cashier Sessions
- Platform POS Reports
- Steadfast API Settings
- Platform-wide Courier Credentials
- Subscription / My Plan

## Platform Admin Sidebar

Organize the Admin Sidebar into these major modules:

1. Business Overview
2. Marketplace Management
3. Product Approval
4. Vendor Management
5. Customer Management
6. Online Sales Management
7. Vendor Commission Management
8. Vendor Earnings and Payouts
9. Platform POS
10. Inventory Management
11. Purchasing and Suppliers
12. Accounts Management
13. Steadfast Courier
14. Staff and Admin Users
15. Roles and Permissions
16. Reports and Analytics
17. Audit Logs
18. System Settings

The Admin Dashboard must provide a centralized overview of Online Sales, POS Sales, Inventory and Accounts.

Do not create duplicate or confusing navigation items.

All menus must be permission-aware.

Backend authorization is mandatory.

---

# 20. SECURITY, RELIABILITY AND PERFORMANCE

- Strict Vendor tenant isolation.
- Strict Platform/Vendor product ownership isolation.
- Server-side tenant resolution.
- Server-side product approval enforcement.
- Server-side commission calculation.
- Commission snapshots for finalized sales.
- Centralized inventory service.
- Transactional stock and financial operations.
- Concurrency protection.
- Idempotency for retryable operations.
- Safe server-side price validation.
- Strict backend authorization.
- Secure courier credential management.
- Secure webhook validation.
- Duplicate shipment prevention.
- Safe audit logging.
- Pagination and optimized reporting queries.
- Database indexes for ownership-scoped lookups.
- No cross-Vendor data leakage.
- No Vendor access to Platform POS.
- No Vendor access to platform-wide courier credentials.
- No secrets in frontend bundles or logs.

---

# 21. TESTING REQUIREMENTS

## Product Approval

1. Vendor can create a product under its own ownership.
2. Newly created Vendor product defaults to Pending.
3. Pending products do not appear publicly.
4. Pending products cannot be purchased.
5. Authorized Admin can approve a product.
6. Approved active products appear publicly.
7. Rejected products do not appear publicly.
8. Suspended products cannot be purchased.
9. Vendor cannot approve its own product.
10. Product ownership and approval history are preserved.

## Dynamic Vendor Commission

11. Admin can set a commission rate for a selected Vendor.
12. Different Vendors can have different rates.
13. Changing one Vendor's rate does not affect another Vendor.
14. Vendor cannot change its commission.
15. Historical orders retain their original commission snapshots.
16. New qualifying sales use the effective commission rate.
17. Partial refunds adjust commission correctly.
18. Cancelled or unpaid orders do not generate earned commission.
19. Duplicate commission postings are prevented.
20. Commission changes are audited.

## Vendor Sales Reports

21. Admin can view Vendor-wise sales.
22. Admin can view Product-wise Vendor sales.
23. Quantity sold is calculated correctly.
24. Gross and net sales reconcile.
25. Commission and Vendor earnings reconcile.
26. Vendor reports exclude Platform POS.
27. Date filters use Asia/Dhaka boundaries.
28. Exports respect permissions and filters.

## Platform POS

29. Authorized Admin can use POS.
30. Unauthorized Admin cannot use POS.
31. Vendor cannot access Platform POS.
32. POS can sell Platform-owned products.
33. POS cannot sell Vendor-owned products.
34. POS reduces only Platform-owned stock.
35. POS does not create Marketplace orders.
36. POS does not generate Vendor commission.
37. POS cancellation and return follow correct accounting and inventory workflows.

## Inventory

38. Vendor Online Sales reduce the correct Vendor stock.
39. Platform POS reduces the correct Platform stock.
40. Concurrent checkout cannot oversell.
41. Cross-ownership stock updates are rejected.
42. Stock movements are auditable.

## Accounts

43. Financial transactions balance.
44. Online Sales and Platform POS remain separate.
45. Vendor commission reconciles with Vendor payables.
46. Vendor payouts reconcile with outstanding payables.
47. Refunds and reversals are idempotent.
48. Combined reports do not double-count.
49. Purchase receiving and returns reconcile with inventory.
50. Cash and bank balances reconcile with posted transactions.

## Courier

51. Authorized Admin can access Steadfast management.
52. Vendor cannot access Steadfast API settings.
53. Vendor cannot read courier secrets.
54. Shipment creation validates Marketplace order eligibility.
55. Duplicate shipment creation is prevented.
56. Invalid webhook requests are rejected.
57. Duplicate webhook events are idempotent.
58. Secrets never appear in logs or API responses.

## Regression

59. Existing Marketplace, Cart, Checkout and Vendor isolation tests continue passing.
60. Existing dynamic RBAC tests continue passing.
61. Existing inventory tests continue passing.
62. Existing courier-specific work is preserved unless separately approved.

Run:

- Full backend test suite.
- Frontend TypeScript check.
- Frontend production build.
- Isolated browser QA.
- API security tests.
- Financial reconciliation tests.

Do not use production data or credentials.

---

# 22. STRICT APPROVAL BOUNDARIES

- Do not modify production.
- Do not modify production credentials or `.env`.
- Back up the local database before migrations.
- Never run production migrations.
- Do not commit or push.
- Do not reset, rebase, force-push or rewrite Git history.
- Do not delete QA databases or backups.
- Do not delete existing data.
- Do not remove migrations without explicit approval.
- Do not implement Vendor POS.
- Do not implement Vendor Subscription Plans or Subscription Fees.
- Do not implement offline POS.
- Do not implement payroll or multi-branch functionality unless separately approved.
- Do not invent undocumented Steadfast API endpoints or payloads.
- Do not send real production courier requests during automated tests.
- Do not expose courier secrets.
- Preserve existing pending courier-specific work.
- Inspect existing Courier Commit 2 and related files before modifying them.
- Do not overwrite or discard unrelated pending changes.

If a requested implementation conflicts with existing approved work, stop and report the conflict before changing it.

---

# 23. IMPLEMENTATION PLAN

Work incrementally. Do not implement everything in one unreviewed change.

## Phase 1: Architecture and Safety Audit

- Inspect repositories.
- Inspect database schema.
- Inspect Vendor/Tenant relationship.
- Inspect product ownership and approval.
- Inspect shared inventory.
- Inspect existing POS ownership.
- Inspect Vendor commission and earnings.
- Inspect Accounts Management.
- Inspect RBAC.
- Inspect old subscription implementation and dependencies.
- Inspect Steadfast integration.
- Inspect Admin Dashboard and sidebars.
- Report gaps and risks.

## Phase 2: Product Approval and Ownership

- Implement Vendor product submission.
- Implement Pending Approval queue.
- Implement Admin approval/rejection.
- Enforce public visibility rules.
- Enforce backend purchase eligibility.
- Preserve product ownership and approval history.

## Phase 3: Dynamic Vendor Commission

- Implement Vendor-specific commission configuration.
- Build Admin Commission Management UI.
- Implement commission snapshots.
- Implement refund and cancellation adjustments.
- Reconcile Vendor earnings.
- Add commission history and audit logs.

## Phase 4: Vendor Online Sales and Analytics

- Preserve Vendor Online Sales.
- Verify Vendor order isolation.
- Implement Vendor-wise sales reports.
- Implement Product-wise sales reports.
- Implement Vendor earnings and payout reports.
- Verify commission reconciliation.

## Phase 5: Shared Inventory and Ownership

- Verify centralized stock service.
- Enforce ownership-aware stock operations.
- Integrate Online checkout.
- Integrate Platform POS.
- Implement stock movement reporting.
- Test concurrency and rollback.

## Phase 6: Platform Admin POS

- Platform POS database and APIs.
- Platform-owned product lookup.
- POS Terminal.
- Payments.
- Cash Registers.
- Returns.
- POS reports.
- Platform Admin RBAC.

## Phase 7: Centralized Admin Dashboard

- Business Overview.
- Marketplace Online Sales Overview.
- Platform POS Overview.
- Inventory Overview.
- Accounts Overview.
- Vendor Performance Overview.
- Centralized Admin navigation.
- Permission-aware dashboards and reports.

## Phase 8: Accounts and Financial Management

- Chart of Accounts.
- Financial ledger.
- Online Sales accounting.
- Platform POS accounting.
- Marketplace commission.
- Vendor earnings and payouts.
- Purchasing and supplier accounts.
- Refund and reversal accounting.
- Financial reconciliation.

## Phase 9: Steadfast Courier Integration

- Inspect official documentation.
- Verify actual endpoints and response formats.
- Build secure API service.
- Configure credentials safely.
- Add Admin Sidebar.
- Build shipment management.
- Implement tracking.
- Implement webhook if supported.
- Add logs and duplicate prevention.
- Test with mocked API responses.

## Phase 10: Full QA and Regression

- Backend tests.
- Frontend TypeScript check.
- Production build.
- Isolated browser QA.
- Vendor isolation checks.
- Product approval checks.
- Commission reconciliation.
- Admin POS checks.
- Inventory checks.
- Accounts reconciliation.
- Courier integration checks.
- Security review.

Do not move to a high-risk phase if the previous phase has unresolved failures.

---

# 24. FINAL REPORT

At the end of each implementation phase, report:

1. What was inspected.
2. What was implemented.
3. What was reused.
4. What database changes were made.
5. Backup location.
6. API routes added or changed.
7. Frontend pages and sidebar changes.
8. RBAC changes.
9. Product approval verification.
10. Vendor commission verification.
11. Vendor sales reporting verification.
12. Platform POS verification.
13. Inventory verification.
14. Accounts reconciliation results.
15. Steadfast integration status.
16. Test results.
17. TypeScript and build results.
18. Browser QA results.
19. Remaining issues.
20. Unimplemented features.
21. Any approval required before continuing.

Never report a feature as complete unless it has been implemented and verified.

---

# FINAL BUSINESS RULES

BazarBariOnline is a Multi-Tenant Marketplace.

1. Vendors can create their own products, but products must be approved by Platform Admin before public publication and sale.
2. Vendors sell online only. Vendor POS does not exist.
3. Platform POS is a separate Platform Admin module and sells Platform-owned products only.
4. Platform Admin can manage each Vendor's commission percentage independently and dynamically.
5. Historical sales retain the commission percentage that applied when the sale was finalized.
6. Admin can view each Vendor's total products sold, sales revenue, commission, refunds and net earnings.
7. The Platform Admin Dashboard combines Marketplace Online Sales, Platform POS Sales, Inventory Management and Accounts Management into one centralized business management experience.
8. Combined dashboards must not mix or double-count the underlying transaction channels.
9. Steadfast Courier API is centrally managed through the Platform Admin Sidebar.
10. Vendor Online Sales, Platform POS Sales, Product Ownership, Inventory, Commission, Accounting and Courier Operations must remain correctly separated and securely integrated.
11. There is NO Vendor Subscription System, NO Subscription Fee and NO Subscription Plan.

**Build this system using the existing project architecture wherever safely possible. Inspect first, implement incrementally, verify with tests, and preserve all existing approved work.**

# Critical Business Architecture Requirement — One Purchase System, Two Sales Channels

This is a mandatory platform-wide business architecture requirement for BazarBari Online.

## 1. One Central Purchase System

The entire platform must have ONE centralized Purchase Management System.

There must not be separate purchase systems for POS and Online Sales.

The shared Purchase System must manage:

- Suppliers
- Purchase orders
- Purchase invoices
- Purchase items
- Purchase payments
- Purchase returns
- Purchase history
- Purchase reports
- Stock receiving
- Inventory cost records

All purchases must enter the central inventory system through the same purchase workflow.

## 2. Exactly Two Sales Channels

The platform must have exactly two sales channels:

### Channel 1: POS Sales
- Physical retail/counter sales.
- Operated through the POS terminal.
- Uses POS registers and cashier sessions.
- Uses the shared inventory.
- Maintains separate POS sales records and reports.
- Supports POS-specific receipts, payments, voids and returns.

### Channel 2: Online Sales
- Sales generated through the online storefront.
- Uses the shared inventory.
- Maintains separate online order and payment records.
- Supports online customer orders, delivery, order status, payment and returns.
- Must not create POS register sessions or POS cash drawer transactions.

## 3. Shared Inventory Rules

Both sales channels must use the same authoritative stock system.

Example:

- Purchased stock: 100 units.
- POS sale: 5 units.
- Online sale: 3 units.
- Remaining stock: 92 units.

Both channels must update inventory correctly through the existing inventory service.

Prevent overselling through proper stock validation and database transaction/locking mechanisms.

## 4. Sales Channel Separation

Keep POS and Online Sales logically separate.

- Separate sales workflows.
- Separate channel identification.
- Separate payment handling where business rules require it.
- Separate return/refund workflows.
- Separate sales reports.
- Separate permissions where appropriate.

Every sale must have a reliable sales channel identifier.

Do not create a third sales channel.

## 5. Combined Reporting

The platform administrator must be able to see:

- POS Sales Total
- Online Sales Total
- Combined Sales Total
- POS Returns
- Online Returns
- Total Returns
- POS Payments
- Online Payments
- Combined Financial Summary

Never double-count sales, refunds or payments.

## 6. Vendor Business Rule

*(Corrected 2026-11-26 by owner decision D1 of 2026-11-25.)*

There is ONE central Purchase System for the platform AND every vendor, with strict shop-level isolation:

- Platform purchasing data (vendor_id NULL) and each vendor's purchasing data are kept apart.
- Each vendor sees and changes only its own suppliers, purchase orders, receipts, invoices, payments, returns and reports.
- Stock received by a vendor is that vendor's stock only; the platform never changes vendor stock, and a vendor never changes platform or another vendor's stock.

The two sales channels (POS and Online) apply to platform-owned inventory and platform-owned sales. Vendors sell online only.

Vendor products and vendor online sales must remain under their existing vendor ownership and business rules.

Vendor online sales must not become Platform POS sales.

Do not create vendor commissions or vendor earnings from Platform POS sales.

## 7. Implementation Instructions

Before changing code:

1. Audit the existing purchase, inventory, POS and online sales architecture.
2. Identify existing tables, APIs, models, services and relationships.
3. Identify any duplicate purchase or inventory workflows.
4. Explain how the two sales channels will share stock safely.
5. Identify required schema changes and migration dependencies.
6. Identify possible conflicts with existing POS implementation.
7. Present a detailed implementation plan.

Do not create duplicate purchase systems.

Do not create duplicate inventory systems.

Do not modify production.

Do not run unapproved migrations.

Do not delete existing QA data.

Do not start implementation until the architecture audit and plan are presented for review.