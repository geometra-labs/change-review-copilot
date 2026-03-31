from __future__ import annotations

import pytest
import trimesh

from app.services.parser_adapters.mesh_stub import MeshStubParserAdapter
from app.services.parse_service import ParseService
from app.tests.helpers import temporary_workspace_dir


def test_mesh_parser_adapter_parses_obj_box() -> None:
    mesh = trimesh.creation.box(extents=[2.0, 4.0, 6.0])

    with temporary_workspace_dir("mesh_parser_obj") as tmp_dir:
        path = tmp_dir / "fixture.obj"
        path.write_text(mesh.export(file_type="obj"), encoding="utf-8")

        parsed = MeshStubParserAdapter().parse(str(path))

    assert parsed.assembly_id == "fixture"
    assert len(parsed.parts) == 1
    assert parsed.parts[0].metadata["source"] == "trimesh"
    assert parsed.parts[0].geometry_signature is not None


def test_parse_service_uses_mesh_adapter_for_obj() -> None:
    mesh = trimesh.creation.box(extents=[1.0, 1.0, 1.0])

    with temporary_workspace_dir("parse_service_mesh") as tmp_dir:
        path = tmp_dir / "fixture.obj"
        path.write_text(mesh.export(file_type="obj"), encoding="utf-8")

        parsed = ParseService().parse_model(str(path))

    assert parsed.name == "fixture"
    assert len(parsed.parts) == 1
    assert parsed.parts[0].part_key.startswith("mesh_part_0_")


def test_mesh_parser_applies_scene_node_transforms() -> None:
    mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
    scene = trimesh.Scene()
    scene.add_geometry(
        mesh,
        node_name="translated_box",
        transform=trimesh.transformations.translation_matrix([10.0, 5.0, -3.0]),
    )

    with temporary_workspace_dir("mesh_parser_scene") as tmp_dir:
        path = tmp_dir / "fixture.glb"
        path.write_bytes(scene.export(file_type="glb"))

        parsed = MeshStubParserAdapter().parse(str(path))

    assert len(parsed.parts) == 1
    assert parsed.parts[0].name == "translated_box"
    assert parsed.parts[0].centroid.x == pytest.approx(10.0)
    assert parsed.parts[0].centroid.y == pytest.approx(5.0)
    assert parsed.parts[0].centroid.z == pytest.approx(-3.0)
