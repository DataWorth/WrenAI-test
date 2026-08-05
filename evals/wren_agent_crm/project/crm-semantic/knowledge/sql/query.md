---
nl: 赢单率是多少
sql: SELECT CASE WHEN (won + lost) = 0 THEN NULL ELSE won * 1.0 / (won + lost) END
  AS win_rate FROM (SELECT SUM(CASE WHEN status = '赢单' THEN 1 ELSE 0 END) AS won,
  SUM(CASE WHEN status = '输单' THEN 1 ELSE 0 END) AS lost FROM opportunities)
source: user
tags:
- source:enrich
- topic:win-rate
---
