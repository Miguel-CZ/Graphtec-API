import time
from gl100.utils.logger import logger
from typing import cast

RESPUESTAS_SIMULADAS = {
    "*IDN?": b"GRAPHTEC,GL100,012345,1.10\r\n",
    ":COMMON:INFO?": b"Model=GL100,FW=1.10,Channels=8\r\n",
    ":COMMON:STAT?": b"READY\r\n",
    ":COMMON:MODEL?": b"GL100\r\n",
    ":COMMON:VER?": b"1.10\r\n",
    ":COMMON:SERIAL?": b"012345\r\n",
    "*SAV": b"OK\r\n",
    ":COMMON:RESET": b"OK\r\n",
    "*CLS": b"OK\r\n",
    
}

class MockUSBConnection:
    """
    Simulación de una conexión USB con un GL100.
    Permite probar los módulos device sin hardware físico.
    """

    def __init__(self, port="COM_MOCK", baudrate=9600,
                 bytesize=8, parity="N", stopbits=1,
                 timeout=3, write_timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.timeout=timeout
        self.write_timeout=write_timeout

        #Propias de simulación
        self.is_open = False
        self.sent_commands = []
        self.responses = dict(RESPUESTAS_SIMULADAS)
        logger.debug(f"[MockUSBConnection] Inicializado")

    # =========================================================
    # Apertura / Cierre de conexión
    # =========================================================
    def open(self):
        """Simula la apertura del puerto USB."""
        self.is_open = True
        logger.debug(f"[MockUSBConnection] Puerto simulado abierto ({self.port})")

    def close(self):
        """Simula el cierre del puerto USB."""
        self.is_open = False
        logger.debug("[MockUSBConnection] Puerto simulado cerrado")

    # =========================================================
    # Envío de comandos
    # =========================================================
    def send(self, command: bytes | str):
        """Guarda el comando enviado (no hace nada más)."""
        if not self.is_open:
            raise ConnectionError("Puerto simulado no abierto")

        if isinstance(command, str) and not command.endswith("\r\n"):
            command = (command + "\r\n").encode()
        elif isinstance(command,str):
            command = command.encode()
        elif isinstance(command, bytes) and not command.endswith(b"\r\n"):
            command += b"\r\n"

        self.sent_commands.append(command.decode().strip())# type: ignore[arg-type]
        logger.debug(f"[MockUSBConnection] << {command}")
        time.sleep(0.05)  # pequeña pausa simbólica

    # =========================================================
    # Consulta de comandos (query)
    # =========================================================
    def query(self, command: bytes | str) -> bytes:
        """Simula el envío de un comando y devuelve una respuesta predefinida."""
        if not self.is_open:
            raise ConnectionError("Puerto simulado no abierto")

        self.send(command)

        # Buscar respuesta simulada
        response = self.responses.get(command, b"OK\r\n")# type: ignore[arg-type]
        logger.debug(f"[MockUSBConnection] >> {response.decode(errors='ignore').strip()}")
        return response

    # =========================================================
    # Propiedad para compatibilidad con BaseConnection
    # =========================================================
    @property
    def _connection(self):
        """Compatibilidad con BaseConnection (para evitar errores en tests)."""
        return self if self.is_open else None
