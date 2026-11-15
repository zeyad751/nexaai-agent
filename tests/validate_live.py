"""Live validation of the API with the REAL agent (this costs OpenAI credit).

Start the server first, with the rate limit raised for this test (PowerShell):
    $env:RATE_LIMIT_CHATS="30"; uvicorn backend.main:app --port 8000

Then, in a second terminal (venv active, project root):
    python tests/validate_live.py              # both parts
    python tests/validate_live.py sequential   # only the multi-step questions
    python tests/validate_live.py concurrency  # only the simultaneous requests

Every event of every run is saved under validation_results/ for review.
"""
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("VALIDATE_URL", "http://localhost:8000")
CODE = os.getenv("NEXAAI_ACCESS_CODE", "")
OUT = Path("validation_results")

SEQUENTIAL = {
    "Q23": "How does Enterprise AI Transformation's schedule/budget performance compare "
           "between Nour Telecom and Meridian National Bank?",
    "Q25": "Compare the three \"poor start, strong recovery\" projects (PRJ-009, PRJ-028, "
           "PRJ-040) — is there a common structural cause behind the early struggles, or is "
           "each one unrelated?",
    "Q36": "Analyze all projects from 2022-2025, identify the main factors associated with "
           "underperformance, and recommend three concrete strategic improvements.",
    "Q37": "Investigate whether a specific group of employees tends to produce above-average "
           "outcomes when staffed together, and quantify how much better those outcomes are "
           "versus the portfolio average.",
    "Q38": "Build a risk register summary across the portfolio: which risk categories most "
           "strongly associate with schedule delay, budget overrun, and low adoption "
           "respectively, and which mitigation approaches actually worked when a risk was "
           "Realized rather than Mitigated?",
}

# Four questions sent at the same moment. Each is about a different project and needs
# document search, so Chroma is hit in parallel. With MAX_CONCURRENT_RUNS=3, exactly one
# of the four should be refused as busy.
CONCURRENT = {
    "C1-PRJ-003": "What caused the schedule delay on PRJ-003?",
    "C2-PRJ-021": "Why did PRJ-021 run so far over budget?",
    "C3-PRJ-009": "What happened during PRJ-009 that caused its rocky start, and what fixed it?",
    "C4-PRJ-030": "Why does PRJ-030 combine strong ROI with low adoption?",
}


def ask(question: str, history=None) -> dict:
    """Send one question; return all events plus timing."""
    started, events = time.monotonic(), []
    with httpx.stream("POST", f"{URL}/chat", timeout=600,
                      headers={"X-Access-Code": CODE},
                      json={"message": question, "history": history or []}) as resp:
        if resp.status_code != 200:
            return {"http": resp.status_code, "error": resp.read().decode(), "events": [],
                    "seconds": round(time.monotonic() - started, 1)}
        event = None
        for line in resp.iter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: ") and event:
                events.append((event, json.loads(line[6:])))
    return {"http": 200, "events": events, "seconds": round(time.monotonic() - started, 1)}


def save(name: str, question: str, result: dict) -> None:
    OUT.mkdir(exist_ok=True)
    lines = [f"QUESTION: {question}", f"HTTP {result['http']}  wall time {result['seconds']} s", ""]
    answer = ""
    for event, data in result["events"]:
        if event == "tool_calls":
            for call in data["calls"]:
                lines.append(f"[step {data['step']}] {call['name']}: {call['detail']}")
        elif event == "tool_result":
            lines.append(f"    -> {data['name']} {'ok' if data['ok'] else 'ERROR'}")
        elif event == "answer":
            answer = data["content"]
            lines.append(f"\n[answer after {data['seconds']} s, {data['steps']} steps]")
        elif event == "error":
            lines.append(f"\n[ERROR {data['code']}] {data['message']}")
    if result.get("error"):
        lines.append(f"\n[HTTP ERROR] {result['error']}")
    lines += ["", "========== FINAL ANSWER ==========", answer]
    (OUT / f"{name}.txt").write_text("\n".join(lines), encoding="utf-8")


def summary(result: dict) -> str:
    kinds = [e for e, _ in result["events"]]
    if result["http"] != 200:
        return f"HTTP {result['http']}"
    if "error" in kinds:
        return "error: " + next(d["code"] for e, d in result["events"] if e == "error")
    steps = next((d["steps"] for e, d in result["events"] if e == "answer"), "?")
    failed = sum(1 for e, d in result["events"] if e == "tool_result" and not d["ok"])
    return f"answered in {result['seconds']} s, {steps} steps, {failed} failed tool calls"


def run_sequential():
    print("\n=== Part 1: multi-step questions (one at a time) ===")
    for qid, question in SEQUENTIAL.items():
        print(f"{qid} ...", end=" ", flush=True)
        result = ask(question)
        save(qid, question, result)
        print(summary(result))


def run_concurrency():
    print("\n=== Part 2: four simultaneous requests ===")
    results, threads = {}, []
    barrier = threading.Barrier(len(CONCURRENT))

    def worker(name, question):
        barrier.wait()
        results[name] = ask(question)

    for name, question in CONCURRENT.items():
        threads.append(threading.Thread(target=worker, args=(name, question)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    busy, problems = 0, []
    for name, question in CONCURRENT.items():
        result = results[name]
        save(name, question, result)
        print(f"{name}: {summary(result)}")
        codes = [d["code"] for e, d in result["events"] if e == "error"]
        if codes == ["busy"]:
            busy += 1
            continue
        own = name.split("-", 1)[1]
        ids_used = {
            found for e, d in result["events"] if e == "tool_calls"
            for call in d["calls"] for found in re.findall(r"PRJ-\d{3}", call["detail"])
        }
        # A leak = this run touching a project that belongs to ANOTHER simultaneous question.
        # Other project IDs can be legitimate cross-references (check the saved trace).
        others = {key.split("-", 1)[1] for key in CONCURRENT} - {own}
        if ids_used & others:
            problems.append(f"{name}: tool calls used another simultaneous request's project "
                            f"{sorted(ids_used & others)}: possible state leak")
        doc_failures = [d for e, d in result["events"]
                        if e == "tool_result" and d["name"] == "search_documents_tool" and not d["ok"]]
        if doc_failures:
            problems.append(f"{name}: document search failed (possible Chroma concurrency issue)")
        answer = next((d["content"] for e, d in result["events"] if e == "answer"), "")
        if own not in answer:
            problems.append(f"{name}: answer does not mention {own}")

    print(f"\nRefused as busy: {busy} (expected exactly 1 with MAX_CONCURRENT_RUNS=3)")
    for problem in problems:
        print("PROBLEM:", problem)
    if busy == 1 and not problems:
        print("Concurrency checks passed: isolation, limit and document search all OK.")


if __name__ == "__main__":
    if not CODE:
        sys.exit("NEXAAI_ACCESS_CODE is not set in .env")
    part = sys.argv[1] if len(sys.argv) > 1 else "all"
    if part in ("all", "sequential"):
        run_sequential()
    if part in ("all", "concurrency"):
        run_concurrency()
    print(f"\nTraces saved in {OUT.resolve()}")
