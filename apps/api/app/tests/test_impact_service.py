from app.services.impact_service import ImpactService


def test_impact_service_generates_findings() -> None:
    payload = ImpactService().generate_findings(
        changed_part_keys={"p1"},
        parts=[
            {"part_key": "p1", "name": "Changed Part"},
            {"part_key": "p2", "name": "Bracket"},
        ],
        relationships=[
            {
                "source_part_key": "p1",
                "target_part_key": "p2",
                "relationship_type": "adjacent",
                "score": 0.8,
                "evidence": {"distance_mm": 0.4},
            }
        ],
    )

    assert payload["summary"]["direct_changes"] == 1
    assert payload["summary"]["affected_parts"] == 1
    assert payload["findings"][0]["part_name"] == "Bracket"
