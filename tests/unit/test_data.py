def test_data_sampling(device):
    data = device.data
    resp = data.get_data_sampling()
    assert resp.endswith("500")


def test_data_capture_mode(device):
    data = device.data
    resp = data.get_data_capture_mode()
    assert resp.endswith("CONT")