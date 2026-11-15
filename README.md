# NexaAI-Agent

A LangGraph agent that answers business-intelligence questions about NexaAI Solutions, a
synthetic AI consultancy (40 projects, 20 clients, 100 employees, 60 risks, KPIs, milestones,
decisions and 150 narrative documents).

## How it works

The agent loops between an LLM step and a tool step until it can answer:

- **LLM:** OpenAI `gpt-5.6-sol`, temperature 0, with a 31-rule system prompt (`src/agent.py`).
- **13 database tools:** fixed, parameterized queries on `data/nexaai.sqlite`.
- **`run_sql_tool`:** read-only analytical SQL on the CSV folder `data/nexaai_database`,
  loaded into in-memory SQLite (SELECT/WITH only, 200-row cap).
- **`search_documents_tool`:** semantic search over the 150 documents in a Chroma index
  (`data/vector_db`), embedded with OpenAI `text-embedding-3-small`.

The two structured data sources must stay identical. Check them with
`python -m scripts.check_data_consistency`.

## Evaluation

- **Question bank:** 40 questions in eight categories (retrieval, multi-table,
  cross-entity, analytical, comparative, investigative, strategic, agentic).
- **Graded first runs:** 21 questions, 20 passed (about 95%). Every figure in the answered
  questions matched the database; the one failure was a non-attempt, fixed on rerun.
- **Latest batch:** 8 questions, all passed (2 with flags).

Results were graded by hand against the dataset; the sample is small and synthetic.

## Setup

Requires Python 3.11.

```
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # then put your OpenAI key in .env
python test_agent.py
```

## Running the API

```
uvicorn backend.main:app --reload --port 8000
```

Then open http://localhost:8000/docs to try `/health` and `/chat`. `/chat` needs the
`X-Access-Code` header to match `NEXAAI_ACCESS_CODE` in `.env`, and streams progress
events (`start`, `tool_calls`, `tool_result`, `answer`, `done`, or `error`).

Backend checks that need no OpenAI key: `python tests/test_backend.py`.
