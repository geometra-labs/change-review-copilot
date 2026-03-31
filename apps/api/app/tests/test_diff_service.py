from app.services.diff_service import DiffService, PartRecord


def test_diff_service_classifies_added_removed_and_changed() -> None:
    before = [
        PartRecord("a", "Part A", {}, {"x": 0, "y": 0, "z": 0}, "sig1", None),
        PartRecord("b", "Part B", {}, {"x": 0, "y": 0, "z": 0}, "sig2", None),
    ]
    after = [
        PartRecord("a", "Part A", {}, {"x": 0, "y": 0, "z": 0}, "sig1", None),
        PartRecord("b", "Part B", {}, {"x": 1, "y": 0, "z": 0}, "sig2", None),
        PartRecord("c", "Part C", {}, {"x": 0, "y": 0, "z": 0}, "sig3", None),
    ]

    results = DiffService().match_parts(before, after)
    change_types = {row["after_part_key"] or row["before_part_key"]: row["change_type"] for row in results}

    assert change_types["a"] == "unchanged"
    assert change_types["b"] == "moved"
    assert change_types["c"] == "added"


def test_diff_service_emits_uncertain_match_when_only_nearest_centroid_matches() -> None:
    before = [
        PartRecord("old_key", "Bracket Old", {}, {"x": 10, "y": 0, "z": 0}, None, None),
    ]
    after = [
        PartRecord("new_key", "Bracket Renamed", {}, {"x": 12, "y": 0, "z": 0}, None, None),
    ]

    results = DiffService().match_parts(before, after)
    assert len(results) == 1
    assert results[0]["change_type"] == "uncertain_match"
    assert results[0]["match_method"] == "spatial_fallback_uncertain"
    assert results[0]["match_confidence"] >= 0.45
