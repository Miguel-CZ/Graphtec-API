# gl100/core/__init__.py
"""
Núcleo de la librería GL100
===========================

Este paquete contiene las implementaciones de bajo nivel que gestionan:

- La comunicación física (USB / LAN)
- El envío y recepción de comandos IF
- La configuración y control del dispositivo

Módulos principales:
    - connection: manejo de transporte (serial o TCP/IP)
    - device: capa de control lógico del GL100
    - commands: plantillas SCPI/IF y utilidades de protocolo
"""

from gl100.core.device import GL100Device
from gl100.core.commands import *
from gl100.core.connection import GL100Connection

# También puedes importar directamente las subclases si las necesitas:
from gl100.core.connection.usb_connection import USBConnection
from gl100.core.connection.wlan_connection import LANConnection

__all__ = [
    "GL100Connection",
    "USBConnection",
    "LANConnection",
    "GL100Device",
]
