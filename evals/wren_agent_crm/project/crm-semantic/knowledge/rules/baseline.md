# CRM Business Rules — Baseline

## Master data definitions

The following are the canonical master data entities in this CRM:

- **accounts**: 客户组织 (customer organizations) — the unique master data for customers
- **contacts**: 客户联系人 (customer contacts) — people associated with accounts
- **leads**: 尚未转化的线索 (unconverted leads) — prospects not yet qualified
- **opportunities**: 销售机会 (sales opportunities) — potential deals in the pipeline
- **sales_orders**: 已下单业绩 (confirmed orders) — booked revenue
- **contracts**: 合同 (contracts) — formal agreements
- **invoices**: 应收账单 (receivables) — amounts billed to customers
- **payments**: 实收 (actual receipts) — amounts received from customers
- **cases**: 客户服务工单 (customer service tickets) — support requests

Use only existing foreign key relationships defined in the database schema. Do not create new relationships beyond what the FK structure provides.

## Time conventions

- **created_at**: Record creation timestamp. Business timezone is **Asia/Shanghai** (UTC+8).
- **No soft-delete columns**: This CRM does not use logical deletion (no `deleted_at`, `is_active`, or similar flags). Closed or completed records are retained for historical reporting.
- **No default filters**: Do not apply implicit filters (e.g., `WHERE status != 'deleted'`) when querying. Reports must explicitly filter based on the specific analytical question.

## Analysis dimensions

The following fields serve as analysis dimensions **only for business entities** (customers, leads, opportunities, and commercial documents like orders/contracts/invoices):

- **region**: 销售大区 (sales regions). Valid values: 华东, 华北, 华南, 华中, 西南.
- **source**: 获客或创建来源 (acquisition or creation source). Valid values: 官网咨询, 行业峰会, 渠道伙伴, 客户转介绍, 内容营销.
- **industry**: 客户所属行业 (customer industry).

In pure configuration, association, history, or communication tables (e.g., `account_addresses`, `contact_tags`, `activities`, `notes`, `email_messages`), same-named fields (`region`, `source`, `industry`) are **test fill values** and should not be interpreted as inherent business attributes of those entities. Do not use them as analysis dimensions for those tables.

## Enum value semantics

Confirmed enum meanings for specific tables:

### opportunities.status
- **赢单** (won): Opportunity closed successfully
- **输单** (lost): Opportunity lost to competitor or abandoned
- **进行中** (in progress): Active opportunity in the pipeline

### leads.status
- **已转化** (converted): Lead converted to opportunity or customer
- **已合格** (qualified): Lead meets qualification criteria
- **已联系** (contacted): Initial contact made with lead

### cases.status
- **新建** (new): Ticket just created, not yet assigned or worked on
- **处理中** (in progress): Ticket actively being worked on
- **待客户反馈** (awaiting customer feedback): Ticket waiting for customer response
- **已关闭** (closed): Ticket resolved and closed

**Important**: Other tables containing values like 新建, 进行中, 已完成, 已关闭, 待跟进 are **demo lifecycle placeholders**. Unless a specific table is explicitly queried and confirmed, do not create cross-table enum rules or assume consistent semantics across tables.

## Amount, quantity, and numeric field semantics

### Currency and amounts
**CNY (Chinese Yuan)** applies **only** to the following tables and their line items:
- opportunities
- quotes, quote_items
- sales_orders, sales_order_items
- contracts, contract_lines
- invoices, invoice_lines
- payments
- renewals

For these tables:
- **amount**: 未税演示金额 (pre-tax demo amount). This is a demonstration figure with unclear cross-table aggregation semantics. **Do not sum amounts across different document types** (e.g., do not add opportunities.amount + sales_orders.amount).
- **unit_price**: CNY unit price
- **quantity**: 件数 (piece count / quantity)

### Special numeric fields
- **probability**: **Only valid for opportunities** — win probability, range 0–100 (percentage).
- **score**: **Only valid for customer_health_scores** — customer health score, range 0–100.

Same-named numeric fields (e.g., `amount`, `probability`, `score`) in other tables are **test placeholders** and should not be used to generate business metrics or interpreted as having business units.

## Pipeline metrics

One cube is authorized: **crm_sales_funnel**. This cube defines the following measures **and no others**:

1. **线索数** (Lead count): `COUNT(leads.*)`
2. **已合格线索数** (Qualified leads): `COUNT(leads.*) WHERE leads.status = '已合格'`
3. **已转化线索数** (Converted leads): `COUNT(leads.*) WHERE leads.status = '已转化'`
4. **机会数** (Opportunity count): `COUNT(opportunities.*)`
5. **进行中管道金额** (In-progress pipeline amount): `SUM(opportunities.amount) WHERE opportunities.status = '进行中'`
6. **赢单金额** (Won amount): `SUM(opportunities.amount) WHERE opportunities.status = '赢单'`
7. **输单金额** (Lost amount): `SUM(opportunities.amount) WHERE opportunities.status = '输单'`
8. **赢单率** (Win rate): `赢单机会数 / (赢单机会数 + 输单机会数)`. Returns NULL if denominator is 0.
9. **订单金额** (Order amount): `SUM(sales_orders.amount)`
10. **开票金额** (Invoice amount): `SUM(invoices.amount)`
11. **回款金额** (Payment amount): `SUM(payments.amount)`

**Do not create any other derived metrics or aggregation cubes** beyond this single cube.

## Privacy and sensitive data

The following tables contain fields that must be treated as **potential PII or sensitive communication content**:

- contacts
- contact_addresses
- notes
- email_messages
- email_events
- meetings
- meeting_attendees
- case_comments
- knowledge_articles

Specifically:
- **record_name** and body/content fields in these tables should not be used as default retrieval or aggregation text.
- Do not expose these fields in summary reports or use them for grouping/filtering without explicit user request.

**All ID fields** (e.g., `account_id`, `contact_id`, `opportunity_id`) are **join keys only**. They are not business document numbers, invoice numbers, or monetary amounts. Do not interpret them as business metrics.

## Test data disclaimer

Database values may contain character encoding imperfections. The Chinese enum business meanings defined above are the authoritative reference. For any column whose business meaning cannot be determined from this baseline, mark the description as **"需真实业务确认"** (needs real business confirmation) rather than inferring or fabricating semantics.
