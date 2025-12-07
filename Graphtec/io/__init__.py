# gl100/io/__init__.py
"""
Módulos de entrada/salida de datos (I/O) para GL100
===================================================

- realtime: adquisición de datos en tiempo real.
- capture: descarga y lectura de datos almacenados (memoria o SD).
"""

from graphtec.io.realtime import GraphtecRealtime
from graphtec.io.capture import GraphtecCapture

__all__ = ["GraphtecRealtime", "GraphtecCapture"]
