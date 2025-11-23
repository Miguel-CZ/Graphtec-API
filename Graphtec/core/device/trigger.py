from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class TriggerModule(BaseModule):
    """Grupo Trigger: """
    def set_trigger(self,status):
        self.connection.send(SET_TRIG_STATUS.format(status=status))
        logger.debug(f"[GL100Device] Se ha actualizado el trigger a {status}")

    def set_trigger_source(self, source,datetime=""):
        if source != "DATE":
            self.connection.send(SET_TRIG_SOURCE.format(source=source))
        else:
            self.connection.send(SET_TRIG_SOURCE_DATE.format(datetime=datetime))
        logger.debug(f"[GL100Device] Se ha actualizado el trigger-source a {source}")

    def set_trigger_comb(self,comb):
        self.connection.send(SET_TRIG_COMBINATION.format(comb=comb))
        logger.debug(f"[GL100Device] Trigger con {comb}")
    
    def set_trigger_channel(self,ch,mode,value=""):
        self.connection.send(SET_TRIG_CHANNEL.format(ch=ch,mode=mode,value=value))
        logger.debug(f"[GL100Device] Trigger de valor en canal {ch}")
    
    def set_pretrigger(self,level):
        self.connection.send(SET_TRIG_PRETRIGGER.format(level=level))
        logger.debug(f"[GL100Device] Pre-Trigger activado con {level}%")

    def get_trigger(self):
        response = self.connection.query(GET_TRIG_STATUS)
        response = response.decode().strip()
        return response
    
    def get_trigger_source(self):
        response = self.connection.query(GET_TRIG_SOURCE)
        response = response.decode().strip()
        return response
        
    def get_trigger_channel(self,ch):
        response = self.connection.query(GET_TRIG_CHANNEL.format(ch=ch))
        response = response.decode().strip()
        return response

    def get_pretrigger(self):
        response = self.connection.query(GET_TRIG_PRETRIGGER)
        response = response.decode().strip()
        return response
