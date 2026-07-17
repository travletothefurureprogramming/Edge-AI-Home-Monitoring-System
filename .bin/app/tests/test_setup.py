def test_setup_page(client):
    response = client.get("/setup")

    assert response.status_code == 200