# WrenAI 30表 CRM 语义构建与 Chat BI 测试报告

## 执行范围

- Run ID：`20260811T170540Z`
- 测试运行脚本提交：`d659d92f`
- Wren 源码基线：`74bf59e1d8400988f5269048cdeed983e77dc20d`
- Agent 镜像：`wrenai-test-agent:official-30-core-v1@sha256:625f5e366e2f2fb9a5153e0d255a2fdcd9b3ea76938eab5bb9b060a522c23dc4`
- Chat BI 模型：`qwen3.7-plus`
- 数据范围：CRM 30张核心表、46条内部外键；历史55表测试集未参与本次运行。
- 路径：先官方 `generate-mdl`，再官方 `enrich-context` Grill 真人逐题补充业务语义，随后 `validate`、`build`、MCP Chat BI 烟测和100题评测。

## 语义构建结果

- 模型文件：30
- 关系文件条目：46
- 知识文件：13
- Grill 记录的问答：19

| 模型 | 文件 | 字段项 | 描述 |
|---|---|---:|---|
| accounts | `models/accounts/metadata.yml` | 15 | 客户账户主表，记录企业客户的基本信息、所属行业、区域、状态及负责销售 |
| campaign_members | `models/campaign_members/metadata.yml` | 15 | 营销活动成员关联表，记录线索与营销活动的参与关系 |
| campaigns | `models/campaigns/metadata.yml` | 14 | 营销活动表，记录市场推广活动的基本信息、预算、负责人 |
| cases | `models/cases/metadata.yml` | 16 | 客户服务工单表，记录客户反馈的问题、处理进度、优先级 |
| contacts | `models/contacts/metadata.yml` | 15 | 联系人表，记录客户方的具体联系人信息（姓名、电话、邮箱等） |
| contracts | `models/contracts/metadata.yml` | 16 | 合同表，记录与客户签订的合同信息、关联商机、有效期 |
| crm_users | `models/crm_users/metadata.yml` | 14 | CRM 系统用户表，记录内部销售/客服人员的基本信息及所属团队 |
| departments | `models/departments/metadata.yml` | 14 | 部门表，记录公司组织架构中的部门信息 |
| invoices | `models/invoices/metadata.yml` | 15 | 发票表，记录向客户开具的发票信息、关联合同和账户 |
| lead_assignments | `models/lead_assignments/metadata.yml` | 15 | 线索分配记录表，记录线索分配给销售人员的历史 |
| lead_sources | `models/lead_sources/metadata.yml` | 13 | 线索来源字典表，定义线索的可能来源（如官网、展会等） |
| lead_statuses | `models/lead_statuses/metadata.yml` | 13 | 线索状态字典表，定义线索的生命周期状态 |
| leads | `models/leads/metadata.yml` | 17 | 线索主表，记录潜在客户的基本信息、来源、评分、意向度 |
| nurture_sequences | `models/nurture_sequences/metadata.yml` | 13 | 线索培育序列表，定义自动化培育计划（如邮件序列） |
| opportunities | `models/opportunities/metadata.yml` | 17 | 商机主表，记录销售机会的金额、阶段、赢率、负责销售 |
| opportunity_contacts | `models/opportunity_contacts/metadata.yml` | 15 | 商机联系人关联表，记录商机涉及的客户方联系人 |
| opportunity_products | `models/opportunity_products/metadata.yml` | 15 | 商机产品行项目表，记录商机包含的产品明细、数量、单价 |
| opportunity_stages | `models/opportunity_stages/metadata.yml` | 13 | 商机阶段字典表，定义销售漏斗的阶段（如需求确认、方案报价等） |
| organizations | `models/organizations/metadata.yml` | 13 | 组织表，记录运行 CRM 的公司本身的信息 |
| payments | `models/payments/metadata.yml` | 14 | 付款记录表，记录客户的付款信息、关联发票 |
| price_books | `models/price_books/metadata.yml` | 13 | 价格手册表，定义产品在不同市场/客户群体的标准价格 |
| product_categories | `models/product_categories/metadata.yml` | 13 | 产品类别字典表，定义产品的分类体系 |
| products | `models/products/metadata.yml` | 14 | 产品表，记录可销售的产品信息、类别、标准价格 |
| quotes | `models/quotes/metadata.yml` | 16 | 报价单表，记录向客户提供的报价信息、关联商机 |
| roles | `models/roles/metadata.yml` | 13 | 角色字典表，定义系统角色（如销售经理、销售代表等） |
| sales_order_items | `models/sales_order_items/metadata.yml` | 15 | 销售订单行项目表，记录订单包含的产品明细 |
| sales_orders | `models/sales_orders/metadata.yml` | 17 | 销售订单表，记录客户成交后的正式订单信息 |
| teams | `models/teams/metadata.yml` | 15 | 团队表，记录销售团队信息、所属部门和区域 |
| territories | `models/territories/metadata.yml` | 13 | 区域字典表，定义销售区域（如华北、华东等） |
| user_roles | `models/user_roles/metadata.yml` | 15 | 用户角色关联表，记录用户与角色的多对多关系 |

### 业务语义问答

| 问题 | 业务负责人回答 |
|---|---|
| Which Wren project do you want me to augment for this session? (Locked for the whole session — re-run the skill to change.) | /workspace (Recommended)（选项 1） |
| [Lane 1+3 · MDL 列描述] 所有 30 个表都带 amount 列，但在不同表上语义不同。我猜 — 对 opportunities/quotes/sales_orders/invoices 是预期/合同/发票金额；对 opportunity_products/sales_order_items 是行小计；对 accounts 是客户累计交易额；其他表(cases/contacts/leads/roles/...)上的 amount 是模板污染。推荐按“每表各有所指”写描述，非交易表标注为“模板字段，业务上忽略”。接受吗？ | 每个表各有所指(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] probability 列在所有 30 表上都存在，类型 DECIMAL(6,2)。我猜 — 它是 0–100 百分比(而非 0–1 小数)，按表各有所指：opportunities = 嬴单率；leads = 转化率；quotes/contracts = 签约概率；accounts = 加权概率；其他表 = 模板字段忽略。接受吗？ | 0–100 百分比，按表各有所指(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] quantity(INT) 和 unit_price(DECIMAL(18,2)) 同样在所有 30 表上存在。我猜 — 它们只在行项目表(opportunity_products/sales_order_items/quotes报价行)有业务意义：行数量 × 行单价 = 行小计；其他表的 quantity/unit_price = 模板字段，业务忽略。接受吗？ | 仅 opportunity_products 和 sales_order_items 的 quantity/unit_price 有行项目意义，amount=quantity×unit_price；quotes 是报价单头表，仅amount有意义，quantity/unit_price忽略；其余表也忽略。 |
| [Lane 3 · MDL 列描述] score(DECIMAL(8,2)) 列在所有 30 表上存在。我猜 — 它仅在 opportunities/leads/accounts 上有业务义：商机优先级分 / 线索热度分 / 客户价值分，范围 0–100；其他表 = 模板字段忽略。接受吗？ | 商机/线索/账户的优先级分(推荐)（选项 1） |
| [Lane 3 · knowledge/rules/#9 Currency + MDL [currency] tag] 本 CRM 所有金额列(amount/unit_price) 的默认币种是什么？我猜 — 人民币 CNY(因为整个 CRM 业务上下文是中文且针对中国市场)。 | 人民币 CNY(推荐)（选项 1） |
| [Lane 3 · MDL [time] tag] 所有 30 表的 created_at(DATETIME) 是什么时区？我猜 — Asia/Shanghai (UTC+8)，精度到秒。 | Asia/Shanghai, 秒精度(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] record_name(VARCHAR(180)) 列在所有 30 表上存在，当前描述“记录名称/编号（业务主键显示名）”。我猜 — 它是每张表的默认显示字段，内容按表义不同(accounts = 客户名, contacts = 联系人姓名, opportunities = 商机名称, cases = 工单主题, sales_orders = 订单编号...)。接受吗？ | 实体特定可读名(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] stage(VARCHAR(60)) 与枚举“商务谈判/合同审批/方案报价/输单/需求确认/赢单”在所有 30 表上都相同。我猜 — 它是销售管线阶段，仅在销售实体(accounts/leads/opportunities/quotes/contracts/sales_orders)有意义，其他表 = 模板字段，业务忽略。接受吗？ | 销售表专有，其他表忽略(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] source(VARCHAR(60)) 与枚举“内容营销/官网咨询/客户转介绍/渠道伙伴/行业峰会”在所有 30 表上存在。我猜 — source 原始记录在 leads 上，当 lead 转化为 account/opportunity/contact 时被继承下去；其他无关表(cases/products/roles)的 source = 模板字段。接受吗？ | 继承自 lead，仅销售链有义(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] region(VARCHAR(30)) 与枚举“华南/华中/华东/华北/西南”在所有 30 表上存在。我猜 — 权威来源是 accounts(客户注册地) 和 leads(线索所在地区)，其他销售链(opportunities/cases/contacts/sales_orders)从 accounts 继承；用户/领地/团队/活动有自己的 region；产品/角色/部门 = 模板字段。接受吗？ | accounts/leads 权威，销售链继承(推荐)（选项 1） |
| [Lane 3 · MDL 列描述] industry 是否遵循与 region 完全相同的传播模式？我猜 — 是：accounts/leads 权威，销售链继承，参考表忽略。 | 与 region 同样模式(推荐)（选项 1） |
| [Lane 3 · MDL [magic] tag] 所有数值列(amount, probability, quantity, unit_price, score) 都是 NOT NULL，但许多表上这些列是模板污染。那些表上的 0 / 0.00 代表什么？我猜 — 就是字面 0，业务上靠“哪张表该列有意义”来区分，不需要靠 0 值过滤。接受吗？ | 0 = 字面 0，不过滤(推荐)（选项 1） |
| [Lane 1 · knowledge/rules/#4 Default filters] 本 CRM 没有 deleted_at/is_active 列，但 status 列含“已关闭”“输单”等终态值。是否需要设置默认过滤规则？我猜 — 不需要：所有 status 值默认包含，因为终态记录在报表中有分析价值(如完成率/输单分析)。接受吗？ | 不过滤(推荐)（选项 1） |
| [Lane 3 · knowledge/rules/#6 Naming conventions] 业务用户常说“客户”“商机”“工单”等术语，与表名(accounts/opportunities/cases)不匹配。我猜 — 应加以下同义词规则：客户=accounts, 联系人=contacts, 线索=leads, 商机=opportunities, 工单=cases, 合同=contracts, 订单=sales_orders, 报价=quotes, 发票=invoices, 回款=payments, 营销活动=campaigns, 产品=products, 销售/用户=crm_users。接受吗？ | 接受推荐清单(推荐)（选项 1） |
| [Lane 1 · knowledge/rules/#8 External identifiers] MDL 中未见到 *_external_id 或类似跨系统 ID 列。本 CRM 是否有与外部系统(ERP/SAP/HR)的主键同步关系？我猜 — 没有，*_id 就是权威主键。 | 无外部系统同步(推荐)（选项 1） |
| [Lane 3 · cubes/pipeline] 典型 CRM 项目常需要管线分析。我猜 — 应创建一个 pipeline cube：base_object = opportunities，度量 = SUM(amount)(总管线) 和 SUM(amount × probability / 100)(加权预期收入)，维度 = stage/region/owner_user_id/created_at(按月)。接受吗？ | 创建(推荐)（选项 1） |
| [Lane 3 · cubes/win_loss] 我猜 — 还应创建 win_loss cube：base_object = opportunities，度量 = 嬴单数/输单数/总商机数(三个 COUNT)，运行时可算 嬴单率 = 嬴单数/(嬴单数+输单数)。维度 = region/owner/source/industry/created_at(按月)。接受吗？ | 跳过（选项 2） |
| [Lane 3 · cubes] 除了 pipeline 外，还需要创建其他 Cube 吗(如 revenue 收入、case_resolution 工单解决、lead_conversion 线索转化)？我猜 — 不需要，现有 pipeline cube + 原始 MDL + knowledge/sql/ NL→SQL 示例 已足够。 | 不再创建 Cube(推荐)（选项 1） |

### 知识文件

- `knowledge/caveats/.gitkeep`
- `knowledge/caveats/chinese_encoding_issue.md`
- `knowledge/glossary/.gitkeep`
- `knowledge/knowledge.yml`
- `knowledge/metrics/.gitkeep`
- `knowledge/rules/.gitkeep`
- `knowledge/rules/conventions.md`
- `knowledge/sql/.gitkeep`
- `knowledge/sql/pipeline-cube.md`
- `knowledge/sql/query-2.md`
- `knowledge/sql/query-3.md`
- `knowledge/sql/query-4.md`
- `knowledge/sql/query.md`

## Chat BI 结果

- 测试题数：100
- SQL可运行：100/100
- 精确答案：47/100 (47.00%)
- 值集合匹配：73/100 (73.00%)
- 官方 usage 指南已加载：99/100

| 类别 | 题数 | SQL可运行 | 精确答案 | 值集合匹配 |
|---|---:|---:|---:|---:|
| region_amount | 15 | 15 | 3 | 3 |
| relationship | 15 | 15 | 6 | 10 |
| single_count | 30 | 30 | 11 | 27 |
| stage_amount | 15 | 15 | 5 | 9 |
| status_distribution | 25 | 25 | 22 | 24 |

### 每题结果

| ID | 类别 | 问题 | 候选SQL | SQL可运行 | 精确答案 | 值集合匹配 | 错误 |
|---:|---|---|---|:---:|:---:|:---:|---|
| 1 | single_count | 统计组织的记录数。 | `SELECT COUNT(*) AS organization_count FROM organizations` | 是 | 否 | 是 |  |
| 2 | single_count | 统计部门的记录数。 | `SELECT region, COUNT(*) AS record_count FROM departments GROUP BY region ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 3 | single_count | 统计销售辖区的记录数。 | `SELECT COUNT(*) AS record_count FROM territories` | 是 | 是 | 是 |  |
| 4 | single_count | 统计团队的记录数。 | `SELECT COUNT(*) AS record_count FROM teams` | 是 | 是 | 是 |  |
| 5 | single_count | 统计CRM用户的记录数。 | `SELECT COUNT(*) AS user_count FROM crm_users` | 是 | 否 | 是 |  |
| 6 | single_count | 统计角色的记录数。 | `SELECT COUNT(*) AS role_count FROM roles` | 是 | 否 | 是 |  |
| 7 | single_count | 统计用户角色分配的记录数。 | `SELECT COUNT(*) AS user_role_count FROM user_roles` | 是 | 否 | 是 |  |
| 8 | single_count | 统计客户的记录数。 | `SELECT COUNT(*) AS customer_count FROM accounts` | 是 | 否 | 是 |  |
| 9 | single_count | 统计联系人的记录数。 | `SELECT COUNT(*) AS contact_count FROM contacts` | 是 | 否 | 是 |  |
| 10 | single_count | 统计线索来源的记录数。 | `SELECT source, COUNT(*) AS record_count FROM leads GROUP BY source ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 11 | single_count | 统计线索状态的记录数。 | `SELECT status, COUNT(*) AS record_count FROM leads GROUP BY status ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 12 | single_count | 统计线索培育序列的记录数。 | `SELECT COUNT(*) AS record_count FROM nurture_sequences` | 是 | 是 | 是 |  |
| 13 | single_count | 统计线索的记录数。 | `SELECT COUNT(*) FROM leads` | 是 | 否 | 是 |  |
| 14 | single_count | 统计线索分配的记录数。 | `SELECT COUNT(*) AS lead_assignment_count FROM lead_assignments` | 是 | 否 | 是 |  |
| 15 | single_count | 统计营销活动的记录数。 | `SELECT COUNT(*) AS record_count FROM campaigns` | 是 | 是 | 是 |  |
| 16 | single_count | 统计活动成员的记录数。 | `SELECT COUNT(*) AS campaign_member_count FROM campaign_members` | 是 | 否 | 是 |  |
| 17 | single_count | 统计商机阶段的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunity_stages` | 是 | 是 | 是 |  |
| 18 | single_count | 统计产品分类的记录数。 | `SELECT COUNT(*) AS record_count FROM product_categories` | 是 | 是 | 是 |  |
| 19 | single_count | 统计产品的记录数。 | `SELECT COUNT(*) AS product_count FROM products` | 是 | 否 | 是 |  |
| 20 | single_count | 统计价目表的记录数。 | `SELECT COUNT(*) AS total_count FROM price_books` | 是 | 否 | 是 |  |
| 21 | single_count | 统计商机的记录数。 | `SELECT COUNT(*) AS opportunity_count FROM opportunities` | 是 | 否 | 是 |  |
| 22 | single_count | 统计商机联系人的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunity_contacts` | 是 | 是 | 是 |  |
| 23 | single_count | 统计商机产品的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunity_products` | 是 | 是 | 是 |  |
| 24 | single_count | 统计报价单的记录数。 | `SELECT COUNT(*) AS record_count FROM quotes` | 是 | 是 | 是 |  |
| 25 | single_count | 统计销售订单的记录数。 | `SELECT COUNT(*) AS order_count FROM sales_orders` | 是 | 否 | 是 |  |
| 26 | single_count | 统计销售订单明细的记录数。 | `SELECT COUNT(*) AS record_count FROM sales_order_items` | 是 | 是 | 是 |  |
| 27 | single_count | 统计合同的记录数。 | `SELECT COUNT(contract_id) AS contract_count FROM contracts` | 是 | 否 | 是 |  |
| 28 | single_count | 统计发票的记录数。 | `SELECT COUNT(*) FROM invoices` | 是 | 否 | 是 |  |
| 29 | single_count | 统计回款的记录数。 | `SELECT COUNT(*) AS payment_record_count FROM payments` | 是 | 否 | 是 |  |
| 30 | single_count | 统计客服工单的记录数。 | `SELECT COUNT(*) AS record_count FROM cases` | 是 | 是 | 是 |  |
| 31 | status_distribution | 按状态统计组织的记录数。 | `SELECT status, COUNT(*) AS record_count FROM organizations GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 32 | status_distribution | 按状态统计部门的记录数。 | `SELECT status, COUNT(*) AS record_count FROM departments GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 33 | status_distribution | 按状态统计销售辖区的记录数。 | `SELECT status, COUNT(*) AS record_count FROM territories GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 34 | status_distribution | 按状态统计团队的记录数。 | `SELECT status, COUNT(*) AS record_count FROM teams GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 35 | status_distribution | 按状态统计CRM用户的记录数。 | `SELECT status, COUNT(*) AS record_count FROM crm_users GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 36 | status_distribution | 按状态统计角色的记录数。 | `SELECT status, COUNT(*) AS record_count FROM roles GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 37 | status_distribution | 按状态统计用户角色分配的记录数。 | `SELECT status, COUNT(*) AS record_count FROM user_roles GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 38 | status_distribution | 按状态统计客户的记录数。 | `SELECT status, COUNT(*) AS record_count FROM accounts GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 39 | status_distribution | 按状态统计联系人的记录数。 | `SELECT status, COUNT(*) AS record_count FROM contacts GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 40 | status_distribution | 按状态统计线索来源的记录数。 | `SELECT status, COUNT(*) AS record_count FROM lead_sources GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 41 | status_distribution | 按状态统计线索状态的记录数。 | `SELECT status, COUNT(*) AS record_count FROM leads GROUP BY status ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 42 | status_distribution | 按状态统计线索培育序列的记录数。 | `SELECT status, COUNT(*) AS record_count FROM nurture_sequences GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 43 | status_distribution | 按状态统计线索的记录数。 | `SELECT leads.status AS "线索状态", COUNT(*) AS "记录数" FROM leads GROUP BY leads.status ORDER BY "记录数" DESC` | 是 | 否 | 是 |  |
| 44 | status_distribution | 按状态统计线索分配的记录数。 | `SELECT status, COUNT(*) AS record_count FROM lead_assignments GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 45 | status_distribution | 按状态统计营销活动的记录数。 | `SELECT status, COUNT(*) AS campaign_count FROM campaigns GROUP BY status ORDER BY campaign_count DESC` | 是 | 否 | 是 |  |
| 46 | status_distribution | 按状态统计活动成员的记录数。 | `SELECT status, COUNT(*) AS record_count FROM campaign_members GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 47 | status_distribution | 按状态统计商机阶段的记录数。 | `SELECT status, COUNT(*) AS record_count FROM opportunity_stages GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 48 | status_distribution | 按状态统计产品分类的记录数。 | `SELECT status, COUNT(*) AS record_count FROM product_categories GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 49 | status_distribution | 按状态统计产品的记录数。 | `SELECT status, COUNT(*) AS record_count FROM products GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 50 | status_distribution | 按状态统计价目表的记录数。 | `SELECT status, COUNT(*) AS record_count FROM price_books GROUP BY status` | 是 | 是 | 是 |  |
| 51 | status_distribution | 按状态统计商机的记录数。 | `SELECT status, COUNT(*) AS record_count FROM opportunities GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 52 | status_distribution | 按状态统计商机联系人的记录数。 | `SELECT status, COUNT(*) AS record_count FROM opportunity_contacts GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 53 | status_distribution | 按状态统计商机产品的记录数。 | `SELECT status, COUNT(*) AS record_count FROM opportunity_products GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 54 | status_distribution | 按状态统计报价单的记录数。 | `SELECT status, COUNT(*) AS record_count FROM quotes GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 55 | status_distribution | 按状态统计销售订单的记录数。 | `SELECT status, COUNT(*) AS record_count<br>FROM sales_orders<br>GROUP BY status<br>ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 56 | region_amount | 按区域汇总组织的金额。 | `SELECT region, SUM(amount) AS total_amount FROM accounts GROUP BY region ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 57 | region_amount | 按区域汇总部门的金额。 | `SELECT departments.region AS 区域, departments.record_name AS 部门, SUM(departments.amount) AS 金额 FROM departments GROUP BY departments.region, departments.record_name ORDER BY 区域, 部门` | 是 | 否 | 否 |  |
| 58 | region_amount | 按区域汇总销售辖区的金额。 | `SELECT territories.region, SUM(accounts.amount) AS total_amount FROM accounts JOIN territories ON accounts.territory_id = territories.territory_id GROUP BY territories.region` | 是 | 否 | 否 |  |
| 59 | region_amount | 按区域汇总团队的金额。 | `SELECT t.region AS team_region, SUM(o.amount) AS total_amount<br>FROM opportunities o<br>JOIN crm_users u ON o.owner_user_id = u.user_id<br>JOIN teams t ON u.team_id = t.team_id<br>GROUP BY t.region<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 60 | region_amount | 按区域汇总CRM用户的金额。 | `SELECT crm_users.region, HEX(crm_users.region) AS region_hex FROM crm_users GROUP BY crm_users.region` | 是 | 否 | 否 |  |
| 61 | region_amount | 按区域汇总角色的金额。 | `SELECT accounts.region, roles.record_name, SUM(accounts.amount) AS total_amount<br>FROM accounts<br>JOIN crm_users ON accounts.owner_user_id = crm_users.user_id<br>JOIN user_roles ON crm_users.user_id = user_roles.user_id<br>JOIN roles ON user_roles.role_id = roles.role_id<br>GROUP BY accounts.region, roles.record_name<br>ORDER BY accounts.region, total_amount DESC` | 是 | 否 | 否 |  |
| 62 | region_amount | 按区域汇总用户角色分配的金额。 | `SELECT<br>  accounts.region,<br>  roles.record_name AS role_name,<br>  SUM(accounts.amount) AS total_amount<br>FROM accounts<br>JOIN crm_users ON accounts.owner_user_id = crm_users.user_id<br>JOIN user_roles ON crm_users.user_id = user_roles.user_id<br>JOIN roles ON user_roles.role_id = roles.role_id<br>GROUP BY accounts.region, roles.record_name<br>ORDER BY accounts.region, total_amount DESC` | 是 | 否 | 否 |  |
| 63 | region_amount | 按区域汇总客户的金额。 | `SELECT region, SUM(amount) AS total_amount FROM accounts GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 64 | region_amount | 按区域汇总联系人的金额。 | `SELECT contacts.region, SUM(accounts.amount) AS total_amount<br>FROM contacts<br>JOIN accounts ON contacts.account_id = accounts.account_id<br>GROUP BY contacts.region<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 65 | region_amount | 按区域汇总线索来源的金额。 | `SELECT region AS region, source AS source, SUM(amount) AS total_amount FROM opportunities GROUP BY 1, 2` | 是 | 否 | 否 |  |
| 66 | region_amount | 按区域汇总线索状态的金额。 | `SELECT region, status, SUM(amount) AS total_amount FROM opportunities GROUP BY region, status ORDER BY region, total_amount DESC` | 是 | 否 | 否 |  |
| 67 | region_amount | 按区域汇总线索培育序列的金额。 | `SELECT region, SUM(amount) AS total_amount FROM nurture_sequences GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 68 | region_amount | 按区域汇总线索的金额。 | `SELECT DISTINCT region FROM opportunities ORDER BY region` | 是 | 否 | 否 |  |
| 69 | region_amount | 按区域汇总线索分配的金额。 | `SELECT l.region, SUM(o.amount) AS total_amount<br>FROM lead_assignments la<br>JOIN leads l ON la.lead_id = l.lead_id<br>JOIN opportunities o ON o.lead_id = l.lead_id<br>GROUP BY l.region<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 70 | region_amount | 按区域汇总营销活动的金额。 | `SELECT region, SUM(amount) AS total_amount FROM campaigns GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 71 | stage_amount | 按阶段统计活动成员的记录数和金额。 | `SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM campaign_members GROUP BY stage ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 72 | stage_amount | 按阶段统计商机阶段的记录数和金额。 | `SELECT HEX(stage) AS stage_hex, COUNT(*) AS count, SUM(amount) AS total_amount FROM opportunities GROUP BY 1 ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 73 | stage_amount | 按阶段统计产品分类的记录数和金额。 | `SELECT<br>  opportunities.stage,<br>  product_categories.record_name AS product_category,<br>  COUNT(*) AS record_count,<br>  SUM(opportunity_products.amount) AS total_amount<br>FROM opportunity_products<br>JOIN opportunities ON opportunity_products.opportunity_id = opportunities.opportunity_id<br>JOIN products ON opportunity_products.product_id = products.product_id<br>JOIN product_categories ON products.product_category_id = product_categories.product_category_id<br>GROUP BY opportunities.stage, product_categories.record_name<br>ORDER BY opportunities.stage, total_amount DESC` | 是 | 否 | 否 |  |
| 74 | stage_amount | 按阶段统计产品的记录数和金额。 | `SELECT <br>  opportunities.stage,<br>  COUNT(*) AS record_count,<br>  SUM(opportunity_products.amount) AS total_amount<br>FROM opportunity_products<br>JOIN opportunities ON opportunity_products.opportunity_id = opportunities.opportunity_id<br>GROUP BY opportunities.stage<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 75 | stage_amount | 按阶段统计价目表的记录数和金额。 | `SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM price_books GROUP BY stage ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 76 | stage_amount | 按阶段统计商机的记录数和金额。 | `SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM opportunities GROUP BY stage ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 77 | stage_amount | 按阶段统计商机联系人的记录数和金额。 | `SELECT o.stage,<br>       COUNT(oc.opportunity_contact_id) AS record_count,<br>       SUM(o.amount) AS total_amount<br>FROM opportunity_contacts oc<br>JOIN opportunities o ON oc.opportunity_id = o.opportunity_id<br>GROUP BY o.stage<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 78 | stage_amount | 按阶段统计商机产品的记录数和金额。 | `SELECT <br>  opportunities.stage,<br>  COUNT(opportunity_products.opportunity_product_id) AS record_count,<br>  SUM(opportunity_products.amount) AS total_amount<br>FROM opportunity_products<br>JOIN opportunities ON opportunity_products.opportunity_id = opportunities.opportunity_id<br>GROUP BY opportunities.stage<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 79 | stage_amount | 按阶段统计报价单的记录数和金额。 | `SELECT stage, COUNT(*) AS quote_count, SUM(amount) AS total_amount FROM quotes GROUP BY stage ORDER BY total_amount DESC` | 是 | 否 | 是 |  |
| 80 | stage_amount | 按阶段统计销售订单的记录数和金额。 | `SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM sales_orders GROUP BY stage ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 81 | stage_amount | 按阶段统计销售订单明细的记录数和金额。 | `SELECT <br>    sales_orders.stage,<br>    COUNT(sales_order_items.sales_order_item_id) AS record_count,<br>    SUM(sales_order_items.amount) AS total_amount<br>FROM sales_order_items<br>JOIN sales_orders ON sales_order_items.sales_order_id = sales_orders.sales_order_id<br>GROUP BY sales_orders.stage<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 82 | stage_amount | 按阶段统计合同的记录数和金额。 | `SELECT stage, COUNT(*) AS contract_count, SUM(amount) AS total_amount FROM contracts GROUP BY stage ORDER BY total_amount DESC` | 是 | 否 | 是 |  |
| 83 | stage_amount | 按阶段统计发票的记录数和金额。 | `SELECT stage, COUNT(*) AS invoice_count, SUM(amount) AS total_amount FROM invoices GROUP BY stage ORDER BY total_amount DESC` | 是 | 否 | 是 |  |
| 84 | stage_amount | 按阶段统计回款的记录数和金额。 | `SELECT<br>  stage AS "阶段",<br>  COUNT(*) AS "回款记录数",<br>  SUM(amount) AS "回款金额"<br>FROM payments<br>GROUP BY stage<br>ORDER BY SUM(amount) DESC` | 是 | 否 | 是 |  |
| 85 | stage_amount | 按阶段统计客服工单的记录数和金额。 | `SELECT stage, COUNT(*) AS record_count, SUM(amount) AS total_amount FROM cases GROUP BY stage ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 86 | relationship | 按客户区域统计商机数量与商机金额。 | `SELECT region, COUNT(*) AS opportunity_count, SUM(amount) AS total_amount FROM opportunities GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 87 | relationship | 按商机阶段统计商机数量和加权管道金额。 | `SELECT stage, COUNT(*) AS count, SUM(amount * probability / 100) AS weighted_amount FROM opportunities GROUP BY stage ORDER BY weighted_amount DESC` | 是 | 否 | 否 |  |
| 88 | relationship | 按线索来源统计线索数量和金额。 | `SELECT<br>  leads.source AS lead_source,<br>  COUNT(*) AS lead_count,<br>  SUM(leads.amount) AS total_amount<br>FROM leads<br>GROUP BY leads.source<br>ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 89 | relationship | 按客户区域统计联系人数量。 | `SELECT region, COUNT(contact_id) AS contact_count FROM contacts GROUP BY region ORDER BY contact_count DESC` | 是 | 是 | 是 |  |
| 90 | relationship | 按客户区域统计销售订单金额。 | `SELECT accounts.region, SUM(sales_orders.amount) AS total_amount<br>FROM sales_orders<br>JOIN accounts ON sales_orders.account_id = accounts.account_id<br>GROUP BY accounts.region<br>ORDER BY total_amount DESC` | 是 | 否 | 是 |  |
| 91 | relationship | 按客户区域统计未关闭工单数量。 | `SELECT region, COUNT(*) AS open_case_count FROM cases WHERE status != '已关闭' GROUP BY region ORDER BY open_case_count DESC` | 是 | 是 | 是 |  |
| 92 | relationship | 按销售辖区统计客户数量。 | `SELECT t.record_name, t.region, COUNT(a.account_id) AS customer_count<br>FROM accounts a<br>JOIN territories t ON a.territory_id = t.territory_id<br>GROUP BY t.record_name, t.region<br>ORDER BY t.record_name` | 是 | 否 | 否 |  |
| 93 | relationship | 按客户区域统计合同金额。 | `SELECT contracts.region, SUM(contracts.amount) AS total_amount FROM contracts GROUP BY contracts.region ORDER BY total_amount DESC` | 是 | 否 | 是 |  |
| 94 | relationship | 按客户区域统计发票金额。 | `SELECT region, SUM(amount) AS total_invoice_amount FROM invoices GROUP BY region ORDER BY total_invoice_amount DESC` | 是 | 否 | 是 |  |
| 95 | relationship | 按客户区域统计回款金额。 | `SELECT accounts.region, SUM(payments.amount) AS payment_total FROM payments JOIN invoices ON payments.invoice_id = invoices.invoice_id JOIN accounts ON invoices.account_id = accounts.account_id GROUP BY accounts.region ORDER BY payment_total DESC` | 是 | 否 | 是 |  |
| 96 | relationship | 按产品分类统计产品数量和产品金额。 | `SELECT pc.record_name AS product_category, COUNT(p.product_id) AS product_count, SUM(p.amount) AS total_amount FROM products p JOIN product_categories pc ON p.product_category_id = pc.product_category_id GROUP BY pc.record_name ORDER BY total_amount DESC` | 是 | 否 | 否 |  |
| 97 | relationship | 按销售人员区域统计负责商机数量。 | `SELECT crm_users.region, COUNT(opportunities.opportunity_id) AS opportunity_count<br>FROM opportunities<br>JOIN crm_users ON opportunities.owner_user_id = crm_users.user_id<br>GROUP BY crm_users.region<br>ORDER BY opportunity_count DESC` | 是 | 是 | 是 |  |
| 98 | relationship | 按营销活动统计活动成员数量。 | `SELECT c.record_name AS campaign_name, COUNT(cm.campaign_member_id) AS member_count FROM campaigns c LEFT JOIN campaign_members cm ON c.campaign_id = cm.campaign_id GROUP BY c.record_name ORDER BY member_count DESC` | 是 | 是 | 是 |  |
| 99 | relationship | 按商机状态统计报价单数量和金额。 | `SELECT opportunities.status, COUNT(quotes.quote_id) AS quote_count, SUM(quotes.amount) AS total_amount FROM quotes JOIN opportunities ON quotes.opportunity_id = opportunities.opportunity_id GROUP BY opportunities.status ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 100 | relationship | 按产品分类统计销售订单明细数量。 | `SELECT product_categories.record_name AS product_category,<br>       COUNT(sales_order_items.sales_order_item_id) AS order_detail_count<br>FROM sales_order_items<br>JOIN products ON sales_order_items.product_id = products.product_id<br>JOIN product_categories ON products.product_category_id = product_categories.product_category_id<br>GROUP BY product_categories.record_name<br>ORDER BY order_detail_count DESC` | 是 | 否 | 否 |  |

## 验证证据

- `generate-mdl.log`、`enrich-context.log`、Grill JSONL、`validate`/`build`输出、MCP烟测和每题原始结果均保留在服务器本次 run 对应结果目录。
- 评分以Wren语义层执行候选SQL后与同一数据库快照的参考SQL结果对比；未把题目或参考SQL提供给语义构建Agent。
