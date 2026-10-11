"""Pytest fixtures for demo app background server and browser sessions."""

import socket
import threading
import pytest
import werkzeug.serving
from demo_app.app import create_app
from engine.browser import BrowserSession
from engine.config import Settings


def get_free_port() -> int:
    """Find an available ephemeral port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def demo_server_url():
    """Start the Flask demo shop on a free local port in a background daemon thread."""
    port = get_free_port()
    app = create_app()
    server = werkzeug.serving.make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.shutdown()


@pytest.fixture
def make_settings(demo_server_url):
    """Factory fixture returning test Settings pointed at the running demo server."""
    def _make(start_path: str = "/v/a/", headless: bool = True) -> tuple[Settings, str]:
        settings = Settings(
            DEMO_BASE_URL=demo_server_url,
            ALLOWED_ORIGINS=(demo_server_url,),
            HEADLESS=headless,
        )
        start_url = f"{demo_server_url}{start_path}"
        return settings, start_url
    return _make


@pytest.fixture
async def browser_session(make_settings):
    """Async BrowserSession fixture pointed at Version A start URL."""
    settings, start_url = make_settings("/v/a/")
    async with BrowserSession(settings=settings, start_url=start_url) as session:
        yield session


@pytest.fixture
async def session_b(make_settings):
    """Async BrowserSession fixture pointed at Version B start URL."""
    settings, start_url = make_settings("/v/b/")
    async with BrowserSession(settings=settings, start_url=start_url) as session:
        yield session

