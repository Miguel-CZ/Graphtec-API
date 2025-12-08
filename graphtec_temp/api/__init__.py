"""
API pública de la librería Graphtec
================================

Este módulo expone la clase principal 'Graphtec', que permite controlar
el registrador de datos Graphtec mediante USB o LAN.

Ejemplo de uso:
    from graphtec import Graphtec

    gl = Graphtec(conn_type="lan", address="192.168.0.10",tcp_port=8023)
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()
"""

from graphtec.api.public import Graphtec

__all__ = ["Graphtec"]
