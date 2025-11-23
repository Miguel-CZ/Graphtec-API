from Graphtec.core.device.base import BaseModule
from Graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class StatusModule(BaseModule):
    # =========================================================
    # STATUS: Estado del dispositivo
    # =========================================================
    def get_power_voltage(self):
        response = self.connection.query(GET_POWER_VOLTAGE)
        response = response.decode().strip()
        return response
    
    def get_power_source(self):
        response = self.connection.query(GET_POWER_SOURCE)
        response = response.decode().strip()
        return response
    
    def get_power_status(self):
        response = self.connection.query(GET_POWER_STATUS)
        response = response.decode().strip()
        return response
    
    def get_status(self):
        response = self.connection.query(GET_STATUS)
        response = response.decode().strip()
        return response
    
    def get_info(self):
        response = self.connection.query(GET_INFO)
        response = response.decode().strip()
        return response
    
    def get_communication_status(self):
        response = self.connection.query(GET_COM_STATUS)
        response = response.decode().strip()
        return response
    
    def get_sensor_status(self):
        response = self.connection.query(GET_SENSOR_STATUS)
        response = response.decode().strip()
        return response
    
    def get_error_status(self):
        response = self.connection.query(GET_ERROR_STATUS)
        response = response.decode().strip()
        return response