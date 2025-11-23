from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class MeasureModule(BaseModule):
    """Grupo MEAS: Ajustes de medición"""
    def start_measurement(self):
        self.connection.send(START_MEASUREMENT)
        logger.debug("[GL100Device] Iniciando medición...")

    def stop_measurement(self):
        self.connection.send(STOP_MEASUREMENT)
        logger.debug("[GL100Device] Medición detenida.")

    def read_one_measurement(self):
        response = self.connection.query(READ_ONCE)
        response = response
        return response
    
    def read_cont_measurement(self):
        response = self.connection.query(READ_CONT)
        response = response.decode().strip()
        return response
    
    def set_read_format(self,mode):
        self.connection.send(SET_MEAS_FORMAT.format(mode=mode))
        logger.debug(f"[GL100Device] Formato de medición cambiado a {mode}")

    def get_last_datetime(self):
        response = self.connection.query(GET_LAST_DATETIME)
        response = response.decode().strip()
        return response
    
    def get_capture_points(self):
        response = self.connection.query(GET_CAPTURE_POINTS)
        response = response.decode().strip()
        return response
    
    def get_headers(self):
        response = self.connection.query(GET_HEADERS)
        response = response.decode().strip()
        return response
    
    def get_data_format(self):
        response = self.connection.query(GET_DATA_FORMAT)
        response = response.decode().strip()
        return response
    
    