from src.tools.database_tools import (
    get_project_tool,
    get_project_risks_tool,
)

from src.tools.rag_tools import search_documents_tool


print("=== DATABASE TOOL ===")

result = get_project_tool.invoke({
    "project_id": "PRJ-001"
})

print(result)


print("\n=== RISKS TOOL ===")

result = get_project_risks_tool.invoke({
    "project_id": "PRJ-001"
})

print(result)


print("\n=== RAG TOOL ===")

result = search_documents_tool.invoke({
    "query": "What were the major risks discussed during the project?"
})

for item in result:
    print("\n---")
    print("Source:", item["source"])
    print("Project:", item["project_id"])
    print(item["content"][:500])