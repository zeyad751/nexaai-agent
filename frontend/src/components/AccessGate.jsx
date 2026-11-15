import { useState } from "react";
import Brand from "./Brand.jsx";

// Asks for the shared access code. The code is checked by the backend on the first
// question; it is stored only in this browser and never built into the app.

export default function AccessGate({ onSubmit, rejected }) {
  const [code, setCode] = useState("");

  const submit = (event) => {
    event.preventDefault();
    if (code.trim()) onSubmit(code.trim());
  };

  return (
    <main className="gate">
      <form className="gate-panel" onSubmit={submit}>
        <Brand />
        <h1>Enter your access code</h1>
        <p>This demo is shared by invitation. Use the code you were given.</p>
        {rejected && (
          <p className="gate-error" role="alert">
            That code was not accepted. Check it and enter it again.
          </p>
        )}
        <label htmlFor="access-code">Access code</label>
        <input
          id="access-code"
          type="password"
          autoComplete="off"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          autoFocus
        />
        <button type="submit" className="button-primary" disabled={!code.trim()}>
          Continue
        </button>
        <p className="gate-note">The code is saved in this browser only.</p>
      </form>
    </main>
  );
}
