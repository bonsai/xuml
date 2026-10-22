"""Load and validate the YAML catalog used by the xuml router."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class CatalogError(ValueError):
    """Raised when a catalog is missing or invalid."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogError(f"Cannot read YAML file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise CatalogError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CatalogError(f"Expected a YAML mapping in {path}")
    return value


def load_catalog(path: str | Path) -> dict[str, Any]:
    data = load_yaml(path)
    if data.get("version") != 1:
        raise CatalogError("Catalog version must be 1")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise CatalogError("Catalog must contain a non-empty 'entries' list")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise CatalogError("Each catalog entry must be a mapping")
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id.strip():
            raise CatalogError("Each catalog entry needs a non-empty string id")
        if entry_id in seen:
            raise CatalogError(f"Duplicate catalog entry id: {entry_id}")
        seen.add(entry_id)
        if not isinstance(entry.get("supports", {}), dict):
            raise CatalogError(f"'supports' must be a mapping for {entry_id}")
    return data


def load_dimensions(path: str | Path) -> dict[str, Any]:
    data = load_yaml(path)
    if data.get("version") != 1 or not isinstance(data.get("dimensions"), dict):
        raise CatalogError("Dimensions file must have version: 1 and a dimensions mapping")
    return data
