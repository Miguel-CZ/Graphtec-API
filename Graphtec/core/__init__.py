"""
Núcleo principal del control del GL100.

Contiene las clases y utilidades esenciales para manejar el dispositivo:
- GL100Device: interfaz de alto nivel con el hardware
- Excepciones específicas del GL100
- Logger del núcleo
"""

import logging
logger = logging.getLogger(__name__)
from .device import GraphtecDevice
from .exceptions import (
    GraphtecError,
    ConnectionError,
    CommandError,
    DataError,
)

__all__ = [
    "GraphtecDevice",
    "GraphtecError",
    "ConnectionError",
    "CommandError",
    "DataError",
    "logger",
]

# Inicialización del logger del núcleo
logger.debug("[GL100.Core] Núcleo inicializado correctamente")
