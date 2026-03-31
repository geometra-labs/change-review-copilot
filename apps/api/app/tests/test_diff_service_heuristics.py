from app.services.diff_service import DiffService, PartRecord


def test_name_parent_match_recovers_renamed_part_key() -> None:
    before = [
        PartRecord(
            "old_1",
            "Mount Bracket",
            {"min": [0, 0, 0], "max": [1, 1, 1]},
            {"x": 0, "y": 0, "z": 0},
            "sigA",
            "parent",
        ),
    ]
    after = [
        PartRecord(
            "new_99",
            "Mount Bracket",
            {"min": [0, 0, 0], "max": [1, 1, 1]},
            {"x": 0, "y": 0, "z": 0},
            "sigA",
            "parent",
        ),
    ]

    results = DiffService().match_parts(before, after)
    assert results[0]["match_method"] == "normalized_name_parent"
    assert results[0]["match_confidence"] >= 0.88


def test_geometry_bbox_match_recovers_same_shape() -> None:
    before = [
        PartRecord(
            "old",
            "A",
            {"min": [0, 0, 0], "max": [2, 2, 2]},
            {"x": 1, "y": 1, "z": 1},
            "sigX",
            None,
        ),
    ]
    after = [
        PartRecord(
            "new",
            "B",
            {"min": [0, 0, 0], "max": [2.1, 2, 2]},
            {"x": 1.05, "y": 1, "z": 1},
            "sigX",
            None,
        ),
    ]

    results = DiffService().match_parts(before, after)
    assert results[0]["match_method"] == "geometry_bbox_similarity"
