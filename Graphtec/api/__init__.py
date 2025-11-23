"""
API pública de la librería GL100
================================

Este módulo expone la clase principal 'GL100', que permite controlar
el registrador de datos Graphtec GL100 mediante USB o LAN.

Ejemplo de uso:
    from gl100 import GL100

    gl = GL100(conn_type="lan", address="192.168.0.10")
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()
"""

from Graphtec.api.public import GL100

__all__ = ["GL100"]
