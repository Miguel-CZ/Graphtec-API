from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class AlarmModule(BaseModule):
    """Grupo ALM: Alarmas """
    def set_alarm(self,mode):
        self.connection.send(SET_ALARM.format(mode=mode))
        logger.debug(f"[GL100Device] Alarma {mode}")
    
    def set_alarm_mode(self,mode):
        self.connection.send(SET_ALARM_MODE.format(mode=mode))
        logger.debug(f"[GL100Device] Alarma en estado: {mode}")
    
    def set_alarm_level(self,ch,mode,level):
        self.connection.send(SET_ALARM_LEVEL.format(ch=ch,mode=mode,level=level))
        logger.debug(f"[GL100Device] Alarma {mode} en {level}")

    def get_alarm(self):
        response = self.connection.query(GET_ALARM)
        response = response.decode().strip()
        return response
    
    def get_alarm_mode(self):
        response = self.connection.query(GET_ALARM_MODE)
        response = response.decode().strip()
        return response
    
    def get_alarm_level(self,ch):
        response = self.connection.query(GET_ALARM_LEVEL.format(ch=ch))
        response = response.decode().strip()
        return response