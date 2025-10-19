# tests/test_io.py
from gl100.io.realtime import GL100Realtime
from gl100.io.capture import GL100Capture

class DummyConn:
    def __init__(self): self.sent = []
    def send(self, data): self.sent.append(data)
    def receive(self, size=4096): return b"#6000004\x00\x64\x00\xc8\x01\x2c"
    def query(self, cmd): return "OK"

def test_realtime_read():
    conn = DummyConn()
    rt = GL100Realtime(conn)
    data = rt.read()
    assert "CH1" in data and isinstance(data["CH1"], int)

def test_capture_download(tmp_path):
    conn = DummyConn()
    cap = GL100Capture(conn)
    dest = tmp_path / "test.bin"
    result = cap.download(str(dest))
    assert "test" in result or dest.exists()
