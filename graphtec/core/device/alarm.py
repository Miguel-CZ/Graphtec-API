from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError
import logging

logger = logging.getLogger(__name__)


class AlarmModule(BaseModule):
    """Grupo ALARM: Configuración y lectura de alarmas"""

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _to_str(response):
        """Convierte la respuesta a str y la limpia."""
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    @staticmethod
    def _validate_channel(ch):
        try:
            ch_int = int(ch)
        except (TypeError, ValueError):
            raise CommandError(f"Canal inválido: {ch}")

        if ch_int <= 0:
            raise CommandError(f"Canal inválido: {ch_int} (debe ser > 0)")
        return ch_int

    # -------------------------
    # SETTERS
    # -------------------------
    def set_alarm_mode(self, mode: str):
        # mode: LEVEL / OFF
        mode = mode.upper()
        mode_options = {"LEVEL", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_ALARM_MODE.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm FUNC -> {mode}")

    def set_alarm_level(self, ch, mode: str, level):
        # mode: HIGH / LOW / OFF
        # level: valor numérico/umbral (según el equipo)
        ch = self._validate_channel(ch)

        mode = mode.upper()
        mode_options = {"HIGH", "LOW", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")
        
        if level is None:
            raise CommandError("level no puede ser None")

        self.connection.send(SET_ALARM_LEVEL.format(ch=ch, mode=mode, level=level))
        logger.debug(f"[GL-ALARM] Alarm CH{ch} SET -> mode={mode}, level={level}")

    def set_alarm_output(self, mode: str):
        # mode: ON / OFF
        mode = mode.upper()
        mode_options = {"ON", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_ALARM_OUTPUT.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm OUTP -> {mode}")

    def set_alarm_exec(self, mode: str):
        # mode: ON / OFF
        mode = mode.upper()
        mode_options = {"ON", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_ALARM.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm EXEC -> {mode}")

    # -------------------------
    # GETTERS
    # -------------------------
    def get_alarm_status(self, ch):
        ch = self._validate_channel(ch)
        return self._to_str(self.connection.query(GET_ALARM_STATUS.format(ch=ch)))

    def get_alarm_mode(self):
        return self._to_str(self.connection.query(GET_ALARM_MODE))

    def get_alarm_level(self, ch):
        ch = self._validate_channel(ch)
        return self._to_str(self.connection.query(GET_ALARM_LEVEL.format(ch=ch)))

    def get_alarm_exec(self):
        return self._to_str(self.connection.query(GET_ALARM))

    def get_alarm_output(self):
        return self._to_str(self.connection.query(GET_ALARM_OUTPUT))