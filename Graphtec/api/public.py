"""
API pública del GL100.

Ejemplo de funcionamiento:
    from graphtec import Graphtec #Importa directamente todos los módulos.

    gl = Graphtec(port="COM3") 
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()

Autor: Miguel Chen Zheng
"""

from graphtec.connection import GraphtecConnection
from graphtec.core.device import GraphtecDevice
from graphtec.io.realtime import GraphtecRealtime
from graphtec.io.capture import GraphtecCapture
import logging
logger = logging.getLogger(__name__)


class Graphtec:
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
            #! Se deja en la arquitectura conexión LAN para futuras actualizaciones si se desea.
            **kwargs: Parámetros específicos del tipo de conexión.
                - USB: port, baudrate, timeout, etc.
                - LAN: address, tcp_port, timeout, etc.
        """
        self.conn_type = conn_type
        self.conn = GraphtecConnection(conn_type=conn_type, **kwargs)

        self.device = GraphtecDevice(self.conn)
        self.realtime = GraphtecRealtime(self.device)
        self.capture = GraphtecCapture(self.conn)
        
        self.connected = False
        self.channels = None

    # =========================================================
    # CONEXIÓN
    # =========================================================
    def connect(self):
        """Abre la conexión con el GL100."""
        self.conn.open()
        self.connected = True
        logger.info(f"[GL100] Conectado vía {self.conn_type.upper()}")

        #Inicializar dispositivo
        #self.channels = self.update_channels()

        


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
    
    # =========================================================
    # REALTIME (realtime)
    # =========================================================
    def read(self):
        """Lee un bloque de datos en tiempo real."""
        return self.realtime.read()
    
    # =========================================================
    # Grupo AMP 
    # =========================================================
    def get_channels(self):
        """Devuelve la configuración de los canales."""
        return self.device.amp.get_channels()
    
    def update_channels(self):
        """Actualiza la configuración de los canales desde el dispositivo."""
        return self.device.amp.update_channels()
    
    def list_files(self, path="\\MEM\\LOG\\",long=True, filt="GBD"):
        """Lista los archivos de captura almacenados en el dispositivo."""
        return self.capture.list_files(path=path,long=long, filt=filt)
    
    def download_file(self, path_in_gl: str, dest_folder: str):
        """Descarga un archivo de captura desde el dispositivo.

        Args:
            filename (str): Nombre del archivo en el dispositivo.
            dest_path (str): Ruta local donde guardar el archivo.
        """
        return self.capture.download_file(path_in_gl, dest_folder)
    
    