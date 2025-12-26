def test_get_id(device):
    info = device.common.get_id()

    assert info["fabricante"] == "GRAPHTEC"
    assert info["dispositivo"] == "GL100"
    assert info["id"] == "0"
    assert info["firmware"] == "01.45"
