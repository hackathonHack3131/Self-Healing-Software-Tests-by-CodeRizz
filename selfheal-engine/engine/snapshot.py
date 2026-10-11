"""UI Snapshot and inventory capture for deterministic E2E testing.

Captures structural UI metadata (accessible roles, names, labels, IDs, headings,
paths) without ever recording input values, secrets, cards, cookies, or tokens.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import Page
from engine.browser import BrowserSession
from engine.executor import run_recipe
from engine.models import (
    Intent,
    PageSnapshot,
    Recipe,
    UIElement,
    UIInventory,
)
from engine.recipes import get_project_root
from engine.verifier import verify_outcome

BASELINE_FILE_NAME = "version_a_inventory.json"


class BaselineVerificationError(RuntimeError):
    """Raised when Version A fails deterministic verification during baseline creation."""
    pass


def get_baseline_path(base_dir: Path | str | None = None) -> Path:
    """Return the absolute path to the trusted Version A baseline inventory file."""
    if base_dir is not None:
        return Path(base_dir) / BASELINE_FILE_NAME
    return get_project_root() / "baselines" / BASELINE_FILE_NAME


def save_baseline_inventory(
    inventory: UIInventory, path: Path | str | None = None
) -> Path:
    """Atomically save the trusted Version A baseline inventory.

    Refuses to save or replace the baseline if inventory is not from Version A (Requirement 5).
    """
    if inventory.app_version.lower() != "a":
        raise ValueError(
            f"Refusing to save baseline: inventory app_version is '{inventory.app_version}'. "
            "Only Version A is trusted and allowed as the baseline."
        )

    target_path = Path(path) if path else get_baseline_path()

    # Guard: Never allow non-Version A into the official baseline file
    if target_path.name == BASELINE_FILE_NAME and inventory.app_version.lower() != "a":
        raise ValueError("Cannot replace trusted baseline with non-Version-A inventory.")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.parent / f".tmp_{target_path.name}"

    try:
        content = inventory.model_dump_json(indent=2)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, target_path)
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise

    return target_path


def load_baseline_inventory(path: Path | str | None = None) -> UIInventory:
    """Load and validate the trusted Version A baseline inventory."""
    target_path = Path(path) if path else get_baseline_path()
    if not target_path.exists() or target_path.stat().st_size == 0:
        raise FileNotFoundError(
            f"Baseline inventory not found or empty at {target_path}. "
            "Run Version A verification first to generate the trusted baseline."
        )

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return UIInventory.model_validate(data)


_DOM_EXTRACTOR_JS = """
() => {
    // Collect all headings on the page
    const headings = [];
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]').forEach(el => {
        const text = (el.innerText || el.textContent || '').trim();
        if (text && !headings.includes(text)) {
            headings.push(text);
        }
    });

    // Helper to find associated label for an input
    function findLabel(el) {
        if (el.getAttribute('aria-label')) {
            return el.getAttribute('aria-label').trim();
        }
        if (el.getAttribute('aria-labelledby')) {
            const ref = document.getElementById(el.getAttribute('aria-labelledby'));
            if (ref) {
                const txt = (ref.innerText || ref.textContent || '').trim();
                if (txt) return txt;
            }
        }
        if (el.id) {
            try {
                const labelEl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                if (labelEl) {
                    const txt = (labelEl.innerText || labelEl.textContent || '').trim();
                    if (txt) return txt;
                }
            } catch (e) {}
        }
        const parentLabel = el.closest('label');
        if (parentLabel) {
            const clone = parentLabel.cloneNode(true);
            clone.querySelectorAll('input, select, textarea').forEach(i => i.remove());
            const txt = (clone.innerText || clone.textContent || '').trim();
            if (txt) return txt;
        }
        return null;
    }

    // Helper to compute accessible name without reading any sensitive values
    function computeAccessibleName(el, role, label) {
        if (label) return label;
        if (el.getAttribute('aria-label')) return el.getAttribute('aria-label').trim();
        if (role === 'button' || el.tagName.toLowerCase() === 'button' || el.tagName.toLowerCase() === 'a') {
            const text = (el.innerText || el.textContent || '').trim();
            if (text) return text;
        }
        if (el.getAttribute('placeholder')) {
            return el.getAttribute('placeholder').trim();
        }
        if (el.getAttribute('title')) {
            return el.getAttribute('title').trim();
        }
        return '';
    }

    // Helper to find nearest preceding section heading
    function findNearestHeading(el) {
        let current = el;
        while (current && current !== document.body) {
            let prev = current.previousElementSibling;
            while (prev) {
                if (/^H[1-6]$/.test(prev.tagName) || prev.getAttribute('role') === 'heading') {
                    return (prev.innerText || prev.textContent || '').trim();
                }
                const nestedHeading = prev.querySelector('h1, h2, h3, h4, h5, h6, [role="heading"]');
                if (nestedHeading) {
                    return (nestedHeading.innerText || nestedHeading.textContent || '').trim();
                }
                prev = prev.previousElementSibling;
            }
            current = current.parentElement;
        }
        return headings.length > 0 ? headings[0] : null;
    }

    // Check visibility
    function isVisible(el) {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
            return false;
        }
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    }

    const selector = 'input, select, textarea, button, a[href], [role="button"], [role="link"], [role="textbox"], [role="checkbox"], [role="radio"], [role="combobox"]';
    const rawElements = Array.from(document.querySelectorAll(selector));

    const elements = [];
    for (const el of rawElements) {
        const tagName = el.tagName.toLowerCase();
        const inputType = el.getAttribute('type') ? el.getAttribute('type').toLowerCase() : (tagName === 'input' ? 'text' : null);

        // Omit hidden inputs entirely
        if (inputType === 'hidden') continue;

        let role = el.getAttribute('role');
        if (!role) {
            if (tagName === 'button' || inputType === 'submit' || inputType === 'button' || inputType === 'reset') {
                role = 'button';
            } else if (tagName === 'input' && inputType === 'checkbox') {
                role = 'checkbox';
            } else if (tagName === 'input' && inputType === 'radio') {
                role = 'radio';
            } else if (tagName === 'select') {
                role = 'combobox';
            } else if (tagName === 'a') {
                role = 'link';
            } else if (tagName === 'textarea' || (tagName === 'input' && ['text', 'email', 'password', 'tel', 'search', 'url', 'number'].includes(inputType))) {
                role = 'textbox';
            } else {
                role = tagName;
            }
        }

        const label = findLabel(el);
        const name = computeAccessibleName(el, role, label);
        const elementId = el.id ? el.id.trim() : null;
        const placeholder = el.getAttribute('placeholder') ? el.getAttribute('placeholder').trim() : null;
        const inputName = el.getAttribute('name') ? el.getAttribute('name').trim() : null;
        const heading = findNearestHeading(el);
        const enabled = !el.disabled && !el.hasAttribute('disabled');
        const visible = isVisible(el);

        // PRIVACY ENFORCEMENT:
        // NEVER read el.value, NEVER read passwords, NEVER touch cookies or storage!
        elements.push({
            role: role,
            name: name,
            label: label,
            element_id: elementId,
            tag_name: tagName,
            element_type: inputType,
            placeholder: placeholder,
            input_name: inputName,
            heading: heading,
            page_path: window.location.pathname || '/',
            enabled: enabled,
            visible: visible
        });
    }

    return {
        headings: headings,
        elements: elements
    };
}
"""


async def capture_page_snapshot(page: Page) -> PageSnapshot:
    """Capture structural UI information of the current page.

    Enforces strict privacy: Never captures input values, passwords, card details,
    cookies, tokens, or browser storage.
    """
    raw_url = page.url
    page_path = urlsplit(raw_url).path or "/"

    try:
        title = (await page.title()).strip()
    except Exception:
        title = ""

    # Safe deterministic in-browser DOM extraction
    extracted = await page.evaluate(_DOM_EXTRACTOR_JS)

    headings = extracted.get("headings", [])
    raw_elements = extracted.get("elements", [])

    elements: list[UIElement] = []
    for item in raw_elements:
        elem = UIElement(
            role=item.get("role", "generic"),
            name=item.get("name", ""),
            label=item.get("label"),
            element_id=item.get("element_id"),
            tag_name=item.get("tag_name", "div"),
            element_type=item.get("element_type"),
            placeholder=item.get("placeholder"),
            input_name=item.get("input_name"),
            heading=item.get("heading"),
            page_path=page_path,
            enabled=item.get("enabled", True),
            visible=item.get("visible", True),
        )
        elements.append(elem)

    return PageSnapshot(
        page_path=page_path,
        title=title,
        headings=headings,
        elements=elements,
    )


async def create_version_a_baseline(
    session: BrowserSession,
    recipe: Recipe,
    intent: Intent,
    output_path: Path | str | None = None,
) -> UIInventory:
    """Create the trusted Version A baseline only after Version A passes the verifier.

    Requirements 4 and 5:
    - Creates the baseline ONLY after the real Version A test passes the deterministic verifier.
    - Never replaces the trusted baseline with Versions B, C, or D.
    """
    # Guard: Confirm session is targeting Version A
    if "/v/a/" not in session.start_url:
        raise ValueError(
            f"Refusing to create baseline: session start_url '{session.start_url}' "
            "is not Version A (/v/a/). Trusted baseline can ONLY be created for Version A."
        )

    # 1. Navigate to Version A start and capture initial checkout page snapshot
    await session.goto_start()
    checkout_snapshot = await capture_page_snapshot(session.page)

    # 2. Run recipe deterministically
    run_res = await run_recipe(recipe, intent, session)
    if run_res.failed_step_index is not None:
        raise BaselineVerificationError(
            f"Cannot create baseline: Recipe failed at step {run_res.failed_step_index}: "
            f"{run_res.steps[run_res.failed_step_index].error_message}"
        )

    # 3. Deterministic verification of the outcome
    ver_res = await verify_outcome(session.page, intent, session.monitor)
    if not ver_res.passed:
        failed_checks = [c.name for c in ver_res.checks if not c.passed]
        raise BaselineVerificationError(
            f"Cannot create baseline: Version A failed verification checks: {failed_checks}"
        )

    # 4. Capture confirmation page snapshot
    confirmation_snapshot = await capture_page_snapshot(session.page)

    # 5. Build inventory
    now_iso = datetime.now(timezone.utc).isoformat()
    inventory = UIInventory(
        intent_id=intent.id,
        app_version="a",
        pages=[checkout_snapshot, confirmation_snapshot],
        created_at=now_iso,
    )

    # 6. Save baseline atomically
    save_baseline_inventory(inventory, output_path)

    return inventory
