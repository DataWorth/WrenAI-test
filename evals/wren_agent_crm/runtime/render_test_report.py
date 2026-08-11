import argparse
import json
import re
from pathlib import Path


def markdown_cell(value):
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def yaml_value(text, key):
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\n\"']+)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def model_inventory(project):
    rows = []
    for path in sorted((project / "models").rglob("*.yml")):
        text = path.read_text(encoding="utf-8")
        columns = len(re.findall(r"^-\s+name:", text, re.MULTILINE))
        description_match = re.search(r"^\s+description:\s*([^\n]+)", text, re.MULTILINE)
        rows.append({
            "file": path.relative_to(project).as_posix(),
            "name": yaml_value(text, "name") or path.stem,
            "description": description_match.group(1).strip(" |-") if description_match else "",
            "columns": columns,
        })
    return rows


def transcript_rows(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        question = item.get("question") or item.get("prompt") or item.get("text") or ""
        answer = item.get("answer") or item.get("response") or item.get("input") or ""
        if isinstance(question, dict):
            options = question.get("options") or []
            if isinstance(answer, str) and answer.isdigit() and 1 <= int(answer) <= len(options):
                choice = options[int(answer) - 1].get("label", "")
                answer = f"{choice}（选项 {answer}）" if choice else answer
            question = question.get("question", "")
        if question or answer:
            rows.append((question, answer))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--wren-source-commit", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    project = Path(args.project)
    results = Path(args.results)
    models = model_inventory(project)
    relationships = project / "relationships.yml"
    relation_count = len(re.findall(r"^\s*-\s+name:", relationships.read_text(encoding="utf-8"), re.MULTILINE)) if relationships.exists() else 0
    knowledge = [path.relative_to(project).as_posix() for path in sorted((project / "knowledge").rglob("*")) if path.is_file()]
    benchmark_path = results / "chatbi-benchmark" / "benchmark_report.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8")) if benchmark_path.exists() else {}
    grill = transcript_rows(results / "human-grill-transcript.jsonl")

    lines = [
        "# SemWave 30表 CRM 语义构建与 Chat BI 测试报告",
        "",
        "## 执行范围",
        "",
        f"- Run ID：`{args.run_id}`",
        f"- 测试运行脚本提交：`{args.source_commit}`",
        f"- Wren 源码基线：`{args.wren_source_commit}`",
        f"- Agent 镜像：`{args.image}`",
        f"- Chat BI 模型：`{args.model}`",
        "- 数据范围：CRM 30张核心表、46条内部外键；历史55表测试集未参与本次运行。",
        "- 路径：先官方 `generate-mdl`，再官方 `enrich-context` Grill 真人逐题补充业务语义，随后 `validate`、`build`、MCP Chat BI 烟测和100题评测。",
        "",
        "## 语义构建结果",
        "",
        f"- 模型文件：{len(models)}",
        f"- 关系文件条目：{relation_count}",
        f"- 知识文件：{len(knowledge)}",
        f"- Grill 记录的问答：{len(grill)}",
        "",
        "| 模型 | 文件 | 字段项 | 描述 |",
        "|---|---|---:|---|",
    ]
    for item in models:
        lines.append(f"| {markdown_cell(item['name'])} | `{item['file']}` | {item['columns']} | {markdown_cell(item['description'])} |")
    lines.extend(["", "### 业务语义问答", ""])
    if grill:
        lines.extend(["| 问题 | 业务负责人回答 |", "|---|---|"])
        for question, answer in grill:
            lines.append(f"| {markdown_cell(question)} | {markdown_cell(answer)} |")
    else:
        lines.append("未解析到 Grill 逐题问答记录。")
    lines.extend(["", "### 知识文件", ""])
    lines.extend([f"- `{item}`" for item in knowledge] or ["- 无"])

    lines.extend(["", "## Chat BI 结果", ""])
    if benchmark:
        lines.extend([
            f"- 测试题数：{benchmark.get('total', 0)}",
            f"- SQL可运行：{benchmark.get('sql_runnable', 0)}/{benchmark.get('total', 0)}",
            f"- 精确答案：{benchmark.get('answer_exact', 0)}/{benchmark.get('total', 0)} ({benchmark.get('accuracy_exact', 0):.2%})",
            f"- 值集合匹配：{benchmark.get('value_set_match', 0)}/{benchmark.get('total', 0)} ({benchmark.get('accuracy_value_set', 0):.2%})",
            f"- 官方 usage 指南已加载：{benchmark.get('usage_guide_fetched', 0)}/{benchmark.get('total', 0)}",
            "",
            "| 类别 | 题数 | SQL可运行 | 精确答案 | 值集合匹配 |",
            "|---|---:|---:|---:|---:|",
        ])
        for category, item in benchmark.get("categories", {}).items():
            lines.append(f"| {category} | {item['total']} | {item['sql_runnable']} | {item['answer_exact']} | {item['value_set_match']} |")
        lines.extend(["", "### 每题结果", "", "| ID | 类别 | 问题 | 候选SQL | SQL可运行 | 精确答案 | 值集合匹配 | 错误 |", "|---:|---|---|---|:---:|:---:|:---:|---|"])
        for item in benchmark.get("items", []):
            lines.append(
                f"| {item['id']} | {markdown_cell(item['category'])} | {markdown_cell(item['question'])} | "
                f"`{markdown_cell(item.get('candidate_sql'))}` | "
                f"{'是' if item['sql_runnable'] else '否'} | {'是' if item['answer_exact'] else '否'} | "
                f"{'是' if item['value_set_match'] else '否'} | {markdown_cell(item.get('execution_error') or item.get('agent_error'))} |"
            )
    else:
        lines.append("未找到完整100题评分报告。")
    lines.extend(["", "## 验证证据", "", "- `generate-mdl.log`、`enrich-context.log`、Grill JSONL、`validate`/`build`输出、MCP烟测和每题原始结果均保留在服务器本次 run 对应结果目录。", "- 评分以Wren语义层执行候选SQL后与同一数据库快照的参考SQL结果对比；未把题目或参考SQL提供给语义构建Agent。", ""])
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
