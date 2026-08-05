import { runAgent } from "./agent-common.mjs";

const prompt = "帮我对连接的 CRM 业务数据库的所有表进行语义化。";
console.error("用户请求：" + prompt);

const result = await runAgent(
  prompt,
  "wren_semantic",
  "http://wren-eval-executor:8081/mcp",
  220,
  {
    skills: ["generate-mdl"],
    cwd: "/workspace",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "For a request to construct or populate a Wren semantic model, invoke the enabled generate-mdl skill before schema discovery or file changes. Follow the loaded skill's current YAML schema exactly; do not use legacy MDL formats.",
    },
    allowedTools: [
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "mcp__wren_semantic__workspace_status",
      "mcp__wren_semantic__list_tables",
      "mcp__wren_semantic__inspect_table",
      "mcp__wren_semantic__read_project_file",
      "mcp__wren_semantic__validate",
      "mcp__wren_semantic__build",
    ],
  },
);
if (result.resultSubtype !== "success") process.exitCode = 1;
