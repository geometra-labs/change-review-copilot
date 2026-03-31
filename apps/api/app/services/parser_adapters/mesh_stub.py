from __future__ import annotations

from pathlib import Path

import trimesh

from app.schemas.normalized_model import (
    BBox,
    NormalizedAssembly,
    NormalizedPart,
    Transform,
    Vector3Object,
)
from app.services.parser_adapters.base import ParserAdapter, ParserError


class MeshStubParserAdapter(ParserAdapter):
    supported_extensions = {".obj", ".stl", ".glb"}
    is_production_ready = True
    notes = "Mesh parser using trimesh. Produces one or more normalized parts from scene geometry."

    def parse(self, file_uri: str) -> NormalizedAssembly:
        path = Path(file_uri)

        try:
            loaded = trimesh.load(str(path), force="scene")
        except Exception as exc:
            raise ParserError(f"Failed to load mesh file: {exc}") from exc

        if loaded is None:
            raise ParserError("Mesh file could not be loaded")

        parts: list[NormalizedPart] = []

        if isinstance(loaded, trimesh.Scene):
            node_names = list(loaded.graph.nodes_geometry)
            if not node_names:
                raise ParserError("Mesh scene contains no geometry")

            for index, node_name in enumerate(node_names):
                transform, geometry_name = loaded.graph[node_name]
                geometry = loaded.geometry.get(geometry_name)
                if geometry is None:
                    continue

                mesh = geometry.copy()
                mesh.apply_transform(transform)
                label = str(node_name or geometry_name or f"mesh_{index}")
                parts.append(self._mesh_to_part(label, mesh, index))

            if not parts:
                raise ParserError("Mesh scene contains no usable geometry")
        elif isinstance(loaded, trimesh.Trimesh):
            parts.append(self._mesh_to_part(path.stem, loaded, 0))
        else:
            raise ParserError(f"Unsupported trimesh object type: {type(loaded).__name__}")

        return NormalizedAssembly(
            assembly_id=path.stem,
            name=path.stem,
            parts=parts,
            relationships=[],
        )

    def _mesh_to_part(self, name: str, mesh: trimesh.Trimesh, index: int) -> NormalizedPart:
        if mesh.vertices is None or len(mesh.vertices) == 0:
            raise ParserError(f"Mesh '{name}' contains no vertices")

        bounds = mesh.bounds
        if bounds is None or len(bounds) != 2:
            raise ParserError(f"Mesh '{name}' missing valid bounds")

        min_corner = bounds[0].tolist()
        max_corner = bounds[1].tolist()
        centroid = mesh.centroid.tolist()

        volume_estimate = None
        try:
            if mesh.is_volume:
                volume_estimate = float(abs(mesh.volume))
            else:
                extents = mesh.extents.tolist()
                volume_estimate = float(abs(extents[0] * extents[1] * extents[2]))
        except Exception:
            volume_estimate = None

        return NormalizedPart(
            part_key=f"mesh_part_{index}_{self._slug(name)}",
            name=name,
            parent_part_key=None,
            bbox=BBox(min=[float(value) for value in min_corner], max=[float(value) for value in max_corner]),
            centroid=Vector3Object(
                x=float(centroid[0]),
                y=float(centroid[1]),
                z=float(centroid[2]),
            ),
            transform=Transform(translation=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0]),
            volume_estimate=volume_estimate,
            geometry_signature=self._geometry_signature(mesh),
            metadata={
                "vertex_count": int(len(mesh.vertices)),
                "face_count": int(len(mesh.faces)) if mesh.faces is not None else 0,
                "source": "trimesh",
            },
        )

    def _geometry_signature(self, mesh: trimesh.Trimesh) -> str:
        extents = [round(float(value), 4) for value in mesh.extents.tolist()]
        vertex_count = int(len(mesh.vertices))
        face_count = int(len(mesh.faces)) if mesh.faces is not None else 0
        return f"ext:{extents[0]}:{extents[1]}:{extents[2]}|v:{vertex_count}|f:{face_count}"

    def _slug(self, text: str) -> str:
        safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
        while "__" in safe:
            safe = safe.replace("__", "_")
        return safe.strip("_") or "part"
