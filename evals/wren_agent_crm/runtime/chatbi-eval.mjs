import fs from "node:fs";
import { runAgent } from "./agent-common.mjs";

const id = Number(process.argv[2]);
if (!Number.isInteger(id)) throw new Error("题目 ID 必须是整数");
const maxTurns = Number(process.env.WRENAI_TEST_MAX_TURNS || "16");
if (!Number.isInteger(maxTurns) || maxTurns < 1) throw new Error("WRENAI_TEST_MAX_TURNS 必须是正整数");

const benchmarkPath = process.env.WRENAI_TEST_BENCHMARK || "/benchmarks/crm_30_core_100_qna.jsonl";
const tests = fs.readFileSync(benchmarkPath, "utf8").trim().split("\n").map(JSON.parse);
const test = tests.find((item) => item.id === id);
if (!test) throw new Error("找不到题目：" + id);

const prompt = [
  "Use the /wren skill for this request.",
  "Before answering, run `wren skills get usage` and follow the returned official guide.",
  "You are a Chat BI evaluation Agent. Use only wren_chatbi MCP tools for database context and SQL operations.",
  "You must call dry_plan, then dry_run, then run_sql before finalizing. Do not guess.",
  "Bash is allowed only to fetch the official usage guide. Execute read-only SQL only. Do not store an NL-to-SQL pair or modify memory during this independent benchmark question.",
  "Question: " + test.question,
].join("\n\n");

let result;
try {
  result = await runAgent(prompt, "wren_chatbi", "http://127.0.0.1:8080/mcp", maxTurns, {
    cwd: "/workspace",
    skills: ["wren"],
    tools: ["Bash"],
    allowedTools: ["Bash", "mcp__wren_chatbi__*"],
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Use the official Wren usage guide and Wren MCP tools only. Never write files, call raw database clients, or store memory in this benchmark.",
    },
  });
} catch (error) {
  result = {
    runSql: [],
    toolCalls: [],
    usageEvents: [],
    usageGuideFetched: false,
    finalText: "",
    resultSubtype: "error",
    error: error instanceof Error ? error.message : String(error),
  };
}

fs.writeFileSync("/results/" + id + ".json", JSON.stringify({
  id,
  category: test.category,
  question: test.question,
  benchmark_path: benchmarkPath,
  run_sql: result.runSql,
  mcp_tool_calls: result.toolCalls,
  usage_guide_fetched: result.usageGuideFetched,
  usage_events: result.usageEvents,
  result_subtype: result.resultSubtype,
  final_text: result.finalText,
  ...(result.error ? { error: result.error } : {}),
}, null, 2) + "\n", "utf8");

if (result.resultSubtype !== "success") process.exitCode = 1;
