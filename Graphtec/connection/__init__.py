from graphtec.connection.usb_connection import USBConnection
from graphtec.connection.wlan_connection import WLANConnection
import logging
logger = logging.getLogger(__name__)

def GL100Connection(conn_type="usb", **kwargs):
    """
    Método fabricación para la conexión.
    Se contempla por Serial y por WLAN.

    Ejemplo:
        conn = GL100Connection("usb", port="COM3")
        conn.open()
        conn.send(":MEAS:OUTP:ONE?")
    """
    conn_type = conn_type.lower().strip()

    usb_aliases = ["usb", "serial", "com", "uart"]
    lan_aliases = ["wlan","lan", "ethernet", "net", "tcp", "ip", "wifi"]

    if conn_type in usb_aliases:
        return USBConnection(**kwargs)
    elif conn_type in lan_aliases:
        return WLANConnection(**kwargs)
    else:
        raise ValueError(f"Tipo de conexión no reconocido: {conn_type}")
