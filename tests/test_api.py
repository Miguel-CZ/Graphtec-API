import pytest
from gl100.api.public import GL100

def test_connect_disconnect():
    gl = GL100(conn_type="usb")
    gl.connect()
    assert gl.conn.opened
    gl.disconnect()
    assert gl.conn.closed

def test_sampling_methods():
    gl = GL100()
    gl.connect()
    gl.set_sampling_interval("1s")
    gl.get_sampling_interval()
    gl.disconnect()

def test_measurement_cycle():
    gl = GL100()
    gl.connect()
    gl.start_measurement()
    gl.stop_measurement()
    gl.disconnect()

def test_read_realtime():
    gl = GL100()
    gl.connect()
    data = gl.read_realtime()
    assert "CH1" in data and isinstance(data["CH1"], float)
    gl.disconnect()

def test_download_captured_data(tmp_path):
    gl = GL100()
    gl.connect()
    output = tmp_path / "capture"
    path = gl.download_captured_data(str(output))
    assert "fake_download" in path
    gl.disconnect()

def test_trigger_and_alarm_methods():
    gl = GL100()
    gl.connect()
    gl.set_trigger_source("AMP")
    gl.set_trigger_level(1, 5.0, "high")
    gl.get_trigger_status()
    gl.set_alarm(1, 10.0, "low")
    gl.enable_alarm_output(True)
    gl.get_alarm_status()
    gl.disconnect()

def test_file_operations():
    gl = GL100()
    gl.connect()
    gl.list_files("/")
    gl.save_settings("test.cfg")
    gl.load_settings("test.cfg")
    gl.delete_file("test.cfg")
    gl.get_free_space()
    gl.disconnect()

def test_network_and_system_options():
    gl = GL100()
    gl.connect()
    gl.get_ip()
    gl.set_ip("192.168.0.10", "255.255.255.0", "192.168.0.1")
    gl.enable_dhcp(True)
    gl.wifi_connect("TestSSID", "password")
    gl.get_signal_strength()
    gl.reset_factory()
    gl.set_datetime("2025-10-18 12:00:00")
    gl.get_datetime()
    gl.set_temperature_unit("C")
    gl.set_device_name("TestGL100")
    gl.disconnect()

def test_status_info_methods():
    gl = GL100()
    gl.connect()
    gl.get_status_flags()
    gl.get_battery_level()
    gl.get_firmware_version()
    gl.get_model_info()
    gl.clear_status()
    gl.disconnect()
