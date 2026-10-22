from xuml.catalog import load_catalog, load_dimensions
from xuml.router import route
from xuml.validate import validate_intent

CATALOG = "schemas/catalog.yaml"
DIMENSIONS = "schemas/dimensions.yaml"


def test_catalog_and_dimensions_load():
    assert len(load_catalog(CATALOG)["entries"]) >= 3
    assert "workflow" in load_dimensions(DIMENSIONS)["dimensions"]


def test_routes_agent_workflow():
    result = route({
        "dimensions": {
            "domain": "ai",
            "use_case": "workflow",
            "granularity": "agent",
            "layer": "orchestration",
            "workflow": "multi_agent",
            "diagram_type": "flowchart",
            "output_format": "svg",
        }
    }, load_catalog(CATALOG))
    assert result["status"] == "matched"
    assert result["selected"]["id"] == "diagram.agent-workflow"
    assert {"domain", "use_case", "workflow"} <= set(result["matched_dimensions"])


def test_unknown_dimensions_are_preserved():
    intent = {"dimensions": {"diagram_type": "architecture", "output_format": "svg", "made_up_dimension": "kept"}}
    result = route(intent, load_catalog(CATALOG))
    assert result["requested"]["made_up_dimension"] == "kept"
    assert "made_up_dimension" in result["unknown_dimensions"]
    assert any("Unknown dimensions" in warning for warning in result["warnings"])


def test_validation_reports_unknown_but_does_not_drop_it():
    diagnostics = validate_intent({"dimensions": {"mystery": "x"}}, load_dimensions(DIMENSIONS))
    assert diagnostics[0]["severity"] == "warning"
    assert diagnostics[0]["code"] == "dimension.unknown"


def test_router_does_not_match_conflicting_supported_dimension():
    result = route({"dimensions": {"domain": "finance", "workflow": "multi_agent"}}, load_catalog(CATALOG))
    assert result["status"] == "matched"
    assert result["selected"]["id"] == "diagram.general-intent"
