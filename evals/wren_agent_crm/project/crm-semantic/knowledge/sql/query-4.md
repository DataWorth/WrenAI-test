---
nl: 订单金额和开票金额对比
sql: SELECT (SELECT SUM(amount) FROM sales_orders) AS order_amount, (SELECT SUM(amount)
  FROM invoices) AS invoice_amount
source: user
tags:
- source:enrich
- topic:revenue
---
