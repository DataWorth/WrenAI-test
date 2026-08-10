import { query } from "@anthropic-ai/claude-agent-sdk";
import { createLiveUserInput } from "./wrenai-test-user-input.mjs";

const transcriptPath = process.env.WRENAI_TEST_TRANSCRIPT
  || "/results/generate-mdl-transcript.jsonl";
const liveUser = createLiveUserInput(transcriptPath);

if (process.env.WRENAI_TEST_INPUT_SMOKE === "1") {
  const answer = await liveUser.readAnswer();
  console.log("INPUT_SMOKE=success");
  console.log("ANSWER_LENGTH=" + answer.length);
  liveUser.close();
  process.exit(0);
}

for (const name of ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"]) {
  if (!process.env[name]) throw new Error("Missing runtime variable: " + name);
}

const userRequest = process.env.WRENAI_TEST_USER_REQUEST
  || "请为当前连接的 CRM 数据库搭建 MDL。";
const prompt = [
  "Use the /wren skill for this request.",
  "Before doing any other work, run `wren skills get generate-mdl` and follow the returned official guide.",
  "Follow every user-confirmation gate in the guide. Do not add model or column descriptions, inferred relationships, knowledge rules, NL-to-SQL examples, calculated columns, views, or cubes unless the user explicitly approves them through AskUserQuestion.",
  "When resetting this run-specific project, preserve the existing wren_project.yml project identity, data source, catalog, schema, and profile. Do not invent or rename a connection profile.",
  userRequest,
].join("\n\n");

console.error("USER_REQUEST=" + userRequest);
let resultSubtype = "unknown";
try {
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
        append: "Use AskUserQuestion whenever the Wren workflow requires user input. Never ask a question only in text because this terminal host returns answers through AskUserQuestion. Never read or print credential values from .env.",
      },
      tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "AskUserQuestion"],
      allowedTools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
      canUseTool: liveUser.canUseTool,
    },
  })) {
    if (message.type === "system" && message.subtype === "init") {
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
} finally {
  liveUser.close();
  console.error("USER_QA_TOTAL=" + liveUser.getQuestionCount());
}

if (resultSubtype !== "success") process.exitCode = 1;
