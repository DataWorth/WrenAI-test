# AGENTS.md

Repository-wide instructions live in `.claude/CLAUDE.md`. Please refer to that file for shared build commands, architecture, and conventions.

**Before opening a pull request, read the "Contribution Bar" section of that file.** It sets out what is expected of a change here — reproduce a failure before claiming one, label honestly, make tests exercise the code they cover — and what will be closed rather than reviewed.

Per-module instructions live in `core/<module>/.claude/CLAUDE.md`, each with its own `AGENTS.md` pointing at it.

## WrenAI-test fork

This checkout is the development fork `DataWorth/WrenAI-test`. Keep these remotes and roles distinct:

- `origin`: `https://github.com/DataWorth/WrenAI-test.git`
- `upstream`: `https://github.com/Canner/WrenAI.git`
- local development checkout: `/Users/0scar/project/WrenAI-test`
- remote runtime and acceptance environment: SSH alias `nexus-data-22`, project root `/opt/wrenai-test`
- `/Users/0scar/project/refs/WrenAI` is a separate locked upstream reference checkout; never edit it for this fork

All source edits start in this fork. Do not edit Wren source directly on the server. Sync an identified local commit to the existing server project only after the user confirms the deployment/test action.

## Safety and environment boundaries

- Local execution is limited to source editing and service-free static checks. Do not start Wren, MySQL, Claude Agent SDK, MCP, Docker builds, or benchmark processes locally.
- Run dependency installation, compilation, containers, Wren CLI integration checks, semantic Agents, Chat BI, and benchmarks on `nexus-data-22`.
- Preserve `/opt/wrenai-test`, its MySQL data, logs, results, runs, backups, and existing test history. Do not relocate or recreate the project unless the user explicitly requests it.
- Never modify or remove containers whose names start with `nexus-dp-`. Container cleanup must name only the intended `wrenai-test-*` containers.
- Never use unscoped `rsync --delete`, `docker system prune`, broad recursive deletion, or database reset commands.
- `evals/wren_agent_crm/runtime/bootstrap_crm.py` emits `DROP DATABASE IF EXISTS crm_demo`. Running it or importing its generated SQL is destructive and requires separate explicit confirmation.
- Real `bailian.env`, `.env`, `connection.yml`, `profiles.yml`, API keys, and database passwords stay on the server. Never print them, copy them into Git, or include their values in logs.
- The MCP services use the internal Docker network `wrenai-test-net`; ordinary testing does not require opening a public port.

## Change workflow

1. Inspect the relevant code, `.claude/CLAUDE.md`, module instructions, and current server state read-only.
2. State the exact files, exclusions, test selection, server impact, and rollback plan; wait for confirmation before writes or remote changes.
3. Make the smallest local change on a `codex/` branch.
4. Run the service-free local checks below.
5. After deployment confirmation, sync only the reviewed files or commit to `/opt/wrenai-test` and run the selected remote tests.
6. Record the Git commit, source baseline, image tags, model name, commands, exit status, result directory, and known limitations.
7. Commit and push only the intended files. Recheck that local HEAD and its tracking branch are `0/0`.

## Test selection

Choose tests by changed surface; do not run the full benchmark for an unrelated edit.

| Changed surface | Required tests |
|---|---|
| Documentation only | Markdown/path review, `git diff --check` |
| Agent JavaScript or Python | Static syntax checks, secret scan, one remote targeted smoke test |
| `wrenai-testctl` or Dockerfile | Shell/static path checks, remote container/image preflight, targeted command smoke test |
| `core/wren` CLI or Skill | `just lint`, relevant `just test`, MDL validate/build, targeted Agent reproduction |
| `core/wren-core-py` | `just test` in that module, plus the affected CLI integration test |
| `core/wren-core` | Cargo check/test/fmt/clippy, plus the affected Python/CLI integration path |
| CRM MDL YAML or Knowledge | YAML parse, `wren context validate`, `wren context build`, representative Chat BI questions |
| Model-comparison benchmark | Single-question smoke first, then the explicitly approved 100-question benchmark |

## Service-free local checks

Run from the repository root. These checks do not constitute runtime acceptance.

```bash
git diff --check
bash -n evals/wren_agent_crm/runtime/wrenai-testctl
for file in evals/wren_agent_crm/runtime/*.mjs; do node --check "$file"; done
jq empty evals/wren_agent_crm/runtime/package.json
ruby -ryaml -rdate -e 'Dir["evals/wren_agent_crm/project/crm-semantic/**/*.yml"].each { |file| YAML.safe_load(File.read(file), permitted_classes: [Date, Time], aliases: true) }'
python3 - <<'PY'
import ast
import json
from pathlib import Path

root = Path("evals/wren_agent_crm")
for path in root.glob("runtime/*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
with (root / "benchmarks/crm_100_qna.jsonl").open(encoding="utf-8") as handle:
    rows = [json.loads(line) for line in handle]
assert len(rows) == 100
PY
```

Scan the staged candidate for literal credentials before every commit. Placeholder values in `*.example` files are allowed; a real token or password is not.

## Official module tests

Run only the affected module on `nexus-data-22`. The authoritative commands remain in `.claude/CLAUDE.md` and the module-specific instruction file.

```bash
# Rust semantic core
cd /opt/wrenai-test/source/core/wren-core
cargo check --all-targets
RUST_MIN_STACK=8388608 cargo test --lib --tests --bins
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings

# Python bindings
cd /opt/wrenai-test/source/core/wren-core-py
just test

# Python SDK and CLI
cd /opt/wrenai-test/source/core/wren
just lint
just test
```

Do not claim a bug fix from a source-text assertion. Reproduce the failing behavior and make the test exercise the real parser, CLI, engine, connector, or Agent path.

## Remote CRM preflight

Run this before any CRM runtime test. It checks presence only and must not display credential values.

```bash
ssh nexus-data-22
set -e
WRENAI_TEST_ROOT=/opt/wrenai-test
WRENAI_TEST_PROJECT="${WRENAI_TEST_PROJECT:-$WRENAI_TEST_ROOT/project}"
test -d "$WRENAI_TEST_PROJECT/models"
test -s "$WRENAI_TEST_PROJECT/relationships.yml"
test -s "$WRENAI_TEST_PROJECT/.env"
test -s "$WRENAI_TEST_ROOT/runtime/bailian.env"
test -s "$WRENAI_TEST_ROOT/runtime/wren-home/profiles.yml"
docker network inspect wrenai-test-net >/dev/null
docker image inspect wrenai-test-cli:74bf59e1-relfix1 >/dev/null
docker image inspect wrenai-test-agent:official-baseline-v1 >/dev/null
```

## MDL structure validation and build

`validate` is the first gate. `build` writes `target/mdl.json`, so use a user-approved test workspace when the generated output must not touch the canonical project.

```bash
WRENAI_TEST_ROOT=/opt/wrenai-test
WRENAI_TEST_PROJECT="${WRENAI_TEST_PROJECT:-$WRENAI_TEST_ROOT/project}"

docker run --rm --network wrenai-test-net \
  --env-file "$WRENAI_TEST_ROOT/project/.env" \
  -e WREN_HOME=/wren-home \
  -v "$WRENAI_TEST_PROJECT:/workspace:rw" \
  -v "$WRENAI_TEST_ROOT/runtime/wren-home:/wren-home:ro" \
  -w /workspace \
  wrenai-test-cli:74bf59e1-relfix1 context validate

docker run --rm --network wrenai-test-net \
  --env-file "$WRENAI_TEST_ROOT/project/.env" \
  -e WREN_HOME=/wren-home \
  -v "$WRENAI_TEST_PROJECT:/workspace:rw" \
  -v "$WRENAI_TEST_ROOT/runtime/wren-home:/wren-home:ro" \
  -w /workspace \
  wrenai-test-cli:74bf59e1-relfix1 context build

test -s "$WRENAI_TEST_PROJECT/target/mdl.json"
python3 -m json.tool "$WRENAI_TEST_PROJECT/target/mdl.json" >/dev/null
```

Acceptance requires a zero exit status, a parseable manifest, 30 expected models, valid relationships, and no unapproved source-YAML changes.

## Semantic-model Agent tests

### Recommended generate-mdl path

Use `runtime/wrenai-test-mdl-agent.mjs` for the official discovery flow. It accepts the short user request `请为当前连接的 CRM 数据库搭建 MDL。`, invokes the `/wren` Skill, obtains the current `generate-mdl` guide from the installed CLI, and lets the Agent use its built-in file and Bash tools plus SQLAlchemy for database discovery. It has no modeling Executor or custom modeling MCP. Its current cap is 260 SDK turns.

Semantic construction writes project files. Never run it against the canonical project. Create a run-specific workspace with `wrenai-testctl new-run` and retain the full log and project under the reported run ID.

```bash
WRENAI_TEST_ROOT=/opt/wrenai-test
RUN_PROJECT="$($WRENAI_TEST_ROOT/runtime/wrenai-testctl new-run)"
$WRENAI_TEST_ROOT/runtime/wrenai-testctl generate "$RUN_PROJECT"
```

The canonical project remains blank and is only copied into run-specific workspaces. Do not generate MDL directly in the canonical project.

### Recommended enrich-context Grill path

Use `runtime/wrenai-test-human-agent.mjs` when the test operator will answer business questions live. It loads the official `enrich-context` guide, asks exactly one question at a time through Claude Agent SDK's built-in `AskUserQuestion`, blocks for terminal input, and writes a complete JSONL transcript. It contains no hard-coded CRM business baseline. Its current cap is 420 SDK turns.

The Grill run is successful only if:

- the official Wren and `enrich-context` guides were loaded;
- every business-semantic write is backed by a recorded business-owner answer;
- `human-grill-transcript.jsonl` is non-empty and the question count is reported;
- final validation/build succeeds;
- no credential value appears in the transcript or log.

Start the live Grill only on the same run-specific project after `generate` succeeds:

```bash
/opt/wrenai-test/runtime/wrenai-testctl enrich "$RUN_PROJECT"
```

The operator reads each question and enters one answer or `/skip`. Starting it creates only the ephemeral `wrenai-test-human-agent`; get explicit confirmation before doing so.

The previous `official-agent.mjs`, hard-coded `grill-agent.mjs`, and `agentctl` are legacy evaluation artifacts. They are not active `wrenai-test` entrypoints and must not be used for current acceptance.

## Chat BI tests

`wrenai-testctl start-mcp` recreates `wrenai-test-mcp`, so obtain confirmation before running it. The MCP service stays inside `wrenai-test-net`; no public port is required.

```bash
WRENAI_TEST_ROOT=/opt/wrenai-test
$WRENAI_TEST_ROOT/runtime/wrenai-testctl start-mcp "$RUN_PROJECT"
```

The interactive Chat BI Agent is capped at 40 SDK turns. A successful smoke test must use Wren MCP tools, return `success`, execute only read-only SQL, and reconcile the result with a direct reference query.

## 100-question model benchmark

Run the benchmark only after a single-question smoke test passes and the user confirms the model name and expected API cost.

`wrenai-testctl benchmark <project>` runs the active 30-table benchmark (`benchmarks/crm_30_core_100_qna.jsonl`) and writes its per-question artifacts under the corresponding run result directory. The historical 55-table set (`benchmarks/crm_100_qna.jsonl`) is retained for comparison only and must not be used against the 30-table database.

Each benchmark question is capped at 16 SDK turns. `score.py` must report SQL-runnable, exact-answer, and value-set metrics. Preserve the generated result directory and record:

- Git commit and Wren source/image tag;
- model and endpoint platform, without credentials;
- total questions, Agent failures, runnable count, and accuracy metrics;
- per-question logs and scoring report;
- any timeout, MCP, SQL, encoding, or semantic-model failure separately.

Do not compare models from different MDL revisions, database snapshots, question sets, scoring code, or turn limits.
