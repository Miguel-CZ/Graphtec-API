# tests/conftest.py
import pytest

# -------------------------------
# Dummies globales para el proyecto
# -------------------------------
class DummyConnection:
    """Simula la conexión (USB o LAN)"""
    def __init__(self, *a, **k): 
        self.sent = []
        self.opened = False
        self.closed = False
    def open(self): self.opened = True
    def close(self): self.closed = True
    def send(self, data): self.sent.append(data)
    def query(self, cmd): 
        self.sent.append(cmd)
        return "OK"

class DummyRealtime:
    """Simula lectura en tiempo real"""
    def __init__(self, conn): pass
    def read(self): 
        return {"CH1": 1.23, "CH2": 4.56, "CH3": 7.89}

class DummyCapture:
    """Simula descarga de datos"""
    def __init__(self, conn): pass
    def download(self, dest, start=None, end=None):
        return f"{dest}_fake_download.bin"
    def read_header(self):
        return "HEADER:CH1,CH2,CH3"

# -------------------------------
# Fixture global para sustituir clases reales
# -------------------------------
@pytest.fixture(autouse=True)
def patch_gl100_classes(monkeypatch):
    """Aplica dummies globalmente a GL100 para todos los tests."""
    monkeypatch.setattr("gl100.api.public.GL100Connection", lambda *a, **k: DummyConnection())
    monkeypatch.setattr("gl100.api.public.GL100Realtime", DummyRealtime)
    monkeypatch.setattr("gl100.api.public.GL100Capture", DummyCapture)
