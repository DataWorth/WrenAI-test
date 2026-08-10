import { execFileSync } from "node:child_process";
import { query } from "@anthropic-ai/claude-agent-sdk";

for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
  if (!process.env[name]) throw new Error("Missing runtime variable: " + name);
}

const userRequest = process.env.WRENAI_TEST_USER_REQUEST
  || "请为当前连接的 CRM 数据库搭建 MDL。";
const guidedPrompt = execFileSync("wren", ["ask", userRequest, "--guided"], {
  cwd: "/workspace",
  encoding: "utf8",
  env: process.env,
});
const prompt = [
  "Use the /wren skill for this request.",
  "The original user request is: " + userRequest,
  "Wren's official guided task framing follows:",
  guidedPrompt,
].join("\n\n");

console.error("USER_REQUEST=" + userRequest);
console.error("WREN_GUIDED_PROMPT=loaded");
let resultSubtype = "unknown";
for await (const message of query({
  prompt,
  options: {
    settingSources: [],
    cwd: "/workspace",
    maxTurns: 260,
    skills: ["wren"],
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Load the Wren discovery skill first. For MDL construction, fetch and follow `wren skills get generate-mdl`. Use only discovered database metadata for structural semantics. Do not invent business definitions, metrics, or cubes. Never read or print credential values from .env.",
    },
    mcpServers: {
      wrenai_test: {
        type: "http",
        url: "http://wrenai-test-executor:8081/mcp",
        alwaysLoad: true,
      },
    },
    allowedTools: [
      "Skill(wren)", "Bash", "Read", "Write", "Edit", "Glob", "Grep",
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
    console.error("AVAILABLE_TOOLS=" + JSON.stringify(message.tools || []));
  }
  if (message.type === "assistant" && message.message?.content) {
    for (const block of message.message.content) {
      if ("text" in block) console.log(block.text);
      if ("name" in block) {
        console.error("TOOL=" + block.name);
        if (block.name === "Skill" && block.input?.skill) {
          console.error("SKILL_LOADED=" + block.input.skill);
        }
        if (block.name === "Bash" && /wren skills get generate-mdl/.test(block.input?.command || "")) {
          console.error("GENERATE_MDL_GUIDE_FETCHED=yes");
        }
        if (block.name === "Write" && block.input?.file_path) {
          console.error("WRITE_PATH=" + block.input.file_path);
        }
      }
    }
  }
  if (message.type === "result") {
    resultSubtype = message.subtype;
    console.log("RESULT=" + message.subtype);
  }
}

if (resultSubtype !== "success") process.exitCode = 1;
