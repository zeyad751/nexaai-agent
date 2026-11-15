
from src.connection import get_connection


def fetch_all_as_dicts(cursor):
    columns = [column[0] for column in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def fetch_one_as_dict(cursor):
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()

    if row is None:
        return None

    return dict(zip(columns, row))


def _fetch_all(query: str, params: tuple = ()):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return fetch_all_as_dicts(cursor)
    finally:
        connection.close()


def _fetch_one(query: str, params: tuple = ()):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return fetch_one_as_dict(cursor)
    finally:
        connection.close()


def get_project(project_id: str):
    return _fetch_one(
        """
        SELECT *
        FROM projects
        WHERE project_id = ?
        """,
        (project_id,)
    )


def get_project_team(project_id: str):
    return _fetch_all(
        """
        SELECT
            e.employee_id,
            e.full_name,
            e.job_title,
            pt.role_on_project,
            pt.allocation_percentage,
            pt.start_date,
            pt.end_date
        FROM project_team pt
        JOIN employees e
            ON pt.employee_id = e.employee_id
        WHERE pt.project_id = ?
        """,
        (project_id,)
    )


def get_project_kpis(project_id: str):
    return _fetch_all(
        """
        SELECT *
        FROM project_kpis
        WHERE project_id = ?
        ORDER BY reporting_period
        """,
        (project_id,)
    )


def get_project_risks(project_id: str):
    return _fetch_all(
        """
        SELECT *
        FROM risks
        WHERE project_id = ?
        ORDER BY severity DESC, probability DESC
        """,
        (project_id,)
    )


def get_client(client_id: str):
    return _fetch_one(
        """
        SELECT *
        FROM clients
        WHERE client_id = ?
        """,
        (client_id,)
    )


def search_projects(keyword: str):
    return _fetch_all(
        """
        SELECT *
        FROM projects
        WHERE project_name LIKE ?
           OR project_type LIKE ?
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )


def search_clients(keyword: str):
    return _fetch_all(
        """
        SELECT *
        FROM clients
        WHERE company_name LIKE ?
           OR industry LIKE ?
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )


def search_employees(keyword: str):
    return _fetch_all(
        """
        SELECT *
        FROM employees
        WHERE full_name LIKE ?
           OR job_title LIKE ?
           OR specialization LIKE ?
        """,
        (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )


def get_employee(employee_id: str):
    return _fetch_one(
        """
        SELECT *
        FROM employees
        WHERE employee_id = ?
        """,
        (employee_id,)
    )


def get_project_milestones(project_id: str):
    return _fetch_all(
        """
        SELECT *
        FROM milestones
        WHERE project_id = ?
        ORDER BY planned_date
        """,
        (project_id,)
    )


def get_project_decisions(project_id: str):
    return _fetch_all(
        """
        SELECT
            d.decision_id,
            d.decision_date,
            d.decision_category,
            d.decision,
            d.rationale,
            d.outcome,
            e.employee_id,
            e.full_name
        FROM decisions d
        LEFT JOIN employees e
            ON d.decision_maker_id = e.employee_id
        WHERE d.project_id = ?
        ORDER BY d.decision_date
        """,
        (project_id,)
    )


def get_project_technologies(project_id: str):
    return _fetch_all(
        """
        SELECT
            t.technology_id,
            t.technology_name,
            t.category,
            t.description,
            t.maturity_level,
            t.typical_use_cases
        FROM project_technologies pt
        JOIN technologies t
            ON pt.technology_id = t.technology_id
        WHERE pt.project_id = ?
        ORDER BY t.technology_name
        """,
        (project_id,)
    )


def get_project_strategy(project_id: str):
    return _fetch_one(
        """
        SELECT
            s.strategy_id,
            s.strategy_name,
            s.description,
            s.target_conditions,
            s.strengths,
            s.weaknesses,
            s.recommended_use_cases
        FROM projects p
        JOIN strategies s
            ON p.strategy_id = s.strategy_id
        WHERE p.project_id = ?
        """,
        (project_id,)
    )
