def test_option_name(device):
    opt = device.option
    assert opt.get_name() == "GL100"
