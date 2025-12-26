from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
import logging

logger = logging.getLogger(__name__)


class FileModule(BaseModule):
    """Grupo FILE: Gestión de ficheros"""

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    # -------------------------
    # LISTADO
    # -------------------------
    def file_ls(self):
        """Devuelve el listado según el formato/filtro configurados en el equipo."""
        return self._to_str(self.connection.query(FILE_LS))

    def file_ls_number(self):
        """Devuelve el número de archivos (según SD/MEM y ruta actual)."""
        return self._to_str(self.connection.query(FILE_LS_NUM))

    def set_ls_format(self, fmt: str):
        # LONG / SHORT
        fmt = fmt.upper()
        options = {"LONG", "SHORT"}
        if fmt not in options:
            raise CommandError(f"format inválido: {fmt} (válidos: {sorted(options)})")
        self.connection.send(FILE_LS_FORMAT.format(format=fmt))
        logger.debug(f"[GL-FILE] LIST FORM -> {fmt}")

    def get_ls_format(self):
        return self._to_str(self.connection.query(GET_LS_FORMAT))

    def set_ls_filter(self, extension: str):
        """
        Filtra por extensión: 'TXT', 'GBD', etc.
        Usa 'OFF' para desactivar filtro.
        """
        extension = extension.upper()
        # No fuerzo lista cerrada porque depende de formatos reales
        if not extension:
            raise CommandError("extension no puede ser vacío (usa 'OFF' para desactivar)")
        self.connection.send(FILE_LS_FILTER.format(extension=extension))
        logger.debug(f"[GL-FILE] LIST FILT -> {extension}")

    def get_ls_filter(self):
        return self._to_str(self.connection.query(GET_LS_FILTER))

    # -------------------------
    # RUTAS / DIRECTORIOS
    # -------------------------
    def file_cd(self, dirpath: str = "."):
        self.connection.send(FILE_CD.format(dirpath=dirpath))
        logger.debug(f"[GL-FILE] CD -> {dirpath}")

    def file_pwd(self):
        resp = self._to_str(self.connection.query(FILE_PWD))
        if not resp:
            raise ResponseError("Sin respuesta a :FILE:CD?")
        logger.debug(f"[GL-FILE] PWD -> {resp}")
        return resp

    def file_mkdir(self, dirpath: str):
        if not dirpath:
            raise CommandError("dirpath no puede ser vacío")
        self.connection.send(FILE_MKDIR.format(dirpath=dirpath))
        logger.debug(f"[GL-FILE] MD -> {dirpath}")

    def file_rmdir(self, dirpath: str):
        if not dirpath:
            raise CommandError("dirpath no puede ser vacío")
        self.connection.send(FILE_RMDIR.format(dirpath=dirpath))
        logger.debug(f"[GL-FILE] RD -> {dirpath}")

    # -------------------------
    # FICHEROS
    # -------------------------
    def file_rm(self, filepath: str):
        if not filepath:
            raise CommandError("filepath no puede ser vacío")
        self.connection.send(FILE_RM.format(filepath=filepath))
        logger.debug(f"[GL-FILE] RM -> {filepath}")

    def file_cp(self, file_source: str, file_dest: str):
        if not file_source or not file_dest:
            raise CommandError("file_source y file_dest no pueden ser vacíos")
        self.connection.send(FILE_CP.format(file_source=file_source, file_dest=file_dest))
        logger.debug(f"[GL-FILE] CP -> {file_source} -> {file_dest}")

    def file_mv(self, file_source: str, file_dest: str):
        if not file_source or not file_dest:
            raise CommandError("file_source y file_dest no pueden ser vacíos")
        self.connection.send(FILE_MV.format(file_source=file_source, file_dest=file_dest))
        logger.debug(f"[GL-FILE] MV -> {file_source} -> {file_dest}")

    def get_free_space(self):
        """Devuelve el espacio libre (bytes) según el equipo."""
        return self._to_str(self.connection.query(FILE_SPACE))

    # -------------------------
    # SAVE/LOAD CONFIG (según tus comandos FILE_SAVE/FILE_LOAD)
    # -------------------------
    def save_file_settings(self, filepath: str):
        if not filepath:
            raise CommandError("filepath no puede ser vacío")
        self.connection.send(FILE_SAVE.format(filepath=filepath))
        logger.debug(f"[GL-FILE] SAVE -> {filepath}")

    def load_file_settings(self, filepath: str):
        if not filepath:
            raise CommandError("filepath no puede ser vacío")
        self.connection.send(FILE_LOAD.format(filepath=filepath))
        logger.debug(f"[GL-FILE] LOAD -> {filepath}")
