import csv
import os
import re
import sqlite3
import threading
import time
from pathlib import Path

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Config. The data is a FOLDER OF CSV FILES: one file per table, file name = table name
# (clients.csv -> table "clients"). This file lives in <project>/src/tools/, so parents[2]
# is the project root (D:\NexaAI-Agent) and the default folder is
# D:\NexaAI-Agent\data\nexaai_database. Set the NEXAAI_DATA_DIR environment variable to
# use a different folder.
# ---------------------------------------------------------------------------
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "nexaai_database"
DATA_DIR = Path(os.getenv("NEXAAI_DATA_DIR", str(DEFAULT_DATA_DIR)))

MAX_ROWS = 200       # rows returned to the model; the rest are reported as truncated
TIMEOUT_SECONDS = 5  # abort runaway queries

_STARTS_OK = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)
_BLOCKED = re.compile(r"\b(attach|detach|pragma|load_extension)\b", re.IGNORECASE)
_INT = re.compile(r"^-?\d+$")
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _strip_sql_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", " ", sql)


# ---------------------------------------------------------------------------
# CSV -> in-memory SQLite.
# The CSV folder stays the single source of truth. It is loaded into an in-memory SQLite
# database once, and reloaded automatically when any CSV file changes (so patched data is
# picked up without restarting the agent). Every query runs on its own private in-memory
# COPY, so nothing the model sends can alter the master data or affect other queries.
# ---------------------------------------------------------------------------
_LOCK = threading.Lock()
_MASTER = None
_SIGNATURE = None


def _csv_files():
    files = sorted(DATA_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no .csv files found in {DATA_DIR}")
    return files


def _column_type(values):
    """INTEGER / REAL / TEXT, decided per column from all its non-empty values."""
    non_empty = [v for v in values if v != ""]
    if not non_empty:
        return "TEXT"
    if all(_INT.match(v) for v in non_empty):
        return "INTEGER"
    try:
        for v in non_empty:
            float(v)
        return "REAL"
    except ValueError:
        return "TEXT"


def _convert(value, sql_type):
    if value == "":
        return None  # empty CSV cell -> NULL
    if sql_type == "INTEGER":
        return int(value)
    if sql_type == "REAL":
        return float(value)
    return value


def _build_master(files):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    for path in files:
        table = path.stem
        if not _NAME.match(table):
            continue
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            rows = [(r + [""] * len(header))[: len(header)] for r in reader]
        types = [_column_type([r[i] for r in rows]) for i in range(len(header))]
        columns = ", ".join(f'"{name}" {sql_type}' for name, sql_type in zip(header, types))
        conn.execute(f'CREATE TABLE "{table}" ({columns})')
        placeholders = ", ".join("?" * len(header))
        conn.executemany(
            f'INSERT INTO "{table}" VALUES ({placeholders})',
            [[_convert(v, t) for v, t in zip(row, types)] for row in rows],
        )
    conn.commit()
    return conn


def _snapshot_connection():
    """Return a private in-memory copy of the data (rebuilding the master if CSVs changed)."""
    global _MASTER, _SIGNATURE
    with _LOCK:
        files = _csv_files()
        signature = tuple((f.name, f.stat().st_mtime_ns, f.stat().st_size) for f in files)
        if _MASTER is None or signature != _SIGNATURE:
            if _MASTER is not None:
                _MASTER.close()
            _MASTER = _build_master(files)
            _SIGNATURE = signature
        copy = sqlite3.connect(":memory:")
        _MASTER.backup(copy)
    return copy


@tool
def run_sql_tool(query: str):
    """Run ONE read-only SQL query (SQLite) on the NexaAI database (loaded from CSV files) and get exact rows back.
    USE THIS for anything that needs counting, summing, averaging, ranking, grouping,
    filtering or joining across several projects / clients / employees / risks (e.g. "which
    risk category is most common", "average score by industry", "projects per strategy").
    Do the arithmetic in SQL, never by hand. Do NOT use it for "why" questions (use
    search_documents_tool). Only SELECT / WITH queries are allowed; results are capped at
    200 rows (add ORDER BY / LIMIT / GROUP BY). Dates are ISO text (YYYY-MM-DD).

    TABLES (* = primary key):
    clients(client_id*, company_name, industry, country_region, company_size,
            annual_revenue_band, account_manager_id, strategic_priority, relationship_start_date)
    projects(project_id*, project_name, client_id, project_manager_id, start_date, end_date,
             planned_end_date, project_status, project_type, strategy_id, budget, actual_cost,
             revenue, team_size, primary_technology, complexity_level, strategic_importance)
    project_kpis(kpi_id*, project_id, reporting_period, roi, revenue, cost, budget_variance,
             revenue_growth, customer_satisfaction, employee_utilization, delivery_delay_days,
             model_accuracy, adoption_rate, operational_efficiency_gain, risk_score,
             overall_project_score)
    risks(risk_id*, project_id, risk_category, description, severity, probability,
          identified_date, mitigation_strategy, status, resolution_date)
    milestones(milestone_id*, project_id, milestone_name, planned_date, actual_date, status, notes)
    decisions(decision_id*, project_id, decision_date, decision_maker_id, decision_category,
              decision, rationale, outcome)
    project_team(project_id*, employee_id*, role_on_project, allocation_percentage,
                 start_date, end_date)
    project_technologies(project_id*, technology_id*)
    employees(employee_id*, full_name, job_title, department_id, seniority, years_experience,
              location, skills, specialization, hire_date, manager_id, employment_status)
    departments(department_id*, department_name, department_description, department_head)
    strategies(strategy_id*, strategy_name, description, target_conditions, strengths,
               weaknesses, recommended_use_cases)
    technologies(technology_id*, technology_name, category, description, maturity_level,
                 typical_use_cases)

    JOINS: projects.client_id -> clients.client_id; projects.strategy_id -> strategies.strategy_id;
    x.project_id -> projects.project_id; project_team.employee_id and
    decisions.decision_maker_id -> employees.employee_id; employees.department_id ->
    departments.department_id; departments.department_head holds an employee_id;
    clients.account_manager_id and projects.project_manager_id -> employees.employee_id.
    The client's industry is clients.industry: ALWAYS join projects to clients to get it.

    VALUES: project_status = Completed | Completed - Delayed | Cancelled | In Progress.
    risks.status = Mitigated | Realized. milestones.status = Completed | Completed - Delayed |
    Cancelled | Not Started. decisions.outcome = Positive | Mixed | Negative;
    decision_category = Budget Approval | Risk Response | Go-Live Approval | Strategy Pivot |
    Scope Change | Cancellation. strategic_priority / complexity_level = High | Medium | Low;
    projects.strategic_importance = Critical | High | Medium | Low.

    KPI RULES: project_kpis has several rows per project (reporting_period is text, either
    'YYYY-MM' or 'YYYY-Qn', consistent within one project). The "final / latest period" of a
    project is its MAX(reporting_period):
      ... FROM project_kpis k WHERE k.reporting_period =
          (SELECT MAX(k2.reporting_period) FROM project_kpis k2 WHERE k2.project_id = k.project_id)
    revenue and cost in project_kpis are CUMULATIVE, so the latest row is the project total;
    never sum them across periods. ROI = (revenue - cost) / cost * 100 (the roi column already
    holds it). budget_variance is a % against the prorated budget; delivery_delay_days is
    cumulative. A project may have no KPI rows.

    METRIC DEFINITIONS (use these exactly):
    - Project budget overrun % = (actual_cost - budget) * 100.0 / budget, from the projects table.
      It equals the project's final-period budget_variance. budget_variance is ALREADY a
      percent (e.g. 27.5 means 27.5%): never multiply it by 100.
    - Project-level questions need ONE value per project: use the projects table, or the
      final KPI period. Never average or sum across all KPI rows of a project (that
      weights projects by how many periods they have, and cumulative revenue/cost would be
      counted several times).
    - Project profit = revenue - actual_cost (projects table); ROI % = (revenue - actual_cost)
      * 100.0 / actual_cost.
    - SANITY CHECK before answering: a project-level overrun above ~100%, a score above 100
      or a percentage above 100 almost always means a unit or grain mistake. Re-check the
      query instead of explaining the number away.

    EXAMPLE (shape of a typical query: join, filter, group, order): average team size and
    number of projects per complexity level, completed projects only:
      SELECT p.complexity_level, ROUND(AVG(p.team_size), 1) AS avg_team_size, COUNT(*) AS n
      FROM projects p
      WHERE p.project_status IN ('Completed', 'Completed - Delayed')
      GROUP BY p.complexity_level ORDER BY avg_team_size DESC
    Ties: if the question asks for "the top" item, do not use LIMIT 1 blindly; check whether
    other rows share the top value. When a question can be read two ways (e.g. a split for
    one category vs for all rows), answer the more literal reading and state the other figure
    too if it costs one extra query.

    Returns {"columns": [...], "rows": [[...]], "row_count": N, "truncated": bool} or a
    string starting with "SQL ERROR". An error is not evidence that data is missing: fix the
    query and retry. Say how many rows/projects the numbers are based on."""
    cleaned = _strip_sql_comments(query or "").strip().rstrip(";").strip()

    if not cleaned:
        return "SQL ERROR: empty query."
    if not _STARTS_OK.match(cleaned):
        return "SQL ERROR: only read-only SELECT / WITH queries are allowed."
    if ";" in cleaned:
        return "SQL ERROR: send exactly one statement (no ';' inside the query)."
    if _BLOCKED.search(cleaned):
        return "SQL ERROR: ATTACH / PRAGMA / extensions are not allowed."

    deadline = time.monotonic() + TIMEOUT_SECONDS
    try:
        # Private in-memory copy per call: safe under parallel tool calls.
        conn = _snapshot_connection()
    except (OSError, ValueError, StopIteration, sqlite3.Error) as exc:
        return f"SQL ERROR: cannot load the data files from {DATA_DIR} ({exc})."

    try:
        conn.execute("PRAGMA query_only = ON")
        conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
        cursor = conn.execute(cleaned)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        fetched = cursor.fetchmany(MAX_ROWS + 1)
    except sqlite3.Error as exc:
        if "interrupted" in str(exc).lower():
            return (f"SQL ERROR: the query ran longer than {TIMEOUT_SECONDS} seconds and was "
                    "stopped. The query is too expensive (often a missing join condition), not "
                    "wrong: simplify it, add join conditions or aggregate in fewer steps, then retry.")
        return (f"SQL ERROR: {exc}. Check table and column names against the schema in the "
                "tool description, then fix the query and retry.")
    finally:
        conn.close()

    truncated = len(fetched) > MAX_ROWS
    rows = [list(r) for r in fetched[:MAX_ROWS]]
    return {"columns": columns, "rows": rows, "row_count": len(rows), "truncated": truncated}
