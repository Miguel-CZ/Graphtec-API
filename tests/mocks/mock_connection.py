from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Union

BytesLike = Union[bytes, bytearray, memoryview]


@dataclass
class MockConnection:
    """
    Mock que cubre el interfaz que usa tu librería (según tu código):
      - open(), close()
      - send(cmd)
      - query(cmd) -> bytes
      - read_ascii() (compatibilidad con GraphtecCapture/TRANS)
      - propiedad _connection para que BaseConnection.is_open() funcione
    """
    responses: Dict[str, bytes]
    strict: bool = True
    is_open: bool = False
    sent_commands: List[str] = field(default_factory=list)

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    @staticmethod
    def _norm(cmd: Union[str, bytes]) -> str:
        if isinstance(cmd, (bytes, bytearray, memoryview)):
            cmd = bytes(cmd).decode("latin-1", errors="replace")
        return str(cmd).strip()

    def send(self, command: Union[str, bytes]) -> None:
        if not self.is_open:
            raise ConnectionError("MockConnection cerrada")
        cmd = self._norm(command)
        self.sent_commands.append(cmd)

    def query(self, command: Union[str, bytes]) -> bytes:
        if not self.is_open:
            raise ConnectionError("MockConnection cerrada")
        cmd = self._norm(command)
        self.send(cmd)

        if cmd in self.responses:
            return self.responses[cmd]

        if self.strict:
            raise KeyError(f"Comando no mockeado: {cmd!r}")

        return b""

    def read_ascii(self) -> bytes:
        """
        Compatibilidad: en tu código hay casos donde, tras un query binario,
        se lee el 'terminador' por read_ascii(). Aquí devolvemos vacío.
        """
        if not self.is_open:
            raise ConnectionError("MockConnection cerrada")
        return b""

    @property
    def _connection(self):
        """
        Compatibilidad con BaseConnection.is_open() que suele mirar _connection.
        """
        return self if self.is_open else None
