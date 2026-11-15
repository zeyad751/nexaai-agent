// Browser-side persistence. Conversations and the access code live only in this
// browser's localStorage. Every access is wrapped: storage can be full, disabled or
// unavailable (private windows), and the app must still work without it.

const CONVERSATIONS_KEY = "nexaai.conversations.v1";
const ACCESS_CODE_KEY = "nexaai.accessCode";
const MAX_CONVERSATIONS = 50;

function read(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function write(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

export function loadConversations() {
  const list = read(CONVERSATIONS_KEY, []);
  if (!Array.isArray(list)) return [];
  // A run that was in progress when the page closed can never finish: mark it stopped.
  return list.map((c) => ({
    ...c,
    messages: (c.messages || []).map((m) =>
      m.status === "running"
        ? { ...m, status: "error", error: { code: "interrupted", message: "This answer was interrupted when the page closed." } }
        : m,
    ),
  }));
}

export function saveConversations(list) {
  const sorted = [...list].sort((a, b) => b.updatedAt - a.updatedAt).slice(0, MAX_CONVERSATIONS);
  write(CONVERSATIONS_KEY, sorted);
}

export function loadAccessCode() {
  return read(ACCESS_CODE_KEY, "");
}

export function saveAccessCode(code) {
  write(ACCESS_CODE_KEY, code);
}

export function clearAccessCode() {
  try {
    window.localStorage.removeItem(ACCESS_CODE_KEY);
  } catch {
    /* storage unavailable: nothing to clear */
  }
}
