from app.schemas.normalized_model import (
    BBox,
    NormalizedAssembly,
    NormalizedPart,
    Transform,
    Vector3Object,
)
from app.services.relationship_inference_service import RelationshipInferenceService


def test_infers_adjacency_when_relationships_missing() -> None:
    model = NormalizedAssembly(
        assembly_id="asm_1",
        name="demo",
        parts=[
            NormalizedPart(
                part_key="p1",
                name="Part 1",
                bbox=BBox(min=[0, 0, 0], max=[10, 10, 10]),
                centroid=Vector3Object(x=5, y=5, z=5),
                transform=Transform(translation=[0, 0, 0], rotation=[0, 0, 0]),
                geometry_signature="sig1",
            ),
            NormalizedPart(
                part_key="p2",
                name="Part 2",
                bbox=BBox(min=[10.5, 0, 0], max=[20.5, 10, 10]),
                centroid=Vector3Object(x=15.5, y=5, z=5),
                transform=Transform(translation=[0, 0, 0], rotation=[0, 0, 0]),
                geometry_signature="sig2",
            ),
        ],
        relationships=[],
    )

    enriched = RelationshipInferenceService().infer_missing_relationships(
        model,
        adjacency_threshold_mm=1.0,
    )

    assert len(enriched.relationships) == 1
    assert enriched.relationships[0].relationship_type == "adjacent"
