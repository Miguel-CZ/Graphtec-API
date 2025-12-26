from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
from graphtec.utils import get_last_token
import logging

logger = logging.getLogger(__name__)

#TODO: Hay que revisar esto
class StatusModule(BaseModule):
    """Grupo STATUS: Estado del dispositivo"""

    # Bits del Condition register según tu tabla
    _COND_BITS = {
        0: "REC",   # Capturing data
        1: "MEM",   # Memory input/output status
        2: "WTR",   # Awaiting trigger status
        3: "TRG",   # Triggered status
        5: "ACS",   # Accessing disk
        9: "NUM",   # While the file number restriction is occurring
        10: "SPC",  # During the disc capacity investigation
        11: "FMT",  # Executing disk format
        12: "SET",  # Executing setup
        13: "INIT", # Executing initialization
        14: "CAL",  # During zero point adjustment
    }

    _ERR_CODES = {
        1: "Illegal setup parameter",
        2: "Current setting not possible",
        3: "No function",
        16: "Command error",
        17: "Invalid channel specification",
    }

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    @staticmethod
    def _parse_int_last_token(text: str) -> int:
        """
        Para respuestas tipo ':STAT:COND 11' o ':TRIG:COND:PRET 0'
        """
        tok = get_last_token(text).strip()
        # Algunos equipos devuelven '+11' o similares
        try:
            return int(tok)
        except ValueError:
            # fallback por si viene algo tipo '11,....'
            try:
                return int(tok.split(",", 1)[0])
            except Exception as e:
                raise ResponseError(f"No se pudo parsear entero desde: {text}") from e

    # -------------------------
    # GETTERS básicos
    # -------------------------
    def get_power_status(self):
        # CMD: :STAT:POW?
        text = self._to_str(self.connection.query(GET_POWER_STATUS))
        if not text:
            raise ResponseError("Sin respuesta a :STAT:POW?")
        return text

    def get_status_raw(self):
        # CMD: :STAT:COND?
        text = self._to_str(self.connection.query(GET_STATUS))
        if not text:
            raise ResponseError("Sin respuesta a :STAT:COND?")
        return text

    def get_status_value(self) -> int:
        # Valor numérico del Condition register
        return self._parse_int_last_token(self.get_status_raw())

    def get_status_flags(self) -> dict:
        """
        Devuelve un dict con los flags interpretados del COND register.
        Ejemplo:
          {
            "value": 11,
            "active": ["REC","MEM","TRG"],
            "bits": {"REC": True, "MEM": True, ...}
          }
        """
        value = self.get_status_value()

        bits_state = {}
        active = []
        for bit, name in self._COND_BITS.items():
            is_on = bool(value & (1 << bit))
            bits_state[name] = is_on
            if is_on:
                active.append(name)

        return {"value": value, "active": active, "bits": bits_state}

    def get_extended_status_raw(self):
        """
        EESR: se pone a 1 cuando ocurre el evento según el filtro.
        OJO: tu comando está como ':STAT:EESR' sin '?'. Para query, normalmente es '?',
        así que lo fuerzo si falta.
        """
        cmd = GET_EXTENDED_STATUS
        if not cmd.endswith("?"):
            cmd = cmd + "?"
        text = self._to_str(self.connection.query(cmd))
        if not text:
            raise ResponseError("Sin respuesta a :STAT:EESR?")
        return text

    def get_extended_status_value(self) -> int:
        # Normalmente será 0/1
        text = self.get_extended_status_raw()
        return self._parse_int_last_token(text)

    def get_error_status_raw(self):
        # CMD: :STAT:ERR?
        text = self._to_str(self.connection.query(GET_ERROR_STATUS))
        if not text:
            raise ResponseError("Sin respuesta a :STAT:ERR?")
        return text

    def get_error_status(self):
        """
        Devuelve:
        - 'NONE' si no hay error (según manual)
        - o un dict con {code, meaning}
        """
        text = self.get_error_status_raw()
        last = get_last_token(text).strip().strip('"')

        if last.upper() == "NONE":
            return "NONE"

        # A veces puede venir solo un número, o 'ERR 16', etc.
        try:
            code = int(last)
            return {"code": code, "meaning": self._ERR_CODES.get(code, "Unknown error")}
        except ValueError:
            # Si no es parseable, lo devolvemos raw
            return {"raw": text}

    # -------------------------
    # FILT: configuración de filtros por bit
    # -------------------------
    def set_status_filter(self, number: int, value: str):
        """
        number: 0-15 (bit)
        value: NEV / RISE / FALL / BOTH
        """
        try:
            n = int(number)
        except (TypeError, ValueError):
            raise CommandError(f"number inválido: {number}")

        if not (0 <= n <= 15):
            raise CommandError(f"number fuera de rango: {n} (válido 0..15)")

        value = value.upper()
        options = {"NEV", "RISE", "FALL", "BOTH"}
        if value not in options:
            raise CommandError(f"value inválido: {value} (válidos: {sorted(options)})")

        self.connection.send(SET_STATUS_FILTER.format(number=n, value=value))
        logger.debug(f"[GL-STATUS] FILT{n} -> {value}")

    def get_status_filter(self, number: int):
        try:
            n = int(number)
        except (TypeError, ValueError):
            raise CommandError(f"number inválido: {number}")

        if not (0 <= n <= 15):
            raise CommandError(f"number fuera de rango: {n} (válido 0..15)")

        text = self._to_str(self.connection.query(GET_STATUS_FILTER.format(number=n)))
        if not text:
            raise ResponseError(f"Sin respuesta a :STAT:FILT{n}?")
        return get_last_token(text).strip()
