# WrenAI-test CRM MDL 项目

## 项目定位

这是 22 服务器 `WrenAI-test` 的空白 canonical MDL 模板。数据库 `crm_demo` 只保留以下 8 张核心表：

- `accounts`
- `contacts`
- `leads`
- `opportunities`
- `sales_orders`
- `contracts`
- `invoices`
- `payments`

Canonical 项目保持 0 模型、0 Cube、无 `target/mdl.json`。每次测试必须先复制到 `/opt/wrenai-test/runs/<run-id>/project`，不得直接在 canonical 项目中生成 MDL。

## 用户模拟流程

基础 MDL 使用一句简短请求：

```text
请为当前连接的 CRM 数据库搭建 MDL。
```

业务语义补充使用：

```text
请用 Grill 模式补充当前 CRM 项目的业务语义，每次只问一个问题。
```

`wrenai-test-human-agent.mjs` 会逐题等待测试操作者输入。它没有预置 CRM 业务答案；每次问题、拟稿、回答和写入位置记录在本次运行的 `human-grill-transcript.jsonl` 中。

## 运行方式

```bash
WRENAI_TEST_ROOT=/opt/wrenai-test
RUN_PROJECT="$($WRENAI_TEST_ROOT/runtime/wrenai-testctl new-run)"

$WRENAI_TEST_ROOT/runtime/wrenai-testctl generate "$RUN_PROJECT"
$WRENAI_TEST_ROOT/runtime/wrenai-testctl enrich "$RUN_PROJECT"
$WRENAI_TEST_ROOT/runtime/wrenai-testctl validate "$RUN_PROJECT"
$WRENAI_TEST_ROOT/runtime/wrenai-testctl build "$RUN_PROJECT"
$WRENAI_TEST_ROOT/runtime/wrenai-testctl start-mcp "$RUN_PROJECT"
```

`generate` 应只根据数据库真实元数据生成 8 个模型和现有外键关系，不应自行创建业务指标或 Cube。业务描述、枚举、金额单位、时间口径、默认过滤和 Cube 必须在 `enrich` 阶段逐项确认。

## 连接边界

- 数据库：`crm_demo`
- MySQL 服务：`wrenai-test-mysql:3306`
- Wren Profile：`wrenai-test-mysql`
- Docker 网络：`wrenai-test-net`
- 真实凭据仅存在于22服务器配置文件中，不得写入本文件、日志或Git。

## 验收要求

- 数据库发现结果恰好为 8 张表；
- 所有结构关系来自真实外键；
- `wren context validate` 成功；
- `wren context build` 成功并生成可解析的 `target/mdl.json`；
- 每项业务语义写入都有对应的现场回答记录；
- canonical 项目在测试前后保持空白。
