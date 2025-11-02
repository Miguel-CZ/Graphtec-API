import serial
import time
from gl100.core.connection.base import BaseConnection
from gl100.utils.log import logger


class USBConnection(BaseConnection):
    """
    Implementación de la comunicación USB/Serial con el dipositivo.
    """

    def __init__(self, port="COM3", baudrate=9600,
                 bytesize=8, parity="N", stopbits=1,
                 timeout=3, write_timeout=1,):
        
        super().__init__() # Inicializa la ABC.
        #TODO: Probar conexión USB en Linux?
        self.port = port # Puerto serial (ej. "COM3" o "/dev/ttyUSB0")
        self.baudrate = baudrate # Velocidad de transmisión
        self.bytesize = bytesize # Tamaño de byte
        self.parity = parity # Paridad: En nuestro caso  siempre "N" (ninguna)
        self.stopbits = stopbits # Bits de parada
        self.timeout = timeout # Timeout de lectura
        self.write_timeout = write_timeout # Timeout de escritura

    # =========================================================
    # Abrir/Cerrar Conexión
    # =========================================================
    def open(self):
        """
        Abre el puerto serial.
        
        Raises:
            serial.SerialException: Si no se puede abrir el puerto.
        
        """
        try:
            self._connection = serial.Serial(
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
        if self._connection:
            try:
                self._connection.close()
                logger.info("[GL100 USB] Conexión cerrada")
            finally:
                self._connection = None

    # =========================================================
    # Envío de comando
    # =========================================================
    def send(self, command: bytes | str):
        """
        Envía comando.
        Args:
            command (bytes | str): Datos a enviar.
        """
        #* Se deja la opción por ahora de enviar comandos por bytes por si se requiere 
        #* cuando se implemente el resto de módulos.

        # Asegurar que los comandos terminen en CRLF.
        if isinstance(command, str) and not command.endswith("\r\n"):
            command = (command + "\r\n").encode()
        elif isinstance(command,str):
            command = command.encode()
        elif isinstance(command, bytes) and not command.endswith(b"\r\n"):
            command += b"\r\n"

        if not self._connection:
            raise ConnectionError("Puerto USB no abierto")
        
        self._connection.write(command)
        self._connection.flush()  # Asegurar que los datos se envíen enteros.
        time.sleep(0.1) # Pequeña pausa para no saturar el buffer

    # =========================================================
    # lectura de respuesta
    # =========================================================
    # Receive -> Nº de bytes
    # Receive_until -> Reciba hasta encontrar un terminador.
    # Receive -> Recibe una línea (Encontrar un \n)

    def receive(self, size=4096) -> bytes:
        """
        Lee n bytes de datos.
        Args:
            size (int): Número de bytes a leer.
        
        Returns:
            bytes: Datos recibidos.
        """
        if not self._connection:
            raise ConnectionError("Puerto USB no abierto")
        
        response=self._connection.read(size)

        return response

    def receive_until(self, terminator: bytes = b"\r\n") -> bytes:
        """
        Lee datos hasta encontrar el terminador especificado.
        
        Args:
            terminator (bytes): Secuencia de bytes que indica el final del mensaje.
        
        Returns:
            bytes: Datos recibidos incluyendo el terminador.
        """
        if not self._connection:
            raise ConnectionError("Puerto USB no abierto")
        
        response=self._connection.read_until(terminator)  # Lee hasta el terminador.
        #Terminador por defecto CRLF

        return response
    
    def receive_line(self)-> bytes:
        """
        Lee una línea completa. Pyserial usa '\n' como terminador de línea.
        """
        if not self._connection:
            raise ConnectionError("Puerto USB no abierto")
        
        line=self._connection.readline()  # Lee hasta el terminador de línea.

        return line