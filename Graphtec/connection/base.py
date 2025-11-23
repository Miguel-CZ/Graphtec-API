import time
from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class BaseConnection(ABC):
    """
    Clase base abstracta para gestionar la comunicación con el GL100.
    Define la interfaz común para USB y LAN.
    """

    def __init__(self):
        self._connection = None

    @abstractmethod
    def open(self):
        """Abre la conexión."""
        pass

    @abstractmethod
    def close(self):
        """Cierra la conexión."""
        pass

    @abstractmethod
    def send(self, command: bytes | str):
        """Envía comando al dispositivo."""
        pass

    @abstractmethod
    def receive(self, size=4096) -> bytes:
        """Recibe {size} datos desde el dispositivo."""
        pass

    @abstractmethod
    def receive_until(self, terminator: bytes = b"\r\n") -> bytes:
        """Recibe datos hasta {terminator} desde el dispositivo."""
        pass
    @abstractmethod
    def receive_line(self)->bytes:
        """Recibe datos hasta eol desde el dispositivo."""
        pass

    def query(self, command: str) -> bytes:
        """Envía un comando y devuelve la respuesta."""
        pass

    def is_open(self) -> bool:
        """Devuelve True si la conexión está activa."""
        return self._connection is not None
