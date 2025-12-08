import struct
import logging
from typing import Dict, Any

from graphtec.io.decoder import (
    extract_meas_payload,
    decode_special,
    convert_4vt_voltage,
)

logger = logging.getLogger(__name__)


class GraphtecRealtime:
    """
    Módulo de lectura en tiempo real del GL100.
    """

    def __init__(self, device):
        """
        device debe proporcionar al menos:
          - device.measure.read_one_measurement() -> bytes
          - device.amp.get_channels() -> dict[int, {"type","input","range"}]
        """
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
        """
        Usa la utilidad común extract_meas_payload para quitar
        la cabecera #6****** de :MEAS:OUTP:ONE?.
        """
        if isinstance(data, str):
            data = data.encode("latin-1", errors="ignore")
        return extract_meas_payload(data)

    # ---------------------------------------------------------
    # Conversión oficial de voltaje GS-4VT (reutiliza decoder)
    # ---------------------------------------------------------
    def _convert_voltage(self, raw: int, rng: str) -> float:
        """
        Convierte el valor crudo de un canal DC_V según la tabla oficial.
        Reutiliza la implementación común de decoder.
        """
        return convert_4vt_voltage(raw, rng)

    # ---------------------------------------------------------
    # API pública
    # ---------------------------------------------------------
    def read(self) -> Dict[str, Any]:
        """
        Lee una muestra real-time :MEAS:OUTP:ONE? y devuelve
        un diccionario con los valores físicos interpretados.

        Soporta todos los módulos GL100:
          - GS-4VT: voltaje y termopar
          - GS-4TSR: termistor
          - GS-TH: temperatura, humedad, punto de rocío, acumulados
          - GS-3AT: aceleración + temperatura
          - GS-LXUV: lux, UV y acumulados
          - GS-CO2: CO2 + alarmas
        """
        raw = self.read_raw()
        payload = self._strip_prefix(raw)
        if not payload:
            return {}

        channels: Dict[int, Dict[str, Any]] = self.device.amp.get_channels()
        parsed: Dict[str, Any] = {}

        offset = 0

        # Para no parsear dos veces los módulos que comparten datos
        parsed_th = False
        parsed_acc = False
        parsed_luxuv = False
        parsed_co2 = False

        for ch in range(1, 5):
            if offset >= len(payload):
                break

            info = channels[ch]
            tipo = info["type"]
            entrada = info["input"]
            rango = info["range"]

            # Canal OFF -> solo saltamos de forma segura en módulos por canal
            if entrada == "OFF" and tipo in ("VT", "TSR"):
                # En 4VT/4TSR hay un word por canal aunque esté OFF
                if offset + 2 <= len(payload):
                    offset += 2
                continue

            # -----------------------------------------------------
            # GS-4VT: Voltaje o termopar (módulo por canal)
            # -----------------------------------------------------
            if tipo == "VT":
                if offset + 2 > len(payload):
                    break
                raw_val = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = decode_special(raw_val)

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
                if flag:
                    parsed[f"CH{ch}_Flag"] = flag
                continue

            # -----------------------------------------------------
            # GS-4TSR (Thermistor, módulo por canal)
            # -----------------------------------------------------
            if tipo == "TSR":
                if offset + 2 > len(payload):
                    break
                raw_val = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = decode_special(raw_val)
                key = f"CH{ch}_Temp_TSR"
                parsed[key] = None if val is None else val / 10.0
                if flag:
                    parsed[f"{key}_Flag"] = flag
                continue

            # -----------------------------------------------------
            # GS-TH (Temp + Humedad + DewPoint + AccumTemp)
            # Frame único con dummy inicial
            # -----------------------------------------------------
            if tipo == "TH":
                if parsed_th:
                    # Ya consumido el bloque de este módulo
                    continue
                parsed_th = True

                # dummy + TEMP + RH + DEW + ATEMPH + ATEMPL
                if offset + 12 > len(payload):
                    logger.warning("[GL100Realtime] Payload insuficiente para TH.")
                    break

                # Data1 dummy
                _ = struct.unpack_from(">h", payload, offset)[0]
                offset += 2

                # Data2–6
                temp, rh, dew, aH, aL = struct.unpack_from(">5H", payload, offset)
                offset += 10

                parsed[f"CH{ch}_Temp_C"] = temp / 10.0
                parsed[f"CH{ch}_Humidity_%"] = rh / 200.0
                parsed[f"CH{ch}_Dew_C"] = dew / 100.0
                parsed[f"CH{ch}_AccumTemp"] = ((aH << 16) | aL) / 100.0

                # Data7–9: A, AO, STATUS (opcionales)
                if offset + 6 <= len(payload):
                    a, ao, status = struct.unpack_from(">3H", payload, offset)
                    offset += 6
                    parsed[f"CH{ch}_Alarm"] = a
                    parsed[f"CH{ch}_AlarmOut"] = ao
                    parsed[f"CH{ch}_Status"] = status

                continue

            # -----------------------------------------------------
            # GS-3AT (aceleración + temp)
            # Frame único con dummy inicial
            # -----------------------------------------------------
            if tipo == "ACC":
                if parsed_acc:
                    continue
                parsed_acc = True

                # dummy + X + Y + Z + TEMP
                if offset + 10 > len(payload):
                    logger.warning("[GL100Realtime] Payload insuficiente para ACC.")
                    break

                # Data1 dummy
                _ = struct.unpack_from(">h", payload, offset)[0]
                offset += 2

                # Data2–5
                x, y, z, t = struct.unpack_from(">4h", payload, offset)
                offset += 8

                parsed[f"CH{ch}_X"] = x
                parsed[f"CH{ch}_Y"] = y
                parsed[f"CH{ch}_Z"] = z
                parsed[f"CH{ch}_Temp"] = t / 10.0

                # Data6–8: A, AO, STATUS (opcionales)
                if offset + 6 <= len(payload):
                    a, ao, status = struct.unpack_from(">3H", payload, offset)
                    offset += 6
                    parsed[f"CH{ch}_Alarm"] = a
                    parsed[f"CH{ch}_AlarmOut"] = ao
                    parsed[f"CH{ch}_Status"] = status

                continue

            # -----------------------------------------------------
            # GS-LXUV (LUX + UV + acumulados)
            # Frame único con dummy inicial
            # -----------------------------------------------------
            if tipo in ("LUX", "UV"):
                if parsed_luxuv:
                    continue
                parsed_luxuv = True

                # Localizar qué canal es LUX y cuál UV en la config
                lux_ch = None
                uv_ch = None
                for idx, cinfo in channels.items():
                    if cinfo.get("type") == "LUX" and lux_ch is None:
                        lux_ch = idx
                    elif cinfo.get("type") == "UV" and uv_ch is None:
                        uv_ch = idx

                # dummy + LUX + UV + ALUXH + ALUXL + AUVH + AUVL
                if offset + 14 > len(payload):
                    logger.warning("[GL100Realtime] Payload insuficiente para LXUV.")
                    break

                # Data1 dummy
                _ = struct.unpack_from(">h", payload, offset)[0]
                offset += 2

                # Data2–7
                lux, uv, aluxh, aluxl, auvh, auvl = struct.unpack_from(">6H", payload, offset)
                offset += 12

                if lux_ch is not None:
                    parsed[f"CH{lux_ch}_LUX"] = lux
                if uv_ch is not None:
                    parsed[f"CH{uv_ch}_UV"] = uv

                parsed["AccumLux"] = (aluxh << 16) | aluxl
                parsed["AccumUV"] = (auvh << 16) | auvl

                # Data8–10: A, AO, STATUS (opcionales)
                if offset + 6 <= len(payload):
                    a, ao, status = struct.unpack_from(">3H", payload, offset)
                    offset += 6
                    parsed["LXUV_Alarm"] = a
                    parsed["LXUV_AlarmOut"] = ao
                    parsed["LXUV_Status"] = status

                continue

            # -----------------------------------------------------
            # GS-CO2
            # Frame único con dummy inicial
            # -----------------------------------------------------
            if tipo == "CO2":
                if parsed_co2:
                    continue
                parsed_co2 = True

                # dummy + CO2
                if offset + 4 > len(payload):
                    logger.warning("[GL100Realtime] Payload insuficiente para CO2.")
                    break

                # Data1 dummy
                _ = struct.unpack_from(">h", payload, offset)[0]
                offset += 2

                # Data2 CO2
                raw_val = struct.unpack_from(">H", payload, offset)[0]
                offset += 2
                parsed[f"CH{ch}_CO2_ppm"] = raw_val / 4.0

                # Data3–5: A, AO, STATUS (opcionales)
                if offset + 6 <= len(payload):
                    a, ao, status = struct.unpack_from(">3H", payload, offset)
                    offset += 6
                    parsed[f"CH{ch}_Alarm"] = a
                    parsed[f"CH{ch}_AlarmOut"] = ao
                    parsed[f"CH{ch}_Status"] = status

                continue

            # -----------------------------------------------------
            # Genérico: cualquier cosa no contemplada
            # -----------------------------------------------------
            if offset + 2 > len(payload):
                break
            raw_val = struct.unpack_from(">h", payload, offset)[0]
            offset += 2
            val, flag = decode_special(raw_val)
            parsed[f"CH{ch}_raw"] = val
            if flag:
                parsed[f"CH{ch}_Flag"] = flag

        return parsed
