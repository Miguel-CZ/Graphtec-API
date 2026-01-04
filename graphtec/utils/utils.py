from graphtec.core.exceptions import CommandError, ResponseError

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
        raise CommandError(f"Canal inválido: {ch}")
    if ch_int not in (1, 2, 3, 4):
        raise CommandError(f"Canal inválido: {ch_int} (válidos: 1..4)")
    return ch_int

def to_str(response):
    if response is None:
        return ""
    if isinstance(response, (bytes, bytearray)):
        return response.decode(errors="replace").strip()
    return str(response).strip()