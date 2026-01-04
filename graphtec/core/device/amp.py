from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import *
from graphtec.utils.utils import get_last_token
import logging

logger = logging.getLogger(__name__)



class AmpModule(BaseModule):
    """Grupo AMP: Configuración de canales analógicos del GL100."""

    # Tipos de entrada disponibles por tipo de sensor
    TIPOS_ENTRADA = {
        "VT": ["OFF", "TEMP", "DC_V"], # Módulo GS-4VT
        "TSR": ["OFF", "TEMP"], # Módulo GS-4TSR
        "AC": ["AC1_2", "AC1_3", "AC3_3"], # Módulo GS-3AT
        "TH":[], # Módulo GS-TH
        "AT":[], # Módulo GS-AT
        "LU":[], # Módulo GS-LU
        "CO2":[], # Módulo GS-CO2
        "CO2_TH":[], # Módulo GS-CO2-TH
        "CO2_LU":[], # Módulo GS-CO2-LU
        "LU_TH":[] # Módulo GS-LU-TH
    }

    #Rangos compatibles por tipo de entrada
    RANGOS_COMPATIBLES = {
    "DC_V": ["NONE","20MV", "50MV", "100MV", "200MV", "500MV", "1V", "2V", "5V", "10V", "20V", "50V","1_5V"],
    "TEMP": ["NONE","TCK", "TCT"],
    "LXUV": ["NONE","2000LX", "20000LX","200000LX"],
    "ACC": ["NONE","2G", "5G", "10G","20MPSS","50MPSS","100MPSS"],
    "AC": ["OFF","50A", "100A", "200A"]
    }

    
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
            self.get_channel(ch)
        return self.channels
    
    def get_channel(self,channel:int) -> dict:
        ch_type = self.get_channel_type(channel)
        ch_input = self.get_channel_input(channel)
        ch_range = self.get_channel_range(channel)
        self.channels[channel]["type"] = ch_type
        self.channels[channel]["input"] = ch_input
        self.channels[channel]["range"] = ch_range
        logger.info(f"[GL-AMP] CH{channel} - TYPE: {ch_type}, INPUT: {ch_input}, RANGE: {ch_range}")
        return self.channels[channel]
    
    def get_channel_type(self,channel:int):
        cmd = GET_CHANNEL_TYPE.format(ch=channel)
        resp = self.connection.query(cmd)
        response = get_last_token(resp.decode().strip())
        return response
    
    def get_channel_input(self,channel:int):
        cmd = GET_CHANNEL_INPUT.format(ch=channel)
        resp = self.connection.query(cmd)
        response = get_last_token(resp.decode().strip())
        return response
    
    def get_channel_range(self,channel:int):
        cmd = GET_CHANNEL_RANGE.format(ch=channel)
        resp = self.connection.query(cmd)
        response = get_last_token(resp.decode().strip())
        return response

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================
    def set_channel(self, channel: int, ch_input: str, ch_range: str):
        if ch_input: 
            self.device.amp.set_channel_input(channel=channel,ch_input=ch_input)
        if ch_range:
            self.device.amp.set_channel_range(channel=channel,ch_range=ch_range)
        
        return self.device.amp.get_channel(channel)

    def set_channel_input(self, channel: int, ch_input: str):
        tipo_actual = self.channels[channel]["type"]
        # Si no hemos consultado tipo todavía, primero lo obtenenemos 
        if tipo_actual == "":
            tipo_actual = self.get_channel_type(channel)

        if self._validate_type(tipo_actual, ch_input):
            cmd = SET_CHANNEL_INPUT.format(ch=channel, mode=ch_input)
            self.connection.send(cmd)
            self.channels[channel]["input"] = ch_input
            logger.debug(f"[GL-AMP] CH{channel} INPUT ← {ch_input}")
        else:
            raise CommandError(f"Modo de entrada inválido para CH{channel}: {ch_input} no es compatible con el tipo {self.channels[channel]['type']}")

    def set_channel_range(self, channel: int, ch_range: str):
        modo_actual = self.channels[channel]["input"]
        # Si no hemos consultado el modo todavía, primero lo obtenenemos 
        if modo_actual == "":
            modo_actual = self.get_channel_input(channel)
        
        if self._validate_range(modo_actual, ch_range):
            cmd = SET_CHANNEL_RANGE.format(ch=channel, value=ch_range)
            self.connection.send(cmd)
            self.channels[channel]["range"] = ch_range
            logger.debug(f"[GL-AMP] CH{channel} RANGE ← {ch_range}")
        else:
            raise CommandError(f"Configuración inválida para CH{channel}: {modo_actual} no es compatible con {ch_range}")
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
    
    def _validate_range(self, mode: str, value: str):
        """Verifica si el rango es compatible con el tipo de entrada."""
        if mode in self.RANGOS_COMPATIBLES:
            if value not in self.RANGOS_COMPATIBLES[mode]:
                logger.error(f"[GL-AMP] Error: {value} no es compatible con el modo {mode}")
                return False
        return True
    
    def _validate_type(self, ch_type: str, ch_input: str):
        """Verifica si el tipo de entrada es compatible con el tipo de sensor."""
        if ch_type in self.TIPOS_ENTRADA:
            if ch_input not in self.TIPOS_ENTRADA[ch_type]:
                logger.error(f"[GL-AMP] Error: {ch_input} no es compatible con el tipo {ch_type}")
                return False
        return True