"""
API pública del GL100.

Ejemplo de funcionamiento:
    from gl100 import GL100 #Importa directamente todos los módulos.

    gl = GL100(port="COM3") 
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()

Autor: Miguel Chen Zheng
"""

from gl100.connection import GL100Connection
from gl100.core.device import GL100Device
from gl100.io.realtime import GL100Realtime
from gl100.io.capture import GL100Capture
from gl100.utils.logger import logger


class GL100:
    """
    Clase fachada que encapsula todas las operaciones de alto nivel
    para interactuar con el dispositivo de Graphtec.
    """

    # =========================================================
    # Inicialización
    # =========================================================
    def __init__(self, conn_type="usb", **kwargs):
        """
        Inicializa la instancia del GL100.

        Args:
            conn_type (str): Tipo de conexión. "usb" o "lan".
            #!LAN no implementado por ahora.
            **kwargs: Parámetros específicos del tipo de conexión.
                - USB: port, baudrate, timeout, etc.
                - LAN: address, tcp_port, timeout, etc.
        """
        self.conn_type = conn_type

        self.conn = GL100Connection(conn_type=conn_type, **kwargs)
        self.device = GL100Device(self.conn)
        self.realtime = GL100Realtime(self.conn)
        self.capture = GL100Capture(self.conn)
        self.connected = False

    # =========================================================
    # CONEXIÓN -> core/connection.py
    # =========================================================
    def connect(self):
        """Abre la conexión con el GL100."""
        self.conn.open()
        self.connected = True
        logger.info(f"[GL100] Conectado vía {self.conn_type.upper()}")

    def disconnect(self):
        """Cierra la conexión con el GL100."""
        if not self.connected:
            logger.warning("[GL100] Desconexión ignorada: no hay conexión activa.")
            return
        self.conn.close()
        self.connected = False
        logger.info("[GL100] Conexión cerrada correctamente.")

    def is_connected(self) -> bool:
        """Devuelve True si hay conexión activa."""
        return self.connected
    
    # =========================================================
    # Grupo COMMON
    # =========================================================
    def get_id(self):
        """Devuelve el ID del dipositivo."""
        return self.device.common.get_id()
    
    def save_settings(self):
        """Guarda la configuración en la memoria del dispositivo."""
        return self.device.common.save_settings()
    
    def clear(self):
        """Limpia el estado interno (buffer,errores, etc)"""
        return self.device.common.clear()
    
    # =========================================================
    # ESTADO (device)
    # =========================================================
    def set_nlcode(self,code="CR_LF"):

        return self.device.interface.set_nlcode(code)
    