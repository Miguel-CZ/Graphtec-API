from gl100.core.connection.usb_connection import USBConnection
from gl100.core.connection.wlan_connection import LANConnection
import pytest

def test_usb_connection_open_close(monkeypatch):
    """Simula puerto serial."""
    class DummySerial:
        def __init__(self, **kwargs): pass
        def write(self, data): self.data = data
        def read(self, n): return b"OK"
        def close(self): pass
    monkeypatch.setattr("serial.Serial", DummySerial)

    conn = USBConnection(port="COM_TEST")
    conn.open()
    assert conn.is_open()
    conn.send(":IDN?")
    assert b"IDN" in conn._conn.data
    conn.close()
    assert not conn.is_open()

def test_lan_connection_open_close(monkeypatch):
    """Simula socket TCP."""
    class DummySocket:
        def __init__(self, *a, **kw): pass
        def settimeout(self, t): pass
        def connect(self, addr): self.addr = addr
        def sendall(self, data): self.data = data
        def recv(self, size): return b"READY"
        def close(self): pass
    monkeypatch.setattr("socket.socket", lambda *a, **kw: DummySocket())

    conn = LANConnection(address="127.0.0.1", port=8023)
    conn.open()
    conn.send(":IDN?")
    assert b":IDN" in conn._conn.data
    data = conn.receive()
    assert data == b"READY"
    conn.close()
