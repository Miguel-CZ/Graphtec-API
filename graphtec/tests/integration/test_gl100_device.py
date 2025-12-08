import pytest
from Graphtec.core.device import GL100Device
from Graphtec.tests.mocks.mock_usb_connection import MockUSBConnection


@pytest.fixture
def device():
    conn = MockUSBConnection()
    conn.open()
    dev = GL100Device(conn)
    return dev


def test_device_initialization(device):
    """Comprueba que el dispositivo y sus módulos se inicializan correctamente."""
    # Verifica que la conexión está activa
    assert device.connection.is_open is True

    # Verifica que los módulos principales existen
    assert hasattr(device, "common")
    assert hasattr(device, "interface")
    assert hasattr(device, "status")
    assert hasattr(device, "amp")
    assert hasattr(device, "data")
    assert hasattr(device, "measure")
    assert hasattr(device, "transfer")
    assert hasattr(device, "file")
    assert hasattr(device, "trigger")
    assert hasattr(device, "alarm")
    assert hasattr(device, "logic")

    # Verifica que cada módulo tiene acceso al mismo objeto de conexión
    assert device.common.connection is device.connection
    assert device.amp.connection is device.connection


def test_get_basic_info(device):
    """Prueba los comandos de identificación global del dispositivo."""
    idn = device.common.get_id()
    assert "GRAPHTEC" in idn
    assert "GL100" in idn

    info = device.common.get_device_info()
    assert info["modelo"] == "GL100"
    assert info["version"] == "1.10"
    assert info["serie"] == "012345"


def test_run_common_commands(device):
    """Verifica comandos comunes básicos."""
    device.common.clear()
    device.common.reset()
    device.common.save_settings()

    sent = device.connection.sent_commands
    assert "*CLS" in sent
    assert ":COMMON:RESET" in sent or "*RST" in sent
    assert "*SAV" in sent or ":COMMON:SAV" in sent


def test_device_logging_and_eol(device):
    """Comprueba que se haya enviado la configuración de EOL al iniciar."""
    sent = device.connection.sent_commands
    assert ":IF:NLCODE CR_LF" in sent


def test_config_manager_load(device):
    """Comprueba que el ConfigManager se cargue sin errores."""
    assert device.config is not None
    assert hasattr(device.config, "load_from_device")
