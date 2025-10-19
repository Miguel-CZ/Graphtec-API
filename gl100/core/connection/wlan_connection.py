import socket
from gl100.core.connection.base import BaseConnection
from gl100.utils.log import logger


class WLANConnection(BaseConnection):
    """
    Implementa la comunicación TCP/IP (LAN o WiFi) con el GL100.
    """

    def __init__(self, address="192.168.0.10", port=8023, timeout=3):
        super().__init__()
        self.address = address
        self.port = port
        self.timeout = timeout

    def open(self):
        """Abre una conexión TCP."""
        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._conn.settimeout(self.timeout)
            self._conn.connect((self.address, self.port))
            logger.info(f"[GL100 LAN] Conectado a {self.address}:{self.port}")
        except socket.error as e:
            logger.error(f"[GL100 LAN] Error de conexión: {e}")
            raise

    def close(self):
        """Cierra la conexión TCP."""
        if self._conn:
            try:
                self._conn.close()
                logger.info("[GL100 LAN] Conexión cerrada")
            finally:
                self._conn = None

    def send(self, data: bytes | str):
        """Envía datos por TCP."""
        if isinstance(data, str):
            data = (data + "\r\n").encode()
        if not self._conn:
            raise ConnectionError("Socket TCP no abierto")
        self._conn.sendall(data)

    def receive(self, size=4096) -> bytes:
        """Recibe datos del socket TCP."""
        if not self._conn:
            raise ConnectionError("Socket TCP no abierto")
        return self._conn.recv(size)
