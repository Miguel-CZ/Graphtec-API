from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError
import logging

logger = logging.getLogger(__name__)


class DataModule(BaseModule):
    """Grupo DATA: Manejo de datos"""

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _to_str(response):
        """Convierte la respuesta a str y la limpia."""
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    # -------------------------
    # SETTERS
    # -------------------------
    def set_data_location(self, location: str):
        # location: MEM para memoria, DIRE para directa
        location = location.upper()
        location_options = {"MEM", "DIRE"}
        if location not in location_options:
            raise CommandError(f"location inválido: {location} (válidos: {sorted(location_options)})")

        self.connection.send(SET_DATA_LOCATION.format(location=location))
        logger.debug(f"[GL-DATA] Localización cambiada a {location}")

    def set_data_mem_size(self, size):
        size_options = {"16", "32", "64", "128"}
        size_str = str(size)
        if size_str not in size_options:
             raise CommandError(f"size inválido: {size} (válidos: {sorted(size_options)})")

        self.connection.send(SET_DATA_MEMORY_SIZE.format(size=size))
        logger.debug(f"[GL-DATA] Tamaño de memoria cambiada a {size}")

    def set_data_destination(self, dest: str):
        # dest: MEM para memoria / SD para tarjeta SD
        dest = dest.upper()
        dest_options = {"MEM", "SD"}
        if dest not in dest_options:
            raise CommandError(f"dest inválido: {dest} (válidos: {sorted(dest_options)})")

        self.connection.send(SET_DATA_DESTINATION.format(dest=dest))
        logger.debug(f"[GL-DATA] Destino de datos cambiado a {dest}")

    def set_data_sampling(self, sample):
        # sample: depende de Memory/Direct (no valido estrictamente aquí)
        self.connection.send(SET_DATA_SAMPLING.format(sample=sample))
        logger.debug(f"[GL-DATA] Data Sample cambiado a {sample}")

    def set_data_submode(self, mode: str, sub_type: str):
        # MODE: ON / OFF
        # TYPE: PEAK / AVE / RMS
        mode = mode.upper()
        sub_type = sub_type.upper()

        mode_options = {"ON", "OFF"}
        sub_type_options = {"PEAK", "AVE", "RMS"}

        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")
        if sub_type not in sub_type_options:
            raise CommandError(f"sub_type inválido: {sub_type} (válidos: {sorted(sub_type_options)})")

        # Ojo: tu comando usa placeholders {MODE} y {TYPE} en mayúsculas
        self.connection.send(SET_DATA_SUB.format(mode=mode, sub_type=sub_type))

        logger.debug(f"[GL-DATA] Data Sub-Mode -> MODE={mode}, TYPE={sub_type}")

    def set_data_capture_mode(self, mode: str):
        # mode: CONT // 1H // 24H
        mode = mode.upper()
        mode_options = {"CONT", "1H", "24H"}
        if mode not in mode_options:
            raise CommandError(f"capture mode inválido: {mode} (válidos: {sorted(mode_options)})")

        self.connection.send(SET_DATA_CAPTURE_MODE.format(mode=mode))
        logger.debug(f"[GL-DATA] Modo de captura: {mode}")

    # -------------------------
    # GETTERS
    # -------------------------
    def get_data_location(self):
        return self._to_str(self.connection.query(GET_DATA_LOCATION))

    def get_data_sampling(self):
        return self._to_str(self.connection.query(GET_DATA_SAMPLING))

    def get_data_memory_size(self):
        return self._to_str(self.connection.query(GET_DATA_MEMORY_SIZE))

    def get_data_destination(self):
        return self._to_str(self.connection.query(GET_DATA_DESTINATION))

    def get_data_filepath(self):
        return self._to_str(self.connection.query(GET_DATA_FILEPATH))

    def get_data_points(self):
        return self._to_str(self.connection.query(GET_DATA_POINTS))

    def get_data_capture_mode(self):
        return self._to_str(self.connection.query(GET_DATA_CAPTURE_MODE))

    def get_data_sub(self):
        return self._to_str(self.connection.query(GET_DATA_SUB))
