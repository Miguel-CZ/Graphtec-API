from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.utils import get_last_token
import logging
logger = logging.getLogger(__name__)

class LogicModule(BaseModule):
    """Grupo LOGIPUL: Gestión de lógicas/Pulsos"""
    def __init__(self, device):
        super().__init__(device)
        self.logics = {ch:{"type":"","logic":""} for ch in range(1,5)}
        logger.debug("[GL-LOGIC] Módulo de lógicas inicializado.")


    def set_logic_type(self,mode):
        self.connection.send(SET_LOGIC_TYPE.format(mode=mode))
        logger.debug(f"[GL-LOGIC] Se han establecido todas las lógicas en: {mode}")
    
    def set_logic(self,ch,mode):
        self.connection.send(SET_LOGIC.format(ch=ch,mode=mode))
        logger.debug(f"[GL-LOGIC] Lógica en Canal {ch} con modo {mode}")
    
    def get_logic_type(self):
        response = self.connection.query(GET_LOGIC_TYPE)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_logic(self,ch):
        response = self.connection.query(GET_LOGIC.format(ch=ch))
        response = get_last_token(response.decode().strip())
        return response
    
    def get_logics(self):
        for ch in range(1,5):
            self.logics[ch]["type"] = self.get_logic_type()
            self.logics[ch]["logic"] = self.get_logic(ch)
        return self.logics