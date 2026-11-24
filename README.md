# NexaAI-Agent

A LangGraph agent that answers business-intelligence questions about NexaAI Solutions, a
synthetic AI consultancy (40 projects, 20 clients, 100 employees, 60 risks, KPIs, milestones,
decisions and 150 narrative documents).

**Live demo:** [nexaai-agent.vercel.app](https://nexaai-agent.vercel.app/) (access by invitation:
the site asks for an access code). The backend runs on Render's free plan, so the first
question after a quiet period can take about a minute while the server wakes up.

## How it works

The agent loops between an LLM step and a tool step until it can answer:

- **LLM:** OpenAI `gpt-6.1-sol` through the Responses API, with a 31-rule system prompt
  (`src/agent.py`).
- **13 database tools:** fixed, parameterized queries on `data/nexaai.sqlite`.
- **`run_sql_tool`:** read-only analytical SQL on the same `data/nexaai.sqlite`. Each query
  runs on a private in-memory copy of the database, so it can never change the data file
  (SELECT/WITH only, 5-second timeout, 200-row cap).
- **`search_documents_tool`:** semantic search over the 150 documents in a Chroma index
  (`data/vector_db`), embedded with OpenAI `text-embedding-3-small`.

### Data

`data/nexaai.sqlite` is the single source of structured data: 12 tables covering projects,
clients, employees, departments, project teams, KPIs, risks, milestones, decisions,
strategies and technologies. Every database tool and the SQL tool read this one file, so
they always see the same data. To change the data, edit this file; the SQL tool picks up the
change automatically.

The server checks the database at startup: the file must open and all 12 tables must exist
and contain rows. If the check fails, `/health` reports `degraded` (HTTP 503) and the
hosting platform keeps serving the previous working version. The same check runs locally
with `python -m scripts.check_database`.

The narrative documents live in `data/documents` and are searched through the Chroma
index in `data/vector_db`. After changing documents, rebuild the index with
`python build_vector.py` (this calls the OpenAI embeddings API).

## Evaluation

All results below are for `gpt-6.1-sol`, run through the API. Each answer was checked
against the database and the project documents by an AI reviewer (Claude), with every
figure recomputed independently.

- **Question bank:** 40 questions in eight categories (retrieval, multi-table,
  cross-entity, analytical, comparative, investigative, strategic, agentic). 38 were run;
  two comparative questions (Q21, Q22) were left out of the evaluation.
- **Result:** all 38 passed, plus a false-premise test ("Why did PRJ-014 fail?"), which the
  agent correctly rejected with evidence: **39 of 39**. Every figure checked matched the
  database, apart from a few that differed by 0.1 through rounding. A few answers carried minor flags (for example, a repeated search,
  or an average that included a cancelled project without calling it out).
- **Concurrency:** four simultaneous questions; the limit of three agent runs held, and no
  answer used another request's data.
- **Cost and speed:** about $0.07 per question on average; the heaviest analytical answers
  take about two minutes.

Limits of this evaluation: each question was run once, and the model's answers can vary
between runs, so a pass shows the agent can answer correctly, not that it always will. The
data is synthetic and small.

## Run it locally

The easiest way to try NexaAI-Agent is the live demo above. To run it yourself, you need
Python 3.11, Node.js 20 or newer, and your own OpenAI API key.

1. **Backend**

   ```
   python -m venv .venv
   .venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   copy .env.example .env            # macOS/Linux: cp .env.example .env
   ```

   In `.env`, set `OPENAI_API_KEY` and choose any `NEXAAI_ACCESS_CODE`. Then start the API:

   ```
   uvicorn backend.main:app --port 8000
   ```

2. **Frontend**, in a second terminal:

   ```
   cd frontend
   npm install
   npm run dev
   ```

3. Open http://localhost:5173 and enter the access code you set in `.env`.

For developers: http://localhost:8000/docs lets you call `/health` and `/chat` directly
(`/chat` needs the `X-Access-Code` header and streams progress events), and
`python tests/test_backend.py` runs the backend checks without an OpenAI key.

## Model

The agent uses `gpt-6.1-sol` through OpenAI's Responses API, which this model needs for
tool calling. Another model can be set with `NEXAAI_MODEL` (and
`NEXAAI_USE_RESPONSES_API=false` for models that use Chat Completions) without code
changes; the evaluation above applies only to `gpt-6.1-sol`. `/health` reports the model in
use. Temperature is left at the model's default, so answers can vary between runs.

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
never stored in the repository. `/health` returns 503 when the database check fails, so
Render will not route traffic to a deploy with a missing or incomplete database.
