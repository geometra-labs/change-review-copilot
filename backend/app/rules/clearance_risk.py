"""Where clearance/interference risk may appear."""


def get_clearance_risks(
    component_ids: list[str],
    changed_component_id: str | None,
) -> list[tuple[str, str]]:
    # (message, level): level = high | medium | low
    if not changed_component_id:
        return []
    return [
        (
            "Clearance around changed part should be rechecked.",
            "medium",
        )
    ]
