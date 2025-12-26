from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
from graphtec.utils import get_last_token
import logging

logger = logging.getLogger(__name__)


class OptionModule(BaseModule):
    """Grupo OPT: Opciones"""

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    # -------------------------
    # SETTERS
    # -------------------------
    def set_name(self, name: str):
        if name is None or str(name).strip() == "":
            raise CommandError("name no puede ser vacío")

        # Tu comentario sugiere que el equipo quiere comillas. Las aseguro.
        name_str = str(name).strip()
        if not (name_str.startswith('"') and name_str.endswith('"')):
            name_str = f'"{name_str}"'

        self.connection.send(SET_NAME.format(name=name_str))
        logger.debug(f"[GL-OPT] Nombre del dispositivo cambiado a {name_str}")

    def set_datetime(self, dt_str: str):
        # Formato: YYYY/MM/DD,hh:mm:ss
        if not dt_str or str(dt_str).strip() == "":
            raise CommandError("datetime no puede ser vacío (esperado YYYY/MM/DD,hh:mm:ss)")

        self.connection.send(SET_DATETIME.format(datetime=dt_str))
        logger.debug(f"[GL-OPT] Fecha y hora cambiada a {dt_str}")

    def set_screen_save(self, time: str):
        # time: OFF/1/2/5/10/20/30/60 (MIN)
        time_str = str(time).upper()
        options = {"OFF", "1", "2", "5", "10", "20", "30", "60"}
        if time_str not in options:
            raise CommandError(f"time inválido: {time_str} (válidos: {sorted(options)})")

        self.connection.send(SET_SCREEN_SAVE.format(time=time_str))
        logger.debug(f"[GL-OPT] Screensaver (SCREENS) -> {time_str}")

    def set_temp_unit(self, unit: str):
        # CELS/FAHR
        unit = unit.upper()
        options = {"CELS", "FAHR"}
        if unit not in options:
            raise CommandError(f"unit inválido: {unit} (válidos: {sorted(options)})")

        self.connection.send(SET_TEMP_UNIT.format(unit=unit))
        logger.debug(f"[GL-OPT] Unidad de temperatura -> {unit}")

    def set_burnout(self, mode: str):
        # ON/OFF
        mode = mode.upper()
        options = {"ON", "OFF"}
        if mode not in options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(options)})")

        self.connection.send(SET_BURNOUT.format(mode=mode))
        logger.debug(f"[GL-OPT] Burnout -> {mode}")

    def set_acc_unit(self, unit: str):
        # G/MPSS
        unit = unit.upper()
        options = {"G", "MPSS"}
        if unit not in options:
            raise CommandError(f"unit inválido: {unit} (válidos: {sorted(options)})")

        self.connection.send(SET_ACC_UNIT.format(unit=unit))
        logger.debug(f"[GL-OPT] Unidad de aceleración -> {unit}")

    def set_room_temp(self, mode: str):
        # ON/OFF
        mode = mode.upper()
        options = {"ON", "OFF"}
        if mode not in options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(options)})")

        self.connection.send(SET_ROOM_TEMP.format(mode=mode))
        logger.debug(f"[GL-OPT] Room Temp correction -> {mode}")

    # -------------------------
    # GETTERS
    # -------------------------
    def get_name(self):
        text = self._to_str(self.connection.query(GET_NAME))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:NAME?")

        # Si viene con comillas, las quitamos
        value = get_last_token(text).strip()
        return value.strip('"')

    def get_datetime(self):
        # Probable respuesta tipo ":OPT:DATE 2025/12/21,10:20:30"
        text = self._to_str(self.connection.query(GET_DATETIME))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:DATE?")

        value = get_last_token(text)
        return value.strip('"')

    def get_screen_save(self):
        text = self._to_str(self.connection.query(GET_SCREEN_SAVE))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:SCREENS?")
        return get_last_token(text)

    def get_temp_unit(self):
        text = self._to_str(self.connection.query(GET_TEMP_UNIT))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:TUNIT?")
        return get_last_token(text)

    def get_room_temp(self):
        text = self._to_str(self.connection.query(GET_ROOM_TEMP))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:TEMP?")
        return get_last_token(text)

    def get_burnout(self):
        text = self._to_str(self.connection.query(GET_BURNOUT))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:BURN?")
        return get_last_token(text)

    def get_acc_unit(self):
        text = self._to_str(self.connection.query(GET_ACC_UNIT))
        if not text:
            raise ResponseError("Sin respuesta a :OPT:ACCUNIT?")
        return get_last_token(text)

    
    