from __future__ import annotations

from dataclasses import dataclass
import math
import re


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
        results: list[dict] = []

        unmatched_before = before_parts[:]
        unmatched_after = after_parts[:]

        key_map = {part.part_key: part for part in after_parts}
        next_unmatched_before: list[PartRecord] = []
        used_after: set[str] = set()

        # 1. exact part key
        for before in before_parts:
            match = key_map.get(before.part_key)
            if match:
                used_after.add(match.part_key)
                results.append(self._result(before, match, 1.0, "exact_part_key"))
            else:
                next_unmatched_before.append(before)

        unmatched_before = next_unmatched_before
        unmatched_after = [part for part in unmatched_after if part.part_key not in used_after]

        # 2. normalized name + parent
        unmatched_before, unmatched_after, stage_results = self._greedy_stage(
            unmatched_before,
            unmatched_after,
            self._score_name_parent,
            "normalized_name_parent",
            threshold=0.88,
        )
        results.extend(stage_results)

        # 3. geometry signature + bbox similarity
        unmatched_before, unmatched_after, stage_results = self._greedy_stage(
            unmatched_before,
            unmatched_after,
            self._score_geometry_bbox,
            "geometry_bbox_similarity",
            threshold=0.72,
        )
        results.extend(stage_results)

        # 4. centroid + bbox fallback, uncertain
        unmatched_before, unmatched_after, stage_results = self._greedy_stage(
            unmatched_before,
            unmatched_after,
            self._score_spatial_fallback,
            "spatial_fallback_uncertain",
            threshold=0.45,
            force_uncertain=True,
        )
        results.extend(stage_results)

        for before in unmatched_before:
            results.append(
                {
                    "before_part_key": before.part_key,
                    "after_part_key": None,
                    "match_confidence": 1.0,
                    "match_method": "unmatched_removed",
                    "change_type": "removed",
                }
            )

        for after in unmatched_after:
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

    def _greedy_stage(
        self,
        before_parts: list[PartRecord],
        after_parts: list[PartRecord],
        scorer,
        method_name: str,
        threshold: float,
        force_uncertain: bool = False,
    ) -> tuple[list[PartRecord], list[PartRecord], list[dict]]:
        pairs: list[tuple[float, PartRecord, PartRecord]] = []
        for before in before_parts:
            for after in after_parts:
                score = scorer(before, after)
                if score >= threshold:
                    pairs.append((score, before, after))

        pairs.sort(key=lambda pair: pair[0], reverse=True)

        used_before: set[str] = set()
        used_after: set[str] = set()
        stage_results: list[dict] = []

        for score, before, after in pairs:
            if before.part_key in used_before or after.part_key in used_after:
                continue

            used_before.add(before.part_key)
            used_after.add(after.part_key)
            stage_results.append(
                {
                    "before_part_key": before.part_key,
                    "after_part_key": after.part_key,
                    "match_confidence": round(score, 3),
                    "match_method": method_name,
                    "change_type": "uncertain_match" if force_uncertain else self._classify_change(before, after),
                }
            )

        remaining_before = [before for before in before_parts if before.part_key not in used_before]
        remaining_after = [after for after in after_parts if after.part_key not in used_after]
        return remaining_before, remaining_after, stage_results

    def _classify_change(self, before: PartRecord, after: PartRecord) -> str:
        if before.geometry_signature != after.geometry_signature:
            return "geometry_changed"
        if before.centroid != after.centroid:
            return "moved"
        return "unchanged"

    def _result(self, before: PartRecord, after: PartRecord, confidence: float, method: str) -> dict:
        return {
            "before_part_key": before.part_key,
            "after_part_key": after.part_key,
            "match_confidence": confidence,
            "match_method": method,
            "change_type": self._classify_change(before, after),
        }

    def _normalize_name(self, name: str) -> str:
        normalized = name.lower().strip()
        normalized = re.sub(r"[_\-\s]+", " ", normalized)
        normalized = re.sub(r"\b(v\d+|rev\s*\w+|copy|\(\d+\))\b", "", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    def _bbox_dims(self, bbox: dict) -> tuple[float, float, float]:
        min_corner = bbox.get("min") if isinstance(bbox, dict) else None
        max_corner = bbox.get("max") if isinstance(bbox, dict) else None
        if not min_corner or not max_corner or len(min_corner) < 3 or len(max_corner) < 3:
            return (0.0, 0.0, 0.0)

        return (
            float(max_corner[0] - min_corner[0]),
            float(max_corner[1] - min_corner[1]),
            float(max_corner[2] - min_corner[2]),
        )

    def _bbox_volume(self, bbox: dict) -> float:
        dx, dy, dz = self._bbox_dims(bbox)
        return abs(dx * dy * dz)

    def _centroid_distance(self, c1: dict, c2: dict) -> float:
        dx = float(c1["x"]) - float(c2["x"])
        dy = float(c1["y"]) - float(c2["y"])
        dz = float(c1["z"]) - float(c2["z"])
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def _score_name_parent(self, before: PartRecord, after: PartRecord) -> float:
        score = 0.0
        if self._normalize_name(before.name) == self._normalize_name(after.name):
            score += 0.7
        if before.parent_part_key == after.parent_part_key:
            score += 0.2
        if before.geometry_signature and after.geometry_signature and before.geometry_signature == after.geometry_signature:
            score += 0.1
        return min(score, 1.0)

    def _score_geometry_bbox(self, before: PartRecord, after: PartRecord) -> float:
        score = 0.0
        if before.geometry_signature and after.geometry_signature and before.geometry_signature == after.geometry_signature:
            score += 0.55

        volume_before = self._bbox_volume(before.bbox)
        volume_after = self._bbox_volume(after.bbox)
        if max(volume_before, volume_after) > 0:
            ratio = min(volume_before, volume_after) / max(volume_before, volume_after)
            score += 0.25 * ratio

        dims_before = self._bbox_dims(before.bbox)
        dims_after = self._bbox_dims(after.bbox)
        dim_ratios = []
        for dim_before, dim_after in zip(dims_before, dims_after):
            if max(dim_before, dim_after) == 0:
                dim_ratios.append(1.0)
            else:
                dim_ratios.append(min(dim_before, dim_after) / max(dim_before, dim_after))
        score += 0.2 * sum(dim_ratios) / len(dim_ratios)

        return min(score, 1.0)

    def _score_spatial_fallback(self, before: PartRecord, after: PartRecord) -> float:
        distance = self._centroid_distance(before.centroid, after.centroid)
        spatial_score = max(0.0, 1.0 - distance / 50.0)

        volume_before = self._bbox_volume(before.bbox)
        volume_after = self._bbox_volume(after.bbox)
        volume_score = 1.0 if max(volume_before, volume_after) == 0 else min(volume_before, volume_after) / max(volume_before, volume_after)

        name_score = 0.25 if self._normalize_name(before.name) == self._normalize_name(after.name) else 0.0

        return min(0.5 * spatial_score + 0.25 * volume_score + name_score, 1.0)
