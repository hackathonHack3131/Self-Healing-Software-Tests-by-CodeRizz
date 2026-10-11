"""UI Diff engine for detecting drift, renames, additions, and workflow changes.

Compares UI snapshots and inventories against trusted baselines and classifies
changes into unchanged, renamed, added, removed, ambiguous, and flow differences.
"""

from collections import defaultdict
import difflib
from engine.models import (
    AmbiguousElement,
    FlowDiff,
    PageSnapshot,
    RenamedElement,
    SnapshotDiff,
    UIElement,
    UIInventory,
)

# Standard checkout domain synonyms for semantic rename matching
SYNONYM_GROUPS: list[tuple[set[str], set[str]]] = [
    ({"name"}, {"full name", "first name", "last name", "customer name"}),
    ({"email"}, {"email address", "e-mail"}),
    ({"address"}, {"street address", "shipping address", "delivery address", "billing address"}),
    ({"card number", "card #", "card"}, {"credit card #", "credit card", "card number", "card", "card #"}),
    ({"expiry", "exp"}, {"valid thru", "valid thru (mm/yy)", "expiration", "exp date", "expiry", "mm/yy"}),
    ({"cvc", "cvv"}, {"security code", "cvc", "cvv", "verification code", "card code"}),
    (
        {"checkout"},
        {
            "continue to payment",
            "review order",
            "place order securely",
            "place order",
            "submit order",
            "pay now",
            "proceed to shipping",
            "complete checkout",
        },
    ),
]


def _are_roles_compatible(role_a: str, role_b: str) -> bool:
    """Check if two element roles are functionally compatible for matching."""
    ra = role_a.lower()
    rb = role_b.lower()
    if ra == rb:
        return True
    textbox_types = {"textbox", "input", "textarea"}
    if ra in textbox_types and rb in textbox_types:
        return True
    button_types = {"button", "submit", "reset"}
    if ra in button_types and rb in button_types:
        return True
    return False


def _check_synonym_match(str_a: str, str_b: str) -> bool:
    """Check if str_a and str_b belong to connected synonym groups."""
    sa = str_a.lower().strip()
    sb = str_b.lower().strip()
    for grp_a, grp_b in SYNONYM_GROUPS:
        if (sa in grp_a and sb in grp_b) or (sb in grp_a and sa in grp_b):
            return True
        if any(term in sa for term in grp_a) and any(term in sb for term in grp_b):
            return True
        if any(term in sb for term in grp_a) and any(term in sa for term in grp_b):
            return True
    return False


def compute_rename_score(b: UIElement, c: UIElement) -> float:
    """Compute heuristic similarity score between baseline element b and current candidate c."""
    if not _are_roles_compatible(b.role, c.role):
        return 0.0

    score = 0.0
    b_name = (b.label or b.name or "").strip().lower()
    c_name = (c.label or c.name or "").strip().lower()

    # 1. Semantic synonym match
    if _check_synonym_match(b_name, c_name):
        score += 0.85

    # 2. Input name attribute match
    if b.input_name and c.input_name:
        b_in = b.input_name.strip().lower()
        c_in = c.input_name.strip().lower()
        if b_in == c_in:
            score += 0.85
        elif b_in in c_in or c_in in b_in:
            score += 0.65

    # 3. Placeholder match
    if b.placeholder and c.placeholder:
        if b.placeholder.strip().lower() == c.placeholder.strip().lower():
            score += 0.70

    # 4. Text substring or SequenceMatcher ratio
    if b_name and c_name:
        if b_name in c_name or c_name in b_name:
            score += 0.50
        seq_ratio = difflib.SequenceMatcher(None, b_name, c_name).ratio()
        score += 0.40 * seq_ratio

    # 5. Element ID substring match
    if b.element_id and c.element_id:
        b_id = b.element_id.strip().lower()
        c_id = c.element_id.strip().lower()
        if b_id in c_id or c_id in b_id:
            score += 0.35

    return min(1.0, score)


def _extract_elements_and_paths(
    target: UIInventory | PageSnapshot | list[UIElement],
) -> tuple[list[UIElement], list[str]]:
    """Extract flat element list and page paths from various input formats."""
    if isinstance(target, UIInventory):
        return list(target.all_elements), list(target.page_paths)
    elif isinstance(target, PageSnapshot):
        return list(target.elements), [target.page_path]
    elif isinstance(target, list):
        elements = list(target)
        paths: list[str] = []
        for e in elements:
            if e.page_path and e.page_path not in paths:
                paths.append(e.page_path)
        return elements, paths
    else:
        raise TypeError(f"Unsupported snapshot type: {type(target)}")


def diff_snapshots(
    baseline: UIInventory | PageSnapshot | list[UIElement],
    current: UIInventory | PageSnapshot | list[UIElement],
) -> SnapshotDiff:
    """Compare baseline snapshot or inventory against current UI and report changes.

    Reports:
    - unchanged: elements matching exactly
    - renamed: elements with renamed labels/names detected by heuristic scoring
    - added: new elements present only in current
    - removed: baseline elements missing from current
    - ambiguous: duplicate elements with matching accessible identifiers
    - flow: page path differences and step additions/removals
    - has_drift: boolean flag indicating whether any structural difference exists
    """
    baseline_elements, baseline_paths = _extract_elements_and_paths(baseline)
    current_elements, current_paths = _extract_elements_and_paths(current)

    # -------------------------------------------------------------
    # 1. Ambiguous (duplicate accessible identifier) detection
    # -------------------------------------------------------------
    ambiguous_list: list[AmbiguousElement] = []
    current_groups: dict[tuple[str, str, str], list[UIElement]] = defaultdict(list)
    for c in current_elements:
        c_name = (c.name or "").strip().lower()
        if c_name:
            current_groups[(c.page_path, c.role.lower(), c_name)].append(c)

    for (p_path, role, name), duplicates in current_groups.items():
        if len(duplicates) > 1:
            for el in duplicates:
                ambiguous_list.append(
                    AmbiguousElement(
                        element=el,
                        matching_candidates=[d for d in duplicates if d != el],
                        reason=(
                            f"Multiple elements ({len(duplicates)}) match role '{role}' "
                            f"and name '{el.name}' on '{p_path}'"
                        ),
                    )
                )

    # -------------------------------------------------------------
    # 2. Match Unchanged Elements
    # -------------------------------------------------------------
    matched_baseline_indices: set[int] = set()
    matched_current_indices: set[int] = set()
    unchanged_list: list[UIElement] = []

    for b_idx, b in enumerate(baseline_elements):
        b_name = (b.name or "").strip().lower()
        b_label = (b.label or "").strip().lower()

        # Find candidates in current
        candidates = []
        for c_idx, c in enumerate(current_elements):
            if c_idx in matched_current_indices:
                continue
            if not _are_roles_compatible(b.role, c.role):
                continue

            c_name = (c.name or "").strip().lower()
            c_label = (c.label or "").strip().lower()

            name_matches = b_name and (b_name == c_name)
            label_matches = b_label and (b_label == c_label)

            if name_matches or label_matches:
                candidates.append(c_idx)

        if len(candidates) == 1:
            c_idx = candidates[0]
            matched_baseline_indices.add(b_idx)
            matched_current_indices.add(c_idx)
            unchanged_list.append(current_elements[c_idx])

    # -------------------------------------------------------------
    # 3. Match Renamed Elements
    # -------------------------------------------------------------
    renamed_list: list[RenamedElement] = []

    for b_idx, b in enumerate(baseline_elements):
        if b_idx in matched_baseline_indices:
            continue

        best_score = 0.0
        best_candidates: list[int] = []

        for c_idx, c in enumerate(current_elements):
            if c_idx in matched_current_indices:
                continue

            score = compute_rename_score(b, c)
            if score >= 0.50:
                if score > best_score + 0.01:
                    best_score = score
                    best_candidates = [c_idx]
                elif abs(score - best_score) <= 0.01:
                    best_candidates.append(c_idx)

        if len(best_candidates) == 1:
            c_idx = best_candidates[0]
            matched_baseline_indices.add(b_idx)
            matched_current_indices.add(c_idx)
            c_elem = current_elements[c_idx]
            renamed_list.append(
                RenamedElement(
                    old_element=b,
                    new_element=c_elem,
                    old_name=b.label or b.name,
                    new_name=c_elem.label or c_elem.name,
                    confidence=round(best_score, 2),
                )
            )
        elif len(best_candidates) > 1:
            # Ambiguous rename matches
            ambiguous_candidates = [current_elements[ci] for ci in best_candidates]
            ambiguous_list.append(
                AmbiguousElement(
                    element=b,
                    matching_candidates=ambiguous_candidates,
                    reason=(
                        f"Baseline element '{b.name}' matched {len(best_candidates)} "
                        f"equally confident rename candidates in current UI"
                    ),
                )
            )

    # -------------------------------------------------------------
    # 4. Removed Elements
    # -------------------------------------------------------------
    removed_list: list[UIElement] = [
        b
        for b_idx, b in enumerate(baseline_elements)
        if b_idx not in matched_baseline_indices
    ]

    # -------------------------------------------------------------
    # 5. Added Elements
    # -------------------------------------------------------------
    added_list: list[UIElement] = [
        c
        for c_idx, c in enumerate(current_elements)
        if c_idx not in matched_current_indices
    ]

    # -------------------------------------------------------------
    # 6. Flow Comparison
    # -------------------------------------------------------------
    flow: FlowDiff | None = None
    if baseline_paths or current_paths:
        added_paths = [p for p in current_paths if p not in baseline_paths]
        removed_paths = [p for p in baseline_paths if p not in current_paths]
        is_flow_changed = bool(
            added_paths or removed_paths or (baseline_paths != current_paths)
        )
        flow = FlowDiff(
            baseline_paths=baseline_paths,
            current_paths=current_paths,
            is_flow_changed=is_flow_changed,
            added_paths=added_paths,
            removed_paths=removed_paths,
        )

    # -------------------------------------------------------------
    # 7. Overall Drift
    # -------------------------------------------------------------
    has_drift = bool(
        len(renamed_list) > 0
        or len(added_list) > 0
        or len(removed_list) > 0
        or len(ambiguous_list) > 0
        or (flow and flow.is_flow_changed)
    )

    return SnapshotDiff(
        unchanged=unchanged_list,
        added=added_list,
        removed=removed_list,
        renamed=renamed_list,
        ambiguous=ambiguous_list,
        flow=flow,
        has_drift=has_drift,
    )
