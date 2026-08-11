# SemWave 30表 CRM 语义构建与 Chat BI 测试报告

## 执行范围

- Run ID：`20260811T183706Z`
- 测试运行脚本提交：`36061873`
- Wren 源码基线：`74bf59e1d8400988f5269048cdeed983e77dc20d`
- Agent 镜像：`semwave-agent:official-30-core-v1`
- Chat BI 模型：`qwen3.6-27b`
- 数据范围：CRM 30张核心表、46条内部外键；历史55表测试集未参与本次运行。
- 路径：先官方 `generate-mdl`，再官方 `enrich-context` Grill 真人逐题补充业务语义，随后 `validate`、`build`、MCP Chat BI 烟测和100题评测。

## 语义构建结果

- 模型文件：30
- 关系文件条目：46
- 知识文件：1
- Grill 记录的问答：24

| 模型 | 文件 | 字段项 | 描述 |
|---|---|---:|---|
| accounts | `models/accounts/metadata.yml` | 0 | "客户账户信息表，存储企业客户的基本资料和销售信息" |
| campaign_members | `models/campaign_members/metadata.yml` | 0 | "营销活动参与成员表，记录线索与活动的多对多关联" |
| campaigns | `models/campaigns/metadata.yml` | 0 | "营销活动策划表，记录各类营销活动详情。一个活动可关联多条线索，amount 表示活动预算" |
| cases | `models/cases/metadata.yml` | 0 | "客服工单表，存储客户问题和服务请求的处理记录。工单关联客户和联系人" |
| contacts | `models/contacts/metadata.yml` | 0 | "联系人信息表，存储客户联系人的详细资料。联系人必须关联客户" |
| contracts | `models/contracts/metadata.yml` | 0 | "合同管理表，记录与客户的商务合同信息。合同关联商机，沿销售链从商机→合同→发票→付款" |
| crm_users | `models/crm_users/metadata.yml` | 0 | "CRM 系统用户表，存储系统内销售人员和管理员信息。用户通过 user_roles 关联角色，通过 team_id 关联团队" |
| departments | `models/departments/metadata.yml` | 0 | "部门信息表，存储组织内部的部门架构。组织层级：organization→department→team→crm_user" |
| invoices | `models/invoices/metadata.yml` | 0 | "发票管理表，记录已开具的发票信息。发票关联合同" |
| lead_assignments | `models/lead_assignments/metadata.yml` | 0 | "线索分配记录表，记录线索分配的历史轨迹。leads.assigned_user_id 保存当前负责人" |
| lead_sources | `models/lead_sources/metadata.yml` | 0 | "线索来源定义表，存储各种线索来源类型。来源枚举值：内容营销、官网咨询、客户转介绍、渠道伙伴、行业峰会" |
| lead_statuses | `models/lead_statuses/metadata.yml` | 0 | "线索状态定义表，存储线索生命周期的各状态。状态值：新建、待跟进、跟进中、已转化、已关闭" |
| leads | `models/leads/metadata.yml` | 0 | "销售线索表，存储潜在客户的基本信息。线索可关联多条商机，转化时创建/关联客户、联系人和商机" |
| nurture_sequences | `models/nurture_sequences/metadata.yml` | 0 | "培育序列表，定义线索自动化培育流程。未转化的线索分配到培育序列中持续跟进" |
| opportunities | `models/opportunities/metadata.yml` | 0 | "销售商机表，记录已确认的销售机会。商机可来自线索转化或手动创建，沿 quotes→sales_orders→contracts→invoices→payments 线性流转" |
| opportunity_contacts | `models/opportunity_contacts/metadata.yml` | 0 | "商机联系人关联表，记录商机涉及的多对多联系人关系" |
| opportunity_products | `models/opportunity_products/metadata.yml` | 0 | "商机产品关联表，记录商机中包含的产品。amount = quantity × unit_price" |
| opportunity_stages | `models/opportunity_stages/metadata.yml` | 0 | "商机阶段定义表，存储销售流程的各阶段。阶段与默认概率映射：需求确认=20%、方案报价=40%、商务谈判=60%、合同审批=80%、赢单=100%、输单=0%" |
| organizations | `models/organizations/metadata.yml` | 0 | "组织信息表，存储企业组织的顶层信息。组织层级：organization→department→team→crm_user" |
| payments | `models/payments/metadata.yml` | 0 | "付款记录表，记录客户回款信息。付款关联发票" |
| price_books | `models/price_books/metadata.yml` | 0 | "价目表管理表，存储产品价格版本。报价单使用特定版本的价目表" |
| product_categories | `models/product_categories/metadata.yml` | 0 | "产品分类表，扁平产品分类字典，不建模层级。产品通过 product_category_id 关联" |
| products | `models/products/metadata.yml` | 0 | "产品信息表，存储销售的产品目录。产品关联扁平产品分类" |
| quotes | `models/quotes/metadata.yml` | 0 | "报价单表，记录给客户的报价信息。报价单关联商机，使用特定版本的价目表" |
| roles | `models/roles/metadata.yml` | 0 | "用户角色定义表，存储系统中的角色类型。角色值：系统管理员、销售总监、销售经理、销售代表、客服代表" |
| sales_order_items | `models/sales_order_items/metadata.yml` | 0 | "销售订单明细表，记录订单中的产品明细。amount = quantity × unit_price" |
| sales_orders | `models/sales_orders/metadata.yml` | 0 | "销售订单表，记录已确认的销售订单。订单来自报价单，沿销售链线性流转" |
| teams | `models/teams/metadata.yml` | 0 | "销售团队表，存储销售团队的组织结构。组织层级：organization→department→team→crm_user。每个团队关联一个 sales territory" |
| territories | `models/territories/metadata.yml` | 0 | "销售区域表，存储地理销售区域划分" |
| user_roles | `models/user_roles/metadata.yml` | 0 | "用户角色关联表，记录用户与角色的多对多映射。一个用户可有多角色" |

### 业务语义问答

| 问题 | 业务负责人回答 |
|---|---|
| 我想对数据库中的一些低基数列（如 status、region、source、stage 等）执行 SELECT DISTINCT 查询（每个 LIMIT 30），以获取实际枚举值来辅助后续的业务语义补充。这样可以减少你的输入量——授权吗？ | 可以，开始探测（选项 1） |
| 这些公共列（status、region、source、industry、stage、amount 等）在所有模型中的含义和枚举值是一致的，还是因表而异？ | 含义不一致，逐表定义（选项 2） |
| accounts 表的 status 字段的枚举值和含义如上表所示，请确认或修改。 | 实际 status 枚举统一为：新建、待跟进、进行中、已完成、已关闭；不使用 active 等英文值，具体业务动作随实体而定。 |
| region 字段的取值是否为以上中国七区划分？请确认或给出实际的枚举值。 | 实际值为华南、华中、华东、华北、西南五个销售区域；region 在客户、线索和销售业务实体中表示归属销售区域。 |
| source 字段的取值是否为以上六档？请确认或给出实际的枚举值。 | 实际来源为内容营销、官网咨询、客户转介绍、渠道伙伴、行业峰会；source 记录原始获客渠道，并可沿销售链继承。 |
| industry 字段的取值是否为以上八类行业分类？请确认或给出实际的枚举值。 | 实际行业为信息技术、专业服务、制造业、零售业、金融服务五类；客户和线索是权威来源，销售链可继承。 |
| stage 字段（销售漏斗阶段）的取值是否为以上六阶段？请确认或给出实际的枚举值。 | 实际销售阶段为需求确认、方案报价、商务谈判、合同审批、赢单、输单；仅销售链实体的 stage 有业务意义。 |
| 金额字段单位为人民币(元)、不含税，amount 为独立填写的总金额（非 quantity×unit_price 计算得出），probability 为 0-100 整数（如 50 = 50%）？请确认或修改。 | 币种为人民币元；税务口径未在数据中建模。opportunities、quotes、sales_orders、contracts、invoices 的 amount 是单据/业务金额；accounts.amount 是客户累计交易额；opportunity_products 与 sales_order_items 的 amount=quantity×unit_price。其他表的同名金额字段无业务指标含义。probability 为 0-100 百分比。 |
| score 是 0-100 的线索/客户评分，leads 和 accounts 中有效，基于客户行为自动计算？请确认或给出实际定义。 | score 为 0-100 的业务优先级分：leads 是线索热度、accounts 是客户价值、opportunities 是商机优先级；其余表无业务评分含义，计算来源不在本系统建模。 |
| record_name 在各表中代表该实体的业务名称/标题（如 accounts=客户公司名，contacts=联系人姓名，opportunities=商机名称）？请确认。 | 确认理解准确 (Recommended)（选项 1） |
| created_at 使用 UTC+8(中国标准时间)，且系统中只有 created_at 没有更新时间字段？请确认。 | UTC+8，仅 created_at (Recommended)（选项 1） |
| 一条线索可产生多条商机(一对多)，转化后线索标记'已完成'，商机通过 lead_id FK 引用线索？请确认或描述实际流程。 | 一条线索可关联多条商机；转化时会创建或关联客户、联系人和商机，商机通过 lead_id 引用线索。线索转化状态以 lead_statuses/lead_status_id 为准，转化完成表示已转化。 |
| lead_statuses 表中的状态值是否为：新建、待跟进、跟进中、已转化、已关闭？请确认或给出实际值。 | 确认上述五状态 (Recommended)（选项 1） |
| opportunity_stages 的阶段与概率映射如上表？请确认或修改。 | 确认阶段和概率 (Recommended)（选项 1） |
| 销售链路是线性的：leads→opportunities→quotes→sales_orders→contracts→invoices→payments，每步通过 FK 多对一关联？请确认或描述例外。 | 线性链路 (Recommended)（选项 1） |
| 组织架构为 organization→department→team→crm_user，team 关联 territory，用户可有多角色？请确认或修改。 | 确认架构 (Recommended)（选项 1） |
| nurture_sequences 是自动化培育流程，未转化的线索分配到培育序列中持续跟进，NULL 表示未加入？请确认或修改。 | 确认理解 (Recommended)（选项 1） |
| campaign 通过 campaign_members 多对多关联 leads，amount 表示活动预算，status 使用统一五档？请确认或修改。 | 预算+多对多 (Recommended)（选项 1） |
| cases 表是客服工单（客户问题处理记录）还是客户成功案例？请确认。 | 客服工单 (Recommended)（选项 1） |
| lead_assignments 是否记录线索分配的历史轨迹，而 leads.assigned_user_id 只保存当前负责人？请确认或说明。 | 分配历史记录 (Recommended)（选项 1） |
| price_books 是产品价格版本管理，报价单使用特定版本；product_categories 有层级结构？请确认或修改。 | price_books 为价格版本，quotes 关联所用价目表；product_categories 是扁平产品分类字典，不建模层级。 |
| roles 表中的角色类型是否为：系统管理员、销售总监、销售经理、销售代表、客服代表？请确认或给出实际值。 | 确认上述五角色 (Recommended)（选项 1） |
| 商机可手动创建（opportunities.lead_id 可 NULL），但商机和联系人都必须关联客户；系统无软删除（数据物理删除或靠 status 标记）？请确认。 | 商机可手动创建且 lead_id 可空；商机和联系人必须关联客户；无软删除字段，status 是业务状态而非删除标志，默认不因 status 过滤记录。 |
| 还需要补充以上哪些主题？如果没有，我们就开始将收集的语义写入 MDL 和 knowledge。 | 补充同义词：客户=accounts，联系人=contacts，线索=leads，商机=opportunities，工单=cases，合同=contracts，订单=销售订单=orders，报价=quotes，发票=invoices，回款=payments，销售人员=crm_users。创建一个 pipeline cube：基于 opportunities，按 stage/region/created_at，指标为商机数、总管道金额、加权管道金额=amount*probability/100。 |

### 知识文件

- `knowledge/rules/naming-conventions.md`

## Chat BI 结果

- 测试题数：100
- SQL可运行：100/100
- 精确答案：43/100 (43.00%)
- 值集合匹配：83/100 (83.00%)
- 官方 usage 指南已加载：92/100

| 类别 | 题数 | SQL可运行 | 精确答案 | 值集合匹配 |
|---|---:|---:|---:|---:|
| business_aggregate | 30 | 30 | 7 | 27 |
| relationship | 15 | 15 | 1 | 12 |
| single_count | 30 | 30 | 19 | 24 |
| status_distribution | 25 | 25 | 16 | 20 |

### 每题结果

| ID | 类别 | 问题 | 候选SQL | SQL可运行 | 精确答案 | 值集合匹配 | 错误 |
|---:|---|---|---|:---:|:---:|:---:|---|
| 1 | single_count | 统计组织的记录数。 | `SELECT COUNT(*) AS record_count FROM organizations` | 是 | 是 | 是 |  |
| 2 | single_count | 统计部门的记录数。 | `SELECT record_name, COUNT(*) AS record_count FROM departments GROUP BY record_name ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 3 | single_count | 统计销售辖区的记录数。 | `SELECT territory_id, record_name, region FROM territories ORDER BY territory_id` | 是 | 否 | 否 |  |
| 4 | single_count | 统计团队的记录数。 | `SELECT teams.record_name AS team_name, COUNT(crm_users.user_id) AS record_count FROM teams LEFT JOIN crm_users ON teams.team_id = crm_users.team_id GROUP BY teams.record_name ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 5 | single_count | 统计CRM用户的记录数。 | `SELECT COUNT(*) AS record_count FROM crm_users` | 是 | 是 | 是 |  |
| 6 | single_count | 统计角色的记录数。 | `SELECT COUNT(*) AS record_count FROM roles` | 是 | 是 | 是 |  |
| 7 | single_count | 统计用户角色分配的记录数。 | `SELECT COUNT(*) AS record_count FROM user_roles` | 是 | 是 | 是 |  |
| 8 | single_count | 统计客户的记录数。 | `SELECT COUNT(*) AS record_count FROM accounts` | 是 | 是 | 是 |  |
| 9 | single_count | 统计联系人的记录数。 | `SELECT COUNT(*) AS contact_count FROM contacts` | 是 | 否 | 是 |  |
| 10 | single_count | 统计线索来源的记录数。 | `SELECT source, COUNT(*) AS record_count FROM leads GROUP BY source ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 11 | single_count | 统计线索状态的记录数。 | `SELECT status, COUNT(*) AS count FROM leads GROUP BY status ORDER BY count DESC` | 是 | 否 | 否 |  |
| 12 | single_count | 统计线索培育序列的记录数。 | `SELECT COUNT(*) AS record_count FROM nurture_sequences` | 是 | 是 | 是 |  |
| 13 | single_count | 统计线索的记录数。 | `SELECT COUNT(*) AS count FROM leads` | 是 | 否 | 是 |  |
| 14 | single_count | 统计线索分配的记录数。 | `SELECT COUNT(*) AS record_count FROM lead_assignments` | 是 | 是 | 是 |  |
| 15 | single_count | 统计营销活动的记录数。 | `SELECT COUNT(*) AS campaign_count FROM campaigns` | 是 | 否 | 是 |  |
| 16 | single_count | 统计活动成员的记录数。 | `SELECT COUNT(*) AS record_count FROM campaign_members` | 是 | 是 | 是 |  |
| 17 | single_count | 统计商机阶段的记录数。 | `SELECT stage, COUNT(*) AS record_count FROM opportunities GROUP BY stage ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 18 | single_count | 统计产品分类的记录数。 | `SELECT COUNT(*) AS record_count FROM product_categories` | 是 | 是 | 是 |  |
| 19 | single_count | 统计产品的记录数。 | `SELECT COUNT(*) AS record_count FROM products` | 是 | 是 | 是 |  |
| 20 | single_count | 统计价目表的记录数。 | `SELECT COUNT(*) AS record_count FROM price_books` | 是 | 是 | 是 |  |
| 21 | single_count | 统计商机的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunities` | 是 | 是 | 是 |  |
| 22 | single_count | 统计商机联系人的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunity_contacts` | 是 | 是 | 是 |  |
| 23 | single_count | 统计商机产品的记录数。 | `SELECT COUNT(*) AS record_count FROM opportunity_products` | 是 | 是 | 是 |  |
| 24 | single_count | 统计报价单的记录数。 | `SELECT COUNT(*) AS record_count FROM quotes` | 是 | 是 | 是 |  |
| 25 | single_count | 统计销售订单的记录数。 | `SELECT COUNT(*) AS record_count FROM sales_orders` | 是 | 是 | 是 |  |
| 26 | single_count | 统计销售订单明细的记录数。 | `SELECT COUNT(*) AS record_count FROM sales_order_items` | 是 | 是 | 是 |  |
| 27 | single_count | 统计合同的记录数。 | `SELECT COUNT(*) AS contract_count FROM contracts` | 是 | 否 | 是 |  |
| 28 | single_count | 统计发票的记录数。 | `SELECT COUNT(*) AS record_count FROM invoices` | 是 | 是 | 是 |  |
| 29 | single_count | 统计回款的记录数。 | `SELECT COUNT(*) AS payment_count FROM payments` | 是 | 否 | 是 |  |
| 30 | single_count | 统计客服工单的记录数。 | `SELECT COUNT(*) AS record_count FROM cases` | 是 | 是 | 是 |  |
| 31 | status_distribution | 按状态统计组织的记录数。 | `SELECT status, COUNT(*) AS record_count FROM organizations GROUP BY status ORDER BY status` | 是 | 是 | 是 |  |
| 32 | status_distribution | 按状态统计部门的记录数。 | `SELECT status, COUNT(*) AS record_count FROM departments GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 33 | status_distribution | 按状态统计销售辖区的记录数。 | `SELECT <br>    territories.record_name AS territory_name,<br>    accounts.status,<br>    COUNT(*) AS record_count<br>FROM accounts<br>JOIN territories ON accounts.territory_id = territories.territory_id<br>GROUP BY territories.record_name, accounts.status<br>ORDER BY territories.record_name, accounts.status` | 是 | 否 | 否 |  |
| 34 | status_distribution | 按状态统计团队的记录数。 | `SELECT teams.record_name AS team_name, teams.status, COUNT(*) AS record_count FROM teams GROUP BY teams.record_name, teams.status ORDER BY teams.record_name, teams.status` | 是 | 否 | 否 |  |
| 35 | status_distribution | 按状态统计CRM用户的记录数。 | `SELECT status, COUNT(*) AS record_count FROM crm_users GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 36 | status_distribution | 按状态统计角色的记录数。 | `SELECT status, COUNT(*) AS record_count FROM roles GROUP BY status ORDER BY status` | 是 | 是 | 是 |  |
| 37 | status_distribution | 按状态统计用户角色分配的记录数。 | `SELECT status, COUNT(*) AS record_count FROM user_roles GROUP BY status` | 是 | 是 | 是 |  |
| 38 | status_distribution | 按状态统计客户的记录数。 | `SELECT status, COUNT(*) AS record_count FROM accounts GROUP BY status` | 是 | 是 | 是 |  |
| 39 | status_distribution | 按状态统计联系人的记录数。 | `SELECT status, COUNT(*) AS count FROM contacts GROUP BY status` | 是 | 否 | 是 |  |
| 40 | status_distribution | 按状态统计线索来源的记录数。 | `SELECT status, source, COUNT(*) AS record_count FROM leads GROUP BY status, source ORDER BY status, source` | 是 | 否 | 否 |  |
| 41 | status_distribution | 按状态统计线索状态的记录数。 | `SELECT status, COUNT(*) AS record_count FROM leads GROUP BY status ORDER BY record_count DESC` | 是 | 否 | 否 |  |
| 42 | status_distribution | 按状态统计线索培育序列的记录数。 | `SELECT status, COUNT(*) AS record_count FROM nurture_sequences GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 43 | status_distribution | 按状态统计线索的记录数。 | `SELECT status, COUNT(*) AS record_count FROM leads GROUP BY status` | 是 | 是 | 是 |  |
| 44 | status_distribution | 按状态统计线索分配的记录数。 | `SELECT status, COUNT(*) AS record_count FROM lead_assignments GROUP BY status ORDER BY status` | 是 | 是 | 是 |  |
| 45 | status_distribution | 按状态统计营销活动的记录数。 | `SELECT status, COUNT(*) AS count FROM campaigns GROUP BY status ORDER BY count DESC` | 是 | 否 | 是 |  |
| 46 | status_distribution | 按状态统计活动成员的记录数。 | `SELECT status, COUNT(*) AS record_count<br>FROM campaign_members<br>GROUP BY status<br>ORDER BY status` | 是 | 是 | 是 |  |
| 47 | status_distribution | 按状态统计商机阶段的记录数。 | `SELECT status, stage, COUNT(*) AS record_count FROM opportunities GROUP BY status, stage ORDER BY status, stage` | 是 | 否 | 否 |  |
| 48 | status_distribution | 按状态统计产品分类的记录数。 | `SELECT status, COUNT(*) AS record_count<br>FROM product_categories<br>GROUP BY status<br>ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 49 | status_distribution | 按状态统计产品的记录数。 | `SELECT status, COUNT(*) AS record_count FROM products GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 50 | status_distribution | 按状态统计价目表的记录数。 | `SELECT status, COUNT(*) AS record_count FROM price_books GROUP BY status` | 是 | 是 | 是 |  |
| 51 | status_distribution | 按状态统计商机的记录数。 | `SELECT status AS "状态", COUNT(*) AS "记录数" FROM opportunities GROUP BY status ORDER BY status` | 是 | 否 | 是 |  |
| 52 | status_distribution | 按状态统计商机联系人的记录数。 | `SELECT status, COUNT(*) AS record_count<br>FROM opportunity_contacts<br>GROUP BY status<br>ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 53 | status_distribution | 按状态统计商机产品的记录数。 | `SELECT status, COUNT(*) AS record_count FROM opportunity_products GROUP BY status` | 是 | 是 | 是 |  |
| 54 | status_distribution | 按状态统计报价单的记录数。 | `SELECT status, COUNT(*) AS record_count FROM quotes GROUP BY status ORDER BY record_count DESC` | 是 | 是 | 是 |  |
| 55 | status_distribution | 按状态统计销售订单的记录数。 | `SELECT status, COUNT(*) AS order_count FROM sales_orders GROUP BY status ORDER BY status` | 是 | 否 | 是 |  |
| 56 | business_aggregate | 按客户区域汇总客户累计交易金额。 | `SELECT region, SUM(amount) AS total_amount<br>FROM accounts<br>GROUP BY region<br>ORDER BY region` | 是 | 是 | 是 |  |
| 57 | business_aggregate | 按商机区域汇总商机金额。 | `SELECT region, SUM(amount) AS total_amount FROM opportunities GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 58 | business_aggregate | 按报价单区域汇总报价金额。 | `SELECT region AS "报价单区域", SUM(amount) AS "报价金额合计" FROM quotes GROUP BY region ORDER BY region` | 是 | 否 | 是 |  |
| 59 | business_aggregate | 按销售订单区域汇总订单金额。 | `SELECT region, SUM(amount) AS total_amount FROM sales_orders GROUP BY region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 60 | business_aggregate | 按发票区域汇总发票金额。 | `SELECT region, SUM(amount) AS total_amount FROM invoices GROUP BY region ORDER BY region` | 是 | 是 | 是 |  |
| 61 | business_aggregate | 按合同区域汇总合同金额。 | `SELECT region AS 合同区域, SUM(amount) AS 合同总金额<br>FROM contracts<br>GROUP BY region<br>ORDER BY 合同总金额 DESC` | 是 | 否 | 是 |  |
| 62 | business_aggregate | 按客户区域统计回款金额。 | `SELECT region AS 客户区域, SUM(amount) AS 回款金额 FROM payments GROUP BY region ORDER BY 回款金额 DESC` | 是 | 否 | 是 |  |
| 63 | business_aggregate | 按客户区域统计商机产品行项目金额。 | `SELECT accounts.region AS customer_region, <br>       SUM(opportunity_products.amount) AS total_amount <br>FROM opportunity_products <br>JOIN opportunities ON opportunity_products.opportunity_id = opportunities.opportunity_id <br>JOIN accounts ON opportunities.account_id = accounts.account_id <br>GROUP BY accounts.region <br>ORDER BY accounts.region` | 是 | 否 | 是 |  |
| 64 | business_aggregate | 按客户区域统计销售订单明细金额。 | `SELECT<br>  accounts.region AS 客户区域,<br>  SUM(sales_order_items.amount) AS 明细总金额<br>FROM sales_order_items<br>JOIN sales_orders ON sales_order_items.sales_order_id = sales_orders.sales_order_id<br>JOIN accounts ON sales_orders.account_id = accounts.account_id<br>GROUP BY accounts.region<br>ORDER BY 明细总金额 DESC` | 是 | 否 | 是 |  |
| 65 | business_aggregate | 按商机业务阶段统计商机数量和金额。 | `SELECT stage AS "商机阶段", COUNT(*) AS "商机数量", SUM(amount) AS "商机总金额" FROM opportunities GROUP BY stage ORDER BY stage` | 是 | 否 | 是 |  |
| 66 | business_aggregate | 按报价单业务阶段统计报价单数量和金额。 | `SELECT<br>  stage AS 业务阶段,<br>  COUNT(*) AS 报价单数量,<br>  SUM(amount) AS 报价总金额<br>FROM quotes<br>GROUP BY stage<br>ORDER BY stage` | 是 | 否 | 是 |  |
| 67 | business_aggregate | 按合同业务阶段统计合同数量和金额。 | `SELECT<br>  stage AS 业务阶段,<br>  COUNT(*) AS 合同数量,<br>  SUM(amount) AS 合同金额<br>FROM contracts<br>GROUP BY stage<br>ORDER BY stage` | 是 | 否 | 是 |  |
| 68 | business_aggregate | 按销售订单业务阶段统计订单数量和金额。 | `SELECT<br>  stage AS "业务阶段",<br>  COUNT(*) AS "订单数量",<br>  SUM(amount) AS "订单总金额"<br>FROM sales_orders<br>GROUP BY stage<br>ORDER BY "订单总金额" DESC` | 是 | 否 | 是 |  |
| 69 | business_aggregate | 按商机业务阶段统计商机产品行项目数量和金额。 | `SELECT<br>  o.stage AS 商机业务阶段,<br>  COUNT(*) AS 行项目数量,<br>  SUM(op.amount) AS 总金额<br>FROM opportunity_products op<br>JOIN opportunities o ON op.opportunity_id = o.opportunity_id<br>GROUP BY o.stage<br>ORDER BY o.stage` | 是 | 否 | 是 |  |
| 70 | business_aggregate | 按销售订单业务阶段统计订单明细数量和金额。 | `SELECT<br>    so.stage AS sales_stage,<br>    COUNT(soi.sales_order_item_id) AS item_count,<br>    SUM(soi.quantity) AS total_quantity,<br>    SUM(soi.amount) AS total_amount<br>FROM sales_order_items soi<br>JOIN sales_orders so ON soi.sales_order_id = so.sales_order_id<br>GROUP BY so.stage<br>ORDER BY so.stage` | 是 | 否 | 否 |  |
| 71 | business_aggregate | 按商机业务阶段统计加权管道金额。 | `SELECT stage, SUM(amount * probability / 100) AS weighted_pipeline_amount FROM opportunities GROUP BY stage ORDER BY stage` | 是 | 否 | 是 |  |
| 72 | business_aggregate | 按销售辖区业务区域统计客户数量。 | `SELECT<br>  t.record_name AS territory_name,<br>  t.region AS business_region,<br>  COUNT(a.account_id) AS customer_count<br>FROM accounts a<br>JOIN territories t ON a.territory_id = t.territory_id<br>GROUP BY t.record_name, t.region<br>ORDER BY t.region, t.record_name` | 是 | 否 | 否 |  |
| 73 | business_aggregate | 按客户区域统计客户数量。 | `SELECT region, COUNT(*) AS customer_count FROM accounts GROUP BY region ORDER BY region` | 是 | 否 | 是 |  |
| 74 | business_aggregate | 按客户区域统计联系人数量。 | `SELECT accounts.region AS customer_region, COUNT(contacts.contact_id) AS contact_count FROM contacts JOIN accounts ON contacts.account_id = accounts.account_id GROUP BY accounts.region ORDER BY accounts.region` | 是 | 否 | 是 |  |
| 75 | business_aggregate | 按客户区域统计工单数量。 | `SELECT a.region AS customer_region, COUNT(c.case_id) AS case_count<br>FROM cases c<br>JOIN accounts a ON c.account_id = a.account_id<br>GROUP BY a.region<br>ORDER BY case_count DESC` | 是 | 否 | 是 |  |
| 76 | business_aggregate | 按商机来源统计商机数量。 | `SELECT source, COUNT(*) AS opportunity_count FROM opportunities GROUP BY source ORDER BY opportunity_count DESC` | 是 | 是 | 是 |  |
| 77 | business_aggregate | 按线索实际来源统计线索数量。 | `SELECT source AS lead_source, COUNT(lead_id) AS lead_count<br>FROM leads<br>GROUP BY source<br>ORDER BY lead_count DESC` | 是 | 否 | 是 |  |
| 78 | business_aggregate | 按营销活动统计活动成员数量。 | `SELECT<br>  c.record_name AS campaign_name,<br>  COUNT(cm.campaign_member_id) AS member_count<br>FROM campaigns c<br>JOIN campaign_members cm ON c.campaign_id = cm.campaign_id<br>GROUP BY c.record_name<br>ORDER BY member_count DESC` | 是 | 是 | 是 |  |
| 79 | business_aggregate | 按产品分类统计产品数量。 | `SELECT pc.record_name AS category_name, COUNT(p.product_id) AS product_count FROM products p JOIN product_categories pc ON p.product_category_id = pc.product_category_id GROUP BY pc.record_name ORDER BY product_count DESC` | 是 | 否 | 是 |  |
| 80 | business_aggregate | 按产品分类统计销售订单明细数量。 | `SELECT pc.record_name AS product_category, COUNT(*) AS item_count FROM sales_order_items soi JOIN products p ON soi.product_id = p.product_id JOIN product_categories pc ON p.product_category_id = pc.product_category_id GROUP BY pc.record_name ORDER BY item_count DESC` | 是 | 否 | 是 |  |
| 81 | business_aggregate | 按商机状态统计报价单数量和金额。 | `SELECT<br>  o.status AS opportunity_status,<br>  COUNT(q.quote_id) AS quote_count,<br>  SUM(q.amount) AS total_quote_amount<br>FROM quotes q<br>JOIN opportunities o ON q.opportunity_id = o.opportunity_id<br>GROUP BY o.status<br>ORDER BY o.status` | 是 | 否 | 是 |  |
| 82 | business_aggregate | 按客户区域统计回款笔数。 | `SELECT region AS 客户区域, COUNT(*) AS 回款笔数 FROM payments GROUP BY region ORDER BY region` | 是 | 否 | 是 |  |
| 83 | business_aggregate | 按商机业务阶段统计平均赢单概率。 | `SELECT stage, AVG(probability) AS avg_probability, COUNT(*) AS opportunity_count FROM opportunities GROUP BY stage ORDER BY avg_probability DESC` | 是 | 否 | 否 |  |
| 84 | business_aggregate | 按销售人员区域统计负责商机数量。 | `SELECT<br>  cu.region AS salesperson_region,<br>  COUNT(o.opportunity_id) AS opportunity_count<br>FROM opportunities o<br>JOIN crm_users cu ON o.owner_user_id = cu.user_id<br>GROUP BY cu.region<br>ORDER BY opportunity_count DESC` | 是 | 否 | 是 |  |
| 85 | business_aggregate | 按销售人员区域汇总负责商机金额。 | `SELECT cu.region AS region, SUM(o.amount) AS total_amount FROM opportunities o JOIN crm_users cu ON o.owner_user_id = cu.user_id GROUP BY cu.region ORDER BY total_amount DESC` | 是 | 是 | 是 |  |
| 86 | relationship | 按客户区域统计商机数量与商机金额。 | `SELECT region AS region, COUNT(*) AS opportunity_count, SUM(amount) AS total_pipeline_amount FROM opportunities GROUP BY 1` | 是 | 否 | 是 |  |
| 87 | relationship | 按商机业务阶段统计商机数量和加权管道金额。 | `SELECT stage AS stage, COUNT(*) AS opportunity_count, SUM(amount * probability / 100) AS weighted_pipeline_amount FROM opportunities GROUP BY 1` | 是 | 否 | 是 |  |
| 88 | relationship | 按线索实际来源统计线索数量。 | `SELECT source, COUNT(*) AS lead_count FROM leads GROUP BY source ORDER BY lead_count DESC` | 是 | 否 | 是 |  |
| 89 | relationship | 按客户区域统计联系人数量。 | `SELECT accounts.region AS 客户区域, COUNT(contacts.contact_id) AS 联系人数量 FROM contacts JOIN accounts ON contacts.account_id = accounts.account_id GROUP BY accounts.region ORDER BY 客户区域` | 是 | 否 | 是 |  |
| 90 | relationship | 按客户区域统计销售订单金额。 | `SELECT<br>  accounts.region AS customer_region,<br>  SUM(sales_orders.amount) AS total_order_amount<br>FROM sales_orders<br>JOIN accounts ON sales_orders.account_id = accounts.account_id<br>GROUP BY accounts.region<br>ORDER BY total_order_amount DESC` | 是 | 否 | 是 |  |
| 91 | relationship | 按客户区域统计未关闭工单数量。 | `SELECT region, COUNT(*) AS unclosed_case_count<br>FROM cases<br>WHERE status != '已关闭'<br>GROUP BY region<br>ORDER BY region` | 是 | 否 | 是 |  |
| 92 | relationship | 按销售辖区业务区域统计客户数量。 | `SELECT t.record_name AS territory_name, t.region AS business_region, COUNT(a.account_id) AS customer_count FROM accounts a JOIN territories t ON a.territory_id = t.territory_id GROUP BY t.record_name, t.region ORDER BY t.region, t.record_name` | 是 | 否 | 否 |  |
| 93 | relationship | 按客户区域统计合同金额。 | `SELECT region AS 客户区域, SUM(amount) AS 合同总金额 FROM contracts GROUP BY region ORDER BY 合同总金额 DESC` | 是 | 否 | 是 |  |
| 94 | relationship | 按客户区域统计发票金额。 | `SELECT region AS 客户区域, SUM(amount) AS 发票总金额, COUNT(*) AS 发票数量 FROM invoices GROUP BY region ORDER BY 发票总金额 DESC` | 是 | 否 | 否 |  |
| 95 | relationship | 按客户区域统计回款金额。 | `SELECT region AS "客户区域", SUM(amount) AS "回款金额" FROM payments GROUP BY region ORDER BY "回款金额" DESC` | 是 | 否 | 是 |  |
| 96 | relationship | 按产品分类统计产品数量。 | `SELECT pc.record_name AS category_name, COUNT(p.product_id) AS product_count FROM products p JOIN product_categories pc ON p.product_category_id = pc.product_category_id GROUP BY pc.record_name ORDER BY product_count DESC` | 是 | 否 | 是 |  |
| 97 | relationship | 按销售人员区域统计负责商机数量。 | `SELECT crm_users.region, COUNT(opportunities.opportunity_id) AS opportunity_count FROM opportunities JOIN crm_users ON opportunities.owner_user_id = crm_users.user_id GROUP BY crm_users.region ORDER BY crm_users.region` | 是 | 是 | 是 |  |
| 98 | relationship | 按营销活动统计活动成员数量。 | `SELECT <br>    c.campaign_id,<br>    c.record_name AS campaign_name,<br>    COUNT(cm.campaign_member_id) AS member_count<br>FROM campaigns c<br>LEFT JOIN campaign_members cm ON c.campaign_id = cm.campaign_id<br>GROUP BY c.campaign_id, c.record_name<br>ORDER BY member_count DESC` | 是 | 否 | 否 |  |
| 99 | relationship | 按商机状态统计报价单数量和金额。 | `SELECT<br>  o.status AS opportunity_status,<br>  COUNT(q.quote_id) AS quote_count,<br>  SUM(q.amount) AS total_quote_amount<br>FROM quotes q<br>JOIN opportunities o ON q.opportunity_id = o.opportunity_id<br>GROUP BY o.status<br>ORDER BY o.status` | 是 | 否 | 是 |  |
| 100 | relationship | 按产品分类统计销售订单明细数量。 | `SELECT pc.record_name AS product_category, COUNT(*) AS item_count FROM sales_order_items soi JOIN products p ON soi.product_id = p.product_id JOIN product_categories pc ON p.product_category_id = pc.product_category_id GROUP BY pc.record_name ORDER BY item_count DESC` | 是 | 否 | 是 |  |

## 验证证据

- `generate-mdl.log`、`enrich-context.log`、Grill JSONL、`validate`/`build`输出、MCP烟测和每题原始结果均保留在服务器本次 run 对应结果目录。
- 评分以Wren语义层执行候选SQL后与同一数据库快照的参考SQL结果对比；未把题目或参考SQL提供给语义构建Agent。
