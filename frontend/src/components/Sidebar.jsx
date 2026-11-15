import Brand from "./Brand.jsx";

const SERVER_TEXT = {
  checking: "Checking the server",
  waking: "Starting the server, up to a minute",
  ok: "Server ready",
  degraded: "Server data check failed",
  down: "Server unreachable",
};

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onChangeCode,
  serverState,
  open,
  onClose,
}) {
  return (
    <>
      <aside className={`sidebar ${open ? "is-open" : ""}`} aria-label="Conversations">
        <div className="sidebar-top">
          <Brand />
          <button type="button" className="sidebar-close" onClick={onClose} aria-label="Close menu">
            ✕
          </button>
        </div>

        <button type="button" className="button-primary new-question" onClick={onNew}>
          New question
        </button>

        <nav className="history">
          {conversations.length === 0 ? (
            <p className="history-empty">Your questions will be listed here.</p>
          ) : (
            <ul>
              {conversations.map((c) => (
                <li key={c.id} className={c.id === activeId ? "is-active" : ""}>
                  <button
                    type="button"
                    className="history-item"
                    onClick={() => onSelect(c.id)}
                    aria-current={c.id === activeId ? "page" : undefined}
                  >
                    {c.title}
                  </button>
                  <button
                    type="button"
                    className="history-delete"
                    onClick={() => onDelete(c.id)}
                    aria-label={`Delete conversation: ${c.title}`}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </nav>

        <footer className="sidebar-footer">
          <p className={`server-state state-${serverState}`}>
            <span className="server-dot" aria-hidden="true" />
            {SERVER_TEXT[serverState]}
          </p>
          <button type="button" className="link-button" onClick={onChangeCode}>
            Change access code
          </button>
        </footer>
      </aside>
      {open && <div className="scrim" onClick={onClose} aria-hidden="true" />}
    </>
  );
}
