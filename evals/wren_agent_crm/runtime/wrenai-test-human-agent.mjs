import { query } from "@anthropic-ai/claude-agent-sdk";
import { createLiveUserInput } from "./wrenai-test-user-input.mjs";

const transcriptPath = process.env.WRENAI_TEST_TRANSCRIPT
  || "/results/human-grill-transcript.jsonl";
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
  || "请用 Grill 模式补充当前 CRM 项目的业务语义，每次只问一个问题。";

const prompt = [
  "Use the /wren skill for this request.",
  "Before doing any other work, run `wren skills get enrich-context` and follow the returned official guide.",
  userRequest,
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
  liveUser.close();
  console.error("USER_QA_TOTAL=" + liveUser.getQuestionCount());
}

if (resultSubtype !== "success") process.exitCode = 1;
