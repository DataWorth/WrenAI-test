import { runAgent } from "./agent-common.mjs";
const question = process.argv.slice(2).join(" ").trim();
if (!question) throw new Error("请提供 Chat BI 问题");
await runAgent(question, "wren_chatbi", "http://wren-eval-mcp:8080/mcp", 40);
