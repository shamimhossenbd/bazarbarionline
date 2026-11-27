# ADR-14: Partnership accounting (platform ledger, variable partners with equal shares)

- **Status:** **Approved** by the owner on 2026-11-26, with changes C1–C3 (distribution approvers, courier charges on vendor shipments, month-close checklist), which are written into decision 7 (C1), decision 3a (C2) and decision 1 (C3).
- **Migrations** still run only after verified backups, on local and QA, never on production.
- **Date:** 2026-11-26
- **Sources:**
  - the owner's Partnership Accounting brief;
  - answers AQ1–AQ10 (2026-11-26);
  - the distribution rounding rule (lowest id);
  - the partner amendment (variable number of partners, equal shares) and answers AM1–AM6 (2026-11-26).
- **Depends on:** ADR-08 (money), ADR-09 (time), ADR-13 (first-party retail: reservations, WAC, sales channel)
- **Order of work:** ADR-13 P2 (`000012`) and P3 (reservations) were done on 2026-11-26. AC1 (`000013`) comes next. Each phase is reported before the next starts.
- **Open item:** the owner checks that bcmath is available on cPanel (decision 8.4).

## Context

The platform buys and sells its own stock (ADR-13), so it needs its own books: a double-entry ledger, expenses, profit and loss, balance sheet, cash book and partner statements, plus profit shared among the business partners.

The books cover **the platform only**. Vendor sale money that the platform collects (for example COD) is a **liability** (vendor payables) and never income. Only commission is platform income. The vendor subledger stays in `vendor_ledger_entries`.

The audit of 2026-11-26 found gaps in the source data. They are closed in the phase noted in brackets:
- `payments.status` never becomes `paid` (the unrouted `PaymentController` was deleted on 2026-11-26). No posting depends on it.
- There is no Steadfast remittance record and courier charges are not stored (AC5: `settlements`).
- Online refunds have no amount, date or paid-from account (AC5: `order_refunds`).
- Vendor payouts and purchase payments store a method, not an account (AC5: account ids).
- Checkout shipping is always 0. The delivery income account is reserved for when it exists.
- Purchase returns leave stock at receipt cost, not WAC (AC4: stock value).

## Decisions

Each decision notes where it comes from: "Brief" is the owner's original module brief, "Audit" is the 2026-11-26 audit, and AQ1–AQ10 and AM1–AM6 are the owner's answers.

### 1. Ledger core (Brief, Audit, AQ9)

- **Double entry** (Brief). Every journal entry balances (debits = credits), and the posting service refuses one that does not.
- **Append-only** (Brief). Corrections are reversal entries with a reason.
  - The models refuse updates and deletes on the journal tables.
  - The app's DB user gets only SELECT and INSERT on those tables.
- **BIGINT poisha** (Audit). Journal amounts are integers (1 taka = 100 poisha). This is a deliberate exception to ADR-08's DECIMAL(12,2) storage rule, and it keeps sums exact.
- **Idempotent posting.** The source (type, id, event) is unique, so the same event never posts twice. Each automatic entry posts in the same DB transaction as its source event.
- **Monthly periods, never reopened (AQ9).** Periods follow Asia/Dhaka dates. No entry may be dated inside a closed month.
  - A source event dated in a closed month posts on the first open day, with its original date kept in `source_date`.
  - Corrections go into an open month.
- **Month-close checklist (C3, owner change 3).** A month closes only when every check below passes. Otherwise the close is refused, and the response lists each failing check with its details:
  1. The trial balance difference for the month is 0.
  2. No expense and no `accounting_request` dated in the month is still pending (submitted but not approved or rejected).
  3. Every POS session that opened in the month is closed.
  4. Every reconciliation is either 0 or has an explanation note for its difference: 1200 Inventory, 1210 Inventory issued, 2010 Vendor payables, 2020 Supplier payables, 1100 COD receivable and 1040 Card clearing.
     - Notes are stored in `period_close_notes`: period, account, difference in poisha, note, who wrote it and when.
     - A note covers only the exact difference it was written for. If the difference changes, the note no longer counts.

### 2. Revenue and COGS recognition (AQ1)

- **POS:** revenue and COGS are recognised at the time of sale.
- **Online platform lines** are recognised at **line delivery**, the same moment commission and vendor earnings are recognised.
  - When the reservation converts and the stock leaves (ADR-13 P3), its cost moves from 1200 Inventory to **1210 Inventory issued, awaiting delivery**.
  - On delivery, revenue is recognised and the cost moves from 1210 to COGS.
  - A cancellation after the stock left moves the cost back.

### 3. Coupons (AQ2)

- New `coupons.funded_by` (`platform` by default, or `vendor`) and `coupons.vendor_id`. The value is copied onto `order_items.coupon_funded_by` at checkout.
- A platform-funded coupon on a vendor line is the expense **5040 Coupon subsidy**.
- A vendor-funded coupon **reduces the vendor's payable**, never platform expense.
- A coupon on a platform line is a sales discount (4020).
- Today every coupon is platform-funded and vendors cannot create coupons. The vendor-funded path is built and tested, but it stays unused until vendor coupons exist.

### 3a. Courier charges (C2, owner change 2, option a)

- On a **vendor** shipment, the courier charge is **deducted from that vendor's payable**. J14 posts that share as Dr 2010 / Cr 1100. It also writes a `courier_charge` row in `vendor_ledger_entries`, so 2010 still equals the vendor ledger, and the row shows on the vendor statement.
- On a **platform** line, the courier charge stays platform expense 5105.
- **A shipment holding both vendor and platform lines (proposed, open to review):**
  - The charge is split by each owner's share of the line value in the shipment.
  - Each share is rounded to the nearest poisha, and the rounding remainder goes to the platform (5105).
  - Today shipments are per order, not per vendor order, which is why the split is needed.
- **P&L:** until checkout delivery charges exist, the P&L shows courier cost **per channel** (POS, platform online, marketplace vendor). The vendor-borne part is shown as a memo line, because it is not a platform expense.

### 4. Go-live opening entry (AQ3)

- One **opening-balances entry** on a chosen go-live date. Past events are not replayed.
- The partners supply cash, bank and MFS balances and each partner's capital. The system pre-fills COD receivable, inventory, inventory awaiting delivery, vendor payables and supplier payables, and the partners confirm those figures.
- 3950 Opening balance equity must come out at exactly 0, or the entry is refused.
- **Confirmation by every listed partner (owner, 2026-11-27).** The opening entry is not approved by one checker:
  - each partner listed in it confirms **their own line** (their opening capital, re-typed as the amount) from their own account;
  - it posts only when **all** listed partners have confirmed, at the last confirmation, which re-checks the pre-fill and the empty ledger;
  - the maker is never a confirmer, and a listed partner cannot be the maker;
  - for a listed partner **without an account**, a user with `accounts.manage` (not the maker) may confirm on their behalf **only with a signed consent document attached** (PDF, JPG or PNG, up to 5 MB, kept on the private disk with its name, size and SHA-256; the confirmation and every download are audited);
  - one partner **declining** returns the request to the maker with the partner's reason (status rejected); the maker submits a corrected request, which needs fresh confirmations.
- Events dated before go-live never post. Later events that settle older documents post against the opening balances.

**Go-live checklist (owner, 2026-11-27).** The real opening entry is made only when all of these are done:

1. **Physical stock count.** Count every platform-owned item and record each difference as an audited stock adjustment (Inventory → Stock adjustment, reason required). Only then does the 1200 Inventory pre-fill (stock on hand × weighted average cost) match the real stock.
2. **Costs.** Every platform item with stock has a cost. The pre-fill marks 1200 "not available" while any item lacks one.
3. **Payables.** Supplier invoices, payments and returns, and the vendor ledger, are up to date, so the 2010 and 2020 pre-fills are right.
4. **COD with the courier.** The partners take the 1100 figure from the latest Steadfast statement (the system cannot work it out until AC5).
5. **Cash, bank and MFS.** The partners count the cash and take the bank and MFS balances on the go-live date.
6. **Capital.** The partners agree each partner's opening capital, so that 3950 comes out at exactly 0.
7. **Timing.** The pre-fill shows current values, so count, submit and approve on (or as close as possible to) the go-live date, with no stock movement between the count and the approval. The approval re-checks the pre-fill and refuses a figure that has changed.
8. **Test data.** QA test records are never part of the real opening entry; the real entry is made only on the production database.

### 5. Inventory value (AQ6, AQ7)

- **AQ6:** invoice shipping is added to inventory cost. Purchase tax is added to cost by default. The setting `purchase_tax_treatment` can switch it to input VAT (1300), and a change applies only to invoices posted after it.
- **AQ7:** each stock item stores its value:
  - `stock_value_poisha` on products and variants;
  - a signed `value_poisha` on `stock_movements`;
  - `average_cost` = value ÷ quantity.

  This keeps 1200 Inventory exactly equal to the stock records.
  - **Stock in:** receipt cost × quantity.
  - **Stock out:** value × quantity ÷ on hand. The last unit takes whatever value is left.
  - **Purchase return:** receipt cost × quantity, capped at the current value. Any difference goes to 5030 Inventory adjustment.
  - **Landed cost:** spread over the receipt lines by value. The share for units still on hand goes to stock value, and the share for units already sold goes to COGS.
  - **Backfill:** stock × the current average cost.
- **AQ7:** damaged POS returns move from COGS to **5020 Stock loss**.

### 6. Controls, permissions and maker-checker (Brief, AQ8, AQ10)

- **Permissions (Brief):**
  - `accounts.view`, `accounts.close_period`
  - `expenses.create`, `expenses.approve`
  - `profit.distribute`
  - `partners.view_own`

  **Added by AQ8:** `accounts.manage` (chart of accounts, categories, account mappings, transfers, capital and withdrawal entries) and `partners.manage` (partner membership). All of them belong to the `accounts` module in `PermissionModules`.
- **Expenses (Brief):** anyone with `expenses.create` enters one, and a **different** user with `expenses.approve` approves it. Only approved expenses post and count in profit. `approved_by ≠ created_by` is enforced in the code and by a DB CHECK, for super admins too.
- **Maker-checker (AQ8):** manual journals, capital contributions, withdrawals, transfers and **partner membership changes** (8.6) are `accounting_requests`. Each one posts only when a **different** user approves it.
- **Owner change 4 (2026-11-27): making and approving are separate permissions.**
  - `accounts.requests.create` makes manual journal, reversal, transfer, capital and withdrawal requests. `accounts.manage` makes the opening entry (and keeps the chart and mappings). `partners.manage` makes partner joins and leaves.
  - `accounts.requests.approve` approves or rejects every request type, including partner joins and leaves and the opening entry. The approver is never the maker, super admins included.
  - `profit.distribute` now means *propose*; the new `profit.approve` approves a distribution.
  - Roles (editable): **Accountant** = accounts.view, expenses.create, accounts.requests.create. **Partner** = partners.view_own, accounts.view, expenses.approve, accounts.requests.approve, profit.approve. super_admin and administrator hold everything, except that `partners.manage` and `accounts.close_period` are **super admin only**.
  - Because only super admins hold `partners.manage`, a join or leave is approved with `accounts.requests.approve` rather than `partners.manage` (this replaces the approver rule in 8.3 and test A1).
  - Partners hold `accounts.view`, so they can read every account in the ledger, including other partners' capital. The statement endpoint still limits a `partners.view_own`-only user to their own statement.
  - **Own partnership (owner, 2026-11-27):** nobody approves a request about their own membership, capital or drawings (join, leave, capital contribution, withdrawal, settlement), whatever permissions they hold. "Own" means the partner linked to the approver's account (`partners.user_id`). Code `OWN_MEMBERSHIP`.
- **Card payments (AQ10)** go to 1040 Card settlement clearing. The settlement moves the net amount to Bank and the fee to bank/MFS charges.
- Every create, approve, reject, reverse, close, distribute and mapping change is an audit event in the `accounts` module.

### 7. Reports and profit distribution (Brief, AQ5, rounding rule)

- **Reports (Brief):**
  - P&L, cash book per account, trial balance, balance sheet and partner statements;
  - reconciliation of 1200, 1210, 2010, 2020, 1100 and 1040 against their source records;
  - Dhaka day, week (Saturday start), month, year and custom ranges;
  - CSV export, and PDF through the browser's Save as PDF;
  - for every period, the P&L and balance-sheet totals equal the ledger sums.

  A partner with `partners.view_own` sees **only their own** statement.
- **Distribution (AQ5):**
  - **Closed months only.** A month is distributed only once, and no more than the retained profit can be distributed.
  - **Approvers (C1, owner change 1):** the number of partner approvals required = min(configured number, default 2; active partners − 1). The **proposer is never an approver**.
    - 3 or more active partners: 2 partner approvals (with the default setting).
    - 2 active partners: 1 approval, from the partner who did not propose.
    - 1 active partner: no partner approval is possible. One approval comes instead from a user with `profit.approve` (owner change 4) who is **not** that partner and not the proposer.
    - "Active" is counted on the day the distribution is approved. The number is fixed when the distribution is proposed and checked again when it is posted.
  - Shares are **credited to capital**. Cash taken out later is **drawings**.
- **Rounding:** each line is rounded to 0.01, and the remainder goes to the **lowest partner id**, which replaces largest-remainder. The lines add up exactly.
- The share amounts follow decision 8. This **replaces AQ4** ("split by days under each share version").

### 8. Partners: a variable number with equal shares (amendment, AM1–AM6)

This decision replaces the brief's "5 partners, 20% each" and AQ4's share versions. **No percentage is stored.**

#### 8.1 Data

| Table | Columns | Rules |
| --- | --- | --- |
| `partners` | id, name, user_id (nullable, unique), phone, notes, timestamps | One row per person, kept forever. Its id is used by the rounding rule. Only a partner with a `user_id` can approve a distribution. |
| `partner_memberships` | id, partner_id, joined_on, left_on (nullable), capital_account_id, drawings_account_id, settled_at, settlement_entry_id, request_id, timestamps | One row per period of membership. A partner's periods never overlap. |

The 5 current partners get memberships starting on the go-live date.

#### 8.2 The partner rules

| Rule | Decision |
| --- | --- |
| **AM1 – How a month is split** | The month's net profit **or loss** is spread evenly over its days (result ÷ days in the month). Each day's amount is split equally among that day's active partners. This is not the profit actually booked on each day. |
| **AM2 – Dates** | joined_on is the first day as a partner. left_on is the first day as a **former** partner. A partner is active on day *d* when joined_on ≤ *d* and (left_on is null or *d* < left_on). |
| **AM3 – Settlement timing** | The final statement and the settlement are allowed only after **every month up to left_on is closed and distributed**. Until then the page lists the months still open or undistributed. |
| **AM4 – Losses and negative balances** | Loss months are split equally by the same rules and charged to capital. A negative leaving balance is shown as **"Amount owed by partner"** with a clear warning banner, and the settlement entry collects it. |
| **AM5 – No back-dating** | A joined_on or left_on inside a closed month is refused. Dates in an open or future month are allowed. |
| **AM6 – Returning partners** | A returning partner gets a new membership and **new** capital and drawings accounts. The old accounts stay closed. The statement page lists all their membership periods together. |
| At least one partner | At least one partner is active on every day from go-live onward. A change that breaks this is refused, both when it is requested and when it is approved. |
| Accounts | Capital and drawings accounts are created when a join is approved. They are closed (`is_closed`, no more postings, never deleted) at settlement, and only at a zero balance. |
| Past months | They are never recalculated. AM5 keeps every change out of closed months, and distribution lines are never edited. |
| Display | The Partners page shows "N partners — X% each" for today, for example "4 partners — 25% each" or "3 partners — 33.33% each". The figure is for display only. |

#### 8.3 Membership changes (maker-checker)

| Request | Contents | Applied when approved |
| --- | --- | --- |
| `partner.join` | a new or returning partner, joined_on, optional capital amount and account | membership row, two new accounts, and the capital entry (J27) if there is one |
| `partner.leave` | membership, left_on | sets left_on (no journal entry) |
| `partner.settle` | membership, paid-from or received-into account | entries J36–J38, closes both accounts, sets settled_at |

The maker needs `partners.manage`. The approver needs `accounts.requests.approve` (owner change 4) and must be a **different user**. Every request, approval and rejection is audited with the before and after state.

#### 8.4 Distribution arithmetic

For a closed month with *D* days and result *A* in poisha (*A* may be negative):

1. Partner *p*'s exact share = (*A* ÷ *D*) × Σ 1 ÷ N(*d*), summed over the days when *p* is active. N(*d*) is the number of partners active on day *d*.
2. Each exact share is rounded to the nearest poisha. Halves round away from zero.
3. The remainder (*A* − Σ rounded, which can be positive or negative) goes to the lowest `partners.id` active on at least one day of the month. That may be a partner who left during the month.
4. Σ lines = *A* is checked before posting. If the check fails, the distribution is refused.

The arithmetic is exact. It uses integers over the common denominator *D* × lcm(N values), with bcmath at scale 0, and no floats. If cPanel lacks bcmath, GMP is used. A distribution covering several months is computed and rounded **month by month**.

**Example.** A 30-day month has a profit of ৳3,000.00. Partners 1–3 are active all month, and partner 4 joins on day 21.
- Partners 1–3 each get 20 × 33.333… + 10 × 25 = 916.67 after rounding. Partner 4 gets 250.00.
- The rounded lines add up to 3,000.01, so the remainder is −0.01, and it goes to partner 1.
- Final: partner 1 916.66, partners 2 and 3 916.67 each, partner 4 250.00.

#### 8.5 Final statement (leaving)

The statement shows:
- capital (contributions + distributed profit − distributed losses);
- \+ undistributed share up to left_on;
- − drawings;
- = the balance due.

Because of AM3, the undistributed share is always 0 at settlement. It is still shown as a line so the statement explains itself. If the balance is negative, the statement shows "Amount owed by partner" with a warning.

## Chart of accounts

The seeded accounts are `is_system`: they cannot be deleted or retyped. A **header** account only groups its children and takes no postings. Cash-book accounts appear in the cash book.

| Code | Account | Type | Notes |
| --- | --- | --- | --- |
| 1010 | Cash in hand | Asset | Cash book |
| 1020 | Bank | Asset | Cash book. More bank accounts can be added as 1021 onward. |
| 1030 | bKash | Asset | Cash book |
| 1031 | Nagad | Asset | Cash book |
| 1032 | Rocket | Asset | Cash book |
| 1040 | Card settlement clearing | Asset | Emptied by card settlements (AQ10) |
| 1100 | Steadfast COD receivable | Asset | Emptied by courier settlements |
| 1200 | Inventory | Asset | Always equals the total stock value (AQ7) |
| 1210 | Inventory issued, awaiting delivery | Asset | Online platform lines whose stock has left (AQ1) |
| 1300 | Input VAT recoverable | Asset | Used only when the tax setting is `input_vat` (AQ6) |
| 2010 | Vendor payables | Liability | Equals `vendor_ledger_entries` |
| 2020 | Supplier payables | Liability | Equals supplier finance |
| 2030 | Customer refunds payable | Liability | |
| 3000 | Partner capital | Equity (header) | **Changed by the amendment:** children 3001–3099, one per **membership**, numbered in order as joins are approved. Replaces the fixed 3010–3050. |
| 3100 | Partner drawings | Equity (header) | **Changed by the amendment:** children 3101–3199, one per membership, paired with its capital account. Replaces the fixed 3110–3150. |
| 3900 | Retained earnings | Equity | Receives each month's result at close. Distributions are drawn from it. |
| 3950 | Opening balance equity | Equity | Used only by the opening entry, where it must come out at 0 (AQ3) |
| 4010 | Platform sales | Income | |
| 4020 | Sales discounts | Income (contra) | |
| 4030 | Sales returns | Income (contra) | |
| 4100 | Commission income | Income | |
| 4200 | Other income | Income | |
| 4210 | Cash over / short | Income | Can carry a debit balance |
| 5010 | Cost of goods sold | Expense | |
| 5020 | Stock loss / damage | Expense | Includes damaged POS returns (AQ7) |
| 5030 | Inventory adjustment | Expense | Counts, adjustments and purchase-return differences |
| 5040 | Coupon subsidy | Expense | Platform-funded coupons on vendor lines (AQ2) |
| 5100 | Operating expenses | Expense (header) | Groups the expense categories below |
| 5101 | Rent | Expense | |
| 5102 | Salary | Expense | |
| 5103 | Electricity / utilities | Expense | |
| 5104 | Internet | Expense | |
| 5105 | Delivery / courier | Expense | Courier charges from COD settlements |
| 5106 | Marketing / ads | Expense | |
| 5107 | Packaging | Expense | |
| 5108 | Transport | Expense | |
| 5109 | Maintenance | Expense | |
| 5110 | Bank / MFS charges | Expense | Card and MFS settlement fees |
| 5111 | Miscellaneous | Expense | |
| 5190 | Courier COD shortfall | Expense | |

The plan approved on 2026-11-26 placed the expense categories at "5100–5180". That range has only 9 codes, too few for 11 categories, so they now run from 5101 to 5111. New categories take 5112 onward.

## Journal mapping

"Cost" means the stock movement's `value_poisha`. In the Debit and Credit columns, "·" separates lines.

| # | Event (source) | Debit | Credit |
| --- | --- | --- | --- |
| J1 | **POS sale** (`PosSaleService`) | 1010 / 1040 / 1030–1032, one per payment line · 4020 (line and sale discounts) · 5010 (cost) | 4010 (gross) · 1200 (cost) |
| J2 | **POS void** | Reversal of J1, linked to it | |
| J3 | **POS return, restocked** | 4030 · 1200 (cost) | Refund account · 5010 (cost) |
| J4 | **POS return, damaged** (AQ7) | 4030 · 5020 (cost) | Refund account · 5010 (cost) |
| J5 | **POS session close, over / short** | 1010 (over) or 4210 (short) | 4210 (over) or 1010 (short) |
| J6 | **Online platform line: stock leaves** (reservation converts, ADR-13 P3) (AQ1) | 1210 (cost) | 1200 (cost) |
| J7 | **Online platform line delivered** (AQ1) | 1100 (line − coupon share) · 4020 (coupon share) · 5010 (cost) | 4010 (line total) · 1210 (cost) |
| J8 | **Online vendor line delivered, platform-funded coupon** (AQ2) | 1100 (line − coupon share) · 5040 (coupon share) | 2010 (vendor earning) · 4100 (commission) |
| J9 | **Online vendor line delivered, vendor-funded coupon** (AQ2) | 1100 (line − coupon share) | 2010 (earning − coupon share) · 4100 (commission) |
| J10 | **Online platform line cancelled after stock left, before delivery** | 1200 (cost) | 1210 (cost) |
| J11 | **Refund after delivery, platform line** (`order_refunds`) | 4030 · 1200 if restocked (cost) | 2030 or the paid-from account · 5010 if restocked (cost) |
| J12 | **Refund after delivery, vendor line** | 2010 (earning reversed) · 4100 (commission reversed) | 2030 or the paid-from account · 5040 (subsidy reversed, if platform-funded) |
| J13 | **Customer refund paid later** | 2030 | Paid-from account |
| J14 | **Courier COD settlement** (`settlements`) (owner change 2) | Destination account (net) · 5105 (courier charges on platform lines and the rounding remainder) · 2010 (courier charges on vendor lines, with a `courier_charge` row in the vendor ledger) · 5190 (shortfall) | 1100 (gross) |
| J15 | **Card settlement** (AQ10) | 1020 (net) · 5110 (fee) | 1040 (gross) |
| J16 | **Vendor ledger adjustment** | 2010 (vendor owes more) or an expense account (platform pays the vendor) | 4200 (vendor owes more) or 2010 (platform pays the vendor) |
| J17 | **Vendor payout paid** (`markPaid`) | 2010 | Paid-from account |
| J18 | **Purchase receipt** (platform, `PurchaseService`) | 1200 (receipt cost) | 2020 |
| J19 | **Purchase invoice extras: shipping, tax, discount** (AQ6) | 1200 (share still on hand) · 5010 (share already sold) · 1300 for tax when the setting is `input_vat` | 2020. A discount reverses both sides. |
| J20 | **Purchase payment** | 2020 | Paid-from account |
| J21 | **Purchase payment void** | Reversal of J20 | |
| J22 | **Purchase return credit** (AQ7) | 2020 (credit amount) · 5030 (loss, if any) | 1200 (value removed, capped) · 5030 (gain, if any) |
| J23 | **Stock count or adjustment** | 5030 (decrease) or 1200 (increase) | 1200 (decrease) or 5030 (increase) |
| J24 | **Damage write-off** | 5020 | 1200 |
| J25 | **Approved expense** | Category account (5101–5111) | Paid-from account |
| J26 | **Account transfer** (approved request) | Destination account | Source account |
| J27 | **Capital contribution**: on joining (`partner.join`) or later (approved request) | Cash, bank or MFS account | 30xx Capital – that membership |
| J28 | **Partner withdrawal** (approved request) | 31xx Drawings – that membership | Cash, bank or MFS account |
| J29 | **Manual journal** (approved request) | As entered (must balance and needs a reason) | As entered |
| J30 | **Opening balances** (go-live, approved request) (AQ3) | Cash, bank and MFS (the partners' figures) · 1100, 1200, 1210 (system pre-fill) | 2010, 2020 (system pre-fill) · each partner's 30xx capital · 3950 (must be 0, or the entry is refused) |
| J31 | **Month close** | Every income account down to zero · 3900 if the month made a loss | Every expense and contra account down to zero · 3900 with the net profit |
| J32 | **Profit distribution, profit month** (8.4) | 3900 (the month's distributed total) | Each active membership's 30xx capital (its line) |
| J33 | **Profit distribution, loss month** (AM4) | Each active membership's 30xx capital (its share of the loss) | 3900 (the month's loss total) |
| J34 | **Correction of any posted entry** | Reversal with a reason, dated in an open month | |
| J35 | **Partner leaves** (`partner.leave`) | No entry. Only left_on is set. | |
| J36 | **Settlement step 1: close drawings into capital** (`partner.settle`) | 30xx Capital – membership | 31xx Drawings – membership |
| J37 | **Settlement step 2, positive balance (paid out)** | 30xx Capital – membership | Paid-from account |
| J38 | **Settlement step 2, negative balance (collected)** (AM4) | Received-into account | 30xx Capital – membership |

**Vendor COD money never reaches income.** Vendor lines (J8, J9 and J12) post only to 1100, 2010, 4100 and 5040, and a test proves it.

## Migrations

| # | Migration | Depends on |
| --- | --- | --- |
| 000012 | ADR-13 addendum: reservations, locations, sales_channel | — |
| 000013 | Ledger core: `accounts`, `account_mappings`, `accounting_settings`, `fiscal_periods`, `journal_entries`, `journal_lines`, `accounting_requests`, `period_close_notes`; the chart of accounts seed; permissions | — |
| 000014 | Partners: `partners` and `partner_memberships`. It replaces the former `partner_share_versions` and `partner_share_lines`. | 000013 |
| 000015 | Expenses: `expense_categories` (11 seeded) and `expenses` with the CHECK | 000013 |
| 000016 | AC2 follow-ups (owner, 2026-11-27): `accounting_request_confirmations` for the opening entry, and the Accountant / Partner ledger grants for databases where 000002 ran after 000013/000014 (000002 itself is never edited) | 000014 |
| 000017 | Inventory value: stock value columns and the backfill (planned as 000016 before 2026-11-27) | 000011 |
| 000018 | Money sources: coupon `funded_by`, `settlements` (+ items, with the per-vendor courier-charge split), `order_refunds` (+ items), account ids on payouts and purchase payments, and the `courier_charge` type in `vendor_ledger_entries` | 000013 (and 000012 for online events) |
| 000019 | Profit distributions: `profit_distributions`, `profit_distribution_lines` (membership, partner, month, weight numerator, amount), `profit_distribution_approvals` | 000014 |

Every migration is first proven up and down on the throwaway DB `bb_migration_test`. It then runs on `api-backend` and `bazarbari_cart_qa` after verified backups. **None runs before the owner approves this ADR**, and none runs on production.

Phases:
- AC0: docs.
- AC1: ledger core.
- AC2: partners and the opening entry. **Built 2026-11-27** (000014). Settlement (`partner.settle`, J36-J38) moves to AC7 because AM3 needs closed and distributed months.
- AC3: expenses. **Built 2026-11-27** (000015): categories = accounts 5101-5111, new ones from 5112 (accounts.manage); enter with expenses.create, a different user approves with expenses.approve and J25 posts on the expense date; makers see only their own expenses. No receipt upload yet (planned with the UI, AC8).
- AC4: inventory value. **Built 2026-11-27** (000017): `stock_value_poisha` on products and variants, signed `value_poisha` on movements, backfill = one quantity-0 `revaluation` movement per item (stock × average cost). For every item the movement values sum to its stock value. Rounding: stock out takes value × quantity ÷ on hand rounded half up to the poisha, and the last unit takes what is left, so no poisha is lost. A restored online order comes back at the value it left with; a POS return at its sale-line cost. An item that never had a cost keeps a NULL average while its value is 0, and the 1200 pre-fill stays "not available" until it gets one. The 1200 reconciliation source is the platform stock value as of the day. Unit costs keep 4 decimals in movements and admin screens. Postings to 1200/1210/5010/5020/5030 come with AC5.
- AC5: automatic posting.
- AC6: reports.
- AC7: profit distribution.
- AC8: UI and browser QA.

## Tests

**Ledger and controls (brief and AQ):**
- the trial balance difference is always zero;
- vendor COD money never reaches income;
- an expense does not count until it is approved;
- self-approval is blocked on every approval path;
- a closed month refuses entries, and a late source event lands in the open month;
- a reversal restores the balances;
- posting the same event twice creates nothing;
- an unbalanced entry is refused;
- each reconciliation shows zero difference after a mixed run;
- an opening entry where 3950 is not 0 is refused;
- a vendor-funded coupon lowers the vendor's payable and never posts to 5040;
- the P&L and balance-sheet totals equal the ledger sums for each period;
- permission denials: a partner sees only their own statement; nobody can approve, close, change membership or distribute without the permission.

**Owner changes C1–C3:**

| # | Test |
| --- | --- |
| C1-1 | With 1 active partner: that partner cannot approve, and a non-partner user with `profit.distribute` (not the proposer) can, and 1 approval posts. A user without `profit.distribute` is refused. |
| C1-2 | With 2 active partners: 1 approval from the partner who did not propose posts, and the proposer's own approval is refused. |
| C1-3 | With 3 active partners: 2 approvals are needed, and 1 is not enough. |
| C1-5 | With 5 active partners: 2 approvals with the default setting. With the setting at 4, 4 approvals are needed. With the setting at 6, the requirement is capped at 4. |
| C2-1 | A vendor shipment's courier charge posts Dr 2010 / Cr 1100, writes a `courier_charge` vendor-ledger row, and leaves the 2010 reconciliation at zero. |
| C2-2 | Platform-line courier charges post to 5105. In a mixed shipment the split adds up exactly to the charge, with the remainder going to 5105. |
| C2-3 | The P&L shows courier cost per channel. The vendor-borne part is not counted in net profit. |
| C3-1 | The month close is refused, with every failing check listed, when the trial balance is off, when an expense or request is pending, when a POS session is still open, or when a reconciliation difference has no note. It succeeds when all checks pass. |
| C3-2 | A note on a reconciliation difference stops counting once the difference changes. |

**Partners (amendment and AM1–AM6):**

| # | Test |
| --- | --- |
| P1 | Equal split for 3, 4, 5 and 6 partners active for the whole month. |
| P2 | A partner joining mid-month gets only the days from joined_on onward. |
| P3 | A partner leaving mid-month gets only the days before left_on. |
| P4 | ৳100.00 split 3 ways gives 33.34 / 33.33 / 33.33, with the lowest id getting the extra poisha. A negative remainder is taken from the lowest id. |
| P5 | Property test: for random memberships and amounts, positive and negative, the lines always add up exactly to the month's result. |
| P6 | The remainder goes to the lowest-id partner active in the month, even one who left mid-month. |
| P7 | A closed and distributed month is unchanged after a later join, leave or settlement. |
| P8 | A change that leaves zero active partners on any day is refused, at request time and at approval time. |
| AM1 | Moving a large sale from day 25 to day 5 of the same month changes no partner's share. |
| AM2 | A partner is active on joined_on and not active on left_on. joined_on = left_on − 1 gives exactly one day. |
| AM3 | Settlement is refused while any month up to left_on is open or undistributed, and is allowed once all of them are closed and distributed. |
| AM4a | Loss month: the loss is split equally under the same rounding rule, debited to capital (J33), and the lines add up to the loss. |
| AM4b | Negative leaving balance: the statement shows the amount owed with the warning flag, and settlement collects it (J38) and closes the accounts at zero. |
| AM5 | joined_on or left_on inside a closed month is refused. Dates in the open month and in the future are allowed. |
| AM6 | A returning partner gets a new membership and new 30xx and 31xx accounts. The old accounts stay closed and refuse postings. The statement lists both periods. |
| A1 | A membership change applies only after a second, different user with `partners.manage` approves it. Self-approval and approval without the permission are refused. |
| A2 | Every request, approval and rejection is audited. |
| A3 | Accounts are created on join and closed (not deleted) on settlement. Closing is refused when the balance is not zero. |
| A4 | The Partners page shows "N partners — X% each" and lists former partners with their dates. |

## Consequences

- No percentage can drift out of date. A join or a leave changes every future share automatically, and closed months stay as they were.
- A leaving partner waits for month-end close and distribution before being settled.
- A share depends only on the days of membership, not on which day a sale was booked.
- Capital and drawings accounts are numbered per membership, so a returning partner has more than one pair, and the statement adds them together.

## Alternatives rejected

- **Stored percentages or share versions (the brief's original model and AQ4):** they duplicate what the membership dates already say, and the two can disagree.
- **Actual daily profit (AM1 option a):** it depends on delivery dates, so shares would look random.
- **Largest-remainder rounding:** replaced by the lowest-id rule.
- **Reopening a month for a late change:** it breaks "past periods are never recalculated".
