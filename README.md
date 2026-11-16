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

Results were graded by hand against the dataset; the samples are small and synthetic.

**gpt-5.6-sol (the model the agent was developed and evaluated with):**

- **Question bank:** 40 questions in eight categories (retrieval, multi-table,
  cross-entity, analytical, comparative, investigative, strategic, agentic).
- **Graded first runs:** 21 questions, 20 passed (about 95%). Every figure in the answered
  questions matched the database; the one failure was a non-attempt, fixed on rerun.
- **Latest batch:** 8 questions, all passed (2 with flags).
- In a later live run through the API, Q23 failed: the same question can be answered
  differently on different runs.

**gpt-6.1-sol (the deployed model):** one live validation run through the API, covering
the five heaviest questions (Q23, Q25, Q36, Q37, Q38) and three simultaneous document
questions. All 8 passed, with every figure matching the database. It was slower (heaviest
answer 128 s versus 90 s) and cost about $0.07 per question on average. One run is
evidence, not proof of consistency.

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

## Model

The code default is `gpt-5.6-sol`, the evaluated model; the deployment (`render.yaml`)
uses `gpt-6.1-sol` with `NEXAAI_USE_RESPONSES_API=true`, because its tool calling needs
OpenAI's Responses API. Any model can be set through `NEXAAI_MODEL` without code changes,
and `/health` reports the model in use. The agent's original `temperature=0` never reached
`gpt-5.6-sol`, because LangChain drops non-default temperatures for gpt-5 models, so
answers can vary between runs.

## Limits and cost protection

The API applies these limits, all adjustable through environment variables:

| Limit | Default | Variable |
|---|---|---|
| Agent steps per answer | 40 | `AGENT_RECURSION_LIMIT` |
| Time per answer | 240 s | `AGENT_TIMEOUT_SECONDS` |
| Agent runs at the same time | 3 | `MAX_CONCURRENT_RUNS` |
| Questions per visitor | 10 per 10 min | `RATE_LIMIT_CHATS`, `RATE_LIMIT_WINDOW_SECONDS` |
| Wrong access codes before lockout | 5 per 10 min | `RATE_LIMIT_FAILED_CODES` |
| Questions per server process per day | 200 (30 on Render) | `DAILY_CHAT_LIMIT` |

These counters live in the server's memory. They reset whenever the server restarts, which
on Render's free tier includes waking from sleep, so the daily limit slows abuse but is
**not** a guaranteed daily cost ceiling. The real ceiling is on the OpenAI side: the
deployed key belongs to a separate project with a small prepaid balance that is not
auto-recharged, so requests stop when it runs out and the app says so. A request that hits the time limit keeps its concurrency slot until the
agent actually stops at its next step, so timeouts cannot exceed the concurrency limit.

## Deployment

`render.yaml` defines the Render web service: Python 3.11.9 (pinned, because Render's
default is newer), `/health` as the health-check path, and the three secrets
(`OPENAI_API_KEY`, `NEXAAI_ACCESS_CODE`, `ALLOWED_ORIGINS`) entered in Render's dashboard,
never stored in the repository. `/health` returns 503 when the two data sources disagree,
so Render will not route traffic to a deploy with inconsistent data.
