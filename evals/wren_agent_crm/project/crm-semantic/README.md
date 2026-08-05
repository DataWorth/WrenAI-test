# CRM 数据库语义化模型

## 项目概述

本项目为 CRM 业务数据库（crm_demo）创建了完整的语义化模型，包含 **55 个业务表** 和 **99 个关系定义**。

## 模型统计

- **总表数**: 55
- **总关系数**: 99
- **数据源**: MySQL (crm_demo)
- **项目路径**: /workspace/crm-semantic

## 核心业务模块

### 1. 客户管理 (Account Management)
- `accounts` - 客户主表
- `account_addresses` - 客户地址
- `account_status_history` - 客户状态历史
- `account_tags` - 客户标签
- `customer_health_scores` - 客户健康度评分

### 2. 联系人管理 (Contact Management)
- `contacts` - 联系人主表
- `contact_addresses` - 联系人地址
- `contact_tags` - 联系人标签

### 3. 销售线索 (Lead Management)
- `leads` - 销售线索主表
- `lead_assignments` - 线索分配
- `lead_conversions` - 线索转化
- `lead_sources` - 线索来源
- `lead_statuses` - 线索状态
- `nurture_sequences` - 培育序列

### 4. 商机管理 (Opportunity Management)
- `opportunities` - 商机主表
- `opportunity_contacts` - 商机联系人
- `opportunity_products` - 商机产品
- `opportunity_stages` - 商机阶段

### 5. 营销活动 (Campaign Management)
- `campaigns` - 营销活动主表
- `campaign_members` - 活动成员

### 6. 合同管理 (Contract Management)
- `contracts` - 合同主表
- `contract_lines` - 合同行项目
- `renewals` - 合同续约

### 7. 报价管理 (Quote Management)
- `quotes` - 报价主表
- `quote_items` - 报价项目

### 8. 订单管理 (Order Management)
- `sales_orders` - 销售订单
- `sales_order_items` - 订单项目

### 9. 发票与收款 (Invoice & Payment)
- `invoices` - 发票主表
- `invoice_lines` - 发票行项目
- `payments` - 收款记录

### 10. 产品管理 (Product Management)
- `products` - 产品主表
- `product_categories` - 产品类别
- `price_books` - 价格手册
- `price_book_items` - 价格手册项目

### 11. 客户服务 (Customer Service)
- `cases` - 服务案例
- `case_comments` - 案例评论
- `case_status_history` - 案例状态历史
- `knowledge_articles` - 知识库文章
- `satisfaction_surveys` - 满意度调查

### 12. 活动管理 (Activity Management)
- `activities` - 活动主表
- `activity_participants` - 活动参与者
- `meetings` - 会议
- `meeting_attendees` - 会议参与者
- `tasks` - 任务
- `notes` - 备注

### 13. 邮件管理 (Email Management)
- `email_messages` - 邮件消息
- `email_events` - 邮件事件

### 14. 组织架构 (Organization Structure)
- `organizations` - 组织
- `departments` - 部门
- `teams` - 团队
- `territories` - 区域
- `roles` - 角色
- `user_roles` - 用户角色

### 15. 用户管理 (User Management)
- `crm_users` - CRM 用户

### 16. 标签系统 (Tag System)
- `tags` - 标签主表

## 使用方式

### 查询数据

```bash
# 进入项目目录
cd /workspace/crm-semantic

# 加载环境变量
export $(cat /workspace/.env | xargs)

# 查询客户列表
wren --sql "SELECT account_id, record_name, status FROM accounts LIMIT 10"

# 查询联系人及其所属客户
wren --sql "SELECT c.record_name, a.record_name as account_name FROM contacts c JOIN accounts a ON c.account_id = a.account_id LIMIT 10"

# 查询商机及其阶段
wren --sql "SELECT o.record_name, s.name as stage FROM opportunities o JOIN opportunity_stages s ON o.opportunity_stage_id = s.opportunity_stage_id"
```

### 查看模型信息

```bash
# 查看所有模型
wren context show

# 查看特定模型详情
wren context show | grep -A 20 "accounts"
```

### 验证和构建

```bash
# 验证项目
wren context validate

# 重新构建 MDL
wren context build
```

## 项目结构

```
crm-semantic/
├── wren_project.yml          # 项目配置
├── relationships.yml         # 关系定义 (99 个关系)
├── models/                   # 模型定义
│   ├── accounts/
│   │   └── metadata.yml
│   ├── contacts/
│   │   └── metadata.yml
│   ├── opportunities/
│   │   └── metadata.yml
│   └── ... (共 55 个模型)
├── knowledge/
│   ├── rules/               # 业务规则
│   └── sql/                 # NL-SQL 示例
└── target/
    └── mdl.json            # 构建产物
```

## 下一步优化建议

1. **添加模型描述**: 为每个模型添加 `properties.description` 以提高 AI 查询准确性
2. **添加列描述**: 为关键列添加描述，特别是状态字段、类型字段等
3. **创建视图**: 为常用查询模式创建视图
4. **定义业务规则**: 在 `knowledge/rules/` 中添加业务逻辑
5. **添加示例查询**: 在 `knowledge/sql/` 中添加 NL-SQL 示例对

## 技术细节

- **类型映射**: 使用 Wren 的 MySQL 类型映射器自动转换数据库类型
- **关系推导**: 基于数据库外键约束自动生成关系定义
- **主键识别**: 自动识别每个表的主键
- **命名规范**: 使用 snake_case 命名，Wren 会自动转换为 camelCase

## 连接信息

- **数据库**: crm_demo
- **主机**: wren-eval-mysql:3306
- **用户**: wren_reader
- **数据源类型**: MySQL

---

生成时间: 2026-08-05
生成工具: Wren CLI + generate-mdl skill
