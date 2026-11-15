"""Backend settings, read from environment variables (or a local .env file).

Nothing secret is written in code. Locally the values come from .env; on Render they
are set in the service's Environment settings.
"""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value and value.strip() else default


def _list(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    # Secrets
    access_code: str = field(default_factory=lambda: os.getenv("NEXAAI_ACCESS_CODE", ""))
    openai_key_present: bool = field(default_factory=lambda: bool(os.getenv("OPENAI_API_KEY")))

    # Which frontend addresses may call the API (CORS)
    allowed_origins: list[str] = field(
        default_factory=lambda: _list("ALLOWED_ORIGINS", "http://localhost:5173")
    )

    # Input limits
    max_message_chars: int = field(default_factory=lambda: _int("MAX_MESSAGE_CHARS", 4000))
    max_history_messages: int = field(default_factory=lambda: _int("MAX_HISTORY_MESSAGES", 12))
    max_history_message_chars: int = field(
        default_factory=lambda: _int("MAX_HISTORY_MESSAGE_CHARS", 8000)
    )

    # Agent execution limits
    recursion_limit: int = field(default_factory=lambda: _int("AGENT_RECURSION_LIMIT", 40))
    run_timeout_seconds: int = field(default_factory=lambda: _int("AGENT_TIMEOUT_SECONDS", 240))
    max_concurrent_runs: int = field(default_factory=lambda: _int("MAX_CONCURRENT_RUNS", 3))

    # Abuse and cost limits. These counters are kept in memory and reset when the server
    # restarts or (on Render's free tier) wakes from sleep, so daily_chat_limit slows
    # abuse but is not a guaranteed daily ceiling. Set the real spending cap in OpenAI.
    chats_per_window: int = field(default_factory=lambda: _int("RATE_LIMIT_CHATS", 10))
    rate_window_seconds: int = field(default_factory=lambda: _int("RATE_LIMIT_WINDOW_SECONDS", 600))
    failed_codes_per_window: int = field(default_factory=lambda: _int("RATE_LIMIT_FAILED_CODES", 5))
    daily_chat_limit: int = field(default_factory=lambda: _int("DAILY_CHAT_LIMIT", 200))


settings = Settings()
