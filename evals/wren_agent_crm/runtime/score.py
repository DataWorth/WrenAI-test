import argparse
import datetime
import decimal
import json
import os
import subprocess
from collections import Counter
from pathlib import Path


def normalize(value):
    if isinstance(value, decimal.Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(decimal.Decimal(str(value)).normalize(), "f")
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize(value[key]) for key in sorted(value)}
    return value


def sorted_rows(rows, include_keys=True):
    if not isinstance(rows, list):
        return None
    if include_keys:
        normalized = [normalize(row) for row in rows]
    else:
        normalized = [sorted(normalize(row).values(), key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True)) for row in rows]
    return sorted(normalized, key=lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True))


def run_query(sql, workspace):
    command = ["wren", "query", "--sql", sql, "--output", "json"]
    process = subprocess.run(command, cwd=workspace, text=True, capture_output=True, timeout=120, env=os.environ.copy())
    if process.returncode:
        return None, (process.stdout + process.stderr).strip()[-12000:]
    payload = process.stdout.strip()
    try:
        value = json.loads(payload)
        return value if isinstance(value, list) else [value], None
    except json.JSONDecodeError:
        rows = []
        for line in payload.splitlines():
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, list):
                rows.extend(value)
            else:
                rows.append(value)
        if rows:
            return rows, None
        return None, "Cannot parse JSON result: " + payload[-4000:]


def escape_cell(value):
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default=os.environ.get("WRENAI_TEST_BENCHMARK", "/benchmarks/crm_30_core_100_qna.jsonl"))
    parser.add_argument("--results", default="/results")
    parser.add_argument("--workspace", default="/workspace")
    parser.add_argument("--only", type=int)
    parser.add_argument("--verify-gold", action="store_true")
    return parser.parse_args()


def category_summary(items):
    summary = {}
    for category in sorted({item["category"] for item in items}):
        group = [item for item in items if item["category"] == category]
        summary[category] = {
            "total": len(group),
            "sql_runnable": sum(item["sql_runnable"] for item in group),
            "answer_exact": sum(item["answer_exact"] for item in group),
            "value_set_match": sum(item["value_set_match"] for item in group),
        }
    return summary


def verify_gold(tests, workspace):
    failures = []
    for test in tests:
        answer, error = run_query(test["gold_sql"], workspace)
        if error or sorted_rows(answer, True) != sorted_rows(test["gold_answer"], True):
            failures.append({"id": test["id"], "error": error, "actual": normalize(answer) if answer is not None else None})
    print(json.dumps({"gold_total": len(tests), "gold_matched": len(tests) - len(failures), "gold_failures": failures}, ensure_ascii=False))
    return not failures


def score(tests, results, workspace):
    report = []
    for test in tests:
        result_file = results / f"{test['id']}.json"
        item = {
            "id": test["id"],
            "category": test["category"],
            "question": test["question"],
            "agent_result_present": result_file.exists(),
            "sql_runnable": False,
            "answer_exact": False,
            "value_set_match": False,
        }
        if result_file.exists():
            agent = json.loads(result_file.read_text())
            sql_list = [sql for sql in agent.get("run_sql", []) if isinstance(sql, str)]
            item["agent_result_subtype"] = agent.get("result_subtype")
            item["usage_guide_fetched"] = bool(agent.get("usage_guide_fetched"))
            item["mcp_tool_calls"] = agent.get("mcp_tool_calls", [])
            item["candidate_sql"] = sql_list[-1] if sql_list else None
            item["agent_error"] = agent.get("error")
            if item["candidate_sql"]:
                answer, error = run_query(item["candidate_sql"], workspace)
                if error:
                    item["execution_error"] = error
                else:
                    item["sql_runnable"] = True
                    item["candidate_answer"] = normalize(answer)
                    item["answer_exact"] = sorted_rows(answer, True) == sorted_rows(test["gold_answer"], True)
                    item["value_set_match"] = sorted_rows(answer, False) == sorted_rows(test["gold_answer"], False)
            else:
                item["execution_error"] = item["agent_error"] or "Agent did not invoke run_sql"
        report.append(item)

    total = len(report)
    exact = sum(item["answer_exact"] for item in report)
    value = sum(item["value_set_match"] for item in report)
    runnable = sum(item["sql_runnable"] for item in report)
    guide = sum(item.get("usage_guide_fetched", False) for item in report)
    summary = {
        "model": os.environ.get("ANTHROPIC_MODEL", "unknown"),
        "benchmark": os.environ.get("WRENAI_TEST_BENCHMARK", "unknown"),
        "total": total,
        "sql_runnable": runnable,
        "answer_exact": exact,
        "value_set_match": value,
        "usage_guide_fetched": guide,
        "accuracy_exact": round(exact / total, 4) if total else 0,
        "accuracy_value_set": round(value / total, 4) if total else 0,
        "categories": category_summary(report),
        "items": report,
    }
    results.mkdir(parents=True, exist_ok=True)
    (results / "benchmark_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# CRM Chat BI Benchmark",
        "",
        f"- Model: {summary['model']}",
        f"- Benchmark: {summary['benchmark']}",
        f"- Total: {total}",
        f"- Usage guide fetched: {guide}/{total}",
        f"- SQL runnable: {runnable}/{total}",
        f"- Exact answer accuracy: {exact}/{total} ({summary['accuracy_exact']:.2%})",
        f"- Value-set accuracy: {value}/{total} ({summary['accuracy_value_set']:.2%})",
        "",
        "## Category summary",
        "",
        "| Category | Total | Runnable | Exact | Value set |",
        "|---|---:|---:|---:|---:|",
    ]
    for category, item in summary["categories"].items():
        lines.append(f"| {category} | {item['total']} | {item['sql_runnable']} | {item['answer_exact']} | {item['value_set_match']} |")
    lines.extend([
        "",
        "## Per-question detail",
        "",
        "| ID | Category | Question | Candidate SQL | Guide | Runnable | Exact | Value set | Error |",
        "|---:|---|---|---|:---:|:---:|:---:|:---:|---|",
    ])
    for item in report:
        lines.append(
            "| {id} | {category} | {question} | `{sql}` | {guide} | {runnable} | {exact} | {value} | {error} |".format(
                id=item["id"],
                category=escape_cell(item["category"]),
                question=escape_cell(item["question"]),
                sql=escape_cell(item.get("candidate_sql")),
                guide="Y" if item.get("usage_guide_fetched") else "N",
                runnable="Y" if item["sql_runnable"] else "N",
                exact="Y" if item["answer_exact"] else "N",
                value="Y" if item["value_set_match"] else "N",
                error=escape_cell(item.get("execution_error") or item.get("agent_error")),
            )
        )
    (results / "benchmark_report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({key: summary[key] for key in summary if key not in {"items", "categories"}}, ensure_ascii=False))


def main():
    args = parse_args()
    tests = [json.loads(line) for line in Path(args.benchmark).read_text().splitlines() if line.strip()]
    if args.only is not None:
        tests = [test for test in tests if test["id"] == args.only]
        if not tests:
            raise SystemExit(f"benchmark does not contain id={args.only}")
    if args.verify_gold:
        raise SystemExit(0 if verify_gold(tests, Path(args.workspace)) else 1)
    score(tests, Path(args.results), Path(args.workspace))


if __name__ == "__main__":
    main()
