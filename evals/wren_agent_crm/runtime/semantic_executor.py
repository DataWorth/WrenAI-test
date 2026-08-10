import json
import os
import re
import subprocess
from pathlib import Path

import pymysql
from mcp.server.fastmcp import FastMCP

PROJECT = Path("/workspace").resolve()
mcp = FastMCP("wrenai-test-semantic")


def fail(message):
    raise ValueError(message)


def allowed_path(relative, write=False):
    if not isinstance(relative, str) or not relative or relative.startswith("/") or ".." in relative or "\\" in relative:
        fail("Invalid project-relative path")
    metadata = bool(re.fullmatch(r"models/[^/]+/metadata[.]yml", relative))
    rule = bool(re.fullmatch(r"knowledge/rules/[^/]+[.]md", relative))
    allowed = relative in ("wren_project.yml", "AGENTS.md", "relationships.yml", "target/mdl.json") or metadata or rule
    if not allowed:
        fail("Path is outside the allowed project scope")
    if write and not (relative == "relationships.yml" or metadata or rule):
        fail("This file is read-only")
    result = (PROJECT / relative).resolve()
    if PROJECT not in result.parents:
        fail("Path traversal blocked")
    return result


def run_wren(args):
    process = subprocess.run(
        ["wren", *args],
        cwd=PROJECT,
        text=True,
        capture_output=True,
        timeout=180,
        env=os.environ.copy(),
    )
    output = (process.stdout + process.stderr).strip()
    if process.returncode:
        raise RuntimeError(output[-12000:] or "Wren command failed")
    return output


def readonly_sql(sql):
    if not isinstance(sql, str) or not re.match(r"^\s*(SELECT|WITH)\s", sql, re.IGNORECASE):
        fail("Only SELECT or WITH queries are allowed")
    if ";" in sql or len(sql) > 8000:
        fail("SQL must be a single statement under 8000 characters")
    forbidden = (
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "GRANT",
        "REVOKE", "TRUNCATE", "CALL", "LOAD_FILE", "INTO OUTFILE", "SET ",
    )
    if any(token in sql.upper() for token in forbidden):
        fail("SQL contains a forbidden keyword")
    return sql


def db_connection():
    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
        read_timeout=30,
        connect_timeout=15,
    )


@mcp.tool()
def list_tables() -> str:
    """List the actual tables in the connected CRM database. Use this before per-table inspection."""
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT TABLE_NAME
                   FROM INFORMATION_SCHEMA.TABLES
                   WHERE TABLE_SCHEMA=%s AND TABLE_TYPE='BASE TABLE'
                   ORDER BY TABLE_NAME""",
                (os.environ["MYSQL_DATABASE"],),
            )
            tables = [row["TABLE_NAME"] for row in cursor.fetchall()]
    return json.dumps(tables, ensure_ascii=False)


@mcp.tool()
def inspect_table(table_name: str, sample_limit: int = 3) -> str:
    """Inspect one actual CRM table: columns, types, PK, FKs, and up to five sample rows."""
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", table_name):
        fail("Invalid table name")
    sample_limit = max(1, min(int(sample_limit), 5))
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_COMMENT
                   FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
                   ORDER BY ORDINAL_POSITION""",
                (os.environ["MYSQL_DATABASE"], table_name),
            )
            columns = cursor.fetchall()
            if not columns:
                fail("Table does not exist")
            cursor.execute(
                """SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                   FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                   WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL
                   ORDER BY COLUMN_NAME""",
                (os.environ["MYSQL_DATABASE"], table_name),
            )
            foreign_keys = cursor.fetchall()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_limit}")
            samples = cursor.fetchall()
    return json.dumps(
        {"table": table_name, "columns": columns, "foreign_keys": foreign_keys, "samples": samples},
        default=str,
        ensure_ascii=False,
    )
@mcp.tool()
def workspace_status() -> str:
    """List permitted semantic project files and their contents."""
    paths = []
    for pattern in ("wren_project.yml", "AGENTS.md", "relationships.yml", "models/*/metadata.yml", "knowledge/rules/*.md", "target/mdl.json"):
        for path in sorted(PROJECT.glob(pattern)):
            if path.is_file():
                paths.append({"path": str(path.relative_to(PROJECT)), "content": path.read_text()})
    return json.dumps(paths, ensure_ascii=False)


@mcp.tool()
def read_project_file(path: str) -> str:
    """Read an allowed Wren semantic project file."""
    return allowed_path(path).read_text()


@mcp.tool()
def validate() -> str:
    """Validate the current Wren semantic project."""
    return run_wren(["context", "validate", "--path", str(PROJECT)])


@mcp.tool()
def build() -> str:
    """Build the Wren MDL into target/mdl.json."""
    return run_wren(["context", "build", "--path", str(PROJECT)])


@mcp.tool()
def dry_plan(sql: str) -> str:
    """Translate a single Wren SQL query without executing it."""
    return run_wren(["dry-plan", "--sql", readonly_sql(sql)])


@mcp.tool()
def dry_run(sql: str) -> str:
    """Validate a single Wren SQL query against the CRM source without returning rows."""
    return run_wren(["dry-run", "--sql", readonly_sql(sql)])


@mcp.tool()
def run_sql(sql: str) -> str:
    """Run a single read-only analytics query through Wren against the CRM MySQL source."""
    return run_wren(["query", "--sql", readonly_sql(sql), "--output", "json"])


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8081
    mcp.settings.transport_security.enable_dns_rebinding_protection = False
    mcp.run(transport="streamable-http")
