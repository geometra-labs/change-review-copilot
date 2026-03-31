from __future__ import annotations

from math import sqrt

from app.schemas.normalized_model import NormalizedAssembly, NormalizedRelationship


class RelationshipInferenceService:
    def infer_missing_relationships(
        self,
        model: NormalizedAssembly,
        adjacency_threshold_mm: float = 2.0,
        near_clearance_threshold_mm: float = 6.0,
    ) -> NormalizedAssembly:
        explicit = list(model.relationships)
        inferred: list[NormalizedRelationship] = []
        part_map = {part.part_key: part for part in model.parts}

        for part in model.parts:
            if part.parent_part_key and part.parent_part_key in part_map:
                inferred.append(
                    NormalizedRelationship(
                        source_part_key=part.parent_part_key,
                        target_part_key=part.part_key,
                        relationship_type="parent_child",
                        score=1.0,
                        evidence={"inferred": True, "source": "parent_part_key"},
                    )
                )

        for i in range(len(model.parts)):
            for j in range(i + 1, len(model.parts)):
                p1 = model.parts[i]
                p2 = model.parts[j]

                distance = self._bbox_gap_distance(p1.bbox.min, p1.bbox.max, p2.bbox.min, p2.bbox.max)

                if distance <= adjacency_threshold_mm:
                    inferred.append(
                        NormalizedRelationship(
                            source_part_key=p1.part_key,
                            target_part_key=p2.part_key,
                            relationship_type="adjacent",
                            score=0.8,
                            evidence={"distance_mm": distance, "inferred": True},
                        )
                    )
                elif distance <= near_clearance_threshold_mm:
                    inferred.append(
                        NormalizedRelationship(
                            source_part_key=p1.part_key,
                            target_part_key=p2.part_key,
                            relationship_type="near_clearance",
                            score=0.5,
                            evidence={"distance_mm": distance, "inferred": True},
                        )
                    )

        merged = self._dedupe_relationships(explicit + inferred)

        return NormalizedAssembly(
            assembly_id=model.assembly_id,
            name=model.name,
            parts=model.parts,
            relationships=merged,
        )

    def _dedupe_relationships(
        self,
        relationships: list[NormalizedRelationship],
    ) -> list[NormalizedRelationship]:
        best: dict[tuple[str, str, str], NormalizedRelationship] = {}

        for relationship in relationships:
            pair = tuple(sorted([relationship.source_part_key, relationship.target_part_key]))
            key = (pair[0], pair[1], relationship.relationship_type)
            current = best.get(key)
            if current is None or relationship.score > current.score:
                best[key] = relationship

        return list(best.values())

    def _bbox_gap_distance(
        self,
        min1: list[float],
        max1: list[float],
        min2: list[float],
        max2: list[float],
    ) -> float:
        axis_gaps = []
        for a_min, a_max, b_min, b_max in zip(min1, max1, min2, max2):
            if a_max < b_min:
                axis_gaps.append(b_min - a_max)
            elif b_max < a_min:
                axis_gaps.append(a_min - b_max)
            else:
                axis_gaps.append(0.0)
        return sqrt(sum(gap * gap for gap in axis_gaps))
