import datetime, decimal, json, os, sys
from pathlib import Path
import pymysql

ROOT = Path("/benchmarks")
TABLES = [
"organizations","departments","territories","teams","crm_users","roles","user_roles",
"accounts","account_addresses","contacts","contact_addresses","tags","account_tags",
"contact_tags","account_status_history","lead_sources","lead_statuses","campaigns",
"nurture_sequences","leads","lead_assignments","campaign_members","opportunity_stages",
"product_categories","products","price_books","price_book_items","opportunities",
"opportunity_contacts","opportunity_products","quotes","quote_items","lead_conversions",
"sales_orders","sales_order_items","contracts","contract_lines","invoices","invoice_lines",
"payments","activities","activity_participants","tasks","notes","email_messages",
"email_events","meetings","meeting_attendees","cases","case_comments","case_status_history",
"knowledge_articles","customer_health_scores","renewals","satisfaction_surveys"]
CN = {
"organizations":"组织","departments":"部门","territories":"销售辖区","teams":"团队","crm_users":"CRM用户","roles":"角色","user_roles":"用户角色分配",
"accounts":"客户","account_addresses":"客户地址","contacts":"联系人","contact_addresses":"联系人地址","tags":"标签","account_tags":"客户标签","contact_tags":"联系人标签",
"account_status_history":"客户状态历史","lead_sources":"线索来源","lead_statuses":"线索状态","campaigns":"营销活动","nurture_sequences":"线索培育序列",
"leads":"线索","lead_assignments":"线索分配","campaign_members":"活动成员","opportunity_stages":"商机阶段","product_categories":"产品分类","products":"产品",
"price_books":"价目表","price_book_items":"价目表条目","opportunities":"商机","opportunity_contacts":"商机联系人","opportunity_products":"商机产品",
"quotes":"报价单","quote_items":"报价单条目","lead_conversions":"线索转化","sales_orders":"销售订单","sales_order_items":"销售订单明细",
"contracts":"合同","contract_lines":"合同明细","invoices":"发票","invoice_lines":"发票明细","payments":"回款","activities":"客户活动",
"activity_participants":"活动参与人","tasks":"任务","notes":"客户笔记","email_messages":"邮件","email_events":"邮件事件","meetings":"会议",
"meeting_attendees":"会议参会人","cases":"客服工单","case_comments":"工单评论","case_status_history":"工单状态历史","knowledge_articles":"知识文章",
"customer_health_scores":"客户健康度","renewals":"续约","satisfaction_surveys":"满意度调查"}

def q(id, category, question, sql):
    return {"id": id, "category": category, "question": question, "gold_sql": sql}

def tests():
    out=[]; n=1
    for t in TABLES[:30]:
        out.append(q(n,"single_count",f"统计{CN[t]}的记录数。",f"SELECT COUNT(*) AS record_count FROM {t}")); n+=1
    for t in TABLES[30:55]:
        out.append(q(n,"status_distribution",f"按状态统计{CN[t]}的记录数。",f"SELECT status, COUNT(*) AS record_count FROM {t} GROUP BY status ORDER BY status")); n+=1
    for t in TABLES[:15]:
        out.append(q(n,"region_amount",f"按区域汇总{CN[t]}的金额。",f"SELECT region, SUM(amount) AS total_amount FROM {t} GROUP BY region ORDER BY region")); n+=1
    for t in TABLES[15:30]:
        out.append(q(n,"stage_amount",f"按阶段统计{CN[t]}的记录数和金额。",f"SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM {t} GROUP BY stage ORDER BY stage")); n+=1
    joins = [
      ("按客户区域统计商机数量与商机金额。","SELECT a.region, COUNT(o.opportunity_id) AS opportunity_count, SUM(o.amount) AS total_amount FROM opportunities o JOIN accounts a ON o.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按商机阶段统计商机数量和加权管道金额。","SELECT s.record_name AS stage_name, COUNT(o.opportunity_id) AS opportunity_count, SUM(o.amount*o.probability/100) AS weighted_amount FROM opportunities o JOIN opportunity_stages s ON o.opportunity_stage_id=s.opportunity_stage_id GROUP BY s.record_name ORDER BY stage_name"),
      ("按线索来源统计线索数量和金额。","SELECT s.record_name AS source_name, COUNT(l.lead_id) AS lead_count, SUM(l.amount) AS total_amount FROM leads l JOIN lead_sources s ON l.lead_source_id=s.lead_source_id GROUP BY s.record_name ORDER BY source_name"),
      ("按客户区域统计联系人数量。","SELECT a.region, COUNT(c.contact_id) AS contact_count FROM contacts c JOIN accounts a ON c.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计客户活动数量。","SELECT a.region, COUNT(x.activity_id) AS activity_count FROM activities x JOIN accounts a ON x.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计未关闭工单数量。","SELECT a.region, COUNT(c.case_id) AS open_case_count FROM cases c JOIN accounts a ON c.account_id=a.account_id WHERE c.status <> '已关闭' GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计平均客户健康分。","SELECT a.region, AVG(h.score) AS average_health_score FROM customer_health_scores h JOIN accounts a ON h.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计销售订单金额。","SELECT a.region, SUM(o.amount) AS order_amount FROM sales_orders o JOIN accounts a ON o.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计合同金额。","SELECT a.region, SUM(c.amount) AS contract_amount FROM contracts c JOIN accounts a ON c.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按客户区域统计发票金额。","SELECT a.region, SUM(i.amount) AS invoice_amount FROM invoices i JOIN accounts a ON i.account_id=a.account_id GROUP BY a.region ORDER BY a.region"),
      ("按产品分类统计产品数量和产品金额。","SELECT c.region, COUNT(p.product_id) AS product_count, SUM(p.amount) AS total_amount FROM products p JOIN product_categories c ON p.product_category_id=c.product_category_id GROUP BY c.region ORDER BY c.region"),
      ("按销售人员区域统计负责商机数量。","SELECT u.region, COUNT(o.opportunity_id) AS opportunity_count FROM opportunities o JOIN crm_users u ON o.owner_user_id=u.user_id GROUP BY u.region ORDER BY u.region"),
      ("按营销活动统计活动成员数量。","SELECT c.record_name AS campaign_name, COUNT(m.campaign_member_id) AS member_count FROM campaign_members m JOIN campaigns c ON m.campaign_id=c.campaign_id GROUP BY c.record_name ORDER BY campaign_name"),
      ("按商机状态统计报价单数量和金额。","SELECT o.status, COUNT(q.quote_id) AS quote_count, SUM(q.amount) AS total_amount FROM quotes q JOIN opportunities o ON q.opportunity_id=o.opportunity_id GROUP BY o.status ORDER BY o.status"),
      ("按合同状态统计续约数量和续约金额。","SELECT c.status, COUNT(r.renewal_id) AS renewal_count, SUM(r.amount) AS renewal_amount FROM renewals r JOIN contracts c ON r.contract_id=c.contract_id GROUP BY c.status ORDER BY c.status"),
    ]
    for question, sql in joins:
        out.append(q(n,"relationship",question,sql)); n+=1
    assert len(out)==100
    return out

def normalize(v):
    if isinstance(v, decimal.Decimal): return format(v, "f")
    if isinstance(v, (datetime.date, datetime.datetime)): return v.isoformat()
    if isinstance(v, dict): return {k: normalize(v[k]) for k in sorted(v)}
    if isinstance(v, list): return [normalize(x) for x in v]
    return v

def conn():
    return pymysql.connect(host=os.environ["MYSQL_HOST"],port=int(os.environ["MYSQL_PORT"]),user=os.environ["MYSQL_USER"],password=os.environ["MYSQL_PASSWORD"],database=os.environ["MYSQL_DATABASE"],charset="utf8mb4",cursorclass=pymysql.cursors.DictCursor)

if sys.argv[1] == "generate":
    ROOT.mkdir(parents=True, exist_ok=True)
    with conn() as c, c.cursor() as cur, open(ROOT/"crm_100_qna.jsonl","w",encoding="utf-8") as f:
        for item in tests():
            cur.execute(item["gold_sql"])
            item["gold_answer"] = normalize(cur.fetchall())
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True)+"\n")
    print("generated=100")
else:
    raise SystemExit("usage: benchmark.py generate")
