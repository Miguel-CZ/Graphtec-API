def test_trigger_defaults(device):
    trig = device.trigger

    assert trig.get_trigger() == "OFF"
    assert trig.get_trigger_source() == "OFF"

    ch1 = trig.get_trigger_channel(1)
    assert ch1["mode"] == "OFF"
    assert ch1["value"] == "+0.000V"

    assert trig.get_pretrigger() == "0"
