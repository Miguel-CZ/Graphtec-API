from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
import logging
from graphtec.core.exceptions import (
    CommandError,
    ResponseError,
    ConnectionError,
    DataError,
)

logger = logging.getLogger(__name__)


class CommonModule(BaseModule):
    """Grupo COMMON: Comandos comunes"""

    def __init__(self, device):
        super().__init__(device)
        self.equipo = {
            "fabricante": "",
            "dispositivo": "",
            "id": "",
            "firmware": ""
        }
        logger.debug("[GL-COMMON] Módulo común inicializado.")

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    def get_id_raw(self) -> str:
        """Devuelve la respuesta raw del *IDN? como str."""
        resp = self.connection.query(GET_IDN)
        text = self._to_str(resp)
        if not text:
            raise ResponseError("Sin respuesta del GL100 al comando *IDN?.")
        return text

    def get_id(self):
        """
        Parsea el formato real:
        '*IDN GRAPHTEC,GL100,0,01.45'
        y devuelve dict con fabricante, dispositivo, id, firmware.
        """
        try:
            raw = self.get_id_raw()

            # Esperado: "*IDN <csv>"
            head, sep, tail = raw.partition(" ")
            if not sep:  # no hay espacio
                raise ResponseError(f"Formato *IDN? inesperado (sin espacio): {raw}")

            if head.strip().upper() != "*IDN":
                logger.warning(f"[GL-COMMON] Prefijo inesperado en *IDN?: {head}")

            valores = [v.strip() for v in tail.split(",")]

            if len(valores) != 4:
                raise ResponseError(f"Formato CSV inesperado en *IDN? (esperados 4 campos): {raw}")

            fabricante, dispositivo, id_, firmware = valores

            self.equipo = {
                "fabricante": fabricante,
                "dispositivo": dispositivo,
                "id": id_,
                "firmware": firmware
            }

            logger.debug(f"[GL-COMMON] Consulta ID realizada: {self.equipo}")
            return self.equipo

        except (ResponseError, ConnectionError, DataError):
            raise
        except Exception as e:
            logger.error(f"[GL-COMMON] Error al consultar ID: {e}")
            raise CommandError(f"Error ejecutando *IDN?: {e}") from e

    def clear(self):
        """Limpia el estado interno (errores, buffers, etc). No devuelve respuesta."""
        self.connection.send(CLEAR)
        logger.debug("[GL-COMMON] Estado interno limpiado (*CLS).")

    def save_settings(self):
        """Guarda configuración en el equipo. No devuelve respuesta."""
        self.connection.send(SAVE_SETTINGS)
        logger.debug("[GL-COMMON] Configuración guardada (*SAV).")
