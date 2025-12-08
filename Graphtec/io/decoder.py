"""
Utilidades comunes de decodificación para el GL100.

Incluye:
  - Parseo de bloques #6****** (HEAD / MEAS / TRANS:DATA).
  - Códigos especiales GL100.
  - Conversión de crudo -> físico (GS-4VT y resto de módulos).
"""

import struct
import logging
from typing import Tuple, Optional, Dict, List, Any

logger = logging.getLogger(__name__)

__all__ = [
    "strip_noise",
    "parse_head_block",
    "extract_trans_data_block",
    "extract_meas_payload",
    "decode_special",
    "convert_4vt_voltage",
    "convert_value",
    "convert_row_physical",
    "build_column_names_with_units",
]

# ============================================================
# BLOQUES #6******
# ============================================================
def strip_noise(block: bytes) -> bytes:
    """
    Busca el primer '#' y descarta basura anterior.
    Si no se encuentra '#', devuelve el bloque tal cual.
    """
    if isinstance(block, str):
        block = block.encode("latin-1", errors="ignore")
    if not isinstance(block, (bytes, bytearray)):
        raise TypeError("strip_noise espera bytes o str.")
    idx = block.find(b"#")
    return block[idx:] if idx != -1 else block


def parse_head_block(block: bytes) -> str:
    """
    Parseo de HEAD/HEADER:

        "#6******" + HEADER_ASCII

    Devuelve el texto ASCII del header.
    """
    block = strip_noise(block)

    if not block.startswith(b"#"):
        raise ValueError("Bloque HEAD inválido: no empieza por '#'.")

    try:
        nd = int(block[1:2])
        strlen = int(block[2:2 + nd])
    except ValueError as e:
        raise ValueError("Bloque HEAD inválido: campo de longitud no numérico.") from e

    start = 2 + nd
    end = start + strlen

    if len(block) < end:
        logger.warning(
            "[decoder] HEAD truncado: len=%d, esperado al menos %d.",
            len(block),
            end,
        )
        end = len(block)

    header_bytes = block[start:end]
    return header_bytes.decode("ascii", errors="ignore")


def extract_trans_data_block(block: bytes) -> Tuple[bytes, int, Optional[bool]]:
    """
    Extrae la parte de DATA de un bloque de TRANS:OUTP:DATA?.

    Formato esperado (Data Reception Specs):

      "#6******" + STATUS(2) + DATA(N) + CHECKSUM(2)

    Donde ****** = N (tamaño de DATA, sin STATUS ni CHECKSUM).

    Devuelve:
        (data: bytes, status: int, checksum_ok: bool|None)
    """
    block = strip_noise(block)

    if not block.startswith(b"#"):
        # ascii inesperado
        try:
            text = block.decode("ascii", errors="ignore").strip()
        except Exception:
            text = "?"
        logger.warning("[decoder] Bloque ASCII recibido en TRANS: %s", text)
        return b"", 0, None

    try:
        nd = int(block[1:2])          # normalmente '6'
        strlen = int(block[2:2 + nd]) # longitud de DATA en bytes (N)
    except ValueError:
        logger.error("[decoder] Cabecera #6 inválida en TRANS.")
        return b"", 0, None

    offset = 2 + nd
    remaining = len(block) - offset
    status_val: int = 0  # siempre int para evitar problemas con el linter

    # Caso HEAD/MEAS: "#6******" + DATA(N)
    if remaining == strlen:
        data = block[offset:offset + strlen]
        return data, status_val, None

    # Caso TRANS: "#6******" + STATUS(2) + DATA(N) + CHECKSUM(2)
    if remaining >= strlen + 4:
        status_bytes = block[offset:offset + 2]

        if len(status_bytes) != 2:
            logger.error("[decoder] STATUS bytes incompletos en TRANS.")
            status_val = 0
        else:
            status_val = struct.unpack(">H", status_bytes)[0]
            # Bits 0-2 según especificación
            if status_val & 0x0001:
                logger.error(
                    "[decoder] STATUS de TRANS indica error (0x%04X).",
                    status_val,
                )
            if status_val & 0x0002:
                logger.error(
                    "[decoder] Error en posición END (STATUS=0x%04X).",
                    status_val,
                )
            if status_val & 0x0004:
                logger.error(
                    "[decoder] Error en posición START (STATUS=0x%04X).",
                    status_val,
                )

        data_start = offset + 2
        data_end = data_start + strlen
        data = block[data_start:data_end]

        checksum_bytes = block[data_end:data_end + 2]
        checksum_ok: Optional[bool] = None
        if len(checksum_bytes) == 2:
            checksum_rx = struct.unpack(">H", checksum_bytes)[0]
            checksum_calc = sum(data) & 0xFFFF
            checksum_ok = (checksum_calc == checksum_rx)
            if not checksum_ok:
                logger.error(
                    "[decoder] Checksum inválido: calc=0x%04X, recv=0x%04X",
                    checksum_calc,
                    checksum_rx,
                )

        return data, status_val, checksum_ok

    logger.warning("[decoder] Bloque TRANS truncado o inconsistente.")
    return b"", status_val, None


def extract_meas_payload(block: bytes) -> bytes:
    """
    Extrae el payload de un bloque :MEAS:OUTP:ONE?:

        "#6******" + DATA(N)

    Si no hay cabecera #6, devuelve el bloque tal cual.
    """
    block = strip_noise(block)

    if not block.startswith(b"#"):
        return block

    try:
        nd = int(block[1:2])
        strlen = int(block[2:2 + nd])
    except ValueError:
        logger.error("[decoder] Cabecera #6 inválida en MEAS.")
        return block

    offset = 2 + nd
    end = offset + strlen

    if len(block) < end:
        logger.warning(
            "[decoder] Bloque MEAS truncado: len=%d, esperado al menos %d.",
            len(block),
            end,
        )
        end = len(block)

    return block[offset:end]


# ============================================================
# CÓDIGOS ESPECIALES GL100
# ============================================================
def decode_special(raw: int) -> Tuple[Optional[int], Optional[str]]:
    """
    Decodifica los códigos especiales GL100:

      -0x7fff : UnderFS
       0x7ffc : OverFS
       0x7ffd : Burnout
       0x7ffe : Off
       0x7fff : CalcError

    Devuelve:
        (valor_normalizado | None, flag | None)
    """
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


# ============================================================
# CONVERSIÓN GS-4VT
# ============================================================
def _normalize_4vt_range(rng: str) -> str:
    """
    Normaliza el string de rango GS-4VT para manejar variantes:
      "1-5VDC", "1TO5V", "1_5V" -> "1-5V"
    """
    r = (rng or "").upper().replace(" ", "")
    r = r.replace("TO", "-").replace("_", "-")
    if r in ("1-5VDC",):
        r = "1-5V"
    return r


def convert_4vt_voltage(raw_val: int, rng: str) -> float:
    """
    Conversión EXACTA según "Binary translation of voltage data
    of 4ch voltage temperature (GS-4VT)".

    1) Escalado base (1, 2, 5) → factores 1 / 2 / 4
    2) Ajuste de punto decimal → siempre a Voltios
    """
    rng_norm = _normalize_4vt_range(rng)

    # Factor base (1 / 2 / 4)
    if rng_norm in ("100MV", "1V", "10V"):
        base_factor = 2
    elif rng_norm in ("20MV", "200MV", "2V", "20V"):
        base_factor = 1
    elif rng_norm in ("50MV", "500MV", "5V", "50V", "1-5V"):
        base_factor = 4
    else:
        # Rango desconocido → devolvemos raw sin escalar
        return float(raw_val)

    # Ajuste de punto decimal (siempre a V)
    if rng_norm == "20MV":
        dec_factor = 1_000_000
    elif rng_norm in ("50MV", "100MV", "200MV"):
        dec_factor = 100_000
    elif rng_norm in ("500MV", "1V", "2V"):
        dec_factor = 10_000
    elif rng_norm in ("5V", "10V", "20V", "1-5V"):
        dec_factor = 1_000
    elif rng_norm == "50V":
        dec_factor = 100
    else:
        dec_factor = 1.0

    return raw_val / (base_factor * dec_factor)


# ============================================================
# CONVERSIÓN FÍSICA UNIFICADA (captured data)
# ============================================================
def convert_value(
    module: str,
    inp: str,
    rng: str,
    span: Tuple[int, int],
    raw_val: int,
) -> float:
    """
    Conversión física unificada para todos los módulos GL100.

    - GS-4VT: fórmulas oficiales (sin spans)
    - Resto: conversión lineal por spans + ajustes heurísticos
    """
    module_u = (module or "UNKNOWN").upper()
    inp_u = (inp or "").upper()
    rng_u = (rng or "").upper()

    # ---------------------- GS-4VT ---------------------------
    if module_u.startswith("GS-4VT"):
        if inp_u in ("DC", "DC_V", "V", "VT", "MV"):
            return convert_4vt_voltage(raw_val, rng_u)

        # Temperatura por termopar:
        # [Temperature (°C)] = [Temperature data] / 10
        if inp_u == "TEMP":
            return raw_val / 10.0

        # Logic / Pulse / Alarm → devolver raw
        return float(raw_val)

    # ---------------------- Resto de módulos -----------------
    smin, smax = span

    # Conversión lineal Graphtec en unidades del span
    phys = smin + ((raw_val + 32768) * (smax - smin) / 65535.0)

    # GS-TH
    if module_u.startswith("GS-TH"):
        if inp_u in ("TEMP", "HUM", "HUMID", "RH", "DEW"):
            return phys / 100.0
        return phys

    # GS-3AT
    if module_u.startswith("GS-3AT"):
        if inp_u == "ACC":
            return phys / 1000.0
        if inp_u == "TEMP":
            return phys / 100.0
        return phys

    # GS-LXUV
    if module_u.startswith("GS-LXUV"):
        if inp_u in ("LUX", "UV"):
            return phys / 1000.0
        return phys

    # GS-CO2
    if module_u.startswith("GS-CO2"):
        return phys

    # GS-DPA-AC
    if module_u.startswith("GS-DPA-AC"):
        if "A" in inp_u:
            return phys / 1000.0
        return phys

    # GS-4TSR
    if module_u.startswith("GS-4TSR"):
        return phys / 100.0

    return phys


def convert_row_physical(
    module: str,
    order: List[str],
    raw_row: Any,
    amp_info: Dict[str, Dict[str, str]],
    spans: Dict[str, Tuple[int, int]],
) -> List[Optional[float]]:
    """
    Convierte una fila de datos crudos (lista/tupla de enteros 16-bit)
    en unidades físicas, respetando el Order del header.

    Aplica también los códigos especiales del GL100.
    """
    out: List[Optional[float]] = []

    for name, raw_val in zip(order, raw_row):
        n = name.strip()

        # Campos no canal (Logic, Alarm, etc.) → dejar raw tal cual
        if not n.startswith("CH"):
            out.append(raw_val)
            continue

        # Tratar códigos especiales
        val_raw, flag = decode_special(int(raw_val))
        if val_raw is None:
            # Error / burnout / overFS / etc. → dejamos celda vacía
            out.append(None)
            continue

        span = spans.get(n, (0, 1))
        info = amp_info.get(n, {})
        inp = info.get("input") or ""
        rng = info.get("range") or ""

        val = convert_value(
            module=module,
            inp=inp,
            rng=rng,
            span=span,
            raw_val=val_raw,
        )
        out.append(val)

    return out


def build_column_names_with_units(
    order: List[str],
    amp_info: Dict[str, Dict[str, str]],
) -> List[str]:
    """
    Construye nombres de columnas con sufijos de unidad
    según el tipo de entrada (TEMP, DC_V, ACC, etc.).
    """
    cols: List[str] = []
    for n in order:
        name = n.strip()
        if not name.startswith("CH"):
            cols.append(name)
            continue

        info = amp_info.get(name, {})
        inp = (info.get("input") or "").upper()

        if inp == "TEMP":
            cols.append(f"{name}_C")
        elif inp in ("DC", "DC_V", "V", "VT", "MV"):
            cols.append(f"{name}_V")
        elif inp == "ACC":
            cols.append(f"{name}_G")
        elif inp in ("HUM", "HUMID", "RH"):
            cols.append(f"{name}_RH")
        else:
            cols.append(name)

    return cols
