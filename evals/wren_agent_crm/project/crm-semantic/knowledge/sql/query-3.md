---
nl: 已合格线索数
sql: SELECT COUNT(*) AS qualified_lead_count FROM leads WHERE status = '已合格'
source: user
tags:
- source:enrich
- topic:leads
---
