# WrenAI-test 改动与测试环境说明

## 仓库与环境

- 上游仓库：`Canner/WrenAI`
- 测试 fork：`DataWorth/WrenAI-test`
- 服务器基线分支：`codex/22-test-environment`
- 服务器源码基线：`74bf59e1d8400988f5269048cdeed983e77dc20d`
- 测试服务器：`117.72.76.22`
- 服务器项目根目录：`/opt/wrenai-test`

`/opt/wrenai-test` 是 `WrenAI-test` 的远程测试环境。活动容器、网络、镜像和控制入口统一使用 `wrenai-test` 前缀；后续修改先在本仓库完成并提交，再同步到服务器进行运行验证。

## Wren 源码改动

### generate-mdl 关系文件示例

文件：`core/wren/src/wren/skills_content/generate-mdl/SKILL.md`

上游示例将 `relationships.yml` 写成了裸 YAML 列表，而 Wren 项目脚手架与上下文解析要求顶层 `relationships` 键。测试分支中的示例改为：

```yaml
relationships:
  - name: orders_customers
    models:
      - orders
      - customers
    join_type: many_to_one
    condition: "orders.customer_id = customers.customer_id"
```

该修改只修正 Skill 中生成关系文件的结构指引，不改变关系推导规则、CLI 解析器或 MDL schema。

## Agent 与评测代码

服务器 `/opt/wrenai-test/runtime` 中使用的源文件来自 `evals/wren_agent_crm/runtime`，当前活动入口包括：

- `wrenai-test-mdl-agent.mjs`：用一句简短用户请求驱动官方 `generate-mdl`；
- `wrenai-test-human-agent.mjs`：通过 Claude Agent SDK 内置 `AskUserQuestion` 现场逐题询问测试操作者，不包含写死业务答案；
- `wrenai-test-user-input.mjs`：把 `AskUserQuestion` 映射到终端真人输入并记录 JSONL；
- `wrenai-testctl`：创建 run-specific 项目并控制 generate、enrich、validate、build 和 MCP；
- 构建完成后使用的 Wren MCP 控制入口；
- 100 题 Chat BI 批量运行与评分脚本；
- CRM 数据库初始化脚本；
- CLI 及 Agent 镜像 Dockerfile；
- 旧 `official-agent.mjs`、`grill-agent.mjs` 和 `agentctl` 只作为历史评测代码，不再是服务器活动入口。

百炼通过 Anthropic 兼容环境变量接入。模型名称和访问凭据均由服务器环境文件提供，代码中不保存 API Key。Claude Agent SDK 版本由 `package-lock.json` 固定，Agent 镜像使用 `npm ci` 安装依赖。

## CRM 测试资产

`evals/wren_agent_crm` 保存了服务器测试资产的可审查版本：

| 资产 | 数量或位置 |
|---|---|
| CRM 数据表 | 30 张核心表 |
| Canonical MDL | 空项目，0 个模型、0 个 Cube、无构建产物 |
| 每次测试项目 | `/opt/wrenai-test/runs/<run-id>/project` |
| View | 0 个 |
| Chat BI 基准 | 100 题，活动集位于 `benchmarks/crm_30_core_100_qna.jsonl`；历史55表集 `benchmarks/crm_100_qna.jsonl` 仅保留对照 |
| CRM mock 数据生成器 | `runtime/bootstrap_crm.py` |

`target/mdl.json`、运行日志、评分结果和生成后的 `crm-seed.sql` 不纳入 Git。数据库可由 `bootstrap_crm.py` 重新生成。

旧55模型、99关系和Cube已从活动项目移除并单独备份。活动数据库保留30张核心CRM表及其46条内部外键；新的MDL、业务语义和Cube必须由每次run-specific测试重新生成并通过 `validate`、`build` 和实际查询验证。

## 目录适配

服务器 Dockerfile 统一以仓库根目录为 Docker build context，因此 Dockerfile 的 `COPY` 路径为：

- Wren 包：`core/wren`
- Wren 官方 Skill：`skills/wren/SKILL.md`
- generate-mdl Skill：`core/wren/src/wren/skills_content/generate-mdl/SKILL.md`
- Agent 文件：`evals/wren_agent_crm/runtime/wrenai-test-*.mjs`

活动 Agent 镜像使用 `Dockerfile.wrenai-test-agent`。MDL 搭建阶段由 Claude Agent SDK 直接挂载 Wren Skill、Bash、Read、Write、Edit、Glob、Grep 和 `AskUserQuestion`；不启动语义 Executor，也不挂载自定义建模 MCP。Wren MCP 只在 `target/mdl.json` 构建成功后用于查询。

## 密钥与服务器配置

Git 只保存以下模板：

- `runtime/bailian.env.example`
- `runtime/mysql-root.env.example`
- `runtime/wren-home/profiles.yml.example`
- `project/.env.example`
- `project/connection.example.yml`

真实的百炼 API Key、MySQL 密码、`.env`、`connection.yml` 和 `profiles.yml` 仅保存在 22 服务器，不得提交到仓库。

## 后续开发与测试流程

1. 在本机 `/Users/0scar/project/WrenAI-test` 修改代码。
2. 完成静态检查并提交到 `codex/22-test-environment` 或其后续功能分支。
3. 将已确认的变更同步到 22 服务器 `/opt/wrenai-test` 对应目录。
4. 镜像构建、服务启动、语义 Agent、Chat BI 和基准测试只在 22 服务器运行。
5. 记录代码提交、镜像标签、模型名称、测试结果目录和已知问题。

同步时不得清空服务器数据库、评测结果或日志，不得修改同机的非 WrenAI 容器和项目。
