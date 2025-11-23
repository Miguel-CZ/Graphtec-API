from Graphtec.core.device.base import BaseModule
from Graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class InterfaceModule(BaseModule):
    """Grupo IF: Interfaz"""
    def get_connection_version(self):
        response = self.connection.query(GET_CONN_VERSION)
        response = response.decode().strip()
        return response
    
    def get_connection_status(self):
        response = self.connection.query(GET_CONN_STATUS)
        response = response.decode().strip()
        return response
    
    def get_connection_type(self):
        response = self.connection.query(GET_CONN_TYPE)
        response = response.decode().strip()
        return response
    
    def get_connection_info(self):
        response = self.connection.query(GET_CONN_INFO)
        response = response.decode().strip()
        return response
    
    def reset_connection(self):
        self.connection.send(RESET_CONN)
        logger.debug("[GL100Device] Conexión reseteada")
    
    def set_nlcode(self,nlcode):
        self.connection.send(SET_CONN_NLCODE.format(code=nlcode))
        logger.debug(f"[GL100Device] NLCode cambiado a {nlcode}")

    def set_baudrate(self,baud):
        self.connection.send(SET_CONN_BAUDRATE.format(baud=baud))
        logger.debug(f"[GL100Device] Cambiado baudrate a {baud}")
    
    def set_parity(self,parity):
        self.connection.send(SET_CONN_PARITY.format(parity=parity))
        logger.debug(f"[GL100Device] Cambiado paridad a {parity}")
    
    def set_databits(self,n):
        self.connection.send(SET_CONN_DATABITS.format(n=n))
        logger.debug(f"[GL100Device] Cambiado Databits a {n}")

    def set_stopbits(self,n):
        self.connection.send(SET_CONN_STOPBITS.format(n=n))
        logger.debug(f"[GL100Device] Cambiado Stopbits a {n}")
    
    def set_flow(self,flow):
        self.connection.send(SET_CONN_FLOW.format(flow=flow))
        logger.debug(f"[GL100Device] Cambiado Flujo a {flow}")
    
    def set_timeout(self,timeout):
        self.connection.send(SET_CONN_TIMEOUT.format(timeout=timeout))
        logger.debug(f"[GL100Device] Cambiado Timeout a {timeout}")
    
    def get_nlcode(self):
        response = self.connection.query(GET_CONN_NLCODE)
        response = response.decode().strip()
        return response
    
    def get_baudrate(self):
        response = self.connection.query(GET_CONN_BAUDRATE)
        response = response.decode().strip()
        return response
    
    def get_parity(self):
        response = self.connection.query(GET_CONN_PARITY)
        response = response.decode().strip()
        return response
    
    def get_databits(self):
        response = self.connection.query(GET_CONN_DATABITS)
        response = response.decode().strip()
        return response
    
    def get_stopbits(self):
        response = self.connection.query(GET_CONN_DATABITS)
        response = response.decode().strip()
        return response
    
    def get_flow(self):
        response = self.connection.query(GET_CONN_FLOW)
        response = response.decode().strip()
        return response
    
    def get_timeout(self):
        response = self.connection.query(GET_CONN_TIMEOUT)
        response = response.decode().strip()
        return response