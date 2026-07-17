def test_invalid_route(client):

    response = client.get("/abcdef")

    assert response.status_code == 404

def test_missing_json(auth_client):

    response = auth_client.post("/api/ai")

    assert response.status_code == 400