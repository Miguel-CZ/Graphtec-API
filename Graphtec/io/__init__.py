# gl100/io/__init__.py
"""
Módulos de entrada/salida de datos (I/O) para GL100
===================================================

- realtime: adquisición de datos en tiempo real.
- capture: descarga y lectura de datos almacenados (memoria o SD).
"""

from Graphtec.io.realtime import GL100Realtime
from Graphtec.io.capture import GL100Capture

__all__ = ["GL100Realtime", "GL100Capture"]
