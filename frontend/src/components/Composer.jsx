import { useEffect, useRef, useState } from "react";

export const MAX_CHARS = 4000; // matches the backend's MAX_MESSAGE_CHARS

export default function Composer({ onSend, onStop, running, disabled }) {
  const [text, setText] = useState("");
  const ref = useRef(null);

  // Grow with the text, up to a limit.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }, [text]);

  const tooLong = text.length > MAX_CHARS;
  const canSend = text.trim().length > 0 && !tooLong && !running && !disabled;

  const send = () => {
    if (!canSend) return;
    onSend(text.trim());
    setText("");
  };

  const onKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      send();
    }
  };

  return (
    <div className="composer">
      <div className="composer-box">
        <label htmlFor="question" className="visually-hidden">
          Your question
        </label>
        <textarea
          id="question"
          ref={ref}
          rows={1}
          value={text}
          placeholder="Ask about a project, client, employee, risk or strategy"
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
        />
        {running ? (
          <button type="button" className="button-secondary" onClick={onStop}>
            Stop
          </button>
        ) : (
          <button type="button" className="button-primary" onClick={send} disabled={!canSend}>
            Ask
          </button>
        )}
      </div>
      <p className={`composer-hint ${tooLong ? "is-error" : ""}`}>
        {tooLong
          ? `Shorten the question to ${MAX_CHARS} characters (now ${text.length}).`
          : "Enter to ask, Shift+Enter for a new line."}
      </p>
    </div>
  );
}
