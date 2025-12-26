def test_amp_channel_1(device):
    amp = device.amp

    assert amp.get_channel_input(1) == "DC_V"
    assert amp.get_channel_range(1) == "20V"
    assert amp.get_channel_type(1) == "VT"
    assert amp.get_channel_clamp(1) == "NONE"
    assert amp.get_channel_voltage(1) == "NONE"
    assert amp.get_channel_pf(1) == "NONE"


def test_amp_channel_off(device):
    amp = device.amp

    assert amp.get_channel_input(3) == "OFF"
    assert amp.get_channel_range(3) == "NONE"
