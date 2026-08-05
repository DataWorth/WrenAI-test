from datetime import date, timedelta

specs = [
 ("organizations","organization_id",[],1),
 ("departments","department_id",[("organization_id","organizations","organization_id")],6),
 ("territories","territory_id",[],5),
 ("teams","team_id",[("department_id","departments","department_id"),("territory_id","territories","territory_id")],10),
 ("crm_users","user_id",[("team_id","teams","team_id")],12),
 ("roles","role_id",[],5),
 ("user_roles","user_role_id",[("user_id","crm_users","user_id"),("role_id","roles","role_id")],20),
 ("accounts","account_id",[("territory_id","territories","territory_id"),("owner_user_id","crm_users","user_id")],120),
 ("account_addresses","account_address_id",[("account_id","accounts","account_id")],120),
 ("contacts","contact_id",[("account_id","accounts","account_id"),("owner_user_id","crm_users","user_id")],300),
 ("contact_addresses","contact_address_id",[("contact_id","contacts","contact_id")],300),
 ("tags","tag_id",[],8),
 ("account_tags","account_tag_id",[("account_id","accounts","account_id"),("tag_id","tags","tag_id")],180),
 ("contact_tags","contact_tag_id",[("contact_id","contacts","contact_id"),("tag_id","tags","tag_id")],240),
 ("account_status_history","account_status_history_id",[("account_id","accounts","account_id"),("changed_by_user_id","crm_users","user_id")],180),
 ("lead_sources","lead_source_id",[],5),
 ("lead_statuses","lead_status_id",[],5),
 ("campaigns","campaign_id",[("owner_user_id","crm_users","user_id")],40),
 ("nurture_sequences","nurture_sequence_id",[],4),
 ("leads","lead_id",[("lead_source_id","lead_sources","lead_source_id"),("lead_status_id","lead_statuses","lead_status_id"),("assigned_user_id","crm_users","user_id"),("nurture_sequence_id","nurture_sequences","nurture_sequence_id")],400),
 ("lead_assignments","lead_assignment_id",[("lead_id","leads","lead_id"),("assigned_user_id","crm_users","user_id")],400),
 ("campaign_members","campaign_member_id",[("campaign_id","campaigns","campaign_id"),("lead_id","leads","lead_id")],240),
 ("opportunity_stages","opportunity_stage_id",[],6),
 ("product_categories","product_category_id",[],5),
 ("products","product_id",[("product_category_id","product_categories","product_category_id")],40),
 ("price_books","price_book_id",[],2),
 ("price_book_items","price_book_item_id",[("price_book_id","price_books","price_book_id"),("product_id","products","product_id")],80),
 ("opportunities","opportunity_id",[("account_id","accounts","account_id"),("lead_id","leads","lead_id"),("owner_user_id","crm_users","user_id"),("opportunity_stage_id","opportunity_stages","opportunity_stage_id")],220),
 ("opportunity_contacts","opportunity_contact_id",[("opportunity_id","opportunities","opportunity_id"),("contact_id","contacts","contact_id")],300),
 ("opportunity_products","opportunity_product_id",[("opportunity_id","opportunities","opportunity_id"),("product_id","products","product_id")],500),
 ("quotes","quote_id",[("opportunity_id","opportunities","opportunity_id"),("price_book_id","price_books","price_book_id"),("owner_user_id","crm_users","user_id")],160),
 ("quote_items","quote_item_id",[("quote_id","quotes","quote_id"),("product_id","products","product_id")],360),
 ("lead_conversions","lead_conversion_id",[("lead_id","leads","lead_id"),("account_id","accounts","account_id"),("contact_id","contacts","contact_id"),("opportunity_id","opportunities","opportunity_id")],90),
 ("sales_orders","sales_order_id",[("account_id","accounts","account_id"),("opportunity_id","opportunities","opportunity_id"),("quote_id","quotes","quote_id"),("owner_user_id","crm_users","user_id")],130),
 ("sales_order_items","sales_order_item_id",[("sales_order_id","sales_orders","sales_order_id"),("product_id","products","product_id")],300),
 ("contracts","contract_id",[("account_id","accounts","account_id"),("opportunity_id","opportunities","opportunity_id"),("owner_user_id","crm_users","user_id")],90),
 ("contract_lines","contract_line_id",[("contract_id","contracts","contract_id"),("product_id","products","product_id")],200),
 ("invoices","invoice_id",[("account_id","accounts","account_id"),("contract_id","contracts","contract_id")],110),
 ("invoice_lines","invoice_line_id",[("invoice_id","invoices","invoice_id"),("product_id","products","product_id")],250),
 ("payments","payment_id",[("invoice_id","invoices","invoice_id")],95),
 ("activities","activity_id",[("account_id","accounts","account_id"),("contact_id","contacts","contact_id"),("opportunity_id","opportunities","opportunity_id"),("owner_user_id","crm_users","user_id")],600),
 ("activity_participants","activity_participant_id",[("activity_id","activities","activity_id"),("user_id","crm_users","user_id")],600),
 ("tasks","task_id",[("account_id","accounts","account_id"),("opportunity_id","opportunities","opportunity_id"),("owner_user_id","crm_users","user_id")],220),
 ("notes","note_id",[("account_id","accounts","account_id"),("contact_id","contacts","contact_id"),("opportunity_id","opportunities","opportunity_id"),("author_user_id","crm_users","user_id")],220),
 ("email_messages","email_message_id",[("account_id","accounts","account_id"),("contact_id","contacts","contact_id"),("opportunity_id","opportunities","opportunity_id"),("owner_user_id","crm_users","user_id")],260),
 ("email_events","email_event_id",[("email_message_id","email_messages","email_message_id")],480),
 ("meetings","meeting_id",[("account_id","accounts","account_id"),("opportunity_id","opportunities","opportunity_id"),("organizer_user_id","crm_users","user_id")],100),
 ("meeting_attendees","meeting_attendee_id",[("meeting_id","meetings","meeting_id"),("contact_id","contacts","contact_id")],200),
 ("cases","case_id",[("account_id","accounts","account_id"),("contact_id","contacts","contact_id"),("owner_user_id","crm_users","user_id")],130),
 ("case_comments","case_comment_id",[("case_id","cases","case_id"),("author_user_id","crm_users","user_id")],260),
 ("case_status_history","case_status_history_id",[("case_id","cases","case_id"),("changed_by_user_id","crm_users","user_id")],260),
 ("knowledge_articles","knowledge_article_id",[("owner_user_id","crm_users","user_id")],60),
 ("customer_health_scores","health_score_id",[("account_id","accounts","account_id")],180),
 ("renewals","renewal_id",[("contract_id","contracts","contract_id"),("owner_user_id","crm_users","user_id")],80),
 ("satisfaction_surveys","satisfaction_survey_id",[("account_id","accounts","account_id"),("case_id","cases","case_id")],150),
]
regions = ["华东","华北","华南","华中","西南"]
industries = ["制造业","零售业","金融服务","信息技术","专业服务"]
sources = ["官网咨询","行业峰会","渠道伙伴","客户转介绍","内容营销"]
stages = ["需求确认","方案报价","商务谈判","合同审批","赢单","输单"]
statuses = ["新建","进行中","已完成","已关闭","待跟进"]
counts = {name: rows for name, _, _, rows in specs}

def esc(v):
    return "'" + str(v).replace("'", "''") + "'"

print("DROP DATABASE IF EXISTS crm_demo;")
print("CREATE DATABASE crm_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
print("USE crm_demo;")
for name, pk, parents, _ in specs:
    columns = [f"{pk} BIGINT NOT NULL", "record_name VARCHAR(180) NOT NULL", "status VARCHAR(40) NOT NULL", "region VARCHAR(30) NOT NULL", "source VARCHAR(60) NOT NULL", "industry VARCHAR(60) NOT NULL", "stage VARCHAR(60) NOT NULL", "amount DECIMAL(18,2) NOT NULL", "probability DECIMAL(6,2) NOT NULL", "quantity INT NOT NULL", "unit_price DECIMAL(18,2) NOT NULL", "score DECIMAL(8,2) NOT NULL", "created_at DATETIME NOT NULL"]
    columns += [f"{col} BIGINT NOT NULL" for col, _, _ in parents]
    columns += [f"PRIMARY KEY ({pk})"]
    print(f"CREATE TABLE {name} (" + ",".join(columns) + ") ENGINE=InnoDB;")

for name, pk, parents, rows in specs:
    cols = [pk, "record_name", "status", "region", "source", "industry", "stage", "amount", "probability", "quantity", "unit_price", "score", "created_at"] + [p[0] for p in parents]
    tuples = []
    for i in range(1, rows + 1):
        status = statuses[(i - 1) % len(statuses)]
        if name == "opportunities": status = "赢单" if i <= 55 else ("输单" if i <= 82 else "进行中")
        if name == "leads": status = "已转化" if i <= 90 else ("已合格" if i % 4 == 0 else "已联系")
        if name == "cases": status = ["新建","处理中","待客户反馈","已关闭"][(i-1)%4]
        stage = stages[(i - 1) % len(stages)]
        amount = 50000 + i * 6200
        probability = [20,45,70,85,100,0][(i-1)%6]
        row = [i, f"{name[:-1] if name.endswith('s') else name}-{i:04d}", status, regions[(i-1)%5], sources[(i-1)%5], industries[(i-1)%5], stage, f"{amount:.2f}", f"{probability:.2f}", (i-1)%5+1, f"{5000+((i-1)%40)*800:.2f}", f"{50+(i%50):.2f}", (date(2025,1,1)+timedelta(days=i)).isoformat() + " 09:00:00"]
        for _, parent, _ in parents:
            row.append((i-1) % counts[parent] + 1)
        tuples.append("(" + ",".join(esc(v) if isinstance(v, str) and not v.replace('.','',1).isdigit() else str(v) for v in row) + ")")
    print(f"INSERT INTO {name} (" + ",".join(cols) + ") VALUES " + ",".join(tuples) + ";")

for name, pk, parents, _ in specs:
    for col, parent, parent_pk in parents:
        print(f"ALTER TABLE {name} ADD CONSTRAINT fk_{name}_{col} FOREIGN KEY ({col}) REFERENCES {parent}({parent_pk});")
