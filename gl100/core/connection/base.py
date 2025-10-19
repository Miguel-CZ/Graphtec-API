import time
from abc import ABC, abstractmethod


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
    def send(self, data: bytes | str):
        """Envía datos al dispositivo."""
        pass

    @abstractmethod
    def receive(self, size=4096) -> bytes:
        """Recibe datos desde el dispositivo."""
        pass

    def query(self, command: str) -> str:
        """Envía un comando ASCII y devuelve la respuesta como texto."""
        self.send(command)
        time.sleep(0.05)
        resp = self.receive().decode(errors="ignore")
        return resp.strip()

    def is_open(self) -> bool:
        """Devuelve True si la conexión está activa."""
        return self._conn is not None
