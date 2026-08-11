import { query } from "@anthropic-ai/claude-agent-sdk";

function usageSnapshot(message) {
  const usage = message.usage || message.message?.usage || message.modelUsage;
  if (!usage || typeof usage !== "object") return null;
  return usage;
}

export async function runAgent(prompt, serverName, url, maxTurns, setup = {}) {
  for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
    if (!process.env[name]) throw new Error("缺少运行环境变量：" + name);
  }

  const runSql = [];
  const toolCalls = [];
  const usageEvents = [];
  let finalText = "";
  let resultSubtype = "unknown";
  let usageGuideFetched = false;

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
        if ("text" in block) {
          console.log(block.text);
          finalText += block.text + "\n";
        }
        if ("name" in block) {
          toolCalls.push(block.name);
          console.error("工具调用：" + block.name);
          if (block.name === "Bash" && /wren skills get usage/.test(block.input?.command || "")) {
            usageGuideFetched = true;
            console.error("USAGE_GUIDE_FETCHED=yes");
          }
          if (block.name.endsWith("__run_sql") && block.input?.sql) runSql.push(block.input.sql);
        }
      }
    }
    if (message.type === "result") {
      resultSubtype = message.subtype;
      const usage = usageSnapshot(message);
      if (usage) usageEvents.push(usage);
      console.log("结束：" + message.subtype);
    }
  }

  return { runSql, toolCalls, usageEvents, usageGuideFetched, finalText, resultSubtype };
}
