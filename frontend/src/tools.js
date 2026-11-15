// Plain-language names for the agent's 15 tools, grouped by the kind of source they read.
// The group decides the colour of the marker in the evidence trail.

export const SOURCE_KINDS = {
  database: "Project database",
  sql: "SQL analysis",
  documents: "Project documents",
};

const TOOLS = {
  get_project_tool: ["Project record", "database"],
  search_projects_tool: ["Project search", "database"],
  get_project_team_tool: ["Project team", "database"],
  get_project_kpis_tool: ["KPI history", "database"],
  get_project_risks_tool: ["Risk register", "database"],
  get_project_milestones_tool: ["Milestones", "database"],
  get_project_decisions_tool: ["Decision log", "database"],
  get_project_technologies_tool: ["Technologies", "database"],
  get_project_strategy_tool: ["Strategy", "database"],
  search_clients_tool: ["Client search", "database"],
  get_client_tool: ["Client record", "database"],
  search_employees_tool: ["Employee search", "database"],
  get_employee_tool: ["Employee record", "database"],
  run_sql_tool: ["SQL query", "sql"],
  search_documents_tool: ["Document search", "documents"],
};

export function describeTool(name) {
  const [label, kind] = TOOLS[name] || [name.replace(/_tool$/, "").replace(/_/g, " "), "database"];
  return { label, kind };
}
