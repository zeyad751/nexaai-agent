"""FastAPI layer around the existing NexaAI LangGraph agent.

The agent itself (src/agent.py and its 15 tools) is used exactly as it is. This module
only adds what a web deployment needs: access control, input limits, rate limits,
execution limits, progress streaming and readable errors.

Run locally from the project root:
    uvicorn backend.main:app --reload --port 8000
"""
import hmac
import json
import logging
import queue
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import date
from typing import Literal

import openai
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel, Field

from backend.config import settings
from scripts.check_data_consistency import check as check_data_consistency
from src.agent import graph, tools

log = logging.getLogger("nexaai.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


# ---------------------------------------------------------------------------
# Startup: verify the data before accepting traffic
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    problems = check_data_consistency()
    app.state.data_consistent = not problems
    for problem in problems:
        log.error("Data inconsistency: %s", problem)
    if not settings.access_code:
        log.error("NEXAAI_ACCESS_CODE is not set: /chat will refuse every request.")
    if not settings.openai_key_present:
        log.error("OPENAI_API_KEY is not set: the agent cannot run.")
    log.info("Agent loaded with %d tools; data consistent: %s", len(tools), not problems)
    yield


app = FastAPI(title="NexaAI-Agent API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Access-Code"],
)


def _error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


@app.exception_handler(RequestValidationError)
async def _invalid_request(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    where = ".".join(str(p) for p in first.get("loc", []) if p != "body")
    return JSONResponse(
        status_code=422,
        content={"detail": {"code": "invalid_request",
                            "message": f"Invalid request ({where}): {first.get('msg', 'bad input')}"}},
    )


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.max_message_chars)
    history: list[HistoryItem] = Field(default_factory=list, max_length=200)


# ---------------------------------------------------------------------------
# Rate limiting (in memory: fine for one server instance; resets on restart)
# ---------------------------------------------------------------------------
class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit, self.window = limit, window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def _recent(self, key: str) -> deque:
        hits, now = self._hits[key], time.monotonic()
        while hits and now - hits[0] > self.window:
            hits.popleft()
        return hits

    def allow(self, key: str) -> bool:
        """Count one hit for key; False if the limit was already reached."""
        with self._lock:
            hits = self._recent(key)
            if len(hits) >= self.limit:
                return False
            hits.append(time.monotonic())
            return True

    def blocked(self, key: str) -> bool:
        """True if key is at the limit, without counting a new hit."""
        with self._lock:
            return len(self._recent(key)) >= self.limit

    def record(self, key: str) -> None:
        with self._lock:
            self._recent(key).append(time.monotonic())


chat_limiter = SlidingWindowLimiter(settings.chats_per_window, settings.rate_window_seconds)
failed_code_limiter = SlidingWindowLimiter(settings.failed_codes_per_window, settings.rate_window_seconds)
_daily = {"day": date.today(), "count": 0}
_daily_lock = threading.Lock()
_run_slots = threading.BoundedSemaphore(settings.max_concurrent_runs)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _take_daily_slot() -> bool:
    with _daily_lock:
        if _daily["day"] != date.today():
            _daily["day"], _daily["count"] = date.today(), 0
        if _daily["count"] >= settings.daily_chat_limit:
            return False
        _daily["count"] += 1
        return True


# ---------------------------------------------------------------------------
# Helpers for turning agent output into events
# ---------------------------------------------------------------------------
def _text_of(message) -> str:
    content = message.content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return content or ""


def _summarise_args(args: dict) -> str:
    for key in ("project_id", "employee_id", "client_id", "keyword"):
        if args.get(key):
            return str(args[key])
    query = args.get("query")
    if query:
        query = " ".join(str(query).split())
        return query if len(query) <= 140 else query[:137] + "..."
    return ""


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _build_messages(req: ChatRequest) -> list:
    history = req.history[-settings.max_history_messages:]
    messages = []
    for item in history:
        text = item.content[: settings.max_history_message_chars]
        messages.append(HumanMessage(text) if item.role == "user" else AIMessage(text))
    messages.append(HumanMessage(req.message))
    return messages


def _friendly(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, GraphRecursionError):
        return ("too_many_steps",
                "This question needed more reasoning steps than the agent is allowed to take. "
                "Try narrowing it, for example to one project, client or metric.")
    if isinstance(exc, openai.AuthenticationError):
        return ("server_config", "The server's AI credentials are not valid. Please contact the owner.")
    if isinstance(exc, openai.RateLimitError):
        return ("ai_busy", "The AI provider is rate-limiting requests right now. Please try again shortly.")
    if isinstance(exc, (openai.APITimeoutError, openai.APIConnectionError)):
        return ("ai_unreachable", "The AI provider could not be reached. Please try again.")
    return ("internal_error", "Something went wrong while answering. Please try again.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health(request: Request):
    ok = bool(getattr(request.app.state, "data_consistent", False))
    body = {"status": "ok" if ok else "degraded", "data_consistent": ok, "agent_tools": len(tools)}
    return JSONResponse(status_code=200 if ok else 503, content=body)


@app.post("/chat")
def chat(req: ChatRequest, request: Request, x_access_code: str = Header(default="")):
    ip = _client_ip(request)

    if not settings.access_code:
        raise _error(503, "server_config", "The server is not configured to accept requests.")
    if failed_code_limiter.blocked(ip):
        raise _error(429, "too_many_attempts", "Too many wrong access codes. Try again later.")
    if not hmac.compare_digest(x_access_code.encode(), settings.access_code.encode()):
        failed_code_limiter.record(ip)
        raise _error(401, "invalid_access_code", "The access code is missing or incorrect.")
    if not chat_limiter.allow(ip):
        raise _error(429, "rate_limited",
                     f"Limit of {settings.chats_per_window} questions per "
                     f"{settings.rate_window_seconds // 60} minutes reached. Please wait.")
    if not _take_daily_slot():
        raise _error(429, "daily_limit", "The demo's daily question limit has been reached. Try tomorrow.")

    messages = _build_messages(req)
    return StreamingResponse(
        _run_agent_stream(messages),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _run_agent_stream(messages: list):
    """Run the agent in a worker thread and turn its steps into server-sent events.

    The thread lets this generator send keep-alive comments while a long LLM call is in
    progress, and stop waiting once the time limit is reached.
    """
    # The concurrency slot is taken here, inside the stream, so it can never leak if the
    # client disconnects before the stream starts. The worker releases it when done.
    if not _run_slots.acquire(blocking=False):
        yield _sse("error", {"code": "busy",
                             "message": "The agent is busy with other questions. Try again in a minute."})
        return

    events: queue.Queue = queue.Queue()
    stop = threading.Event()

    def worker():
        try:
            for update in graph.stream(
                {"messages": messages},
                config={"recursion_limit": settings.recursion_limit},
                stream_mode="updates",
            ):
                events.put(("update", update))
                if stop.is_set():
                    return
            events.put(("end", None))
        except Exception as exc:  # passed to the generator, which reports it
            events.put(("error", exc))
        finally:
            _run_slots.release()

    started = time.monotonic()
    threading.Thread(target=worker, daemon=True).start()
    final_answer, steps = "", 0

    try:
        yield _sse("start", {"max_steps": settings.recursion_limit})
        while True:
            remaining = settings.run_timeout_seconds - (time.monotonic() - started)
            if remaining <= 0:
                stop.set()
                yield _sse("error", {"code": "timeout",
                                     "message": "The answer took too long and was stopped. "
                                                "Try a narrower question."})
                return
            try:
                kind, payload = events.get(timeout=min(15, remaining))
            except queue.Empty:
                yield ": keep-alive\n\n"
                continue

            if kind == "error":
                code, message = _friendly(payload)
                log.exception("Agent run failed", exc_info=payload)
                yield _sse("error", {"code": code, "message": message})
                return
            if kind == "end":
                if not final_answer:
                    yield _sse("error", {"code": "empty_answer",
                                         "message": "The agent finished without an answer. Please rephrase."})
                    return
                yield _sse("answer", {"content": final_answer,
                                      "seconds": round(time.monotonic() - started, 1),
                                      "steps": steps})
                yield _sse("done", {})
                return

            for node, output in payload.items():
                for message in (output or {}).get("messages", []):
                    if isinstance(message, AIMessage) and message.tool_calls:
                        steps += 1
                        yield _sse("tool_calls", {"step": steps, "calls": [
                            {"name": call["name"], "detail": _summarise_args(call.get("args") or {})}
                            for call in message.tool_calls
                        ]})
                    elif isinstance(message, AIMessage):
                        final_answer = _text_of(message)
                    elif isinstance(message, ToolMessage):
                        failed = str(message.content).startswith(("SQL ERROR", "ERROR", "DOCUMENT SEARCH ERROR"))
                        yield _sse("tool_result", {"name": message.name, "ok": not failed})
    finally:
        stop.set()  # client disconnected or stream ended: let the worker stop early
