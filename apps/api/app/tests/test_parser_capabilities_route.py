from app.tests.helpers import auth_headers, register_and_login


def test_parser_capabilities_route(client) -> None:
    token = register_and_login(client, "caps@test.com")
    headers = auth_headers(token)

    response = client.get("/parsers/capabilities", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert len(payload["items"]) >= 3
