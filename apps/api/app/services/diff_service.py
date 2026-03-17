from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PartRecord:
    part_key: str
    name: str
    bbox: dict
    centroid: dict
    geometry_signature: str | None
    parent_part_key: str | None


class DiffService:
    def match_parts(self, before_parts: list[PartRecord], after_parts: list[PartRecord]) -> list[dict]:
        after_by_key = {p.part_key: p for p in after_parts}
        matched_after_keys: set[str] = set()
        results: list[dict] = []

        for before in before_parts:
            match = after_by_key.get(before.part_key)
            if match:
                matched_after_keys.add(match.part_key)
                change_type = self._classify_change(before, match)
                results.append(
                    {
                        "before_part_key": before.part_key,
                        "after_part_key": match.part_key,
                        "match_confidence": 1.0,
                        "match_method": "exact_part_key",
                        "change_type": change_type,
                    }
                )
            else:
                results.append(
                    {
                        "before_part_key": before.part_key,
                        "after_part_key": None,
                        "match_confidence": 1.0,
                        "match_method": "unmatched_removed",
                        "change_type": "removed",
                    }
                )

        for after in after_parts:
            if after.part_key not in matched_after_keys:
                results.append(
                    {
                        "before_part_key": None,
                        "after_part_key": after.part_key,
                        "match_confidence": 1.0,
                        "match_method": "unmatched_added",
                        "change_type": "added",
                    }
                )

        return results

    def _classify_change(self, before: PartRecord, after: PartRecord) -> str:
        if before.geometry_signature != after.geometry_signature:
            return "geometry_changed"
        if before.centroid != after.centroid:
            return "moved"
        return "unchanged"
