from graphtec.core.device.base import BaseModule
from graphtec.core.commands import ALARM
from graphtec.core.exceptions import *
from graphtec.utils.utils import get_last_token,validate_channel,to_str
import logging
from types import MappingProxyType

logger = logging.getLogger(__name__)


class AlarmModule(BaseModule):
    """Grupo ALARM: Configuración y lectura de alarmas"""

    # =========================================================
    # MAPEO
    # =========================================================
    HIGH_LOW_MAP = MappingProxyType({
        "H":"HI", "HI":"HI", "HIGH":"HI",
        "L":"LO", "LO":"LO", "LOW":"LO",
        "OFF":"OFF","NONE":"OFF",
    })

    # =========================================================
    # SETTERS
    # =========================================================
    def set_alarm_mode(self, mode: str):
        # mode: LEVEL / OFF
        #TODO: Comprobar tipos (Mapeo con constante?)
        mode = mode.upper()
        mode_options = {"LEVEL", "OFF"}

        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(ALARM.SET_ALARM_MODE.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm FUNC -> {mode}")

    def set_alarm_level(self, channel:int, mode: str, level):
        """
        mode: HIGH / LOW / OFF
        level: valor numérico/umbral (según el equipo)
        """

        channel = validate_channel(channel)

        mode = mode.strip().upper()
        mode_normalized = self.HIGH_LOW_MAP.get(mode)

        if mode_normalized is None:
            raise ValueError(f"Modo inválido: {mode}. (válidos: {sorted(set(self.HIGH_LOW_MAP.values()))}")

        mode_options = {"HI", "LO", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        if level is None:
            raise CommandError("level no puede ser None")

        self.connection.send(ALARM.SET_ALARM_LEVEL.format(ch=channel, mode=mode, level=level))
        logger.debug(f"[GL-ALARM] Alarm CH{channel} SET -> mode={mode}, level={level}")

    def set_alarm_output(self, mode: str):
        # mode: ON / OFF
        mode = mode.upper()
        mode_options = {"ON", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(ALARM.SET_ALARM_OUTPUT.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm OUTP -> {mode}")

    def set_alarm_exec(self, mode: str):
        # mode: ON / OFF
        mode = mode.upper()
        mode_options = {"ON", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_ALARM.format(mode=mode))
        logger.debug(f"[GL-ALARM] Alarm EXEC -> {mode}")

    # =========================================================
    # GETTERS
    # =========================================================
    def get_alarm_status(self, ch):
        ch = validate_channel(ch)
        return to_str(self.connection.query(GET_ALARM_STATUS.format(ch=ch)))

    def get_alarm_mode(self):
        return to_str(self.connection.query(GET_ALARM_MODE))

    def get_alarm_level(self, ch):
        ch = validate_channel(ch)
        return to_str(self.connection.query(GET_ALARM_LEVEL.format(ch=ch)))

    def get_alarm_exec(self):
        return to_str(self.connection.query(GET_ALARM))

    def get_alarm_output(self):
        return to_str(self.connection.query(GET_ALARM_OUTPUT))
