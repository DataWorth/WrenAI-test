---
nl: 各销售大区的进行中管道金额
sql: SELECT region, SUM(amount) AS in_progress_pipeline_amount FROM opportunities
  WHERE status = '进行中' GROUP BY region
source: user
tags:
- source:enrich
- topic:pipeline
- grain:region
---
