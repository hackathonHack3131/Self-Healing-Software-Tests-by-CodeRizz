"""Failure context builder for self-healing tests.

Packages a safe, compact context containing intent goal, allowed field keys (no values),
prior steps, failure location, current inventory, diff summary, and triage verdict.
Ensures context fits well under the ~6k token budget.
"""

from typing import Any
from engine.models import (
    FailureContext,
    FailureType,
    Intent,
    PageSnapshot,
    Recipe,
    RunResult,
    SnapshotDiff,
    Step,
    Triage,
    UIElement,
    UIInventory,
)


def summarize_diff(diff: SnapshotDiff | None) -> str:
    """Produce a concise, readable textual summary of UI structural and flow diffs."""
    if diff is None:
        return "No diff available."

    lines: list[str] = []

    if diff.renamed:
        renames_text = [
            f"'{r.old_name}' -> '{r.new_name}' (conf: {r.confidence:.2f})"
            for r in diff.renamed[:10]
        ]
        suffix = f" ... and {len(diff.renamed) - 10} more" if len(diff.renamed) > 10 else ""
        lines.append(f"Renamed controls ({len(diff.renamed)}): " + ", ".join(renames_text) + suffix)

    if diff.added:
        added_text = [f"'{a.name or a.element_id}' ({a.role})" for a in diff.added[:10]]
        suffix = f" ... and {len(diff.added) - 10} more" if len(diff.added) > 10 else ""
        lines.append(f"Added controls ({len(diff.added)}): " + ", ".join(added_text) + suffix)

    if diff.removed:
        removed_text = [f"'{r.name or r.element_id}' ({r.role})" for r in diff.removed[:10]]
        suffix = f" ... and {len(diff.removed) - 10} more" if len(diff.removed) > 10 else ""
        lines.append(f"Removed controls ({len(diff.removed)}): " + ", ".join(removed_text) + suffix)

    if diff.ambiguous:
        amb_text = [f"'{amb.element.name}' ({amb.reason})" for amb in diff.ambiguous[:5]]
        suffix = f" ... and {len(diff.ambiguous) - 5} more" if len(diff.ambiguous) > 5 else ""
        lines.append(f"Ambiguous controls ({len(diff.ambiguous)}): " + "; ".join(amb_text) + suffix)

    if diff.flow and diff.flow.is_flow_changed:
        flow_parts = []
        if diff.flow.added_paths:
            flow_parts.append(f"new paths: {diff.flow.added_paths}")
        if diff.flow.removed_paths:
            flow_parts.append(f"removed paths: {diff.flow.removed_paths}")
        lines.append(f"Navigation flow shift: {'; '.join(flow_parts)}")

    if not lines:
        return "UI structurally identical: No changes detected."

    return "\n".join(lines)


def _trim_string(text: str, max_chars: int = 250) -> str:
    """Trim a string safely if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def trim_evidence(evidence: dict[str, Any], max_items: int = 5) -> dict[str, Any]:
    """Trim long lists and strings in the evidence dictionary to preserve token budget."""
    trimmed: dict[str, Any] = {}
    for key, val in evidence.items():
        if isinstance(val, list):
            items = []
            for item in val[:max_items]:
                if isinstance(item, dict):
                    items.append({
                        k: _trim_string(str(v)) if isinstance(v, str) else v
                        for k, v in item.items()
                    })
                elif isinstance(item, str):
                    items.append(_trim_string(item))
                else:
                    items.append(item)
            trimmed[key] = items
        elif isinstance(val, str):
            trimmed[key] = _trim_string(val)
        elif isinstance(val, dict):
            trimmed[key] = {
                k: _trim_string(str(v)) if isinstance(v, str) else v
                for k, v in val.items()
            }
        else:
            trimmed[key] = val
    return trimmed


def _trim_inventory(
    inv: UIInventory | PageSnapshot | None, max_elements_per_page: int = 35
) -> UIInventory | PageSnapshot | None:
    """Trim excessive elements in snapshot or inventory to respect token budget."""
    if inv is None:
        return None

    if isinstance(inv, PageSnapshot):
        trimmed_elements = inv.elements[:max_elements_per_page]
        return PageSnapshot(
            page_path=inv.page_path,
            title=inv.title,
            headings=inv.headings[:10],
            elements=trimmed_elements,
        )

    if isinstance(inv, UIInventory):
        trimmed_pages = []
        for p in inv.pages[:5]:
            trimmed_pages.append(
                PageSnapshot(
                    page_path=p.page_path,
                    title=p.title,
                    headings=p.headings[:10],
                    elements=p.elements[:max_elements_per_page],
                )
            )
        return UIInventory(
            intent_id=inv.intent_id,
            app_version=inv.app_version,
            pages=trimmed_pages,
            created_at=inv.created_at,
        )

    return inv


def build_failure_context(
    intent: Intent,
    recipe: Recipe,
    run_result: RunResult,
    triage: Triage,
    current_inventory: UIInventory | PageSnapshot | None = None,
    diff: SnapshotDiff | None = None,
    max_token_budget: int = 6000,
) -> FailureContext:
    """Build a compact, privacy-preserving FailureContext.

    Rules:
    - Never stores test data values, passwords, card numbers, or cookies.
    - Only stores field_keys (e.g. ['full_name', 'email', 'street_address', ...]).
    - Trims long lists to stay well below max_token_budget (~6k tokens).
    """
    # Strict privacy: list of field_keys only, NEVER test data values
    field_keys = list(intent.test_data.keys())

    failed_idx = run_result.failed_step_index
    failure_type = run_result.failure_type

    # Extract passed steps before failure
    if failed_idx is not None and failed_idx >= 0:
        passed_steps = list(recipe.steps[:failed_idx])
        failed_step = (
            recipe.steps[failed_idx] if failed_idx < len(recipe.steps) else None
        )
    else:
        passed_steps = list(recipe.steps)
        failed_step = None

    # Limit passed steps length to 20 if very long
    if len(passed_steps) > 20:
        passed_steps = passed_steps[-20:]

    diff_summary_text = summarize_diff(diff)

    trimmed_ev = trim_evidence(run_result.evidence or {})
    trimmed_inv = _trim_inventory(current_inventory)

    context = FailureContext(
        goal=intent.goal,
        field_keys=field_keys,
        failed_step_index=failed_idx,
        failure_type=failure_type,
        passed_steps=passed_steps,
        failed_step=failed_step,
        current_inventory=trimmed_inv,
        diff_summary=diff_summary_text,
        evidence=trimmed_ev,
        triage=triage,
    )

    # Budget safeguard check
    if context.estimated_tokens() > max_token_budget:
        # Aggressive secondary trim if needed
        trimmed_inv_tight = _trim_inventory(current_inventory, max_elements_per_page=15)
        context = FailureContext(
            goal=intent.goal,
            field_keys=field_keys,
            failed_step_index=failed_idx,
            failure_type=failure_type,
            passed_steps=passed_steps[-10:],
            failed_step=failed_step,
            current_inventory=trimmed_inv_tight,
            diff_summary=_trim_string(diff_summary_text, 1000),
            evidence=trim_evidence(run_result.evidence or {}, max_items=2),
            triage=triage,
        )

    return context
