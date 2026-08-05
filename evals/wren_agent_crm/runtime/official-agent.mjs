import { execFileSync } from "node:child_process";
import { query } from "@anthropic-ai/claude-agent-sdk";

for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
  if (!process.env[name]) throw new Error("Missing runtime variable: " + name);
}

const userRequest = process.env.WREN_USER_REQUEST || "帮我对连接的 CRM 业务数据库的所有表进行语义化。";
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
      append: "For a Wren request explicitly invoking /wren, load that discovery skill first. It directs you to fetch the matching current workflow from the installed Wren CLI. For semantic-model construction, run `wren skills get generate-mdl` before writing any model file, then follow that guide. Never read or print credential values from .env.",
    },
    mcpServers: {
      wren_semantic: { type: "http", url: "http://wren-eval-executor:8081/mcp", alwaysLoad: true },
    },
    allowedTools: [
      "Skill(wren)", "Bash", "Read", "Write", "Edit", "Glob", "Grep",
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
    console.error("AVAILABLE_TOOLS=" + JSON.stringify(message.tools || []));
  }
  if (message.type === "assistant" && message.message?.content) {
    for (const block of message.message.content) {
      if ("text" in block) console.log(block.text);
      if ("name" in block) {
        console.error("TOOL=" + block.name);
        if (block.name === "Skill" && block.input?.skill) console.error("SKILL_LOADED=" + block.input.skill);
        if (block.name === "Bash" && /wren skills get generate-mdl/.test(block.input?.command || "")) console.error("GENERATE_MDL_GUIDE_FETCHED=yes");
        if (block.name === "Write" && block.input?.file_path) console.error("WRITE_PATH=" + block.input.file_path);
      }
    }
  }
  if (message.type === "result") {
    resultSubtype = message.subtype;
    console.log("RESULT=" + message.subtype);
  }
}
if (resultSubtype !== "success") process.exitCode = 1;
