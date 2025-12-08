from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.utils import get_last_token
import logging
logger = logging.getLogger(__name__)

class OptionModule(BaseModule):
    """Grupo OPT: Opciones"""

    def reset_fabric(self,option):
        self.connection.send(RESET_FABRIC.format(option=option))
        logger.debug(f"[GL-Options] Reseteo de fábrica {option}")
    
    def set_name(self,name):
        self.connection.send(SET_NAME.format(name=name))
        logger.debug(f"[GL-Options] Nombre del dispositivo cambiado a {name}")
    
    def set_datetime(self,datetime):
        #Formato YYYY/MM/DD,hh:mm:ss
        self.connection.send(SET_DATETIME.format(datetime=datetime))
        logger.debug(f"[GL-Options] Fecha y hora del dispositivo cambiada a {datetime}")

    def set_screen_eco(self,mode):
        self.connection.send(SET_SCREEN_ECO.format(mode=mode))
        logger.debug(f"[GL-Options] Modo ahorro de pantalla {mode}")
    
    def set_temp_unit(self,unit):
        self.connection.send(SET_TEMP_UNIT.format(unit=unit))
        logger.debug(f"[GL-Options] Unidad de temperatura {unit}")
    
    def set_room_temp(self,mode):
        #ON es INTERNO // OFF es Externo
        self.connection.send(SET_ROOM_TEMP.format(mode=mode))

    def set_burnout(self,mode):
        self.connection.send(SET_BURNOUT.format(mode=mode))
        logger.debug(f"[GL-Options] Modo burnout {mode}")
    
    def set_acc_unit(self,unit):
        self.connection.send(SET_ACC_UNIT.format(unit=unit))
        logger.debug(f"[GL-Options] Unidad de acelerómetro {unit}")

    def get_name(self):
        response = self.connection.query(GET_NAME)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_datetime(self):
        response = self.connection.query(GET_DATETIME)
        response = response.decode().strip().split(" ",1)[1]
        response = response.strip('"')
        return response
    
    def get_screen_eco(self):
        response = self.connection.query(GET_SCREEN_ECO)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_temp_unit(self):
        response = self.connection.query(GET_TEMP_UNIT)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_room_temp(self):
        response = self.connection.query(GET_ROOM_TEMP)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_burnout(self):
        response = self.connection.query(GET_BURNOUT)
        response = get_last_token(response.decode().strip())
        return response
    
    def get_acc_unit(self):
        response = self.connection.query(GET_ACC_UNIT)
        response = get_last_token(response.decode().strip())
        return response

    
    