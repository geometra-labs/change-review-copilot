"""What interfaces may break."""


def get_interfaces_at_risk(
    adjacency: dict,
    changed_component_id: str | None,
) -> list[tuple[str, str]]:
    # (message, level): level = high | medium | low
    if not changed_component_id:
        return []
    neighbors = adjacency.get(changed_component_id, [])
    if not neighbors:
        return [("Interfaces to changed part unknown (no adjacency).", "medium")]
    return [
        (f"Interface with {n} may be affected.", "high" if len(neighbors) == 1 else "medium")
        for n in neighbors
    ]
