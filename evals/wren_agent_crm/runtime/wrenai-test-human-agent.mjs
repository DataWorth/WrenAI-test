import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { createInterface } from "node:readline/promises";
import { stdin as input, stderr as output } from "node:process";
import { createSdkMcpServer, query, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod/v4";

const reader = createInterface({ input, output });

async function readAnswer(prompt) {
  while (true) {
    const answer = (await reader.question(prompt)).trim();
    if (answer) return answer;
    output.write("回答不能为空。请输入一句回答，或输入 /skip。\n");
  }
}

if (process.env.WRENAI_TEST_INPUT_SMOKE === "1") {
  const answer = await readAnswer("BUSINESS_OWNER_ANSWER> ");
  console.log("INPUT_SMOKE=success");
  console.log("ANSWER_LENGTH=" + answer.length);
  reader.close();
  process.exit(0);
}

for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
  if (!process.env[name]) throw new Error("Missing runtime variable: " + name);
}

const userRequest = process.env.WRENAI_TEST_USER_REQUEST
  || "请用 Grill 模式补充当前 CRM 项目的业务语义，每次只问一个问题。";
const transcriptPath = process.env.WRENAI_TEST_TRANSCRIPT
  || "/results/human-grill-transcript.jsonl";
let questionNumber = 0;

mkdirSync(dirname(transcriptPath), { recursive: true });
writeFileSync(transcriptPath, "", "utf8");

function appendRecord(record) {
  appendFileSync(transcriptPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    ...record,
  }) + "\n", "utf8");
}

const businessOwner = createSdkMcpServer({
  name: "business_owner",
  version: "1.0.0",
  instructions: "Ask the live test operator one focused business-semantic question and wait for the answer before writing.",
  alwaysLoad: true,
  tools: [tool(
    "ask_business_owner",
    "Ask one concrete business-semantic question. The live answer is explicit user confirmation for this question only.",
    {
      question: z.string().min(1),
      proposed_answer: z.string().optional(),
      context: z.string().optional(),
      intended_sink: z.string().optional(),
    },
    async ({ question, proposed_answer, context, intended_sink }) => {
      questionNumber += 1;
      output.write(`\nWRENAI_TEST_QUESTION=${questionNumber}\n`);
      output.write(`QUESTION:\n${question}\n`);
      if (proposed_answer) output.write(`PROPOSED_ANSWER:\n${proposed_answer}\n`);
      if (context) output.write(`CONTEXT:\n${context}\n`);
      if (intended_sink) output.write(`INTENDED_SINK:\n${intended_sink}\n`);
      const answer = await readAnswer("BUSINESS_OWNER_ANSWER> ");
      const normalizedAnswer = answer === "/skip"
        ? "跳过本项，不写入任何语义。"
        : answer;
      appendRecord({
        kind: "business_question",
        question_number: questionNumber,
        question,
        proposed_answer: proposed_answer || null,
        context: context || null,
        intended_sink: intended_sink || null,
        answer: normalizedAnswer,
      });
      console.error("BUSINESS_QA_RECORDED=" + questionNumber);
      return { content: [{ type: "text", text: normalizedAnswer }] };
    },
    { alwaysLoad: true },
  )],
});

const prompt = [
  "Use the /wren skill for this request.",
  "The original user request is: " + userRequest,
  "Fetch and follow `wren skills get enrich-context`.",
  "Use Grill mode. Ask exactly one concrete question at a time through mcp__business_owner__ask_business_owner. Wait for the live answer before writing. Do not preload, infer, or invent a business baseline. Treat /skip as no authorization to write that item. Never read or print credential values from .env.",
].join("\n\n");

console.error("USER_REQUEST=" + userRequest);
console.error("HUMAN_GRILL_SESSION=started");
let resultSubtype = "unknown";
try {
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
        append: "This is a live Wren enrich-context Grill session. Every business-semantic write requires a fresh answer from mcp__business_owner__ask_business_owner. Ask one focused question at a time. Never read or print credential values.",
      },
      mcpServers: {
        business_owner: businessOwner,
        wrenai_test: {
          type: "http",
          url: "http://wrenai-test-executor:8081/mcp",
          alwaysLoad: true,
        },
      },
      allowedTools: [
        "Skill(wren)", "Bash", "Read", "Write", "Edit", "Glob", "Grep",
        "mcp__business_owner__ask_business_owner",
        "mcp__wrenai_test__list_tables",
        "mcp__wrenai_test__inspect_table",
        "mcp__wrenai_test__workspace_status",
        "mcp__wrenai_test__read_project_file",
        "mcp__wrenai_test__validate",
        "mcp__wrenai_test__build",
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
          if (block.name === "Skill" && block.input?.skill) {
            console.error("SKILL_LOADED=" + block.input.skill);
          }
          if (block.name === "Bash" && /wren skills get enrich-context/.test(block.input?.command || "")) {
            console.error("ENRICH_CONTEXT_GUIDE_FETCHED=yes");
          }
        }
      }
    }
    if (message.type === "result") {
      resultSubtype = message.subtype;
      console.log("RESULT=" + message.subtype);
    }
  }
} finally {
  reader.close();
  console.error("BUSINESS_QA_TOTAL=" + questionNumber);
}

if (resultSubtype !== "success") process.exitCode = 1;
