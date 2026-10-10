"""Application settings and configuration helpers."""

from dataclasses import dataclass
import os
from urllib.parse import urlsplit
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()


def get_origin(url: str) -> str:
    """Extract scheme and netloc from a URL (e.g. http://127.0.0.1:5000)."""
    parsed = urlsplit(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    return url.rstrip("/")


@dataclass(frozen=True)
class Settings:
    """Frozen application configuration settings."""

    DEEPAGENT_MODEL: str = "google_genai:gemini-2.5-flash"
    GOOGLE_API_KEY: str = ""
    DEMO_BASE_URL: str = "http://127.0.0.1:5000"
    ALLOWED_ORIGINS: tuple[str, ...] = ("http://127.0.0.1:5000",)
    MAX_AGENT_ACTIONS: int = 10
    MAX_HEAL_SECONDS: int = 120
    HEADLESS: bool = True
    RUNS_DIR: str = "runs"

    def __repr__(self) -> str:
        masked_key = "***" if self.GOOGLE_API_KEY else ""
        return (
            f"Settings("
            f"DEEPAGENT_MODEL={self.DEEPAGENT_MODEL!r}, "
            f"GOOGLE_API_KEY={masked_key!r}, "
            f"DEMO_BASE_URL={self.DEMO_BASE_URL!r}, "
            f"ALLOWED_ORIGINS={self.ALLOWED_ORIGINS!r}, "
            f"MAX_AGENT_ACTIONS={self.MAX_AGENT_ACTIONS!r}, "
            f"MAX_HEAL_SECONDS={self.MAX_HEAL_SECONDS!r}, "
            f"HEADLESS={self.HEADLESS!r}, "
            f"RUNS_DIR={self.RUNS_DIR!r}"
            f")"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from current environment variables."""
        return get_settings()


def get_settings() -> Settings:
    """Instantiate frozen Settings from environment variables or defaults."""
    model = os.getenv("DEEPAGENT_MODEL", "google_genai:gemini-2.5-flash")
    api_key = os.getenv("GOOGLE_API_KEY", "")
    demo_base_url = os.getenv("DEMO_BASE_URL", "http://127.0.0.1:5000")

    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env:
        allowed_origins = tuple(
            get_origin(orig.strip())
            for orig in allowed_origins_env.split(",")
            if orig.strip()
        )
    else:
        demo_origin = get_origin(demo_base_url)
        allowed_origins = (demo_origin,)

    max_actions = int(os.getenv("MAX_AGENT_ACTIONS", "10"))
    max_heal_seconds = int(os.getenv("MAX_HEAL_SECONDS", "120"))
    headless = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
    runs_dir = os.getenv("RUNS_DIR", "runs")

    return Settings(
        DEEPAGENT_MODEL=model,
        GOOGLE_API_KEY=api_key,
        DEMO_BASE_URL=demo_base_url,
        ALLOWED_ORIGINS=allowed_origins,
        MAX_AGENT_ACTIONS=max_actions,
        MAX_HEAL_SECONDS=max_heal_seconds,
        HEADLESS=headless,
        RUNS_DIR=runs_dir,
    )


# Alias
load_settings = get_settings


def is_origin_allowed(url_or_origin: str, settings: Settings | None = None) -> bool:
    """Check if the origin of the given URL matches the allowlist."""
    if settings is None:
        settings = get_settings()
    origin = get_origin(url_or_origin)
    allowed = {get_origin(o) for o in settings.ALLOWED_ORIGINS}
    return origin in allowed


def llm_config_status(settings: Settings | None = None) -> str:
    """Return OK or a BLOCKED_CONFIG reason string."""
    if settings is None:
        settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        return "BLOCKED_CONFIG: Missing GOOGLE_API_KEY in environment or .env"
    if not settings.DEEPAGENT_MODEL or "REPLACE_WITH" in settings.DEEPAGENT_MODEL:
        return "BLOCKED_CONFIG: DEEPAGENT_MODEL is not set or contains placeholder"
    return "OK"
