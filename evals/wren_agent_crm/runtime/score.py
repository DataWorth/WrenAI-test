import datetime
import decimal
import json
import os
import subprocess
from pathlib import Path

BENCHMARK = Path("/benchmarks/crm_100_qna.jsonl")
RESULTS = Path("/results")
WORKSPACE = Path("/workspace")


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
        normalized = [sorted(normalize(row).values(), key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)) for row in rows]
    return sorted(normalized, key=lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True))


def run_candidate(sql):
    command = ["wren", "query", "--sql", sql, "--output", "json"]
    process = subprocess.run(command, cwd=WORKSPACE, text=True, capture_output=True, timeout=120, env=os.environ.copy())
    if process.returncode:
        return None, (process.stdout + process.stderr).strip()[-12000:]
    payload = process.stdout.strip()
    try:
        return json.loads(payload), None
    except json.JSONDecodeError:
        lines = [line for line in payload.splitlines() if line.strip()]
        for line in reversed(lines):
            try:
                return json.loads(line), None
            except json.JSONDecodeError:
                pass
        return None, ("Cannot parse JSON result: " + payload[-4000:])


def main():
    tests = [json.loads(line) for line in BENCHMARK.read_text().splitlines() if line.strip()]
    report = []
    for test in tests:
        result_file = RESULTS / f"{test['id']}.json"
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
            item["candidate_sql"] = sql_list[-1] if sql_list else None
            if item["candidate_sql"]:
                answer, error = run_candidate(item["candidate_sql"])
                if error:
                    item["execution_error"] = error
                else:
                    item["sql_runnable"] = True
                    item["candidate_answer"] = normalize(answer)
                    item["answer_exact"] = sorted_rows(answer, True) == sorted_rows(test["gold_answer"], True)
                    item["value_set_match"] = sorted_rows(answer, False) == sorted_rows(test["gold_answer"], False)
            else:
                item["execution_error"] = "Agent did not invoke run_sql"
        report.append(item)

    exact = sum(1 for item in report if item["answer_exact"])
    value = sum(1 for item in report if item["value_set_match"])
    runnable = sum(1 for item in report if item["sql_runnable"])
    summary = {
        "model": os.environ.get("ANTHROPIC_MODEL", "unknown"),
        "total": len(report),
        "sql_runnable": runnable,
        "answer_exact": exact,
        "value_set_match": value,
        "accuracy_exact": round(exact / len(report), 4),
        "accuracy_value_set": round(value / len(report), 4),
        "items": report,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "benchmark_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    lines = [
        "# CRM Chat BI Benchmark",
        "",
        f"- Model: {summary['model']}",
        f"- Total: {summary['total']}",
        f"- SQL runnable: {runnable}/{len(report)}",
        f"- Exact answer accuracy: {exact}/{len(report)} ({summary['accuracy_exact']:.2%})",
        f"- Value-set accuracy: {value}/{len(report)} ({summary['accuracy_value_set']:.2%})",
        "",
        "| ID | Category | Runnable | Exact | Value set |",
        "|---:|---|:---:|:---:|:---:|",
    ]
    for item in report:
        lines.append(f"| {item['id']} | {item['category']} | {'Y' if item['sql_runnable'] else 'N'} | {'Y' if item['answer_exact'] else 'N'} | {'Y' if item['value_set_match'] else 'N'} |")
    (RESULTS / "benchmark_report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({key: summary[key] for key in summary if key != "items"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
