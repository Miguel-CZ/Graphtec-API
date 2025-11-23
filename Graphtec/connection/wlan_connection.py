import socket
from graphtec.connection.base import BaseConnection
import logging
logger = logging.getLogger(__name__)


class WLANConnection(BaseConnection):
    """
    Implementa la comunicación TCP/IP con el dispositivo.
    #* En principio los dispositivos del laboratorio no tienen módulo LAN.
    #? Pero hay un modelo con conexión ethernet. Probar si requiere sockets. Sino descartar.
    """

    def __init__(self, address="192.168.0.10", port=8023, timeout=3):
        super().__init__()
        self.address = address
        self.port = port
        self.timeout = timeout

    def open(self):
        """Abre una conexión TCP."""
        try:
            self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._connection.settimeout(self.timeout)
            self._connection.connect((self.address, self.port))
            logger.info(f"[GL100 LAN] Conectado a {self.address}:{self.port}")
        except socket.error as e:
            logger.error(f"[GL100 LAN] Error de conexión: {e}")
            raise

    def close(self):
        """Cierra la conexión TCP."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("[GL100 LAN] Conexión cerrada")
            finally:
                self._connection = None

    def send(self, command: bytes | str):
        """Envía datos por TCP."""
        if isinstance(command, str):
            command = (command + "\r\n").encode()
        if not self._connection:
            raise ConnectionError("Socket TCP no abierto")
        self._connection.sendall(command)


    def receive(self, size=4096) -> bytes:
        """Recibe datos del socket TCP."""
        if not self._connection:
            raise ConnectionError("Socket TCP no abierto")
        return self._connection.recv(size)
