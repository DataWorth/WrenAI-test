import { appendFileSync, writeFileSync } from "node:fs";
import { query, createSdkMcpServer, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod/v4";

for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
  if (!process.env[name]) throw new Error("Missing runtime variable: " + name);
}

const transcriptPath = process.env.GRILL_TRANSCRIPT || "/results/grill-transcript.jsonl";
let questionNumber = 0;

function appendRecord(record) {
  appendFileSync(transcriptPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    ...record,
  }) + "\n", "utf8");
}

function writePreflight() {
  writeFileSync(transcriptPath, "", "utf8");
  appendRecord({
    kind: "preflight",
    question_number: 0,
    question: "请选择 enrich-context 会话模式。",
    answer: "Grill。由模拟 CRM 业务负责人逐题确认；不得改写 Wren 官方技能流程。",
  });
  appendRecord({
    kind: "preflight",
    question_number: 0,
    question: "请选择要丰富的 Wren 项目。",
    answer: "/workspace（crm-semantic，已包含 55 个结构化模型和 99 条 FK 关系）。",
  });
  appendRecord({
    kind: "preflight",
    question_number: 0,
    question: "是否授权只读抽样以确认低基数字段？",
    answer: "授权。仅限 crm_demo 的只读 SELECT，每个字段最多 30 个去重值；不得读取或输出任何凭据。",
  });
}

const baseline = `
这是一个用于评测的模拟 B2B CRM，不代表真实公司的业务制度。请把以下内容当作已确认的业务事实，并按 enrich-context 的对应 sink 写入；不要把这个统一答复误当作可直接套用到所有表的同名列。

1. 主数据与规范口径：accounts 是客户组织的唯一主数据；contacts 是客户联系人；leads 是尚未转化的线索；opportunities 是销售机会；sales_orders 是已下单业绩；contracts 是合同；invoices 是应收账单；payments 是实收；cases 是客户服务工单。仅用数据库已有 FK 关系，不新增关系。
2. 时间：created_at 是记录创建时间，业务时区 Asia/Shanghai；没有逻辑删除列，也没有通用的默认过滤条件，关闭/完成记录保留历史，报表须按具体问题显式筛选。
3. 统一维度：region 为销售大区（华东、华北、华南、华中、西南）；source 为获客或创建来源（官网咨询、行业峰会、渠道伙伴、客户转介绍、内容营销）；industry 为客户所属行业。它们只在客户、线索、机会和商业单据等业务实体中可作分析维度；在纯配置、关联、历史、沟通类表中，同名字段是测试填充值，不应解释成该实体固有业务属性。
4. 枚举：opportunities.status：赢单、输单、进行中；leads.status：已转化、已合格、已联系；cases.status：新建、处理中、待客户反馈、已关闭。其余表中的新建/进行中/已完成/已关闭/待跟进是演示生命周期占位值，除非该表被问到，否则不要创建跨表枚举规则。
5. 金额与数量：CNY 仅适用于 opportunities、quotes、quote_items、sales_orders、sales_order_items、contracts、contract_lines、invoices、invoice_lines、payments、renewals 及其明细。其 amount 是该业务单据的未税含义不明的演示金额，不能把多个单据金额跨表相加；unit_price 是 CNY 单价，quantity 是件数。probability 仅 opportunities 的赢单概率，范围 0-100；score 仅 customer_health_scores 的健康分（0-100）。其他表中同名数值均为测试占位，不得生成业务指标或单位。
6. 管道指标：允许创建一个 crm_sales_funnel cube，且只可定义：线索数（COUNT leads）、已合格线索数（leads.status=已合格）、已转化线索数（leads.status=已转化）、机会数（COUNT opportunities）、进行中管道金额（SUM opportunities.amount WHERE status=进行中）、赢单金额（SUM opportunities.amount WHERE status=赢单）、输单金额（SUM opportunities.amount WHERE status=输单）、赢单率（赢单机会数/(赢单机会数+输单机会数)，分母为 0 时返回 NULL）、订单金额（SUM sales_orders.amount）、开票金额（SUM invoices.amount）、回款金额（SUM payments.amount）。不要创建任何其他派生指标。
7. 风险与隐私：contacts、contact_addresses、notes、email_messages、email_events、meetings、meeting_attendees、case_comments、knowledge_articles 的 record_name 或正文相关记录都按潜在 PII/敏感沟通内容处理；不得把它们作为默认检索/聚合文本。所有 ID 仅作连接键，不能当作业务编号或金额。
8. 测试数据说明：数据库值可能存在字符编码瑕疵；中文枚举的业务含义以上述确认口径为准。无法由这里确定的具体列含义，请标注“需真实业务确认”，不要臆造。
`.trim();

function ownerAnswer(question, proposedAnswer, context, intendedSink) {
  const q = `${question}\n${proposedAnswer || ""}\n${context || ""}\n${intendedSink || ""}`.toLowerCase();
  let answer;
  if (/raw|文档|资料|文件|知识库/.test(q)) {
    answer = "目前没有外部 CRM 文档。请继续采用 Grill：允许只读低基数抽样，并把我逐题确认的答案作为本轮模拟业务事实；没有确认的含义标为‘需真实业务确认’，不要杜撰。";
  } else if (/模式|grill|auto.?pilot/.test(q)) {
    answer = "选择 Grill；每一个业务决定都先向我提问并取得本工具的明确答复后再写入。";
  } else if (/项目|project|路径|workspace/.test(q)) {
    answer = "使用当前 /workspace 项目；它就是 crm-semantic 的实际 MDL 根目录。";
  } else if (/抽样|采样|sample|distinct|低基数/.test(q)) {
    answer = "同意只读抽样。每个字段最多 30 个去重值；它只用于发现候选枚举，最终业务解释以我的答复为准。";
  } else if (/立方|cube|指标|metric|度量|赢单率|pipeline|漏斗/.test(q)) {
    answer = "同意新增且仅新增 crm_sales_funnel cube。它的合法指标、过滤条件和空分母处理已在统一基线第 6 条逐项确认；不要扩展其他指标，也不要跨单据相加。";
  } else if (/货币|金额|amount|单价|unit_price|数量|quantity|概率|probability|分数|score/.test(q)) {
    answer = "按统一基线第 5 条执行：只有列出的商业单据金额是 CNY；opportunities.probability 是 0-100 赢单概率；customer_health_scores.score 是 0-100 健康分；其余同名数字是测试占位，标‘需真实业务确认’，不要定义单位或指标。";
  } else if (/状态|status|枚举|enum|阶段|stage/.test(q)) {
    answer = "按统一基线第 4 条执行。机会、线索、工单各有确认的状态含义；其他表的通用状态/阶段值仅是演示占位，不得建立跨表通用状态规则。";
  } else if (/主数据|规范|canonical|客户|账户|account|联系人|contact|线索|lead|机会|opportun|订单|order|合同|contract|发票|invoice|回款|payment|工单|case/.test(q)) {
    answer = "按统一基线第 1 条执行：accounts 是客户主数据，contacts 是联系人，leads 是未转化线索，opportunities 是销售机会，sales_orders 是已下单业绩，contracts 是合同，invoices 是应收，payments 是实收，cases 是服务工单。使用现有 FK；不要新增推断关系。";
  } else if (/时间|时区|created_at|删除|软删|soft.?delete|默认过滤|default filter/.test(q)) {
    answer = "按统一基线第 2 条执行：created_at 是 Asia/Shanghai 的创建时间；无逻辑删除；无通用默认过滤。关闭或完成记录保留历史，查询时按具体业务问题显式筛选。";
  } else if (/隐私|pii|敏感|邮箱|邮件|备注|知识|沟通|姓名|地址/.test(q)) {
    answer = "按统一基线第 7 条执行：联系人、地址、备注、邮件、会议、工单评论、知识文章的 record_name 或正文相关内容均潜在敏感，不作为默认检索或聚合文本；所有 ID 仅连接，不是业务指标。";
  } else if (/大区|region|来源|source|行业|industry|维度|dimension/.test(q)) {
    answer = "按统一基线第 3 条执行：region 是销售大区，source 是获客/创建来源，industry 是客户所属行业；仅在客户、线索、机会和商业单据等业务实体中用作分析维度。纯配置、关联、历史、沟通表的同名列是演示填充值。";
  } else if (/关系|relationship|外键|fk|join/.test(q)) {
    answer = "保留并使用所有已有 FK 关系；不新增任何由命名猜测的关系，也不更改基数或连接条件。";
  } else {
    answer = "请把这个问题限定到具体模型、列和拟写内容后再问。已确认的统一 CRM 语义请按下列基线应用；无法映射时写‘需真实业务确认’，不要自行猜测。";
  }
  return `${answer}\n\n${baseline}`;
}

writePreflight();

const mockBusinessOwner = createSdkMcpServer({
  name: "mock_business_owner",
  version: "1.0.0",
  instructions: "这是测试用的模拟 CRM 业务负责人。调用 ask_business_owner 取得每一项业务语义写入前的确认；工具返回即代表用户已确认。",
  alwaysLoad: true,
  tools: [tool(
    "ask_business_owner",
    "向模拟 CRM 业务负责人提出一项具体语义问题。每次只能问一个决定，并在拟写入前调用。调用会完整记录问题与回答。",
    {
      question: z.string().min(1).describe("向业务负责人的单个具体问题"),
      proposed_answer: z.string().optional().describe("基于当前 MDL 和只读证据形成的具体拟稿"),
      context: z.string().optional().describe("相关模型、列、抽样或文档证据"),
      intended_sink: z.string().optional().describe("拟写入的 MDL、规则、cube 或记忆位置"),
    },
    async ({ question, proposed_answer, context, intended_sink }) => {
      questionNumber += 1;
      const answer = ownerAnswer(question, proposed_answer, context, intended_sink);
      appendRecord({
        kind: "business_question",
        question_number: questionNumber,
        question,
        proposed_answer: proposed_answer || null,
        context: context || null,
        intended_sink: intended_sink || null,
        answer,
      });
      console.error(`GRILL_QA_RECORDED=${questionNumber}`);
      return { content: [{ type: "text", text: answer }] };
    },
    { alwaysLoad: true },
  )],
});

const prompt = [
  "Use the /wren skill for this request.",
  "The user asks: use the official enrich-context Grill workflow to construct the CRM project's business semantics.",
  "This is a controlled test. The human has already chosen Grill, selected /workspace, and authorized read-only low-cardinality sampling; those preflight answers are recorded.",
  "Immediately load the Wren discovery skill and run `wren skills get enrich-context`. Follow that guide exactly; do not modify Wren's skill content.",
  "There is no raw business-document corpus. Every business decision must be asked through mcp__mock_business_owner__ask_business_owner before writing it. Ask one specific question at a time and include concrete evidence, proposed answer, and intended sink. The tool answer is an explicit user confirmation. Do not silently answer a semantic question yourself and do not use AskUserQuestion.",
  "Perform a comprehensive Grill session: cover the official semantic gaps across this 55-model CRM, not merely one high-level summary. Use MDL descriptions/tags, knowledge rules, and the explicitly confirmed cube only where the owner answer supports them. For uncertain fields, preserve uncertainty rather than inventing semantics.",
  "After each MDL change run validation as the official guide requires; finish with build and memory indexing if available. Never read or print credentials from .env.",
].join("\n\n");

console.error("GRILL_SESSION=started");
let resultSubtype = "unknown";
for await (const message of query({
  prompt,
  options: {
    settingSources: [],
    cwd: "/workspace",
    maxTurns: 420,
    skills: ["wren"],
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "This is an official Wren enrich-context Grill test. Use the mock_business_owner MCP tool for every business-semantic question before writing. It supplies the simulated user confirmation and records the full Q/A. Never read or print any .env value.",
    },
    mcpServers: {
      mock_business_owner: mockBusinessOwner,
      wren_semantic: { type: "http", url: "http://wren-eval-grill-executor:8081/mcp", alwaysLoad: true },
    },
    allowedTools: [
      "Skill(wren)", "Bash", "Read", "Write", "Edit", "Glob", "Grep",
      "mcp__mock_business_owner__ask_business_owner",
      "mcp__wren_semantic__list_tables",
      "mcp__wren_semantic__inspect_table",
      "mcp__wren_semantic__workspace_status",
      "mcp__wren_semantic__read_project_file",
      "mcp__wren_semantic__validate",
      "mcp__wren_semantic__build",
    ],
  },
})) {
  if (message.type === "system" && message.subtype === "init") {
    console.error("MCP_STATUS=" + JSON.stringify(message.mcp_servers));
  }
  if (message.type === "assistant" && message.message?.content) {
    for (const block of message.message.content) {
      if ("text" in block) console.log(block.text);
      if ("name" in block) {
        console.error("TOOL=" + block.name);
        if (block.name === "Skill" && block.input?.skill) console.error("SKILL_LOADED=" + block.input.skill);
        if (block.name === "Bash" && /wren skills get enrich-context/.test(block.input?.command || "")) console.error("ENRICH_CONTEXT_GUIDE_FETCHED=yes");
      }
    }
  }
  if (message.type === "result") {
    resultSubtype = message.subtype;
    console.log("RESULT=" + message.subtype);
  }
}
console.error("GRILL_QA_TOTAL=" + questionNumber);
if (resultSubtype !== "success") process.exitCode = 1;
