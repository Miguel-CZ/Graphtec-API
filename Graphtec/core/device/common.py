from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)
from graphtec.core.exceptions import (
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
            raise CommandError(f"Error ejecutando *IDN?: {e}") from e
        
    def clear(self):
        """Limpia el estado interno (errores, buffers, etc)"""
        self.connection.send(CLEAR)
        logger.debug("[GL100Device] Estado Interno Limpiado")

    def save_settings(self): 
        self.connection.send(SAVE_SETTINGS)
        logger.debug("[GL100Device] Configuración guardada")
    
    