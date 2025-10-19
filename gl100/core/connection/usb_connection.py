import serial
import time
from gl100.core.connection.base import BaseConnection
from gl100.utils.log import logger


class USBConnection(BaseConnection):
    """
    Implementa la comunicación USB/Serial con el GL100.
    """

    def __init__(self, port="COM3", baudrate=9600,
                 bytesize=8, parity="N", stopbits=1,
                 timeout=3, write_timeout=1,):
        
        super().__init__() # Inicializa la clase base abstracta
        #TODO: Probar conexión USB en Linux
        self.port = port # Puerto serial (ej. "COM3" o "/dev/ttyUSB0")
        self.baudrate = baudrate # Velocidad de transmisión
        self.bytesize = bytesize # Tamaño de byte
        self.parity = parity # Paridad: En nuestro caso  siempre "N" (ninguna)
        self.stopbits = stopbits # Bits de parada
        self.timeout = timeout # Timeout de lectura
        self.write_timeout = write_timeout # Timeout de escritura

    def open(self):
        """Abre el puerto serial.
        
        Raises:
            serial.SerialException: Si no se puede abrir el puerto.
        
        """
        try:
            self._conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
            )
            logger.info(f"[GL100 USB] Conexión abierta en {self.port}")

        except serial.SerialException as e:
            logger.error(f"[GL100 USB] Error al abrir {self.port}: {e}")
            raise

    def close(self):
        """
        Cierra el puerto serial.
        """
        if self._conn:
            try:
                self._conn.close()
                logger.info("[GL100 USB] Conexión cerrada")
            finally:
                self._conn = None

    def send(self, data: bytes | str):
        """
        Envía comando.
        Args:
            data (bytes | str): Datos a enviar.
        """

        # Asegura que los comandos terminen en CRLF
        if isinstance(data, str) and not data.endswith("\r\n"):
                data = (data + "\r\n").encode()
        elif isinstance(data,str):
            data = data.encode()
        elif isinstance(data, bytes) and not data.endswith(b"\r\n"):
            data += b"\r\n"

        if not self._conn:
            raise ConnectionError("Puerto USB no abierto")
        
        self._conn.write(data)
        self._conn.flush()  # Asegurar que los datos se envíen enteros.
        time.sleep(0.1) # Pequeña pausa para no saturar el buffer del GL100

    def receive(self, size=4096) -> bytes:
        """
        Lee n bytes de datos.
        Args:
            size (int): Número de bytes a leer.
        
        Returns:
            bytes: Datos recibidos.
        """
        if not self._conn:
            raise ConnectionError("Puerto USB no abierto")
        
        response=self._conn.read(size)

        return response

    def receive_until(self, terminator: bytes = b"\r\n") -> bytes:
        """
        Lee datos hasta encontrar el terminador especificado.
        
        Args:
            terminator (bytes): Secuencia de bytes que indica el final del mensaje.
        
        Returns:
            bytes: Datos recibidos incluyendo el terminador.
        """
        if not self._conn:
            raise ConnectionError("Puerto USB no abierto")
        
        response=self._conn.read_until(terminator)  # Lee hasta el terminador.
        #Terminador por defecto CRLF

        return response
    
    def read_line(self)-> bytes:
        """
        Lee una línea completa. Pyserial usa '\n' como terminador de línea.
        """
        if not self._conn:
            raise ConnectionError("Puerto USB no abierto")
        
        line=self._conn.readline()  # Lee hasta el terminador de línea.

        return line
