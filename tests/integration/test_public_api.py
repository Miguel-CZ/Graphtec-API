# tests/integration/test_public_api.py
import pytest

from graphtec.core.exceptions import CommandError


def _last_token_as_int(x) -> int:
    """
    Tu API pública a veces documenta ints pero devuelve str (según módulo).
    Este helper hace el test robusto: acepta int/str.
    """
    if isinstance(x, int):
        return x
    if x is None:
        raise AssertionError("Se esperaba int o str, llegó None")
    s = str(x).strip().replace(",", " ")
    parts = [p for p in s.split() if p]
    return int(parts[-1])


def test_connection_cycle(graphtec):
    assert graphtec.is_connected() is False

    graphtec.connect()
    assert graphtec.is_connected() is True

    # Disconnect idempotente (tu código avisa y retorna)
    graphtec.disconnect()
    assert graphtec.is_connected() is False

    graphtec.disconnect()
    assert graphtec.is_connected() is False


def test_common_api(graphtec, conn):
    graphtec.connect()

    info = graphtec.get_id()
    assert info["fabricante"] == "GRAPHTEC"
    assert info["dispositivo"] == "GL100"
    assert info["id"] == "0"
    assert info["firmware"] == "01.45"

    # Estos 2 son comandos "write" (sin respuesta)
    graphtec.clear()
    graphtec.save_settings()

    assert "*CLS" in conn.sent_commands
    assert "*SAV" in conn.sent_commands


def test_channels_api(graphtec, conn):
    graphtec.connect()

    channels = graphtec.get_channels()
    assert isinstance(channels, dict)
    assert set(channels.keys()) == {1, 2, 3, 4}

    # En tus respuestas: CH1/CH2 DC_V 20V, CH3/CH4 OFF NONE
    assert channels[1]["input"] == "DC_V"
    assert channels[1]["range"] == "20V"
    assert channels[1]["type"] == "VT"

    assert channels[3]["input"] == "OFF"
    assert channels[3]["range"] == "NONE"

    # SETTERS (solo verificamos que se envían comandos)
    graphtec.set_channel(1, ch_type="V", ch_input="DC_V", ch_range="10V")
    assert ":AMP:CH1:TYP V" in conn.sent_commands
    assert ":AMP:CH1:INP DC_V" in conn.sent_commands
    assert ":AMP:CH1:RANG 10V" in conn.sent_commands


def test_trigger_api(graphtec):
    graphtec.connect()

    # Getters con respuestas mockeadas
    assert graphtec.get_trigger() == "OFF"
    assert graphtec.get_trigger_source() == "OFF"
    assert _last_token_as_int(graphtec.get_pretrigger()) == 0

    # Canal 1 mockeado: ":TRIG:COND:CH1:SET OFF,+0.000V"
    ch1 = graphtec.get_trigger_channel(1)
    assert isinstance(ch1, dict)
    assert ch1["mode"] == "OFF"
    assert ch1["value"] == "+0.000V"


    # Validación (canal inválido)
    with pytest.raises(CommandError):
        graphtec.set_trigger_channel(9, "OFF", "+0.000V")


def test_logic_api(graphtec, conn):
    graphtec.connect()

    # Getters
    assert graphtec.get_logic_type() == "LOGI"
    assert graphtec.get_logic(1) == "OFF"
    assert graphtec.get_logic(4) == "OFF"

    logics = graphtec.get_logics()
    assert set(logics.keys()) == {1, 2, 3, 4}
    assert logics[1]["type"] == "LOGI"
    assert logics[1]["logic"] == "OFF"

    # Setters -> comandos enviados
    graphtec.set_logic_type("PULSE")
    graphtec.set_logic(1, "ON")

    assert ":LOGIPUL:FUNC PULSE" in conn.sent_commands
    assert ":LOGIPUL:CH1:FUNC ON" in conn.sent_commands


def test_alarm_api(graphtec, conn):
    graphtec.connect()

    # Getters (respuestas mockeadas)
    mode = graphtec.get_alarm()
    assert isinstance(mode, str)
    assert "LEVEL" in mode  # ":ALAR:FUNC LEVEL"

    level_ch2 = graphtec.get_alarm_level(2)
    assert isinstance(level_ch2, str)
    assert "OFF" in level_ch2

    # Setters -> comandos enviados
    graphtec.set_alarm("LEVEL")
    graphtec.set_alarm_level(2, "OFF", "+0.000V")

    assert ":ALAR:FUNC LEVEL" in conn.sent_commands
    assert ":ALAR:CH2:SET OFF,+0.000V" in conn.sent_commands


def test_data_api(graphtec, conn):
    graphtec.connect()

    # Getters (tu wrapper documenta int/str; aceptamos ambos)
    assert _last_token_as_int(graphtec.get_sampling()) == 500
    assert str(graphtec.get_capture_mode()).strip().endswith("CONT")

    # Setters -> comandos enviados (aunque tu responses no los necesite)
    graphtec.set_sampling(500)
    graphtec.set_capture_mode("CONT")

    assert ":DATA:SAMP 500" in conn.sent_commands
    assert ":DATA:CAPTM CONT" in conn.sent_commands
