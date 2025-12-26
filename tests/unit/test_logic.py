def test_logic_type(device):
    logic = device.logic
    assert logic.get_logic_type() == "LOGI"
