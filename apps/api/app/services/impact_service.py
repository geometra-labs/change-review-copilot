from __future__ import annotations

from collections import defaultdict


class ImpactService:
    def generate_findings(
        self,
        changed_part_keys: set[str],
        parts: list[dict],
        relationships: list[dict],
    ) -> dict:
        adjacency: dict[str, list[dict]] = defaultdict(list)
        for rel in relationships:
            src = rel["source_part_key"]
            dst = rel["target_part_key"]
            adjacency[src].append(rel)
            adjacency[dst].append(
                {
                    "source_part_key": dst,
                    "target_part_key": src,
                    "relationship_type": rel["relationship_type"],
                    "score": rel.get("score", 0.0),
                    "evidence": rel.get("evidence", {}),
                }
            )

        parts_by_key = {p["part_key"]: p for p in parts}
        findings: list[dict] = []

        for changed_key in changed_part_keys:
            for rel in adjacency.get(changed_key, []):
                target_key = rel["target_part_key"]
                if target_key in changed_part_keys or target_key not in parts_by_key:
                    continue

                risk_type, severity, recommended_check = self._classify_relationship(rel)
                findings.append(
                    {
                        "part_key": target_key,
                        "part_name": parts_by_key[target_key]["name"],
                        "severity": severity,
                        "risk_type": risk_type,
                        "evidence": {
                            "changed_part_key": changed_key,
                            "relationship_type": rel["relationship_type"],
                            "relationship_score": rel.get("score", 0.0),
                            "relationship_evidence": rel.get("evidence", {}),
                        },
                        "reason_text": self._reason_text(parts_by_key[target_key]["name"], changed_key, rel),
                        "recommended_check": recommended_check,
                        "rank_score": self._rank_score(rel, severity),
                    }
                )

        findings = self._dedupe_highest(findings)

        summary = {
            "direct_changes": len(changed_part_keys),
            "affected_parts": len(findings),
            "high_risk_count": sum(1 for f in findings if f["severity"] == "high"),
        }
        return {"summary": summary, "findings": sorted(findings, key=lambda x: x["rank_score"], reverse=True)}

    def _classify_relationship(self, rel: dict) -> tuple[str, str, str]:
        rel_type = rel["relationship_type"]

        if rel_type in {"intersecting", "interface"}:
            return "interface_risk", "high", "Verify interface alignment, contact faces, and mating assumptions."
        if rel_type in {"adjacent", "near_clearance"}:
            return "clearance_review", "medium", "Check local clearance and envelope around the changed part."
        return "dependency_review", "low", "Inspect downstream dependency and parent assembly assumptions."

    def _reason_text(self, part_name: str, changed_key: str, rel: dict) -> str:
        return (
            f"{part_name} was flagged because it is linked to changed part '{changed_key}' "
            f"through relationship '{rel['relationship_type']}'."
        )

    def _rank_score(self, rel: dict, severity: str) -> float:
        base = {"high": 0.9, "medium": 0.6, "low": 0.3}[severity]
        return base + float(rel.get("score", 0.0)) * 0.1

    def _dedupe_highest(self, findings: list[dict]) -> list[dict]:
        best: dict[str, dict] = {}
        for finding in findings:
            key = finding["part_key"]
            current = best.get(key)
            if current is None or finding["rank_score"] > current["rank_score"]:
                best[key] = finding
        return list(best.values())
