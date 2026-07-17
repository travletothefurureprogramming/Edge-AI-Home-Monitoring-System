from unittest.mock import patch

@patch("ollama.chat")
def test_ai(mock_chat, auth_client):

    mock_chat.return_value = {
        "message":{
            "content":"Hello"
        }
    }

    response = auth_client.post(
        "/api/ai",
        json={
            "prompt":"Hi"
        }
    )

    assert response.json["response"] == "Hello"