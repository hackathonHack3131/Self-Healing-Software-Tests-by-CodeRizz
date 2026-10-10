"""Tests for recipe persistence, versioning, atomic writes, and intent hash integrity."""

import json
from pathlib import Path
import pytest
from engine.models import (
    ActionType,
    CreatedBy,
    ExpectedOutcome,
    Intent,
    Recipe,
    Step,
    StepTarget,
    TargetBy,
)
from engine.recipes import (
    IntentHashMismatchError,
    get_latest_recipe_version,
    load_intent,
    load_recipe,
    save_recipe,
)


@pytest.fixture
def checkout_intent():
    """Load the immutable checkout intent from file."""
    return load_intent("checkout")


def test_load_v1_ok(checkout_intent):
    """Verify v1 recipe loads successfully and passes validation against the real intent."""
    recipe = load_recipe("checkout", version=1, intent=checkout_intent)
    assert recipe.intent_id == "checkout"
    assert recipe.version == 1
    assert recipe.created_by == CreatedBy.HUMAN
    assert recipe.intent_hash == checkout_intent.content_hash
    assert len(recipe.steps) == 8
    assert recipe.steps[0].action == ActionType.GOTO_START


def test_changing_one_character_of_intent_makes_hash_check_fail(checkout_intent):
    """Verify that tampering with even a single character in the intent fails the recipe hash check."""
    # Mutate intent slightly
    tampered_intent = Intent(
        id=checkout_intent.id,
        title=checkout_intent.title,
        goal=checkout_intent.goal + "!",  # 1 character changed
        test_data=checkout_intent.test_data,
        expected_outcome=checkout_intent.expected_outcome,
    )
    assert tampered_intent.content_hash != checkout_intent.content_hash

    with pytest.raises((IntentHashMismatchError, ValueError)):
        load_recipe("checkout", version=1, intent=tampered_intent)


def test_save_recipe_writes_v2_and_refuses_overwrite(tmp_path, checkout_intent):
    """Verify save_recipe creates v2, and attempting to overwrite v2 raises FileExistsError."""
    # Copy v1 recipe to tmp_path
    v1_recipe = load_recipe("checkout", version=1, intent=checkout_intent)
    save_recipe(v1_recipe, base_dir=tmp_path)
    assert (tmp_path / "checkout" / "v1.json").exists()

    # Create v2 recipe
    v2_recipe = Recipe(
        intent_id="checkout",
        version=2,
        steps=v1_recipe.steps,
        created_by=CreatedBy.AGENT,
        parent_version=1,
        intent_hash=checkout_intent.content_hash,
    )

    # First save of v2 should succeed
    saved_v2 = save_recipe(v2_recipe, base_dir=tmp_path, intent=checkout_intent)
    assert saved_v2.version == 2
    assert (tmp_path / "checkout" / "v2.json").exists()

    # Second save of v2 must refuse overwrite
    with pytest.raises(FileExistsError, match="already exists"):
        save_recipe(v2_recipe, base_dir=tmp_path, intent=checkout_intent)


def test_simulated_crash_between_temp_write_and_rename_leaves_no_partial_file(
    tmp_path, checkout_intent, monkeypatch
):
    """Verify atomic write guarantees: a crash before rename leaves no partial or corrupted file."""
    recipe_dir = tmp_path / "checkout"
    recipe_dir.mkdir(parents=True, exist_ok=True)
    target_v2 = recipe_dir / "v2.json"

    v2_recipe = Recipe(
        intent_id="checkout",
        version=2,
        steps=[Step(action=ActionType.GOTO_START)],
        created_by=CreatedBy.AGENT,
        parent_version=1,
        intent_hash=checkout_intent.content_hash,
    )

    # Simulate crash during os.replace
    def crash_replace(src, dst):
        raise OSError("Simulated system crash during atomic rename")

    monkeypatch.setattr("os.replace", crash_replace)

    with pytest.raises(OSError, match="Simulated system crash"):
        save_recipe(v2_recipe, base_dir=tmp_path, intent=checkout_intent)

    # Ensure target file was never created
    assert not target_v2.exists()

    # Ensure no leftover temporary files in directory
    temp_files = list(recipe_dir.glob("*.tmp"))
    assert len(temp_files) == 0


def test_latest_version_resolves_correctly(tmp_path, checkout_intent):
    """Verify load_recipe resolves to the highest numeric version when 'latest' is requested."""
    v1_recipe = load_recipe("checkout", version=1, intent=checkout_intent)
    save_recipe(v1_recipe, base_dir=tmp_path)

    # Save v2 and v3
    v2 = v1_recipe.model_copy(update={"version": 2, "parent_version": 1})
    v3 = v1_recipe.model_copy(update={"version": 3, "parent_version": 2})
    save_recipe(v2, base_dir=tmp_path)
    save_recipe(v3, base_dir=tmp_path)

    assert get_latest_recipe_version("checkout", base_dir=tmp_path) == 3

    loaded_latest = load_recipe("checkout", version="latest", base_dir=tmp_path)
    assert loaded_latest.version == 3
    assert loaded_latest.parent_version == 2
