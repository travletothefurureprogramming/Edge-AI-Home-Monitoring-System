from unittest.mock import patch


TEST_DEVICE = {
    "device": "test_device",
    "room": "living_room",
    "type": "test_type",
    "number": 1,
    "command": "on"
}


def test_home(auth_client):

    response = auth_client.get("/")

    assert response.status_code == 200


@patch("routes.devices.AndroidTV")
@patch("routes.devices.LG_TV")
@patch("routes.devices.Samsung_TV")
def test_tv(mock_samsung, mock_lg, mock_android, auth_client):

    mock_android.return_value.send_command.return_value = True
    mock_lg.return_value.execute_command.return_value = True
    mock_samsung.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/tv",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Tapo_Smart_Bulbs")
def test_tapo_light(mock_tapo, auth_client):

    mock_tapo.return_value.command.return_value = True

    response = auth_client.post(
        "/api/tapo_light",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Tapo_Led_strip")
def test_tapo_led_strip(mock_led, auth_client):

    mock_led.return_value.command.return_value = True

    response = auth_client.post(
        "/api/tapo_led_strip",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Phue")
def test_phue_light(mock_phue, auth_client):

    mock_phue.return_value.command.return_value = True

    response = auth_client.post(
        "/api/phue_light",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Yeelight")
def test_yeelight(mock_yeelight, auth_client):

    mock_yeelight.return_value.command.return_value = True

    response = auth_client.post(
        "/api/yeelight",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.DaikinAC")
def test_daikin(mock_daikin, auth_client):

    mock_daikin.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/daikin",
        json={
            **TEST_DEVICE,
            "mode": "cool"
        }
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Shelly")
def test_shelly(mock_shelly, auth_client):

    mock_shelly.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/shelly",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Kasa")
def test_kasa(mock_kasa, auth_client):

    mock_kasa.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/kasa",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Kasa")
def test_broadlink_ac(mock_kasa, auth_client):

    mock_kasa.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/broadlink/ac",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Broadlink")
def test_broadlink_decoder(mock_broadlink, auth_client):

    mock_broadlink.return_value.send_packet.return_value = True

    response = auth_client.post(
        "/api/broadlink/decoder",
        json=TEST_DEVICE
    )

    assert response.status_code in [200, 404, 503]


@patch("routes.devices.Sonos")
def test_sonos(mock_sonos, auth_client):

    mock_sonos.return_value.execute_command.return_value = True

    response = auth_client.post(
        "/api/music/control",
        json=TEST_DEVICE
    )

    assert response.status_code in [200,404,503]