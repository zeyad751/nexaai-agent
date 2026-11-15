import re
from functools import wraps

from langchain_core.tools import tool

from src.queries import (
    get_project,
    search_projects,
    get_project_team,
    get_project_kpis,
    get_project_risks,
    get_client,
    search_clients,
    search_employees,
    get_employee,
    get_project_milestones,
    get_project_decisions,
    get_project_technologies,
    get_project_strategy,
)


# ---------------------------------------------------------------------------
# ID guard
# Passing a client/employee ID (CLI-17, EMP-080) to a project tool used to return
# an empty list / null, which the agent treated as "no data". The guard returns an
# explicit error that names the mistake instead, and normalises the ID
# (" prj-009 " -> "PRJ-009") before it reaches the database.
# ---------------------------------------------------------------------------
_ID_KINDS = {"PRJ": "project", "CLI": "client", "EMP": "employee"}


def requires_id(arg_name: str, prefix: str):
    """Validate that the first argument is an ID of the right type (PRJ / CLI / EMP)."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if args:
                value, rest = args[0], args[1:]
            else:
                value, rest = kwargs.pop(arg_name, ""), ()

            normalised = str(value or "").strip().upper()

            if not re.fullmatch(rf"{prefix}-\d+", normalised):
                match = re.fullmatch(r"([A-Z]+)-\d+", normalised)
                other = _ID_KINDS.get(match.group(1)) if match else None
                hint = f" '{value}' is a {other} ID." if other else ""
                return (
                    f"ERROR: {arg_name} must look like {prefix}-### "
                    f"(a {_ID_KINDS[prefix]} ID).{hint} "
                    "This is an invalid call, NOT evidence that the data is missing. "
                    "Use a different tool, or look up the correct ID first."
                )

            return fn(normalised, *rest, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Project tools (project_id = PRJ-###)
# ---------------------------------------------------------------------------
@tool
@requires_id("project_id", "PRJ")
def get_project_tool(project_id: str):
    """Get full details of ONE project (name, client, manager, dates, status, budget,
    actual cost, revenue, strategy, importance). project_id must be a project ID like
    PRJ-009. Never pass a client ID (CLI-##) or an employee ID (EMP-###). If you only have
    a project name, call search_projects_tool first to get the ID."""
    return get_project(project_id)


@tool
def search_projects_tool(keyword: str):
    """Find projects whose NAME or TYPE contains the keyword. It cannot filter by client,
    strategy, status, year or team member. Returns project IDs (PRJ-###) to use with the
    other project tools."""
    return search_projects(keyword)


@tool
@requires_id("project_id", "PRJ")
def get_project_team_tool(project_id: str):
    """Get the employees and their roles assigned to ONE project. project_id must be a
    project ID like PRJ-009 (not a client or employee ID)."""
    return get_project_team(project_id)


@tool
@requires_id("project_id", "PRJ")
def get_project_kpis_tool(project_id: str):
    """Get the KPI time series (ROI, revenue, cost, budget variance, satisfaction,
    adoption, delay days, scores) for ONE project. project_id must be a project ID like
    PRJ-009 (not a client or employee ID)."""
    return get_project_kpis(project_id)


@tool
@requires_id("project_id", "PRJ")
def get_project_risks_tool(project_id: str):
    """Get the risks recorded for ONE project (category, severity, probability, status,
    mitigation). project_id must be a project ID like PRJ-009 (not a client or employee
    ID)."""
    return get_project_risks(project_id)


# ---------------------------------------------------------------------------
# Client tools (client_id = CLI-##)
# ---------------------------------------------------------------------------
@tool
def search_clients_tool(keyword: str):
    """Find clients whose company NAME or INDUSTRY contains the keyword (pass '' to list
    all clients). Returns client IDs (CLI-##). It does not return the client's projects."""
    return search_clients(keyword)


@tool
@requires_id("client_id", "CLI")
def get_client_tool(client_id: str):
    """Get details of ONE client (industry, region, size, account manager, strategic
    priority, relationship start). client_id must be a client ID like CLI-17."""
    return get_client(client_id)


# ---------------------------------------------------------------------------
# Employee tools (employee_id = EMP-###)
# ---------------------------------------------------------------------------
@tool
def search_employees_tool(keyword: str):
    """Find employees by NAME, JOB TITLE or SPECIALIZATION using a plain substring match.
    The whole phrase must appear (e.g. 'Ryan Shawky', not 'Shawky Ryan'). Returns employee
    IDs (EMP-###)."""
    return search_employees(keyword)


@tool
@requires_id("employee_id", "EMP")
def get_employee_tool(employee_id: str):
    """Get details of ONE employee. employee_id must be an employee ID like EMP-080."""
    return get_employee(employee_id)


# ---------------------------------------------------------------------------
# More project tools
# ---------------------------------------------------------------------------
@tool
@requires_id("project_id", "PRJ")
def get_project_milestones_tool(project_id: str):
    """Get the milestones (planned vs actual dates, status, notes) of ONE project.
    project_id must be a project ID like PRJ-009 (not a client or employee ID)."""
    return get_project_milestones(project_id)


@tool
@requires_id("project_id", "PRJ")
def get_project_decisions_tool(project_id: str):
    """Get the logged decisions of ONE project (date, category, decision, rationale,
    outcome). Use it together with search_documents_tool for 'why' questions.
    project_id must be a project ID like PRJ-009."""
    return get_project_decisions(project_id)


@tool
@requires_id("project_id", "PRJ")
def get_project_technologies_tool(project_id: str):
    """Get the technologies used by ONE project. project_id must be a project ID like
    PRJ-009 (not a client or employee ID)."""
    return get_project_technologies(project_id)


@tool
@requires_id("project_id", "PRJ")
def get_project_strategy_tool(project_id: str):
    """Get the strategy (STRAT-##) applied to ONE project. project_id must be a project ID
    like PRJ-009. It cannot list the projects that use a given strategy."""
    return get_project_strategy(project_id)
