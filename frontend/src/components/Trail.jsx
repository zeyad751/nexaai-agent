import { useState } from "react";
import { describeTool, SOURCE_KINDS } from "../tools.js";

// The evidence trail: every source the agent consulted, round by round.
// While the agent works it is open and grows live; once the answer arrives it folds
// into a one-line summary that can be reopened.

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

function StatusMark({ ok }) {
  if (ok === null || ok === undefined) return <span className="trail-status pending" aria-label="Running" />;
  return ok ? (
    <span className="trail-status ok" aria-label="Returned results">✓</span>
  ) : (
    <span className="trail-status failed" aria-label="Returned an error">✕</span>
  );
}

export default function Trail({ rounds, running, seconds }) {
  const [open, setOpen] = useState(false);
  const calls = rounds.flatMap((r) => r.calls);
  if (!running && calls.length === 0) return null;

  const kinds = [...new Set(calls.map((c) => describeTool(c.name).kind))];
  const summary = running
    ? calls.length === 0
      ? "Reading the question"
      : `Checking sources, round ${rounds.length}`
    : `Checked ${plural(calls.length, "source")} in ${plural(rounds.length, "round")}${seconds ? `, ${seconds} s` : ""}`;
  const expanded = running || open;

  return (
    <section className={`trail ${running ? "is-running" : ""}`} aria-live={running ? "polite" : "off"}>
      <button
        type="button"
        className="trail-summary"
        onClick={() => setOpen((v) => !v)}
        disabled={running}
        aria-expanded={expanded}
      >
        <span className="trail-kinds" aria-hidden="true">
          {(kinds.length ? kinds : ["database"]).map((k) => (
            <span key={k} className={`kind-dot kind-${k}`} />
          ))}
        </span>
        <span>{summary}</span>
        {!running && <span className="trail-toggle">{open ? "Hide" : "Show"}</span>}
      </button>

      {expanded && calls.length > 0 && (
        <ol className="trail-rounds">
          {rounds.map((round) => (
            <li key={round.step} className="trail-round">
              <span className="trail-round-no">{round.step}</span>
              <ul className="trail-calls">
                {round.calls.map((call, i) => {
                  const { label, kind } = describeTool(call.name);
                  return (
                    <li key={i} className="trail-call">
                      <span className={`kind-dot kind-${kind}`} title={SOURCE_KINDS[kind]} />
                      <span className="trail-label">{label}</span>
                      {call.detail && (
                        <span className={`trail-detail ${kind === "sql" ? "is-code" : ""}`} title={call.detail}>
                          {call.detail}
                        </span>
                      )}
                      <StatusMark ok={call.ok} />
                    </li>
                  );
                })}
              </ul>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
