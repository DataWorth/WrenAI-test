# AGENTS.md

Repository-wide instructions live in `.claude/CLAUDE.md`. Please refer to that file for shared build commands, architecture, and conventions.

**Before opening a pull request, read the "Contribution Bar" section of that file.** It sets out what is expected of a change here — reproduce a failure before claiming one, label honestly, make tests exercise the code they cover — and what will be closed rather than reviewed.

Per-module instructions live in `core/<module>/.claude/CLAUDE.md`, each with its own `AGENTS.md` pointing at it.

## WrenAI-test fork

This checkout is the development fork `DataWorth/WrenAI-test`. Keep these remotes and roles distinct:

- `origin`: `https://github.com/DataWorth/WrenAI-test.git`
- `upstream`: `https://github.com/Canner/WrenAI.git`
- local development checkout: `/Users/0scar/project/WrenAI-test`
- remote runtime and acceptance environment: SSH alias `nexus-data-22`, project root `/opt/wren-agent-eval`
- `/Users/0scar/project/refs/WrenAI` is a separate locked upstream reference checkout; never edit it for this fork

All source edits start in this fork. Do not edit Wren source directly on the server. Sync an identified local commit to the existing server project only after the user confirms the deployment/test action.

## Safety and environment boundaries

- Local execution is limited to source editing and service-free static checks. Do not start Wren, MySQL, Claude Agent SDK, MCP, Docker builds, or benchmark processes locally.
- Run dependency installation, compilation, containers, Wren CLI integration checks, semantic Agents, Chat BI, and benchmarks on `nexus-data-22`.
- Preserve `/opt/wren-agent-eval`, its MySQL data, logs, results, and existing test history. Do not relocate or recreate the project unless the user explicitly requests it.
- Never modify or remove containers whose names start with `nexus-dp-`. Container cleanup must name only the intended `wren-eval-*` containers.
- Never use unscoped `rsync --delete`, `docker system prune`, broad recursive deletion, or database reset commands.
- `evals/wren_agent_crm/runtime/bootstrap_crm.py` emits `DROP DATABASE IF EXISTS crm_demo`. Running it or importing its generated SQL is destructive and requires separate explicit confirmation.
- Real `bailian.env`, `.env`, `connection.yml`, `profiles.yml`, API keys, and database passwords stay on the server. Never print them, copy them into Git, or include their values in logs.
- The MCP services use the internal Docker network `wren-eval-net`; ordinary testing does not require opening a public port.

## Change workflow

1. Inspect the relevant code, `.claude/CLAUDE.md`, module instructions, and current server state read-only.
2. State the exact files, exclusions, test selection, server impact, and rollback plan; wait for confirmation before writes or remote changes.
3. Make the smallest local change on a `codex/` branch.
4. Run the service-free local checks below.
5. After deployment confirmation, sync only the reviewed files or commit to `/opt/wren-agent-eval` and run the selected remote tests.
6. Record the Git commit, source baseline, image tags, model name, commands, exit status, result directory, and known limitations.
7. Commit and push only the intended files. Recheck that local HEAD and its tracking branch are `0/0`.

## Test selection

Choose tests by changed surface; do not run the full benchmark for an unrelated edit.

| Changed surface | Required tests |
|---|---|
| Documentation only | Markdown/path review, `git diff --check` |
| Agent JavaScript or Python | Static syntax checks, secret scan, one remote targeted smoke test |
| `agentctl` or Dockerfile | Shell/static path checks, remote container/image preflight, targeted command smoke test |
| `core/wren` CLI or Skill | `just lint`, relevant `just test`, MDL validate/build, targeted Agent reproduction |
| `core/wren-core-py` | `just test` in that module, plus the affected CLI integration test |
| `core/wren-core` | Cargo check/test/fmt/clippy, plus the affected Python/CLI integration path |
| CRM MDL YAML or Knowledge | YAML parse, `wren context validate`, `wren context build`, representative Chat BI questions |
| Model-comparison benchmark | Single-question smoke first, then the explicitly approved 100-question benchmark |

## Service-free local checks

Run from the repository root. These checks do not constitute runtime acceptance.

```bash
git diff --check
bash -n evals/wren_agent_crm/runtime/agentctl
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
cd /opt/wren-agent-eval/source/core/wren-core
cargo check --all-targets
RUST_MIN_STACK=8388608 cargo test --lib --tests --bins
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings

# Python bindings
cd /opt/wren-agent-eval/source/core/wren-core-py
just test

# Python SDK and CLI
cd /opt/wren-agent-eval/source/core/wren
just lint
just test
```

Do not claim a bug fix from a source-text assertion. Reproduce the failing behavior and make the test exercise the real parser, CLI, engine, connector, or Agent path.

## Remote CRM preflight

Run this before any CRM runtime test. It checks presence only and must not display credential values.

```bash
ssh nexus-data-22
set -e
WREN_EVAL_ROOT=/opt/wren-agent-eval
WREN_EVAL_PROJECT="${WREN_EVAL_PROJECT:-$WREN_EVAL_ROOT/project/crm-semantic}"
test -d "$WREN_EVAL_PROJECT/models"
test -s "$WREN_EVAL_PROJECT/relationships.yml"
test -s "$WREN_EVAL_ROOT/project/.env"
test -s "$WREN_EVAL_ROOT/runtime/bailian.env"
test -s "$WREN_EVAL_ROOT/runtime/wren-home/profiles.yml"
docker network inspect wren-eval-net >/dev/null
docker image inspect wren-eval-cli:74bf59e1-relfix1 >/dev/null
docker image inspect wren-eval-executor:74bf59e1 >/dev/null
docker image inspect wren-eval-official-agent:relfix1 >/dev/null
```

## MDL structure validation and build

`validate` is the first gate. `build` writes `target/mdl.json`, so use a user-approved test workspace when the generated output must not touch the canonical project.

```bash
WREN_EVAL_ROOT=/opt/wren-agent-eval
WREN_EVAL_PROJECT="${WREN_EVAL_PROJECT:-$WREN_EVAL_ROOT/project/crm-semantic}"

docker run --rm --network wren-eval-net \
  --env-file "$WREN_EVAL_ROOT/project/.env" \
  -e WREN_HOME=/wren-home \
  -v "$WREN_EVAL_PROJECT:/workspace:rw" \
  -v "$WREN_EVAL_ROOT/runtime/wren-home:/wren-home:ro" \
  -w /workspace \
  wren-eval-cli:74bf59e1-relfix1 context validate

docker run --rm --network wren-eval-net \
  --env-file "$WREN_EVAL_ROOT/project/.env" \
  -e WREN_HOME=/wren-home \
  -v "$WREN_EVAL_PROJECT:/workspace:rw" \
  -v "$WREN_EVAL_ROOT/runtime/wren-home:/wren-home:ro" \
  -w /workspace \
  wren-eval-cli:74bf59e1-relfix1 context build

test -s "$WREN_EVAL_PROJECT/target/mdl.json"
python3 -m json.tool "$WREN_EVAL_PROJECT/target/mdl.json" >/dev/null
```

Acceptance requires a zero exit status, a parseable manifest, 55 expected models, valid relationships, and no unapproved source-YAML changes.

## Semantic-model Agent tests

### Recommended generate-mdl path

Use `runtime/official-agent.mjs` for the official discovery flow. It invokes the `/wren` Skill, obtains the current `generate-mdl` guide from the installed CLI, and then uses the semantic executor. Its current cap is 260 SDK turns.

Semantic construction writes project files. Never run it against the canonical project when the case requires a blank MDL. Create a run-specific workspace under `results/`, point `WREN_EVAL_PROJECT` at it, and retain the full log.

```bash
WREN_EVAL_ROOT=/opt/wren-agent-eval
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$WREN_EVAL_ROOT/results/semantic-official-$RUN_ID"
RUN_PROJECT="$RUN_DIR/project"
mkdir -p "$RUN_DIR"
cp -a "$WREN_EVAL_ROOT/project/crm-semantic" "$RUN_PROJECT"

WREN_EVAL_PROJECT="$RUN_PROJECT" "$WREN_EVAL_ROOT/runtime/agentctl" start
docker run --rm --network wren-eval-net \
  --env-file "$WREN_EVAL_ROOT/runtime/bailian.env" \
  --env-file "$WREN_EVAL_ROOT/project/.env" \
  -e WREN_USER_REQUEST="帮我对连接的 CRM 业务数据库的所有表进行语义化。" \
  -v "$RUN_PROJECT:/workspace:rw" \
  wren-eval-official-agent:relfix1 /app/official-agent.mjs \
  2>&1 | tee "$RUN_DIR/agent.log"
```

For a true blank-MDL benchmark, initialize a separate empty Wren project instead of copying `crm-semantic`. Do not delete the canonical project to obtain a blank state.

### Recommended enrich-context Grill path

Use `runtime/grill-agent.mjs` when fixed CRM business reference material is unavailable and user-like confirmation must be simulated. It loads the official `enrich-context` guide, calls the mock business-owner MCP tool for each semantic decision, and writes a complete JSONL transcript. Its current cap is 420 SDK turns.

The Grill run is successful only if:

- the official Wren and `enrich-context` guides were loaded;
- every business-semantic write is backed by a recorded business-owner answer;
- `grill-transcript.jsonl` is non-empty and the question count is reported;
- final validation/build succeeds;
- no credential value appears in the transcript or log.

Starting a Grill run recreates only `wren-eval-grill-agent` and `wren-eval-grill-executor`; get explicit confirmation before doing so. Use a run-specific copy of the project.

### Legacy semantic regression

`agentctl semantic` uses the earlier standalone `generate-mdl` Agent in `semantic-agent.mjs`, currently capped at 220 SDK turns. It is retained only for compatibility comparison. Do not report its result as the official Wren Skill workflow or as the preferred semantic-modeling result.

## Chat BI tests

`agentctl start` recreates `wren-eval-mcp` and `wren-eval-executor`, so obtain confirmation before running it. The MCP services stay inside `wren-eval-net`; no public port is required.

```bash
WREN_EVAL_ROOT=/opt/wren-agent-eval
WREN_EVAL_PROJECT="${WREN_EVAL_PROJECT:-$WREN_EVAL_ROOT/project/crm-semantic}"
WREN_EVAL_PROJECT="$WREN_EVAL_PROJECT" "$WREN_EVAL_ROOT/runtime/agentctl" start
"$WREN_EVAL_ROOT/runtime/agentctl" chatbi "2025 年赢单金额是多少？"
```

The interactive Chat BI Agent is capped at 40 SDK turns. A successful smoke test must use Wren MCP tools, return `success`, execute only read-only SQL, and reconcile the result with a direct reference query.

## 100-question model benchmark

Run the benchmark only after a single-question smoke test passes and the user confirms the model name and expected API cost.

```bash
WREN_EVAL_ROOT=/opt/wren-agent-eval
WREN_EVAL_PROJECT="${WREN_EVAL_PROJECT:-$WREN_EVAL_ROOT/project/crm-semantic}"
WREN_EVAL_PROJECT="$WREN_EVAL_PROJECT" \
  "$WREN_EVAL_ROOT/runtime/agentctl" benchmark qwen3.7-plus
```

Each benchmark question is capped at 16 SDK turns. `score.py` must report SQL-runnable, exact-answer, and value-set metrics. Preserve the generated result directory and record:

- Git commit and Wren source/image tag;
- model and endpoint platform, without credentials;
- total questions, Agent failures, runnable count, and accuracy metrics;
- per-question logs and scoring report;
- any timeout, MCP, SQL, encoding, or semantic-model failure separately.

Do not compare models from different MDL revisions, database snapshots, question sets, scoring code, or turn limits.
