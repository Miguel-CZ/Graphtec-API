"""
GL100 API pública
-------------------------------------

Clase principal GL100 que encapsula todas las operaciones de alto nivel
para interactuar con un dispositivo Graphtec GL100.

Ejemplo básico:
    from gl100 import GL100

    gl = GL100(ip="192.168.0.10")
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()

Autor: Miguel Chen Zheng
"""

from gl100.core.connection import GL100Connection
from gl100.core.device import GL100Device
from gl100.io.realtime import GL100Realtime
from gl100.io.capture import GL100Capture
from gl100.utils.log import logger


class GL100:
    """
    Clase principal que encapsula todas las operaciones de alto nivel
    para interactuar con un dispositivo Graphtec GL100.
    """

    # =========================================================
    # Inicialización
    # =========================================================
    def __init__(self, conn_type="usb", **kwargs):
        """
        Inicializa la instancia del GL100.

        Args:
            conn_type (str): Tipo de conexión. "usb" o "lan".
            **kwargs: Parámetros específicos del tipo de conexión.
                - USB: port, baudrate, timeout, etc.
                - LAN: address, tcp_port, timeout, etc.
        """
        self.conn_type = conn_type
        self.conn = GL100Connection(conn_type=conn_type, **kwargs)
        self.device = GL100Device(self.conn)
        self.realtime = GL100Realtime(self.conn)
        self.capture = GL100Capture(self.conn)
        self.connected = False

    # =========================================================
    # CONEXIÓN -> core/connection.py
    # =========================================================
    def connect(self):
        """Abre la conexión con el GL100."""
        self.conn.open()
        self.connected = True
        logger.info(f"[GL100] Conectado vía {self.conn_type.upper()}")

    def disconnect(self):
        """Cierra la conexión con el GL100."""
        if not self.connected:
            logger.warning("[GL100] Desconexión ignorada: no hay conexión activa.")
            return
        self.conn.close()
        self.connected = False
        logger.info("[GL100] Conexión cerrada correctamente.")

    def is_connected(self) -> bool:
        """Devuelve True si hay conexión activa."""
        return self.connected

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================
    def get_channels(self):
        """Devuelve la lista de canales activos detectados."""
        return self.device.get_channels()

    def set_channel_input(self, ch, mode):
        """Configura el tipo de entrada de un canal (DC_V, TEMP, OFF, etc.)."""
        return self.device.set_channel_input(ch, mode)

    def set_channel_range(self, ch, range_value):
        """Establece el rango de medida del canal especificado."""
        return self.device.set_channel_range(ch, range_value)

    def get_channel_type(self, ch):
        """Obtiene el tipo de sensor conectado al canal."""
        return self.device.get_channel_type(ch)

    def calibrate_sensor(self, ch, sensor_type):
        """Ejecuta una calibración para un sensor específico (ACC, CO2, etc.)."""
        return self.device.calibrate_sensor(ch, sensor_type)

    # =========================================================
    # MEDICIÓN / ADQUISICIÓN
    # =========================================================
    def set_sampling_interval(self, value="1s"):
        """Define el intervalo de muestreo del dispositivo."""
        return self.device.set_sampling_interval(value)

    def get_sampling_interval(self):
        """Obtiene el intervalo de muestreo actual."""
        return self.device.get_sampling_interval()

    def start_measurement(self):
        """Inicia una medición continua o programada."""
        return self.device.start_measurement()

    def stop_measurement(self):
        """Detiene la medición en curso."""
        return self.device.stop_measurement()

    def get_measurement_status(self):
        """Devuelve el estado actual de medición (STOP, REC, ARMED)."""
        return self.device.get_measurement_status()

    def read_realtime(self):
        """
        Lee los datos actuales del GL100.
        Devuelve un diccionario o DataFrame con valores decodificados.
        """
        return self.realtime.read()

    def capture_to_file(self, filename):
        """Realiza una captura manual de datos y la guarda en el medio interno."""
        return self.capture.capture_to_file(filename)

    def download_captured_data(self, dest, start=None, end=None):
        """Descarga datos guardados en memoria interna o SD al PC."""
        return self.capture.download(dest, start, end)

    # =========================================================
    # TRIGGERS
    # =========================================================
    def set_trigger_source(self, source="AMP"):
        """Configura la fuente del trigger (AMP, DATE, ALARM, OFF)."""
        return self.device.set_trigger_source(source)

    def set_trigger_level(self, ch, level, edge="high"):
        """Define el nivel y tipo de disparo para un canal."""
        return self.device.set_trigger_level(ch, level, edge)

    def get_trigger_status(self):
        """Consulta el estado del trigger actual."""
        return self.device.get_trigger_status()

    # =========================================================
    # ALARMAS
    # =========================================================
    def set_alarm(self, ch, level, mode="high"):
        """Configura el umbral de alarma en un canal."""
        return self.device.set_alarm(ch, level, mode)

    def enable_alarm_output(self, enabled=True):
        """Activa o desactiva la salida física de alarma."""
        return self.device.enable_alarm_output(enabled)

    def get_alarm_status(self):
        """Consulta el estado de las alarmas activas."""
        return self.device.get_alarm_status()

    # =========================================================
    # ARCHIVOS
    # =========================================================
    def list_files(self, path="/"):
        """Lista los archivos y carpetas del medio de almacenamiento."""
        return self.device.list_files(path)

    def save_settings(self, filename):
        """Guarda la configuración actual en un archivo dentro del GL100."""
        return self.device.save_settings(filename)

    def load_settings(self, filename):
        """Carga una configuración guardada."""
        return self.device.load_settings(filename)

    def delete_file(self, filename):
        """Elimina un archivo del almacenamiento."""
        return self.device.delete_file(filename)

    def get_free_space(self):
        """Consulta el espacio libre disponible."""
        return self.device.get_free_space()

    # =========================================================
    # RED / INTERFAZ
    # =========================================================
    def get_ip(self):
        """Obtiene la dirección IP actual."""
        return self.device.get_ip()

    def set_ip(self, ip, mask, gateway, dns=None):
        """Configura los parámetros de red manualmente."""
        return self.device.set_ip(ip, mask, gateway, dns)

    def enable_dhcp(self, enabled=True):
        """Activa o desactiva el modo DHCP."""
        return self.device.enable_dhcp(enabled)

    def wifi_connect(self, ssid, password):
        """Conecta el GL100 a una red Wi-Fi (solo modelo GL100-WL)."""
        return self.device.wifi_connect(ssid, password)

    def get_signal_strength(self):
        """Obtiene el nivel de señal Wi-Fi actual."""
        return self.device.get_signal_strength()

    # =========================================================
    # OPCIONES DEL SISTEMA
    # =========================================================
    def reset_factory(self):
        """Restaura la configuración de fábrica."""
        return self.device.reset_factory()

    def set_datetime(self, dt):
        """Establece la fecha y hora del GL100."""
        return self.device.set_datetime(dt)

    def get_datetime(self):
        """Obtiene la fecha y hora actual del GL100."""
        return self.device.get_datetime()

    def set_temperature_unit(self, unit="C"):
        """Configura la unidad de temperatura (C o F)."""
        return self.device.set_temperature_unit(unit)

    def set_device_name(self, name):
        """Asigna un nombre al dispositivo GL100."""
        return self.device.set_device_name(name)

    # =========================================================
    # ESTADO / INFORMACIÓN
    # =========================================================
    def get_status_flags(self):
        """Devuelve el estado global del GL100 (REC, ALM, SD, etc.)."""
        return self.device.get_status_flags()

    def get_battery_level(self):
        """Obtiene el nivel de batería (0–100%)."""
        return self.device.get_battery_level()

    def get_firmware_version(self):
        """Devuelve la versión del firmware actual."""
        return self.device.get_firmware_version()

    def get_model_info(self):
        """Obtiene información del modelo (GL100-N, GL100-WL, etc.)."""
        return self.device.get_model_info()

    def clear_status(self):
        """Borra los estados o errores actuales."""
        return self.device.clear_status()
