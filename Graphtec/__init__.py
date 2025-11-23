# gl100/__init__.py
"""
Librería Python para controlar el Graphtec GL100 Petit LOGGER.

Permite comunicación USB y LAN, configuración de canales, lectura
en tiempo real, descarga de capturas y gestión de archivos.
"""

from Graphtec.api import GL100
from Graphtec.utils import setup_logging

__version__ = "0.1.0"
__all__ = ["GL100","setup_logging"]
