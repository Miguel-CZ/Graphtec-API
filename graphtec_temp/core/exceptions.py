"""
Excepciones específicas para la librería GL100.

Todas las excepciones heredan de GL100Error, lo que permite capturar
cualquier error del núcleo con una sola cláusula si se desea.
"""

class GraphtecError(Exception):
    """Excepción base para todos los errores del GL100."""
    pass


# ───────────────────────────────
# Errores de conexión / transporte
# ───────────────────────────────
class ConnectionError(GraphtecError):
    """Error relacionado con la conexión física (USB/WLAN)."""
    pass


class TimeoutError(ConnectionError):
    """Error por tiempo de espera al comunicarse con el dispositivo."""
    pass


class DisconnectedError(ConnectionError):
    """El dispositivo ha sido desconectado inesperadamente."""
    pass


# ───────────────────────────────
# Errores de comandos / protocolo IF
# ───────────────────────────────
class CommandError(GraphtecError):
    """Error al enviar o ejecutar un comando IF."""
    pass


class ResponseError(CommandError):
    """El dispositivo devolvió una respuesta no válida o inesperada."""
    pass


# ───────────────────────────────
# Errores de datos / formato
# ───────────────────────────────
class DataError(GraphtecError):
    """Error en la recepción o decodificación de datos."""
    pass


class ParseError(DataError):
    """Error al interpretar datos binarios o ficheros GBD."""
    pass


class FileFormatError(DataError):
    """El archivo o bloque recibido no cumple el formato esperado."""
    pass


# ───────────────────────────────
# Errores de configuración / estado
# ───────────────────────────────
class ConfigurationError(GraphtecError):
    """Error al aplicar o cargar configuraciones del GL100."""
    pass


class DeviceStateError(GraphtecError):
    """El dispositivo está en un estado incompatible con la operación."""
    pass
