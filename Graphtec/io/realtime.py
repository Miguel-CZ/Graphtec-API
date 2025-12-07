import struct
import logging

logger = logging.getLogger(__name__)


class GraphtecRealtime:
    """
    Módulo de lectura en tiempo real del GL100.
    """

    def __init__(self, device):
        self.device = device

    # ---------------------------------------------------------
    # Lectura RAW
    # ---------------------------------------------------------
    def read_raw(self) -> bytes:
        raw = self.device.measure.read_one_measurement()
        if not raw:
            logger.warning("[GL100Realtime] No se recibió ningún dato.")
            return b""
        return raw

    # ---------------------------------------------------------
    # Limpieza de cabecera #6xxxxxx
    # ---------------------------------------------------------
    def _strip_prefix(self, data: bytes) -> bytes:
        if isinstance(data, str):
            data = data.encode("latin-1")
        data = bytes(data)

        if not data.startswith(b"#6"):
            return data

        length_field = data[2:8]
        try:
            data_len = int(length_field.decode())
        except ValueError:
            logger.error("[GL100Realtime] Cabecera inválida.")
            return data

        return data[8:8 + data_len]

    # ---------------------------------------------------------
    # Valores especiales GL100
    # ---------------------------------------------------------
    @staticmethod
    def _decode_special(raw: int):
        if raw == 0x7fff:
            return None, "CalcError"
        if raw == 0x7ffe:
            return None, "Off"
        if raw == 0x7ffd:
            return None, "Burnout"
        if raw == 0x7ffc:
            return None, "OverFS"
        if raw == -0x7fff:
            return None, "UnderFS"
        return raw, None

    # ---------------------------------------------------------
    # Conversión oficial de voltaje GS-4VT
    # Según GBD File Specification Sheet
    # ---------------------------------------------------------
    def _convert_voltage(self, raw: int, rng: str) -> float:
        """
        Convierte el valor crudo de un canal DC_V según la tabla oficial.
        Coincide con la implementación clásica de tu librería antigua.
        """
        rng = rng.upper()

        # Determina divisor base (1, 2 o 4) según categoría del rango
        if rng in ("100MV", "1V", "10V"):
            divisor = 2
        elif rng in ("20MV", "200MV", "2V", "20V"):
            divisor = 1
        elif rng in ("50MV", "500MV", "5V", "50V", "1_5V"):
            divisor = 4
        else:
            raise ValueError(f"Rango no soportado en GS-4VT: {rng}")

        # Escala decimal para obtener voltios
        if rng == "20MV":
            scale = 1e6
        elif rng in ("50MV", "100MV", "200MV"):
            scale = 1e5
        elif rng in ("500MV", "1V", "2V"):
            scale = 1e4
        elif rng in ("5V", "10V", "20V", "1_5V"):
            scale = 1e3
        elif rng == "50V":
            scale = 1e2
        else:
            scale = 1.0

        return raw / divisor / scale

    # ---------------------------------------------------------
    # API pública
    # ---------------------------------------------------------
    def read(self) -> dict:
        """
        Lee una muestra real-time :MEAS:OUTP:ONE? y devuelve
        un diccionario con los valores físicos interpretados
        según el módulo/sensor conectado.
        """
        raw = self.read_raw()
        payload = self._strip_prefix(raw)
        if not payload:
            return {}

        channels = self.device.amp.get_channels()
        parsed = {}

        offset = 0

        for ch in range(1, 5):
            info = channels[ch]
            tipo = info["type"]
            entrada = info["input"]
            rango = info["range"]

            # Canal OFF -> saltamos pero avanzamos 2 bytes
            if entrada == "OFF":
                offset += 2
                continue

            # -----------------------------------------------------
            # GS-4VT: Voltaje o termopar
            # -----------------------------------------------------
            if tipo == "VT":
                raw_val = struct.unpack_from(">h", payload, offset)[0]
                val, flag = self._decode_special(raw_val)
                offset += 2

                # Voltaje DC_V
                if entrada == "DC_V":
                    if val is not None:
                        try:
                            v = self._convert_voltage(val, rango)
                            parsed[f"CH{ch}_V"] = v
                        except Exception:
                            parsed[f"CH{ch}_raw"] = val
                    if flag:
                        parsed[f"CH{ch}_V_Flag"] = flag
                    continue

                # Termopares TC-K / TC-T
                if entrada in ("TC-K", "TC-T"):
                    key = f"CH{ch}_Temp_{entrada}"
                    parsed[key] = None if val is None else val / 10.0
                    if flag:
                        parsed[f"{key}_Flag"] = flag
                    continue

                # Otros casos VT → valor crudo
                parsed[f"CH{ch}_raw"] = val
                continue

            # -----------------------------------------------------
            # GS-4TSR (Thermistor)
            # -----------------------------------------------------
            if tipo == "TSR":
                raw_val = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = self._decode_special(raw_val)
                key = f"CH{ch}_Temp_TSR"
                parsed[key] = None if val is None else val / 10.0
                if flag:
                    parsed[f"{key}_Flag"] = flag
                continue

            # -----------------------------------------------------
            # GS-TH (Temp + Humedad + DewPoint + AccumTemp)
            # -----------------------------------------------------
            if tipo == "TH":
                if len(payload) < offset + 10:
                    break
                temp, rh, dew, aH, aL = struct.unpack_from(">5H", payload, offset)
                offset += 10
                parsed[f"CH{ch}_Temp_C"] = temp / 10.0
                parsed[f"CH{ch}_Humidity_%"] = rh / 200.0
                parsed[f"CH{ch}_Dew_C"] = dew / 100.0
                parsed[f"CH{ch}_AccumTemp"] = ((aH << 16) | aL) / 100.0
                continue

            # -----------------------------------------------------
            # GS-3AT (aceleración + temp)
            # -----------------------------------------------------
            if tipo == "ACC":
                if len(payload) < offset + 8:
                    break
                x, y, z, t = struct.unpack_from(">4h", payload, offset)
                offset += 8
                parsed[f"CH{ch}_X"] = x
                parsed[f"CH{ch}_Y"] = y
                parsed[f"CH{ch}_Z"] = z
                parsed[f"CH{ch}_Temp"] = t / 10.0
                continue

            # -----------------------------------------------------
            # GS-LXUV
            # -----------------------------------------------------
            if tipo in ("LUX", "UV"):
                raw_val = struct.unpack_from(">H", payload, offset)[0]
                offset += 2
                parsed[f"CH{ch}_{tipo}"] = raw_val
                continue

            # -----------------------------------------------------
            # GS-CO2
            # -----------------------------------------------------
            if tipo == "CO2":
                raw_val = struct.unpack_from(">H", payload, offset)[0]
                offset += 2
                parsed[f"CH{ch}_CO2_ppm"] = raw_val / 4.0
                continue

            # -----------------------------------------------------
            # Genérico
            # -----------------------------------------------------
            raw_val = struct.unpack_from(">h", payload, offset)[0]
            offset += 2
            val, flag = self._decode_special(raw_val)
            parsed[f"CH{ch}_raw"] = val
            if flag:
                parsed[f"CH{ch}_Flag"] = flag

        return parsed
