from gl100.core.device.base import BaseModule
from gl100.core.commands import *
from gl100.utils.logger import logger

class TransferModule(BaseModule):
    """Grupo TRANS: Manejo de la transferencia de datos"""
    def set_transfer_source(self,source,path):
        self.connection.send(SET_TRANS_SOURCE.format(source=source,path=path))
        logger.debug(f"[GL100Device] Fuente de transferencia: {source}/{path}")
    
    def open_transfer(self):
        self.connection.send(TRANS_OPEN)
        logger.debug(f"[GL100Device] Transferencia abierta")

    def get_transfer_header(self):
        response = self.connection.query(TRANS_SEND_HEADER)
        response = response.decode().strip()
        return response
    
    def get_transfer_size(self):
        response = self.connection.query(TRANS_SIZE)
        response = response.decode().strip()
        return response
    
    def set_transfer_data(self,start,end):
        self.connection.send(SET_TRANS_DATA.format(start=start,end=end))
        logger.debug(f"[GL100Device] Datos de transferencia cambiado a {start}/{end}")
    
    def get_transfer_data(self):
        response = self.connection.query(TRANS_SEND_DATA)
        response = response.decode().strip()
        return response
    
    def close_transfer(self):
        self.connection.send(TRANS_CLOSE)
        logger.debug(f"[GL100Device] Transferencia cerrada")