import re
import threading

from langchain_core.tools import tool
from src.rag.retriever import get_retriever

# LangGraph runs several tool calls of one step in parallel threads. Each call used to build
# a new Chroma PersistentClient, and creating clients concurrently crashes Chroma
# ("'RustBindingsAPI' object has no attribute 'bindings'" / "Could not connect to tenant
# default_tenant"). Creating the retriever under a lock avoids the race; the search itself
# still runs in parallel.
_RETRIEVER_LOCK = threading.Lock()


@tool
def search_documents_tool(query: str, project_id: str | None = None):
    """Semantic search over NexaAI's narrative documents. Use it for WHY / WHAT HAPPENED /
    lessons learned / root causes, which the structured database tools cannot answer.

    Corpus: up to five documents per project PRJ-001..PRJ-040 (proposal, kickoff,
    meeting_notes, postmortem, executive_review), plus company-level documents that belong
    to no project (client account reviews such as CLI-17_account_review, the strategy
    retrospective).

    HOW TO CALL:
    - Question about ONE project: ALWAYS pass project_id='PRJ-###'. The search is semantic,
      so writing the ID inside the query does NOT restrict the results.
    - Question about a client, a strategy or the whole portfolio: leave project_id empty
      and put the client or strategy NAME in the query
      (e.g. 'Ministry of Digital Development account review').
    - Every result has 'source' and 'project_id'. Check that they match the entity you
      asked about. If none do, retry with a different query or with the filter; never
      answer from unrelated chunks."""
    # Models often send "" or lower-case IDs; treat "" as "no filter" and normalise the rest.
    if project_id is not None:
        project_id = project_id.strip().upper() or None

    if project_id is not None and not re.fullmatch(r"PRJ-\d+", project_id):
        return (
            f"ERROR: project_id must look like PRJ-### (a project ID), got '{project_id}'. "
            "For a client or company-level question leave project_id empty and put the "
            "client name in the query. This is an invalid call, NOT evidence that no "
            "documents exist."
        )

    try:
        with _RETRIEVER_LOCK:
            retriever = get_retriever(project_id=project_id)
        documents = retriever.invoke(query)
    except Exception as exc:  # a tool failure must reach the model as text, not crash the run
        return (f"DOCUMENT SEARCH ERROR: {type(exc).__name__}: {exc}. This is a tool failure, "
                "NOT evidence that no documents exist. Retry once; if it fails again, say that "
                "the document search is unavailable and do not answer the 'why' from guesses.")

    results = []
    for document in documents:
        results.append({
            "content": document.page_content,
            "source": document.metadata.get("source"),
            "project_id": document.metadata.get("project_id"),
        })

    if not results:
        scope = f"project {project_id}" if project_id else "the document index"
        return f"No documents matched this query in {scope}. Try different wording."

    return results
