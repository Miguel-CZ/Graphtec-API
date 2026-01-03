from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging

logger = logging.getLogger(__name__)


class AmpModule(BaseModule):
    """Grupo AMP: Configuración de canales analógicos del GL100."""

    def __init__(self, device):
        super().__init__(device)
        self.channels = {ch: {"type": "", "input": "", "range": ""} for ch in range(1, 5)}
        logger.debug("[GL-AMP] Módulo de canales inicializado.")

    # =========================================================
    # CONSULTAS
    # =========================================================

    def get_channels(self) -> dict:
        """Devuelve la configuración actual de todos los canales."""
        for ch in range(1, 5):  
            ch_type = self.get_channel_type(ch)
            ch_input = self.get_channel_input(ch)
            ch_range = self.get_channel_range(ch)
            self.channels[ch]["type"] = ch_type
            self.channels[ch]["input"] = ch_input
            self.channels[ch]["range"] = ch_range
            logger.info(f"[GL-AMP] CH{ch} - TYPE: {ch_type}, INPUT: {ch_input}, RANGE: {ch_range}")
        return self.channels
    
    def get_channel_type(self,channel:int):
        cmd = GET_CHANNEL_TYPE.format(ch=channel)
        resp = self.connection.query(cmd)
        response = self._get_last_token(resp.decode().strip())
        return response
    
    def get_channel_input(self,channel:int):
        cmd = GET_CHANNEL_INPUT.format(ch=channel)
        resp = self.connection.query(cmd)
        response = self._get_last_token(resp.decode().strip())
        return response
    
    def get_channel_range(self,channel:int):
        cmd = GET_CHANNEL_RANGE.format(ch=channel)
        resp = self.connection.query(cmd)
        response = self._get_last_token(resp.decode().strip())
        return response

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================
    def set_channel_type(self, channel: int, ch_type: str):
        cmd = SET_CHANNEL_TYPE.format(ch=channel, ch_type=ch_type)
        self.connection.send(cmd)
        self.channels[channel]["type"] = ch_type
        logger.debug(f"[GL-AMP] CH{channel} TYPE ← {ch_type}")

    def set_channel_input(self, channel: int, ch_input: str):
        cmd = SET_CHANNEL_INPUT.format(ch=channel, mode=ch_input)
        self.connection.send(cmd)
        self.channels[channel]["input"] = ch_input
        logger.debug(f"[GL-AMP] CH{channel} INPUT ← {ch_input}")

    def set_channel_range(self, channel: int, ch_range: str):
        cmd = SET_CHANNEL_RANGE.format(ch=channel, value=ch_range)
        self.connection.send(cmd)
        self.channels[channel]["range"] = ch_range
        logger.debug(f"[GL-AMP] CH{channel} RANGE ← {ch_range}")

    # =========================================================
    # UTILIDAD INTERNA
    # =========================================================
    def _get_last_token(self, response: str | None) -> str:
        """Devuelve el último token no vacío de una respuesta SCPI."""
        if not response:
            return ""
        response = response.replace(",", " ").replace(":", " ").replace('"', "").strip()
        parts = response.split()
        return parts[-1] if parts else ""
