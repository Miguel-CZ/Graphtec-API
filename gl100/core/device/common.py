from gl100.core.device.base import BaseModule
from gl100.core.commands import *
from gl100.utils.logger import logger
from gl100.core.exceptions import (
    CommandError,
    ResponseError,
    ConnectionError,
    DataError,
)

class CommonModule(BaseModule):
    """grupo COMMON: Comandos comunes"""
    def get_id(self):
        try:
            response = self.connection.query(GET_IDN)
            if not response:
                raise ResponseError("Sin respuesta del GL100 al comando ID.")
            
            response = response.decode().strip()
            logger.debug("[GL100Device] Consulta ID realizada")
            return response
        except Exception as e:
            logger.error(f"[GL100Device] Error al consultar ID: {e}")
            raise CommandError("Error ejecutando *IDN?") from e

    
    def get_system_info(self):
        response = self.connection.query(GET_SYSTEM_INFO)
        response = response.decode().strip()
        logger.debug("[GL100Device] Consulta información del sistema realizada")
        return response
    
    def get_device_state(self):
        response = self.connection.query(GET_GENERAL_STATUS)
        response = response.decode().strip()
        logger.debug("[GL100Device] Consulta Estado del dispositivo realizada")
        return response
    
    def get_device_info(self):
        model = self.connection.query(GET_MODEL).decode().strip()
        version = self.connection.query(GET_VERSION).decode().strip()
        serie = self.connection.query(GET_SERIES).decode().strip()
        info = {
            "modelo":model,
            "version":version,
            "serie":serie
        }
        logger.debug("[GL100Device] Modelo, versión y NºSerie obtenido")
        return info
    
    def clear(self):
        """Limpia el estado interno (errores, buffers, etc)"""
        self.connection.send(CLEAR)
        logger.debug("[GL100Device] Estado Interno Limpiado")

    def reset(self):
        self.connection.send(RESET_GENERAL)
        logger.debug("[GL100Device] Reseteo general")
    
    def save_settings(self): 
        self.connection.send(SAVE_SETTINGS)
        logger.debug("[GL100Device] Configuración guardada")
    
    