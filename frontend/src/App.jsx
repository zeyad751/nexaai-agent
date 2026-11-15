import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, checkHealth, streamChat } from "./api.js";
import {
  clearAccessCode,
  loadAccessCode,
  loadConversations,
  saveAccessCode,
  saveConversations,
} from "./storage.js";
import AccessGate from "./components/AccessGate.jsx";
import Brand from "./components/Brand.jsx";
import Composer from "./components/Composer.jsx";
import Exchange from "./components/Exchange.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Welcome from "./components/Welcome.jsx";

const HISTORY_EXCHANGES = 6; // last 6 question/answer pairs = 12 messages, the backend's cap
const HISTORY_CHARS = 8000; // the backend trims each history message to this length anyway

const newId = () =>
  (window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`).toString();

function titleFrom(question) {
  const oneLine = question.replace(/\s+/g, " ").trim();
  return oneLine.length > 60 ? `${oneLine.slice(0, 57)}…` : oneLine;
}

// The conversation sent to the backend: only finished question/answer pairs, as plain text.
function historyFor(conversation) {
  const done = (conversation?.messages || []).filter((m) => m.status === "done");
  return done.slice(-HISTORY_EXCHANGES).flatMap((m) => [
    { role: "user", content: m.question.slice(0, HISTORY_CHARS) },
    { role: "assistant", content: m.answer.slice(0, HISTORY_CHARS) },
  ]);
}

export default function App() {
  const [accessCode, setAccessCode] = useState(loadAccessCode);
  const [codeRejected, setCodeRejected] = useState(false);
  const [conversations, setConversations] = useState(loadConversations);
  const [activeId, setActiveId] = useState(null);
  const [serverState, setServerState] = useState("checking");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [runningId, setRunningId] = useState(null); // id of the message being answered
  const [answeredId, setAnsweredId] = useState(null); // answer to bring into view
  const abortRef = useRef(null);
  const scrollRef = useRef(null);

  const active = conversations.find((c) => c.id === activeId) || null;

  useEffect(() => saveConversations(conversations), [conversations]);

  // Check the server on load. Free hosting sleeps when idle, so a slow first answer
  // means it is waking up, not that it is broken.
  useEffect(() => {
    let cancelled = false;
    const slow = setTimeout(() => !cancelled && setServerState("waking"), 3000);
    checkHealth().then(({ ok, body }) => {
      if (cancelled) return;
      clearTimeout(slow);
      setServerState(ok ? "ok" : body ? "degraded" : "down");
    });
    return () => {
      cancelled = true;
      clearTimeout(slow);
    };
  }, []);

  // Keep the newest content in view while an answer streams in, unless the reader has
  // scrolled up to read something earlier.
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 240;
    if (nearBottom) el.scrollTop = el.scrollHeight;
  }, [conversations, activeId]);

  // When an answer arrives, show it from its question, not from its last line.
  useEffect(() => {
    if (!answeredId) return;
    document.getElementById(`exchange-${answeredId}`)?.scrollIntoView({ block: "start" });
    setAnsweredId(null);
  }, [answeredId]);

  const updateMessage = useCallback((conversationId, messageId, change) => {
    setConversations((list) =>
      list.map((c) =>
        c.id !== conversationId
          ? c
          : {
              ...c,
              updatedAt: Date.now(),
              messages: c.messages.map((m) => (m.id === messageId ? { ...m, ...change(m) } : m)),
            },
      ),
    );
  }, []);

  const ask = useCallback(
    async (question, conversationId = activeId) => {
      if (runningId) return;
      const messageId = newId();
      // Read the history from the current render's state, BEFORE queuing the update:
      // React may run state-update functions later, so they must not compute request data.
      const existing = conversations.find((c) => c.id === conversationId);
      const convId = existing ? existing.id : newId();
      const history = existing ? historyFor(existing) : [];
      const message = { id: messageId, question, status: "running", rounds: [], answer: "" };

      setConversations((list) =>
        list.some((c) => c.id === convId)
          ? list.map((c) =>
              c.id === convId ? { ...c, updatedAt: Date.now(), messages: [...c.messages, message] } : c,
            )
          : [
              { id: convId, title: titleFrom(question), createdAt: Date.now(), updatedAt: Date.now(), messages: [message] },
              ...list,
            ],
      );
      setActiveId(convId);
      setRunningId(messageId);
      setDrawerOpen(false);

      const controller = new AbortController();
      abortRef.current = controller;
      const fail = (code, message) =>
        updateMessage(convId, messageId, () => ({ status: "error", error: { code, message } }));

      try {
        let finished = false;
        await streamChat({
          message: question,
          history,
          accessCode,
          signal: controller.signal,
          onEvent: (name, data) => {
            if (name === "tool_calls") {
              updateMessage(convId, messageId, (m) => ({
                rounds: [...m.rounds, { step: data.step, calls: data.calls.map((c) => ({ ...c, ok: null })) }],
              }));
            } else if (name === "tool_result") {
              // Mark the first still-pending call of that tool in the latest round
              // (results arrive in call order). Copies, never mutates, earlier state.
              updateMessage(convId, messageId, (m) => {
                const last = m.rounds.length - 1;
                let marked = false;
                const rounds = m.rounds.map((r, i) =>
                  i !== last
                    ? r
                    : {
                        ...r,
                        calls: r.calls.map((c) => {
                          if (marked || c.name !== data.name || c.ok !== null) return c;
                          marked = true;
                          return { ...c, ok: data.ok };
                        }),
                      },
                );
                return { rounds };
              });
            } else if (name === "answer") {
              finished = true;
              updateMessage(convId, messageId, () => ({ status: "done", answer: data.content, seconds: data.seconds }));
              setAnsweredId(messageId);
            } else if (name === "error") {
              finished = true;
              fail(data.code, data.message);
            }
          },
        });
        if (!finished) fail("incomplete", "The answer stopped before it finished. Ask again.");
        setServerState("ok");
      } catch (err) {
        if (err.name === "AbortError") {
          fail("stopped", "You stopped this answer.");
        } else if (err instanceof ApiError) {
          fail(err.code, err.message);
          if (err.code === "network") setServerState("down");
        } else {
          fail("client_error", "Something went wrong in the page. Reload and ask again.");
        }
      } finally {
        abortRef.current = null;
        setRunningId(null);
      }
    },
    [accessCode, activeId, conversations, runningId, updateMessage],
  );

  const retry = (conversationId, messageId, question) => {
    setConversations((list) =>
      list.map((c) =>
        c.id === conversationId ? { ...c, messages: c.messages.filter((m) => m.id !== messageId) } : c,
      ),
    );
    ask(question, conversationId);
  };

  const deleteConversation = (id) => {
    if (runningId && conversations.find((c) => c.id === id)?.messages.some((m) => m.id === runningId)) {
      abortRef.current?.abort();
    }
    setConversations((list) => list.filter((c) => c.id !== id));
    if (id === activeId) setActiveId(null);
  };

  const changeCode = (rejected = false) => {
    clearAccessCode();
    setCodeRejected(rejected);
    setAccessCode("");
  };

  if (!accessCode) {
    return (
      <AccessGate
        rejected={codeRejected}
        onSubmit={(code) => {
          saveAccessCode(code);
          setCodeRejected(false);
          setAccessCode(code);
        }}
      />
    );
  }

  return (
    <div className="app">
      <Sidebar
        conversations={[...conversations].sort((a, b) => b.updatedAt - a.updatedAt)}
        activeId={activeId}
        onSelect={(id) => {
          setActiveId(id);
          setDrawerOpen(false);
        }}
        onNew={() => {
          setActiveId(null);
          setDrawerOpen(false);
        }}
        onDelete={deleteConversation}
        onChangeCode={() => changeCode(false)}
        serverState={serverState}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />

      <main className="main">
        <header className="topbar">
          <button type="button" className="menu-button" onClick={() => setDrawerOpen(true)} aria-label="Open conversations">
            <span />
            <span />
            <span />
          </button>
          <Brand />
        </header>

        <div className="scroll" ref={scrollRef}>
          <div className="column">
            {!active ? (
              <Welcome onAsk={(q) => ask(q, null)} disabled={Boolean(runningId)} />
            ) : (
              active.messages.map((m) => (
                <Exchange
                  key={m.id}
                  message={m}
                  onRetry={() => retry(active.id, m.id, m.question)}
                  onChangeCode={() => changeCode(true)}
                />
              ))
            )}
          </div>
        </div>

        <div className="composer-wrap">
          <Composer
            onSend={(q) => ask(q)}
            onStop={() => abortRef.current?.abort()}
            running={Boolean(runningId)}
          />
        </div>
      </main>
    </div>
  );
}
