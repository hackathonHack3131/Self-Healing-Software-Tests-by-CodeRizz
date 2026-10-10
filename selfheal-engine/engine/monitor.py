"""Page monitor for capturing HTTP errors, console errors, page crashes, and visible alerts."""

from typing import Any
from urllib.parse import urlsplit
from playwright.async_api import ConsoleMessage, Error as PlaywrightError, Page, Request, Response


class Monitor:
    """Monitors a Playwright Page for errors, failed requests, and alerts without capturing secrets."""

    def __init__(self, page: Page):
        self.page = page
        self.http_errors: list[dict[str, Any]] = []
        self.console_errors: list[dict[str, Any]] = []
        self.page_errors: list[dict[str, Any]] = []
        self.failed_requests: list[dict[str, Any]] = []

        self._attach_listeners()

    def _attach_listeners(self) -> None:
        self.page.on("response", self._handle_response)
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_pageerror)
        self.page.on("requestfailed", self._handle_requestfailed)

    def _handle_response(self, response: Response) -> None:
        if response.status >= 400:
            parsed = urlsplit(response.url)
            self.http_errors.append(
                {
                    "method": response.request.method,
                    "url_path": parsed.path or "/",
                    "status": response.status,
                }
            )

    def _handle_console(self, message: ConsoleMessage) -> None:
        if message.type == "error":
            self.console_errors.append(
                {
                    "text": message.text,
                    "location": str(message.location) if message.location else "",
                }
            )

    def _handle_pageerror(self, error: PlaywrightError) -> None:
        self.page_errors.append(
            {
                "message": str(error),
            }
        )

    def _handle_requestfailed(self, request: Request) -> None:
        parsed = urlsplit(request.url)
        self.failed_requests.append(
            {
                "method": request.method,
                "url_path": parsed.path or "/",
                "failure": request.failure or "Failed",
            }
        )

    def mark(self) -> tuple[int, int, int, int]:
        """Return a cursor representing current lengths of evidence collections."""
        return (
            len(self.http_errors),
            len(self.console_errors),
            len(self.page_errors),
            len(self.failed_requests),
        )

    def since(self, mark: tuple[int, int, int, int]) -> dict[str, list[dict[str, Any]]]:
        """Return evidence collected strictly after the given mark."""
        h_idx, c_idx, p_idx, f_idx = mark
        return {
            "http_errors": list(self.http_errors[h_idx:]),
            "console_errors": list(self.console_errors[c_idx:]),
            "page_errors": list(self.page_errors[p_idx:]),
            "failed_requests": list(self.failed_requests[f_idx:]),
        }

    async def visible_alerts(self, page: Page | None = None) -> list[str]:
        """Collect text from currently visible alert or error elements."""
        target_page = page or self.page
        alerts: list[str] = []

        try:
            selector = '[role="alert"], .alert, .error, .alert-error'
            elements = await target_page.locator(selector).all()
            for el in elements:
                if await el.is_visible():
                    text = (await el.inner_text()).strip()
                    if text and text not in alerts:
                        alerts.append(text)
        except Exception:
            pass

        return alerts

    def get_evidence(self) -> dict[str, list[dict[str, Any]]]:
        """Return all recorded evidence collections."""
        return {
            "http_errors": list(self.http_errors),
            "console_errors": list(self.console_errors),
            "page_errors": list(self.page_errors),
            "failed_requests": list(self.failed_requests),
        }
