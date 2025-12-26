from graphtec.core.device.base import BaseModule
from graphtec.core.commands import *
from graphtec.core.exceptions import CommandError, ResponseError
from graphtec.utils import get_last_token
import logging

logger = logging.getLogger(__name__)


class TriggerModule(BaseModule):
    """Grupo TRIGGER"""

    @staticmethod
    def _to_str(response):
        if response is None:
            return ""
        if isinstance(response, (bytes, bytearray)):
            return response.decode(errors="replace").strip()
        return str(response).strip()

    @staticmethod
    def _validate_channel(ch):
        try:
            ch_int = int(ch)
        except (TypeError, ValueError):
            raise CommandError(f"Canal inválido: {ch}")
        if ch_int not in (1, 2, 3, 4):
            raise CommandError(f"Canal inválido: {ch_int} (válidos: 1..4)")
        return ch_int

    # -------------------------
    # SETTERS
    # -------------------------
    def set_trigger(self, status: str):
        status = status.upper()
        status_options = {"START", "STOP", "OFF"}
        if status not in status_options:
            raise CommandError(f"status inválido: {status} (válidos: {sorted(status_options)})")

        self.connection.send(SET_TRIG_STATUS.format(status=status))
        logger.debug(f"[GL-TRIG] TRIG FUNC -> {status}")

    def set_trigger_source(self, source: str, dt_str: str = ""):
        source = source.upper()
        source_options = {"OFF", "AMP", "ALAR", "DATE"}
        if source not in source_options:
            raise CommandError(f"source inválido: {source} (válidos: {sorted(source_options)})")

        if source != "DATE":
            self.connection.send(SET_TRIG_SOURCE.format(source=source))
        else:
            if not dt_str:
                raise CommandError('Fecha y hora requerido cuando source="DATE" (formato: "YYYY-MM-DD hh:mm:ss")')
            self.connection.send(SET_TRIG_SOURCE_DATE.format(datetime=dt_str))

        logger.debug(f"[GL-TRIG] TRIG SOURCE -> {source}")

    def set_trigger_comb(self, comb: str):
        comb = comb.upper()
        comb_options = {"AND", "OR"}
        if comb not in comb_options:
            raise CommandError(f"comb inválido: {comb} (válidos: {sorted(comb_options)})")

        self.connection.send(SET_TRIG_COMBINATION.format(comb=comb))
        logger.debug(f"[GL-TRIG] TRIG COMB -> {comb}")

    def set_trigger_channel(self, ch, mode: str, value=""):
        ch = self._validate_channel(ch)

        mode = mode.upper()
        mode_options = {"OFF", "HIGH", "LOW"}
        if mode not in mode_options:
            raise CommandError(f"mode inválido: {mode} (válidos: {sorted(mode_options)})")

        if value is None or value == "":
            raise CommandError("value no puede ser vacío (ej: +0.000V)")

        self.connection.send(SET_TRIG_CHANNEL.format(ch=ch, mode=mode, value=value))
        logger.debug(f"[GL-TRIG] TRIG CH{ch} SET -> mode={mode}, value={value}")

    def set_pretrigger(self, value):
        try:
            value_num = float(value)
        except (TypeError, ValueError):
            raise CommandError(f"Pretrigger inválido (no numérico): {value}")

        if not (0 <= value_num <= 100):
            raise CommandError(f"Pretrigger fuera de rango: {value_num} (esperado 0..100)")

        # Placeholder correcto: {value}
        self.connection.send(SET_TRIG_PRETRIGGER.format(value=value))
        logger.debug(f"[GL-TRIG] PRET -> {value}%")

    # -------------------------
    # GETTERS
    # -------------------------
    def get_trigger(self):
        text = self._to_str(self.connection.query(GET_TRIG_STATUS))
        if not text:
            raise ResponseError("Sin respuesta a :TRIG:FUNC?")
        return get_last_token(text)

    def get_trigger_source(self):
        text = self._to_str(self.connection.query(GET_TRIG_SOURCE))
        if not text:
            raise ResponseError("Sin respuesta a :TRIG:COND:SOUR?")
        return get_last_token(text)

    def get_trigger_comb(self):
        text = self._to_str(self.connection.query(GET_TRIG_COMBINATION))
        if not text:
            raise ResponseError("Sin respuesta a :TRIG:COND:COMB?")
        return get_last_token(text)

    def get_trigger_channel(self, ch):
        # RESP: ":TRIG:COND:CH1:SET OFF,+0.000V"
        ch = self._validate_channel(ch)
        text = self._to_str(self.connection.query(GET_TRIG_CHANNEL.format(ch=ch)))
        if not text:
            raise ResponseError(f"Sin respuesta a :TRIG:COND:CH{ch}:SET?")

        # Nos quedamos con lo que viene después de "SET "
        marker = f":TRIG:COND:CH{ch}:SET "
        if marker in text:
            payload = text.split(marker, 1)[1].strip()
        else:
            # fallback: lo último “razonable”
            payload = text.split()[-1].strip()

        # payload esperado: "OFF,+0.000V" / "HIGH,+1.000V" etc.
        if "," in payload:
            mode, value = [p.strip() for p in payload.split(",", 1)]
        else:
            mode, value = payload.strip(), ""

        return {"mode": mode, "value": value}

    def get_pretrigger(self):
        # RESP: ":TRIG:COND:PRET 0" -> "0"
        text = self._to_str(self.connection.query(GET_TRIG_PRETRIGGER))
        if not text:
            raise ResponseError("Sin respuesta a :TRIG:COND:PRET?")
        return get_last_token(text)
