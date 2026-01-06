from graphtec.core.exceptions import CommandError, ParameterError

def get_last_token(response: str | None) -> str:
    """Devuelve el último token no vacío de una respuesta SCPI."""
    if not response:
        return ""
    response = response.replace(",", " ").replace(":", " ").replace('"', "").strip()
    parts = response.split()
    return parts[-1] if parts else ""

def validate_channel(ch):
    try:
        ch_int = int(ch)
    except (TypeError, ValueError):
        raise ParameterError(f"Canal inválido: {ch}")
    if ch_int not in (1, 2, 3, 4):
        raise ParameterError(f"Canal inválido: {ch_int} (válidos: 1..4)")
    return ch_int

def to_str(response):
    """Convierte respuestas a str y la limpia."""
    if response is None:
        return ""
    if isinstance(response, (bytes, bytearray)):
        return response.decode(errors="replace").strip()
    return str(response).strip()

def normalize_choice(value, aliases):
    """
    Normaliza 'value' usando el diccionario 'aliases'
    Devuelve el valor normalizado o lanza ParameterError si no existe.
    """
    if not isinstance(value, str):
        raise ParameterError(f"Se esperaba str, recibido: {type(value).__name__}")

    v = value.strip().upper()

    normalized = aliases.get(v)

    if normalized is None:
        valid_display = ", ".join(sorted(set(aliases.values())))
        raise ValueError(f"Valor inválido: {value!r}. Válidos: {valid_display}")

    return normalized


def check_range_int(value, min_val=None, max_val=None, inclusive=True):
    """
    Convierte 'value' a int, valida que está en rango y devuelve el número como str.
    - inclusive=True: límites inclusivos [min_val, max_val]
    """
    # Evitar que True/False cuelen como 1/0
    if isinstance(value, bool):
        raise ValueError("bool no es válido como entero")

    # Intentar convertir a entero
    if isinstance(value, (int,)):
        ivalue = value
    else:
        # Permite string numérico o float.exacto (como "10" o "10.0")
        try:
            f = float(value)
        except Exception:
            raise ValueError(f"No se pudo convertir a entero: {value!r}")
        if not f.is_integer():
            raise ValueError(f"El valor no es un entero exacto: {value!r}")
        ivalue = int(f)

    # Validación de rango
    if min_val is not None:
        if inclusive:
            if ivalue < int(min_val):
                raise ValueError(f"{ivalue} debe ser >= {int(min_val)}")
        else:
            if ivalue <= int(min_val):
                raise ValueError(f"{ivalue} debe ser > {int(min_val)}")

    if max_val is not None:
        if inclusive:
            if ivalue > int(max_val):
                raise ValueError(f"{ivalue} debe ser <= {int(max_val)}")
        else:
            if ivalue >= int(max_val):
                raise ValueError(f"{ivalue} debe ser < {int(max_val)}")

    return str(ivalue)


def check_range_float(value, min_val=None, max_val=None, inclusive=True):
    """
    Convierte 'value' a float, valida que está en rango y devuelve el número como str,
    con **hasta 3 decimales** (sin ceros de relleno ni punto final).
    """
    if isinstance(value, bool):
        raise ValueError("bool no es válido como float")

    # Conversión a float
    try:
        fvalue = float(value)
    except Exception:
        raise ValueError(f"No se pudo convertir a número: {value!r}")

    # Validación de rango
    if min_val is not None:
        if inclusive:
            if fvalue < float(min_val):
                raise ValueError(f"{fvalue} debe ser >= {float(min_val)}")
        else:
            if fvalue <= float(min_val):
                raise ValueError(f"{fvalue} debe ser > {float(min_val)}")

    if max_val is not None:
        if inclusive:
            if fvalue > float(max_val):
                raise ValueError(f"{fvalue} debe ser <= {float(max_val)}")
        else:
            if fvalue >= float(max_val):
                raise ValueError(f"{fvalue} debe ser < {float(max_val)}")

    # Formateo: máximo 3 decimales, sin ceros finales
    s = f"{fvalue:.3f}".rstrip("0").rstrip(".")
    # Si todo quedó vacío (caso 0.000 -> ""), aseguramos "0"
    return s if s else "0"

