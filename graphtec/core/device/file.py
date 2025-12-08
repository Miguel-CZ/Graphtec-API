from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class FileModule(BaseModule):
    """Grupo FILE: Gestión de Ficheros"""
    def file_ls(self,text_filter=""):
        if not text_filter:
            response = self.connection.query(FILE_LS)
        else: 
            response = self.connection.query(FILE_LS_FILTER.format(pattern=text_filter))

        response = response.decode().strip()
        return response
    
    def file_ls_number(self):
        response = self.connection.query(FILE_LS_NUM)
        response = response.decode().strip()
        return response
    
    def file_cd(self,path="."):
        self.connection.send(FILE_CD.format(path=path))
        logger.debug(f"[GL100Device] Directorio cambiado a {path}")
    
    def file_pwd(self):
        response = self.connection.query(FILE_PWD)
        response = response.decode().strip()
        logger.debug(f"[GL100Device] Directorio actual {response}")
        return response
    
    def file_mkdir(self,path):
        self.connection.send(FILE_MKDIR.format(path=path))
        logger.debug(f"[GL100Device] Directorio creado: {path}")

    def file_rmdir(self,path):
        self.connection.send(FILE_RMDIR.format(path=path))
        logger.debug(f"[GL100Device] Directorio creado: {path}")
    
    def file_rm(self,filename):
        self.connection.send(FILE_RM.format(filename=filename))
        logger.debug(f"[GL100Device] Directorio creado: {filename}")

    def file_cp(self,filename,copyname):
        self.connection.send(FILE_CP.format(filename=filename,copyname=copyname))
        logger.debug(f"[GL100Device] {filename} copiado en {copyname}")
    
    def file_mv(self,filepath,new_path):
        self.connection.send(FILE_MV.format(filepath=filepath,new_path=new_path))
        logger.debug(f"[GL100Device] {filepath} se ha movido a {new_path}")
    
    def get_free_space(self):
        response = self.connection.query(FILE_SPACE)
        response = response.decode().strip()
        return response
    
    def save_file_settings(self,filename):
        self.connection.send(SAVE_FILE_SETTINGS.format(filename=filename))
        logger.debug(f"[GL100Device] Se ha guardado la configuración en {filename}")
    
    def load_file_settings(self,filename):
        self.connection.send(LOAD_FILE_SETTINGS.format(filename=filename))
        logger.debug(f"[[GL100Device] Se ha cargado la configuración en {filename}]")