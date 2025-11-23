from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class LogicModule(BaseModule):
    """Grupo LOGIPUL: Gestión de lógicas/Pulsos"""
    def set_logic_all(self,mode):
        self.connection.send(SET_ALL_LOGIC.format(mode=mode))
        logger.debug(f"[GL100Device] Se han establecido todas las lógicas en: {mode}")
    
    def set_logic(self,ch,mode):
        self.connection.send(SET_LOGIC.format(ch=ch,mode=mode))
        logger.debug(f"[GL100Device] Lógica en Canal {ch} con modo {mode}")
    
    def get_logic_all(self):
        response = self.connection.query(GET_ALL_LOGIC)
        response = response.decode().strip()
        return response
    
    def get_logic(self,ch):
        response = self.connection.query(GET_LOGIC.format(ch=ch))
        response = response.decode().strip()
        return response
    