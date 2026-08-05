import { query } from "@anthropic-ai/claude-agent-sdk";

export async function runAgent(prompt, serverName, url, maxTurns, setup = {}) {
  for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
    if (!process.env[name]) throw new Error("缺少运行环境变量：" + name);
  }
  const runSql = [];
  let finalText = "";
  let resultSubtype = "unknown";
  for await (const message of query({
    prompt,
    options: {
      settingSources: [],
      tools: setup.tools || [],
      maxTurns,
      ...(setup.cwd ? { cwd: setup.cwd } : {}),
      mcpServers: { [serverName]: { type: "http", url, alwaysLoad: true } },
      allowedTools: setup.allowedTools || ["mcp__" + serverName + "__*"],
      ...(setup.skills ? { skills: setup.skills } : {}),
      ...(setup.systemPrompt ? { systemPrompt: setup.systemPrompt } : {}),
    },
  })) {
    if (message.type === "system" && message.subtype === "init") {
      console.error("MCP 状态：" + JSON.stringify(message.mcp_servers));
    }
    if (message.type === "assistant" && message.message?.content) {
      for (const block of message.message.content) {
        if ("text" in block) { console.log(block.text); finalText += block.text + "\n"; }
        if ("name" in block) {
          console.error("工具调用：" + block.name);
          if (block.name === "Skill" && block.input?.skill) {
            console.error("已加载 skill：" + block.input.skill);
          }
          if (block.name.endsWith("__inspect_table") && block.input?.table_name) {
            console.error("逐表探查：" + block.input.table_name);
          }
          if (block.name.endsWith("__write_project_file") && block.input?.path) {
            console.error("语义文件写入：" + block.input.path);
          }
          if (block.name.endsWith("__run_sql") && block.input?.sql) runSql.push(block.input.sql);
        }
      }
    }
    if (message.type === "result") {
      resultSubtype = message.subtype;
      console.log("结束：" + message.subtype);
    }
  }
  return { runSql, finalText, resultSubtype };
}
