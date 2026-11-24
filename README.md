# NexaAI-Agent

An AI business-intelligence assistant for NexaAI Solutions, a fictional AI consultancy. It
answers questions about the company's projects, clients, employees, risks and strategies by
combining a structured database with the company's project documents, and it shows the
evidence behind every answer.

**Live demo:** [nexaai-agent.vercel.app](https://nexaai-agent.vercel.app/), access by
invitation (the site asks for an access code). The first question after a quiet period can
take about a minute while the server wakes up.

## What it can do

- **Look things up:** "Who is the project manager for PRJ-024?"
- **Calculate across the portfolio:** "Which risk category occurs most often, and what
  share of those risks were realized?"
- **Investigate what happened:** "What caused the schedule delay on PRJ-003?"
- **Compare and recommend:** "Should NexaAI keep offering Data-First Transformation, and
  under what conditions?"

While it works, the app shows each source the agent checks (database records, SQL analysis
or project documents), so every answer can be traced back to its evidence. Conversations
are kept in the browser, and follow-up questions use the recent conversation as context.

## How it works

1. **Web app (React):** the chat interface, with the live evidence trail and conversation
   history.
2. **API (FastAPI):** checks the access code and usage limits, runs the agent and streams
   its progress back to the app.
3. **Agent (LangGraph + OpenAI `gpt-6.1-sol`):** decides which tools a question needs, runs
   them, reads the results and repeats until it can answer, following 31 rules on accuracy,
   evidence and honest reporting.
4. **Tools (15):**
   - **13 database tools** for precise lookups: projects, teams, KPIs, risks, milestones,
     decisions, clients, employees, technologies and strategies.
   - **SQL analysis** for portfolio-wide calculations, read-only.
   - **Document search (RAG)** over 150 project documents (proposals, meeting notes,
     postmortems, executive reviews) for the "why" behind the numbers.

## The data

A synthetic dataset built for this project: 40 projects (2022–2025), 20 clients, 100
employees, 60 risks, quarterly KPIs, milestones and decisions, stored in a single SQLite
database, plus 150 narrative documents. The data contains deliberate patterns (for example,
strategies that succeed only under specific conditions) and realistic imperfections, such
as records that conflict with documents, to test whether the agent finds and reports them.

## Evaluation

The agent was tested on 38 questions across eight categories: retrieval, multi-table,
cross-entity, analytical, comparative, investigative, strategic and agentic.

- **39 of 39 passed:** the 38 questions plus a false-premise test ("Why did PRJ-014
  fail?"), which the agent correctly rejected with evidence.
- **Accuracy:** every figure checked matched the database, apart from a few 0.1 rounding
  differences. Each answer was checked against the database and documents by an AI
  reviewer (Claude), with figures recomputed independently.
- **Concurrency:** simultaneous questions stayed fully separate.
- **Cost and speed:** about $0.07 per question; the heaviest analytical answers take about
  two minutes.

Each question was run once, and answers can vary between runs, so a pass shows the agent
can answer correctly, not that it always will.

## Safeguards

- **Access code** checked by the server; it never appears in the website's code.
- **Read-only data:** the agent cannot change the database.
- **Usage limits:** per-visitor and daily question limits, a time limit per answer, and a
  cap on simultaneous questions.
- **Cost cap:** the AI usage runs on a small prepaid budget that is not topped up
  automatically. When it is used up, the app says so instead of answering.

## Limitations

- The same question can be answered differently on different runs.
- The demo runs on free hosting, so the first visit after a quiet period is slow.
- When the monthly AI budget is used up, the demo stops answering until it is renewed.
- Conversation history is stored per browser, not across devices.
- The data is synthetic and small (40 projects).

## Built with

Python, LangGraph, LangChain, OpenAI (`gpt-6.1-sol`, `text-embedding-3-small`), SQLite,
ChromaDB, FastAPI, React and Vite; hosted on Render (API) and Vercel (web app).
