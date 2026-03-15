"""Which parts are likely affected by the change."""


def get_affected_part_ids(
    component_ids: list[str],
    adjacency: dict,
    changed_component_id: str | None,
    change_type: str,
) -> list[str]:
    affected = set(component_ids) if change_type == "part_added_removed" else set()
    if changed_component_id:
        affected.add(changed_component_id)
        for neighbor in adjacency.get(changed_component_id, []):
            affected.add(neighbor)
    if not affected and component_ids:
        affected = set(component_ids[:1])
    return list(affected)
