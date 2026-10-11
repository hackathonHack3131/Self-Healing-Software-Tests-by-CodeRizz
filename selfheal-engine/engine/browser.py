"""Async Playwright browser session manager with origin guard and monitor attachment."""

import os
from typing import Any
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Response,
    Route,
    async_playwright,
)
from engine.config import Settings, get_settings, is_origin_allowed
from engine.monitor import Monitor


class DisallowedOriginError(ValueError):
    """Raised when an action or navigation targets an origin outside the allowlist."""
    pass


class BrowserSession:
    """Async context manager managing a clean browser instance, context, page, and monitor."""

    def __init__(self, settings: Settings | None = None, start_url: str | None = None):
        self.settings = settings or get_settings()
        self.start_url = start_url or f"{self.settings.DEMO_BASE_URL}/v/a/"

        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self.monitor: Monitor | None = None

    async def __aenter__(self) -> "BrowserSession":
        # Validate initial start_url origin
        if not is_origin_allowed(self.start_url, self.settings):
            raise DisallowedOriginError(
                f"Cannot initialize BrowserSession: start_url '{self.start_url}' "
                f"origin is not in ALLOWED_ORIGINS: {self.settings.ALLOWED_ORIGINS}"
            )

        self.playwright = await async_playwright().start()
        launch_args = []
        if (
            os.getenv("PLAYWRIGHT_NO_SANDBOX", "false").lower() in ("true", "1", "yes")
            or os.path.exists("/.dockerenv")
        ):
            launch_args.extend(["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])

        self.browser = await self.playwright.chromium.launch(
            headless=self.settings.HEADLESS,
            args=launch_args if launch_args else None,
        )
        self.context = await self.browser.new_context()

        # Route guard: abort requests to any origin not in ALLOWED_ORIGINS
        async def handle_route(route: Route) -> None:
            req_url = route.request.url
            if req_url.startswith("about:") or req_url.startswith("data:"):
                await route.continue_()
                return

            if is_origin_allowed(req_url, self.settings):
                await route.continue_()
            else:
                await route.abort("blockedbyclient")

        await self.context.route("**/*", handle_route)

        self.page = await self.context.new_page()
        self.monitor = Monitor(self.page)

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if self.page:
                try:
                    await self.page.close()
                except Exception:
                    pass
            if self.context:
                try:
                    await self.context.close()
                except Exception:
                    pass
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

    async def goto(self, url: str, **kwargs: Any) -> Response | None:
        """Navigate to URL with origin check."""
        if not (url.startswith("about:") or url.startswith("data:")):
            if not is_origin_allowed(url, self.settings):
                raise DisallowedOriginError(
                    f"Navigation blocked: URL '{url}' is not in ALLOWED_ORIGINS"
                )

        if not self.page:
            raise RuntimeError("BrowserSession page is not open")
        try:
            return await self.page.goto(url, **kwargs)
        except Exception as exc:
            if "ERR_NO_BUFFER_SPACE" in str(exc) or "ECONNREFUSED" in str(exc):
                await asyncio.sleep(0.2)
                return await self.page.goto(url, **kwargs)
            raise


    async def goto_start(self, **kwargs: Any) -> Response | None:
        """Navigate to the configured start URL."""
        return await self.goto(self.start_url, **kwargs)
