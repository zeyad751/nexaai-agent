// Everything that talks to the FastAPI backend lives here.
// The backend address is public build configuration; the access code is never in the
// code: the user types it, and it is sent per request in the X-Access-Code header.

export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

// Messages for errors that happen before the agent starts (HTTP status errors).
const NETWORK_MESSAGE =
  "The server could not be reached. It may be starting up; wait a moment and try again.";

export async function checkHealth(timeoutMs = 60000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_URL}/health`, { signal: controller.signal });
    const body = await res.json().catch(() => ({}));
    return { ok: res.ok && body.status === "ok", body };
  } catch {
    return { ok: false, body: null };
  } finally {
    clearTimeout(timer);
  }
}

// Sends one question and calls onEvent(name, data) for each server-sent event:
// start, tool_calls, tool_result, answer, done, error.
// Resolves when the stream ends; throws ApiError for request-level failures.
export async function streamChat({ message, history, accessCode, signal, onEvent }) {
  let res;
  try {
    res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Access-Code": accessCode },
      body: JSON.stringify({ message, history }),
      signal,
    });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new ApiError("network", NETWORK_MESSAGE);
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    throw new ApiError(
      detail?.code || `http_${res.status}`,
      detail?.message || `The server answered with an error (${res.status}).`,
    );
  }

  // Parse the event stream: blocks separated by a blank line, each with
  // "event: <name>" and "data: <json>" lines. Lines starting with ":" are keep-alives.
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let split;
    while ((split = buffer.indexOf("\n\n")) !== -1) {
      const block = buffer.slice(0, split);
      buffer = buffer.slice(split + 2);
      let name = null;
      let data = "";
      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) name = line.slice(7);
        else if (line.startsWith("data: ")) data += line.slice(6);
      }
      if (name) onEvent(name, data ? JSON.parse(data) : {});
    }
  }
}
