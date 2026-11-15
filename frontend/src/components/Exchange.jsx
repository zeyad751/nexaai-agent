import Markdown from "./Markdown.jsx";
import Trail from "./Trail.jsx";

// One question and its answer, laid out like a section of a report: the question is
// the heading, the evidence trail sits under it, then the answer.

export default function Exchange({ message, onRetry, onChangeCode }) {
  const { question, rounds = [], answer, status, error, seconds } = message;
  const running = status === "running";

  return (
    <article className="exchange" id={`exchange-${message.id}`}>
      <h2 className="question">{question}</h2>
      <Trail rounds={rounds} running={running} seconds={seconds} />

      {running && rounds.length === 0 && <p className="working">Working out which sources to check…</p>}

      {status === "done" && <Markdown>{answer}</Markdown>}

      {status === "error" && (
        <div className="answer-error" role="alert">
          <p>{error?.message || "Something went wrong."}</p>
          <div className="answer-error-actions">
            {error?.code === "invalid_access_code" && (
              <button type="button" className="button-secondary" onClick={onChangeCode}>
                Enter the code again
              </button>
            )}
            <button type="button" className="button-secondary" onClick={onRetry}>
              Ask again
            </button>
          </div>
        </div>
      )}
    </article>
  );
}
