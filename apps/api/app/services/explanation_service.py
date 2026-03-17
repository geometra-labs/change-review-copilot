from __future__ import annotations


class ExplanationService:
    """
    v1 fallback is deterministic text.
    Replace with an actual LLM call later, but keep the same interface.
    """

    def build_summary(self, report_payload: dict) -> dict:
        summary = report_payload["summary"]
        findings = report_payload["findings"][:3]

        if not findings:
            text = (
                f"The comparison found {summary['direct_changes']} direct changes and no downstream affected parts "
                "were ranked above the current review threshold."
            )
            inspect_next = "Review the changed parts directly and verify that no hidden CAD constraints were omitted."
            return {"summary_text": text, "inspect_next_text": inspect_next}

        top_names = ", ".join(f["part_name"] for f in findings)
        text = (
            f"The comparison found {summary['direct_changes']} direct changes and {summary['affected_parts']} "
            f"affected parts. The highest-priority review targets are {top_names}."
        )
        inspect_next = "Start with the highest-ranked parts, verify interfaces and clearance, then inspect parent assemblies."
        return {"summary_text": text, "inspect_next_text": inspect_next}
