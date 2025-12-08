from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
from graphtec.core.exceptions import (
    CommandError,
    ResponseError,
    ConnectionError,
    DataError,)
logger = logging.getLogger(__name__)

class CommonModule(BaseModule):
    """grupo COMMON: Comandos comunes"""
    
    def __init__(self,device):
        super().__init__(device)
        self.equipo = {
            "fabricante": "",
            "dispositivo": "",
            "id": "",
            "firmware": ""
        }
        logger.debug("[GL-COMMON] Módulo común inicializado.")


    def get_id(self):
        try:
            response = self.connection.query(GET_IDN)
            if not response:
                raise ResponseError("Sin respuesta del GL100 al comando ID.")
            
            response = response.decode().strip().split(' ',1)[1]
            valores = response.split(',')

            self.equipo={
                "fabricante": valores[0],
                "dispositivo": valores[1],
                "id": valores[2],
                "firmware": valores[3]
                }
            logger.debug("[GL-COMMON] Consulta ID realizada")
            return self.equipo
        
        except Exception as e:
            logger.error(f"[GL-COMMON] Error al consultar ID: {e}")
            raise CommandError(f"Error ejecutando *IDN?: {e}") from e
        
    def clear(self):
        """Limpia el estado interno (errores, buffers, etc)"""
        self.connection.send(CLEAR)
        logger.debug("[GL-COMMON] Estado Interno Limpiado")

    def save_settings(self): 
        self.connection.send(SAVE_SETTINGS)
        logger.debug("[GL-COMMON] Configuración guardada")
    
    