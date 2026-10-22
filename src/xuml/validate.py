"""Lightweight validation for intents and route results."""
from __future__ import annotations

from typing import Any


def validate_intent(intent: dict[str, Any], dimension_spec: dict[str, Any]) -> list[dict[str, str]]:
    dimensions = intent.get("dimensions", intent)
    issues: list[dict[str, str]] = []
    if not isinstance(dimensions, dict):
        return [{"severity": "error", "code": "intent.not_mapping", "message": "Intent must be a mapping."}]
    definitions = dimension_spec.get("dimensions", {})
    for key, value in dimensions.items():
        if value is None:
            continue
        definition = definitions.get(key)
        if definition is None:
            issues.append({"severity": "warning", "code": "dimension.unknown", "message": f"Unknown dimension preserved: {key}"})
            continue
        allowed = definition.get("values")
        if allowed and isinstance(value, str) and value not in allowed and "*" not in allowed:
            issues.append({"severity": "warning", "code": "dimension.unlisted_value", "message": f"Unlisted value for {key}: {value}"})
    return issues
