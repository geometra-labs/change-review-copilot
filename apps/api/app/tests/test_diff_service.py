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
