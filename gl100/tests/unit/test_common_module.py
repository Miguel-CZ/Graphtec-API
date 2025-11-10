import pytest
from gl100.core.device import GL100Device
from gl100.tests.mocks.mock_usb_connection import MockUSBConnection


@pytest.fixture
def device():
    """Crea un GL100Device simulado con conexión USB mock."""
    conn = MockUSBConnection()
    conn.open()
    dev = GL100Device(conn)
    return dev


def test_get_id(device):
    result = device.common.get_id()
    assert isinstance(result, str)
    assert "GRAPHTEC" in result
    assert "GL100" in result

def test_get_system_info(device):
    result = device.common.get_system_info()
    assert isinstance(result, str)
    assert "Model" in result
    assert "FW" in result
    assert "Channels" in result

def test_get_device_state(device):
    state = device.common.get_device_state()
    assert state.strip() == "READY"


def test_get_device_info(device):
    """Comprueba que el diccionario de información contenga los campos esperados."""
    info = device.common.get_device_info()
    assert isinstance(info, dict)
    assert info["modelo"] == "GL100"
    assert info["version"] == "1.10"
    assert info["serie"] == "012345"


def test_clear(device):
    device.common.clear()
    sent = device.connection.sent_commands
    assert "*CLS" in sent


def test_reset(device):
    device.common.reset()
    sent = device.connection.sent_commands
    assert ":COMMON:RESET" in sent

def test_save(device):
    device.common.save_settings()
    sent = device.connection.sent_commands
    assert "*SAV" in sent


