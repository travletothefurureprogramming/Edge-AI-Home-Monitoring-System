def test_get_devices(auth_client):

    response = auth_client.get("/api/devices")

    assert response.status_code == 200