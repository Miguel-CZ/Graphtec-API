def test_get_error_status(device):
    err = device.status.get_error_status()
    assert isinstance(err, dict)
    assert err["code"] == 0
    assert "meaning" in err
