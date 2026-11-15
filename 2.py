
from src.queries import (
    get_project,
    get_project_kpis,
    get_project_risks,
    get_project_milestones,
)

project_id = "PRJ-002"

print("PROJECT")
print(get_project(project_id))

print("\nKPIS")
print(get_project_kpis(project_id))

print("\nRISKS")
print(get_project_risks(project_id))

print("\nMILESTONES")
print(get_project_milestones(project_id))
