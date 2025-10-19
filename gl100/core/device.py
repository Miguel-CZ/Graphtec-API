# gl100/core/device.py
from gl100.core.commands import *
from gl100.utils.log import logger
from connection.usb_connection import USBConnection
from connection.wlan_connection import WLANConnection


class GL100Device:
    """Control y configuración de parámetros del GL100."""
    def __init__(self, conn:USBConnection | WLANConnection):
        self.conn = conn
        self.channels = {}

        try:
            self.conn.send(NLCODE.format(eol="CR_LF"))
        except Exception as e:
            logger.error(f"[GL100 Device] Error al configurar eol: {e}")

    # =========================================================
    # Medición
    # =========================================================
    def start_measurement(self):
        logger.debug("Iniciando medición...")
        self.conn.send(START_MEASUREMENT)

    def stop_measurement(self):
        logger.debug("Deteniendo medición...")
        self.conn.send(STOP_MEASUREMENT)

    def get_measurement_status(self):
        return self.conn.query(GET_STATUS)

    # =========================================================
    # Configuración de canales
    # =========================================================
    def get_channel_info(self)->dict:
        self.channels.clear()
        for ch in range(1,5):
            self.conn.send(GET_INPUT_TYPE.format(ch=ch))
            input_type=self._get_last_token(self.conn.receive_until().decode())

            self.conn.send(GET_INPUT_RANGE.format(ch=ch))
            input_range=self._get_last_token(self.conn.receive_until().decode())

            self.channels[ch] = {
                "input": input_type,
                "range": input_range
            }
        return self.channels

    def set_channel_input(self, ch, mode):
        cmd = SET_INPUT_TYPE.format(ch=ch, mode=mode)

        self.conn.send(cmd)
    
    def get_channel_input(self, ch):
        self.conn.send(GET_INPUT_TYPE.format(ch=ch))
        input_type=self._get_last_token(self.conn.receive_until().decode())

        # Modificamos el estado interno con la consulta más reciente
        self.channels[ch]["input"]=input_type

        return input_type


    def set_channel_range(self, ch, value):
        cmd = SET_INPUT_RANGE.format(ch=ch, value=value)
        self.conn.send(cmd)

    def get_channel_type(self, ch):
        cmd = GET_CHANNEL_INFO.format(ch=ch)
        return self.conn.query(cmd)
    
    def _get_last_token(self,response: str | None)-> str:
            if response:
                response = response.replace(","," ").strip()
                parts = response.split()
                return parts[-1] if parts else ""
            else:
                return ""

    # =========================================================
    # Trigger
    # =========================================================
    def set_trigger_source(self, source):
        cmd = SET_TRIG_SOURCE.format(source=source)
        self.conn.send(cmd)

    def set_trigger_level(self, ch, value, edge="high"):
        cmd = SET_TRIG_LEVEL.format(ch=ch, value=value)
        self.conn.send(cmd)

    def get_trigger_status(self):
        return self.conn.query(":TRIG:COND?")

    # =========================================================
    # Alarma
    # =========================================================
    def set_alarm(self, ch, value, mode="high"):
        cmd = SET_ALARM_LEVEL.format(ch=ch, value=value)
        self.conn.send(cmd)

    def enable_alarm_output(self, enabled=True):
        state = "ON" if enabled else "OFF"
        cmd = ENABLE_ALARM_OUT.format(state=state)
        self.conn.send(cmd)

    def get_alarm_status(self):
        return self.conn.query(":ALAR:FUNC?")

    # =========================================================
    # Archivos
    # =========================================================
    def list_files(self, path="/"):
        return self.conn.query(LIST_FILES)

    def save_settings(self, filename):
        cmd = SAVE_SETTINGS.format(filename=filename)
        self.conn.send(cmd)

    def load_settings(self, filename):
        cmd = LOAD_SETTINGS.format(filename=filename)
        self.conn.send(cmd)

    def delete_file(self, filename):
        cmd = DELETE_FILE.format(filename=filename)
        self.conn.send(cmd)

    def get_free_space(self):
        return self.conn.query(GET_FREE_SPACE)

    # =========================================================
    # Sistema
    # =========================================================
    def get_datetime(self):
        return self.conn.query(GET_DATETIME)

    def set_datetime(self, dt):
        cmd = SET_DATETIME.format(datetime=dt)
        self.conn.send(cmd)

    def get_status_flags(self):
        return self.conn.query(GET_STATUS)

    def clear_status(self):
        self.conn.send(CLEAR_STATUS)

    def get_firmware_version(self):
        return self.conn.query(GET_IDN)

    def get_model_info(self):
        return self.conn.query(GET_IDN)
