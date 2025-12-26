from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
from graphtec.utils import get_last_token
import logging

logger = logging.getLogger(__name__)


class LogicModule(BaseModule):
    """Grupo LOGIPUL: Gestión de lógicas/pulsos"""

    def __init__(self, device):
        super().__init__(device)
        self.logics = {ch: {"type": "", "logic": ""} for ch in range(1, 5)}
        logger.debug("[GL-LOGIC] Módulo de lógicas inicializado.")

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _to_str(response):
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
        if ch_int not in (1, 2, 3, 4):
            raise CommandError(f"Canal inválido: {ch_int} (válidos: 1..4)")
        return ch_int

    # -------------------------
    # SETTERS
    # -------------------------
    def set_logic_type(self, mode: str):
        # mode: LOGI / PULSE / OFF
        mode = mode.upper()
        mode_options = {"LOGI", "PUL", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_LOGIC_TYPE.format(mode=mode))
        logger.debug(f"[GL-LOGIC] Tipo global LOGIPUL -> {mode}")

    def set_logic(self, ch, mode: str):
        # mode: ON / INST / COUNT / OFF
        ch = self._validate_channel(ch)

        mode = mode.upper()
        mode_options = {"ON", "INST", "COUNT", "OFF"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_LOGIC.format(ch=ch, mode=mode))
        logger.debug(f"[GL-LOGIC] Canal {ch} FUNC -> {mode}")

    # -------------------------
    # GETTERS
    # -------------------------
    def get_logic_type(self):
        resp = self.connection.query(GET_LOGIC_TYPE)
        text = self._to_str(resp)
        if not text:
            raise ResponseError("Sin respuesta a :LOGIPUL:FUNC?")
        return get_last_token(text)

    def get_logic(self, ch):
        ch = self._validate_channel(ch)
        resp = self.connection.query(GET_LOGIC.format(ch=ch))
        text = self._to_str(resp)
        if not text:
            raise ResponseError(f"Sin respuesta a :LOGIPUL:CH{ch}:FUNC?")
        return get_last_token(text)

    def get_logics(self):
        # El tipo es global, no hace falta pedirlo 4 veces
        logic_type = self.get_logic_type()
        for ch in range(1, 5):
            self.logics[ch]["type"] = logic_type
            self.logics[ch]["logic"] = self.get_logic(ch)
        return self.logics
