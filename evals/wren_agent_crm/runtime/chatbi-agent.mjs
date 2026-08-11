import { writeFileSync } from "node:fs";
import { runAgent } from "./agent-common.mjs";

const question = process.argv.slice(2).join(" ").trim();
if (!question) throw new Error("请提供 Chat BI 问题");

const prompt = [
  "Use the /wren skill for this request.",
  "Before answering, run `wren skills get usage` and follow the returned official guide.",
  "Answer the user's question through the Wren semantic layer.",
  "For all database context, dry_plan, dry_run, and run_sql operations, use only wren_chatbi MCP tools.",
  "Bash is allowed only to fetch the official usage guide. Do not access raw tables, credentials, or project files.",
  "This is an evaluation session: execute read-only SQL only and do not store an NL-to-SQL pair or modify memory.",
  "Question: " + question,
].join("\n\n");

const result = await runAgent(prompt, "wren_chatbi", "http://wrenai-test-mcp:8080/mcp", 40, {
  cwd: "/workspace",
  skills: ["wren"],
  tools: ["Bash"],
  allowedTools: ["Bash", "mcp__wren_chatbi__*"],
  systemPrompt: {
    type: "preset",
    preset: "claude_code",
    append: "Follow the official Wren usage guide. Use Wren MCP tools only for database access and never write to the project during this evaluation.",
  },
});

const resultPath = process.env.WRENAI_TEST_CHATBI_RESULT;
if (resultPath) {
  writeFileSync(resultPath, JSON.stringify({ question, ...result }, null, 2) + "\n", "utf8");
}
if (result.resultSubtype !== "success") process.exitCode = 1;
