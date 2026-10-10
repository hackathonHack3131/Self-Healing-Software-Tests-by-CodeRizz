"""Functions for loading, saving, and verifying immutable intents and versioned recipes."""

import json
import os
from pathlib import Path
import re
import uuid
from engine.models import Intent, Recipe


class IntentHashMismatchError(ValueError):
    """Raised when a recipe's intent_hash does not match the intent's content_hash."""
    pass


def get_project_root() -> Path:
    """Return project root directory."""
    return Path(__file__).resolve().parent.parent


def load_intent(intent_id: str | None = None, path: Path | str | None = None) -> Intent:
    """Load and validate an immutable Intent from JSON."""
    if path is not None:
        intent_path = Path(path)
    elif intent_id is not None:
        root = get_project_root()
        candidates = [
            root / "intents" / f"{intent_id}_intent.json",
            root / "intents" / f"{intent_id}.json",
        ]
        intent_path = next((p for p in candidates if p.exists()), None)
        if intent_path is None:
            raise FileNotFoundError(f"Intent file not found for intent_id: {intent_id}")
    else:
        raise ValueError("Either intent_id or path must be provided")

    with open(intent_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Intent.model_validate(data)


def get_recipe_dir(intent_id: str, base_dir: Path | str | None = None) -> Path:
    """Get the directory storing recipes for a given intent_id."""
    if base_dir is not None:
        return Path(base_dir) / intent_id
    return get_project_root() / "recipes" / intent_id


def get_latest_recipe_version(intent_id: str, base_dir: Path | str | None = None) -> int:
    """Find the highest recipe version number existing in the recipe directory."""
    recipe_dir = get_recipe_dir(intent_id, base_dir)
    if not recipe_dir.exists():
        raise FileNotFoundError(f"Recipe directory does not exist: {recipe_dir}")

    versions = []
    for entry in recipe_dir.glob("v*.json"):
        match = re.match(r"^v(\d+)\.json$", entry.name)
        if match:
            versions.append(int(match.group(1)))

    if not versions:
        raise FileNotFoundError(f"No recipe versions found in {recipe_dir}")

    return max(versions)


def check_intent_hash(recipe: Recipe, intent: Intent) -> None:
    """Verify that the recipe's intent_hash matches the intent's content_hash."""
    if recipe.intent_hash != intent.content_hash:
        raise IntentHashMismatchError(
            f"Recipe intent_hash '{recipe.intent_hash}' does not match "
            f"intent content_hash '{intent.content_hash}'"
        )


def load_recipe(
    intent_id: str,
    version: int | str | None = None,
    intent: Intent | None = None,
    base_dir: Path | str | None = None,
) -> Recipe:
    """Load a recipe by version (or latest) and verify its intent hash if an intent is supplied."""
    recipe_dir = get_recipe_dir(intent_id, base_dir)

    if version is None or version == "latest":
        resolved_version = get_latest_recipe_version(intent_id, base_dir)
    elif isinstance(version, str) and version.startswith("v"):
        resolved_version = int(version[1:])
    else:
        resolved_version = int(version)

    recipe_file = recipe_dir / f"v{resolved_version}.json"
    if not recipe_file.exists():
        raise FileNotFoundError(f"Recipe file not found: {recipe_file}")

    with open(recipe_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipe = Recipe.model_validate(data)

    if intent is not None:
        check_intent_hash(recipe, intent)
        recipe.validate_against_intent(intent)

    return recipe


def save_recipe(
    recipe: Recipe,
    base_dir: Path | str | None = None,
    intent: Intent | None = None,
    assign_next_version: bool = False,
) -> Recipe:
    """Atomically save a recipe to disk. Refuses to overwrite an existing version."""
    if intent is not None:
        check_intent_hash(recipe, intent)
        recipe.validate_against_intent(intent)

    recipe_dir = get_recipe_dir(recipe.intent_id, base_dir)
    recipe_dir.mkdir(parents=True, exist_ok=True)

    target_version = recipe.version
    if assign_next_version:
        try:
            latest = get_latest_recipe_version(recipe.intent_id, base_dir)
            target_version = latest + 1
        except FileNotFoundError:
            target_version = 1
        recipe = recipe.model_copy(update={"version": target_version})

    target_file = recipe_dir / f"v{target_version}.json"
    if target_file.exists():
        raise FileExistsError(
            f"Recipe version v{target_version} already exists at {target_file}. Overwrite refused."
        )

    # Atomic write pattern: write to temporary file in same directory, then rename
    temp_file = recipe_dir / f".v{target_version}_{uuid.uuid4().hex}.tmp"
    try:
        content = recipe.model_dump_json(indent=2)
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename / replace
        os.replace(temp_file, target_file)
    except Exception:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        raise

    return recipe
