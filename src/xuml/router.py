"""Deterministic multi-dimensional routing over catalog metadata."""
from __future__ import annotations

from typing import Any

KNOWN_DIMENSIONS = {
    "domain", "use_case", "granularity", "layer", "network", "workflow",
    "perspective", "diagram_type", "output_format", "constraints",
}


def route(intent: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    """Choose the best compatible catalog entry without discarding unknown intent."""
    dimensions = intent.get("dimensions", intent)
    if not isinstance(dimensions, dict):
        raise ValueError("Intent must be a mapping or contain a dimensions mapping")

    requested = {key: value for key, value in dimensions.items() if value is not None}
    candidates: list[tuple[int, int, dict[str, Any], list[str], list[str]]] = []
    for entry in catalog["entries"]:
        supports = entry.get("supports", {})
        matched: list[str] = []
        conflicts: list[str] = []
        for key, value in requested.items():
            if key not in supports:
                continue
            allowed = supports[key]
            allowed_values = allowed if isinstance(allowed, list) else [allowed]
            values = value if isinstance(value, list) else [value]
            if any(item in allowed_values or "*" in allowed_values for item in values):
                matched.append(key)
            else:
                conflicts.append(key)
        # A conflict is a hard exclusion only when the catalog explicitly claims support.
        if conflicts:
            continue
        specificity = len(supports)
        candidates.append((len(matched), specificity, entry, matched, conflicts))

    candidates.sort(key=lambda item: (item[0], item[1], item[2]["id"]), reverse=True)
    if not candidates:
        return {
            "status": "no_match",
            "selected": None,
            "requested": requested,
            "unknown_dimensions": sorted(set(requested) - KNOWN_DIMENSIONS),
            "matched_dimensions": [],
            "assumptions": ["No catalog entry matched all explicitly supported dimensions."],
            "warnings": ["Add a compatible catalog entry or relax conflicting dimensions."],
        }

    score, _, selected, matched, _ = candidates[0]
    unknown = sorted(set(requested) - KNOWN_DIMENSIONS)
    unsupported = sorted(key for key in requested if key not in selected.get("supports", {}))
    warnings = []
    if unknown:
        warnings.append("Unknown dimensions were preserved but not interpreted: " + ", ".join(unknown))
    if unsupported:
        warnings.append("Dimensions not covered by the selected entry: " + ", ".join(unsupported))
    if not matched:
        warnings.append("No requested dimensions matched; selected the least-specific compatible default.")
    return {
        "status": "matched",
        "selected": {
            "id": selected["id"],
            "kind": selected.get("kind", "diagram"),
            "title": selected.get("title", selected["id"]),
            "output_format": selected.get("output_format", requested.get("output_format", "svg")),
            "template": selected.get("template"),
        },
        "requested": requested,
        "unknown_dimensions": unknown,
        "matched_dimensions": sorted(matched),
        "score": score,
        "assumptions": selected.get("assumptions", []),
        "warnings": warnings,
    }
