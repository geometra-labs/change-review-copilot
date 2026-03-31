from app.services.parser_registry import ParserRegistry


def test_mesh_parser_registered_as_supported() -> None:
    registry = ParserRegistry()
    capabilities = registry.capabilities()

    mesh_capability = next(cap for cap in capabilities if cap.name == "MeshStubParserAdapter")
    assert mesh_capability.supported is True
    assert ".obj" in mesh_capability.extensions


def test_json_parser_registered_as_supported() -> None:
    registry = ParserRegistry()
    capabilities = registry.capabilities()

    json_capability = next(cap for cap in capabilities if cap.name == "JsonNormalizedParserAdapter")
    assert json_capability.supported is True
    assert ".json" in json_capability.extensions
