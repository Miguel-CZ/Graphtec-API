from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
from graphtec.utils import get_last_token
import logging

logger = logging.getLogger(__name__)


class InterfaceModule(BaseModule):
    """Grupo IF: Interfaz"""

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    def set_nlcode(self, nlcode: str):
        # nlcode: CR_LF / CR / LF
        nlcode = nlcode.upper()
        nlcode_options = {"CR_LF", "CR", "LF"}
        if nlcode not in nlcode_options:
            raise CommandError(f"nlcode inválido: {nlcode} (válidos: {sorted(nlcode_options)})")

        self.connection.send(SET_CONN_NLCODE.format(code=nlcode))
        logger.debug(f"[GL-IF] NLCODE cambiado a {nlcode}")

    def get_nlcode(self):
        resp = self.connection.query(GET_CONN_NLCODE)
        text = self._to_str(resp)
        if not text:
            raise ResponseError("Sin respuesta a :IF:NLCODE?")
        return get_last_token(text)
