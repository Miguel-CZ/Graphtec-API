from Graphtec.core.device.base import BaseModule
from Graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class DataModule(BaseModule):
    """Grupo DATA: Manejo de datos"""
    def set_data_location(self,location):
        self.connection.send(SET_DATA_LOCATION.format(location=location))
        logger.debug(f"[GL100Device] Localización cambiada a {location}")
    
    def set_data_destination(self,dest):
        self.connection.send(SET_DATA_DESTINATION.format(dest=dest))
        logger.debug(f"[GL100Device] Destino de datos cambiado a {dest}")
    
    def set_data_size(self,size):
        self.connection.send(SET_DATA_MEMORY_SIZE.format(size=size))
        logger.debug(f"[GL100Device] Tamaño de datos cambiado a {size}")
    
    def set_data_sampling(self,sample):
        self.connection.send(SET_DATA_SAMPLING.format(sample=sample))
        logger.debug(f"[GL100Device] Data Sample cambiado a {sample}")
    
    def set_data_submode(self,mode):
        self.connection.send(SET_DATA_SUB_MODE.format(mode=mode))
        logger.debug(f"[GL100Device] Data Sub-Mode cambiado a {mode}")

    def set_data_sub(self,status):
        self.connection.send(SET_DATA_SUB.format(status=status))
        logger.debug(f"[GL100Device] Estado del Data Sub: {status}")

    def set_data_capture_mode(self,mode):
        self.connection.send(SET_DATA_CAPTURE_MODE.format(mode=mode))
        logger.debug(f"[GL100Device] Modo de captura: {mode}")
    
    def get_data_sampling(self):
        response = self.connection.query(GET_DATA_SAMPLING)
        response = response.decode().strip()
        return response
    
    def get_data_memory_size(self):
        response = self.connection.query(GET_DATA_MEMORY_SIZE)
        response = response.decode().strip()
        return response
    
    def get_data_destination(self):
        response = self.connection.query(GET_DATA_DESTINATION)
        response = response.decode().strip()
        return response
    
    def get_data_points(self):
        response = self.connection.query(GET_DATA_POINTS)
        response = response.decode().strip()
        return response
    
    def get_data_capture_mode(self):
        response = self.connection.query(GET_DATA_CAPTURE_MODE)
        response = response.decode().strip()
        return response
    
    def get_data_capture_state(self):
        response = self.connection.query(GET_DATA_CAPTURE_STATE)
        response = response.decode().strip()
        return response

    def get_data_sub_mode(self):
        response = self.connection.query(GET_DATA_SUB_MODE)
        response = response.decode().strip()
        return response