from gl100.core.connection.usb_connection import USBConnection
from gl100.core.connection.wlan_connection import LANConnection


def GL100Connection(conn_type="usb", **kwargs):
    """
    Fábrica de conexión que selecciona automáticamente la clase adecuada.

    Ejemplo:
        conn = GL100Connection("lan", address="192.168.0.10")
        conn.open()
        conn.send(":MEAS:OUTP:ONE?")
    """
    conn_type = conn_type.lower().strip()

    usb_aliases = ["usb", "serial", "com", "uart"]
    lan_aliases = ["lan", "ethernet", "net", "tcp", "ip", "wifi"]

    if conn_type in usb_aliases:
        return USBConnection(**kwargs)
    elif conn_type in lan_aliases:
        return LANConnection(**kwargs)
    else:
        raise ValueError(f"Tipo de conexión no reconocido: {conn_type}")
