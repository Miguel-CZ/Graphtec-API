"""
Núcleo principal del control del GL100.

Contiene las clases y utilidades esenciales para manejar el dispositivo:
- GL100Device: interfaz de alto nivel con el hardware
- Excepciones específicas del GL100
- Logger del núcleo
"""

from gl100.utils.logger import logger
from .device import GL100Device
from .exceptions import (
    GL100Error,
    ConnectionError,
    CommandError,
    DataError,
)

__all__ = [
    "GL100Device",
    "GL100Error",
    "ConnectionError",
    "CommandError",
    "DataError",
    "logger",
]

# Inicialización del logger del núcleo
logger.debug("[GL100.Core] Núcleo inicializado correctamente")
