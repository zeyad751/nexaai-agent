import json, os, sys, time, dataclasses, threading
os.environ.update(NEXAAI_ACCESS_CODE="demo-code-123", OPENAI_API_KEY="sk-dummy",
                  ALLOWED_ORIGINS="http://localhost:5173,https://nexaai.vercel.app")
sys.path.insert(0, os.getcwd())
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError
import backend.main as m

results = []
def check(name, cond, info=""):
    results.append(cond); print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info and not cond else ""))

def events(resp):
    out = []
    for block in resp.text.split("\n\n"):
        lines = [l for l in block.split("\n") if l and not l.startswith(":")]
        if not lines: continue
        ev = lines[0].split(": ",1)[1]; data = json.loads(lines[1].split(": ",1)[1])
        out.append((ev, data))
    return out

class FakeGraph:
    def __init__(self, script=None, exc=None, delay=0): self.script, self.exc, self.delay, self.seen = script or [], exc, delay, None
    def stream(self, inp, config=None, stream_mode=None):
        self.seen = (inp, config)
        for upd in self.script:
            time.sleep(self.delay); yield upd
        if self.exc: raise self.exc

ok_script = [
  {"llm": {"messages": [AIMessage("", tool_calls=[{"name":"run_sql_tool","args":{"query":"SELECT COUNT(*) FROM projects"},"id":"1"},
                                                  {"name":"get_project_tool","args":{"project_id":"PRJ-014"},"id":"2"}])]}},
  {"tools": {"messages": [ToolMessage("{'rows': [[40]]}", name="run_sql_tool", tool_call_id="1"),
                          ToolMessage("SQL ERROR: x", name="get_project_tool", tool_call_id="2")]}},
  {"llm": {"messages": [AIMessage("There are **40** projects.")]}},
]
H = {"X-Access-Code": "demo-code-123"}
def ipH(ip, code="demo-code-123"): return {"X-Access-Code": code, "X-Forwarded-For": ip}

with TestClient(m.app) as c:
    r = c.get("/health"); check("health ok + data consistent + 15 tools", r.status_code==200 and r.json()=={"status":"ok","data_consistent":True,"agent_tools":15}, r.text)

    r = c.post("/chat", json={"message":"hi"}, headers={"X-Forwarded-For":"1.1.1.1"})
    check("missing code -> 401", r.status_code==401 and r.json()["detail"]["code"]=="invalid_access_code", r.text)
    for _ in range(4): c.post("/chat", json={"message":"hi"}, headers=ipH("2.2.2.2","wrong"))
    r = c.post("/chat", json={"message":"hi"}, headers=ipH("2.2.2.2","wrong")); check("5th wrong code still 401", r.status_code==401, r.text)
    r = c.post("/chat", json={"message":"hi"}, headers=ipH("2.2.2.2")); check("after 5 wrong codes -> 429 even with right code", r.status_code==429 and r.json()["detail"]["code"]=="too_many_attempts", r.text)

    r = c.post("/chat", json={"message":""}, headers=ipH("3.3.3.3")); check("empty message -> 422 readable", r.status_code==422 and r.json()["detail"]["code"]=="invalid_request", r.text)
    r = c.post("/chat", json={"message":"x"*4001}, headers=ipH("3.3.3.4")); check("4001-char message -> 422", r.status_code==422, r.text)
    r = c.post("/chat", json={"message":"hi","history":[{"role":"system","content":"x"}]}, headers=ipH("3.3.3.5")); check("history role 'system' rejected", r.status_code==422, r.text)

    fake = FakeGraph(ok_script); m.graph = fake
    hist = [{"role":"user","content":"q1"},{"role":"assistant","content":"a1"}]
    r = c.post("/chat", json={"message":"How many projects?","history":hist}, headers=ipH("4.4.4.4"))
    ev = events(r); names = [e for e,_ in ev]
    check("stream event order", names==["start","tool_calls","tool_result","tool_result","answer","done"], names)
    check("tool call details summarised", ev[1][1]["calls"]==[{"name":"run_sql_tool","detail":"SELECT COUNT(*) FROM projects"},{"name":"get_project_tool","detail":"PRJ-014"}], ev[1][1])
    check("failed tool flagged ok=false", ev[3][1]=={"name":"get_project_tool","ok":False}, ev[3][1])
    check("final answer delivered", ev[4][1]["content"]=="There are **40** projects.", ev[4][1])
    msgs = fake.seen[0]["messages"]
    check("history passed to agent in order", [type(x).__name__ for x in msgs]==["HumanMessage","AIMessage","HumanMessage"] and msgs[-1].content=="How many projects?")
    check("recursion limit passed", fake.seen[1]=={"recursion_limit":40}, fake.seen[1])

    long_hist = [{"role":"user" if i%2==0 else "assistant","content":f"m{i}"} for i in range(30)]
    m.graph = FakeGraph(ok_script); c.post("/chat", json={"message":"x","history":long_hist}, headers=ipH("4.4.4.5"))
    check("history capped at 12 + new message", len(m.graph.seen[0]["messages"])==13)

    m.graph = FakeGraph(ok_script[:1], exc=GraphRecursionError("limit"))
    ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("5.5.5.5")))
    check("step limit -> readable too_many_steps", ev[-1][0]=="error" and ev[-1][1]["code"]=="too_many_steps", ev[-1])

    m.graph = FakeGraph(ok_script[:1], exc=RuntimeError("secret internal detail /etc/x"))
    ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("5.5.5.6")))
    check("unexpected error hides internals", ev[-1][1]["code"]=="internal_error" and "secret" not in json.dumps(ev), ev[-1])

    m.graph = FakeGraph([]); ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("5.5.5.7")))
    check("no answer -> empty_answer error", ev[-1][1]["code"]=="empty_answer", ev)

    orig = m.settings; m.settings = dataclasses.replace(orig, run_timeout_seconds=1)
    m.graph = FakeGraph(ok_script, delay=3); t=time.time()
    ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("6.6.6.6")))
    check("time limit stops the run", ev[-1][1]["code"]=="timeout" and time.time()-t < 2.5, (ev, time.time()-t))
    m.settings = orig; time.sleep(3)

    m.graph = FakeGraph(ok_script)
    codes = [c.post("/chat", json={"message":"x"}, headers=ipH("7.7.7.7")).status_code for _ in range(11)]
    check("11th question in window -> 429", codes[:10]==[200]*10 and codes[10]==429, codes)

    held = [m._run_slots.acquire(blocking=False) for _ in range(3)]
    ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("8.8.8.8")))
    check("all 3 agent slots busy -> busy error", ev[-1][1]["code"]=="busy", ev)
    for h in held:
        if h: m._run_slots.release()
    ev = events(c.post("/chat", json={"message":"x"}, headers=ipH("8.8.8.9")))
    check("slots free again afterwards", ev[-1][0]=="done", ev)

    pre = dict(Origin="https://nexaai.vercel.app", **{"Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type,x-access-code"})
    r = c.options("/chat", headers=pre); check("CORS allows the frontend", r.headers.get("access-control-allow-origin")=="https://nexaai.vercel.app", dict(r.headers))
    pre["Origin"]="https://evil.example"
    r = c.options("/chat", headers=pre); check("CORS refuses other sites", "access-control-allow-origin" not in r.headers, dict(r.headers))

print(f"\n{sum(results)}/{len(results)} checks passed")
