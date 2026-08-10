import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { stderr as output, stdin as input } from "node:process";
import { createInterface } from "node:readline/promises";

export function createLiveUserInput(transcriptPath) {
  const reader = createInterface({ input, output });
  let questionNumber = 0;

  mkdirSync(dirname(transcriptPath), { recursive: true });
  writeFileSync(transcriptPath, "", "utf8");

  async function readAnswer(prompt = "USER_ANSWER> ") {
    while (true) {
      const answer = (await reader.question(prompt)).trim();
      if (answer) return answer;
      output.write("回答不能为空。请输入一句回答，或输入 /skip。\n");
    }
  }

  async function canUseTool(toolName, toolInput) {
    if (toolName === "ToolSearch") {
      return { behavior: "allow", updatedInput: toolInput };
    }
    if (toolName !== "AskUserQuestion") {
      return {
        behavior: "deny",
        message: "Only AskUserQuestion requires interactive approval.",
      };
    }

    const questions = Array.isArray(toolInput.questions) ? toolInput.questions : [];
    const answers = {};
    for (const question of questions) {
      questionNumber += 1;
      output.write(`\nWRENAI_TEST_QUESTION=${questionNumber}\n`);
      if (question.header) output.write(`HEADER: ${question.header}\n`);
      output.write(`QUESTION:\n${question.question}\n`);
      for (const [index, option] of (question.options || []).entries()) {
        output.write(`${index + 1}. ${option.label} — ${option.description}\n`);
      }
      const answer = await readAnswer();
      const normalizedAnswer = answer === "/skip"
        ? "跳过本项，不写入任何相关内容。"
        : answer;
      answers[question.question] = normalizedAnswer;
      appendFileSync(transcriptPath, JSON.stringify({
        timestamp: new Date().toISOString(),
        kind: "user_question",
        question_number: questionNumber,
        question,
        answer: normalizedAnswer,
      }) + "\n", "utf8");
      console.error("USER_QA_RECORDED=" + questionNumber);
    }
    return { behavior: "allow", updatedInput: { questions, answers } };
  }

  return {
    canUseTool,
    close: () => reader.close(),
    getQuestionCount: () => questionNumber,
    readAnswer,
  };
}
