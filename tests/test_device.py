from gl100.core.device import GL100Device

class DummyConn:
    def __init__(self): self.sent = []
    def send(self, data): self.sent.append(data)
    def query(self, cmd): self.sent.append(cmd); return f"RESP:{cmd}"

def test_start_stop_measurement():
    conn = DummyConn()
    dev = GL100Device(conn)
    dev.start_measurement()
    dev.stop_measurement()
    assert any(":MEAS:STAR" in s for s in conn.sent)
    assert any(":MEAS:STOP" in s for s in conn.sent)

def test_get_status_flags():
    conn = DummyConn()
    dev = GL100Device(conn)
    result = dev.get_status_flags()
    assert result.startswith("RESP:")

def test_channel_config():
    conn = DummyConn()
    dev = GL100Device(conn)
    dev.set_channel_input(1, "TEMP")
    dev.set_channel_range(1, "1V")
    assert ":AMP:CH1" in conn.sent[0]
    assert ":RANG" in conn.sent[1]
