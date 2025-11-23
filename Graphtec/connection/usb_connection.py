import serial
import time
from graphtec.connection.base import BaseConnection
import logging
logger = logging.getLogger(__name__)


class USBConnection(BaseConnection):
    """
    Implementación de la comunicación USB/Serial con el dipositivo.
    """

    def __init__(self, port="COM3", baudrate=38400,
                 bytesize=8, parity="N", stopbits=1,
                 timeout=3, write_timeout=1):
        
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
        logger.debug(f"[USBConnection] << {command}")
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
        logger.debug(f"[USBConnection] >> {response}")

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
        logger.debug(f"[USBConnection] >> {response}")
        return response
    
    def receive_line(self)-> bytes:
        """
        Lee una línea completa. Pyserial usa '\n' como terminador de línea.
        """
        if not self._connection:
            raise ConnectionError("Puerto USB no abierto")
        
        line=self._connection.readline()  # Lee hasta el terminador de línea.

        return line
    
    def query(self, command: str)-> bytes:
        self.send(command)

        cmd_up = command.upper()

        # Realtime
        if cmd_up.startswith(":MEAS:OUTP"):
            return self.read_binary()

        # Transferencia bloque binario
        if cmd_up.startswith(":TRANS:OUTP:DATA?"):
            return self.read_binary()

        # Cabecera GBD
        if cmd_up.startswith(":TRANS:OUTP:HEAD?"):
            return self.read_binary()

        # Apertura TRANS → 3 bytes
        if cmd_up.startswith(":TRANS:OPEN?"):
            if self._connection is not None:
                return self._connection.read(3)
            else: 
                return b""

        return self.read_ascii()
    
    def read_ascii(self) -> bytes:
        """
        Lee una respuesta ASCII hasta CRLF.
        
        Returns:
            bytes: Datos recibidos.
        """
        return self.receive_until(b"\r\n")
    
    def read_binary(self):
        """
        Lee un bloque binario estilo #6xxxxxx del GL100.
        Elimina cualquier basura previa al carácter '#'.
        """
        if not self._connection:
            raise RuntimeError("Serial no inicializado")

        # 1) Leer hasta encontrar '#'
        while True:
            b = self._connection.read(1)
            if not b:
                raise TimeoutError("Timeout esperando inicio de bloque (#)")
            if b == b"#":
                break  # encontrado inicio real
            # si no es "#", es basura → se ignora silenciosamente

        # 2) Leer dígito que indica nº de dígitos del length
        ndigits_b = self._connection.read(1)
        if not ndigits_b or not ndigits_b.isdigit():
            logger.error(f"[USBConnection] Cabecera binaria inválida: {ndigits_b!r}")
            raise ValueError("Cabecera binaria inválida.")

        nd = int(ndigits_b.decode())

        # 3) Leer longitud ASCII
        length_str = self._connection.read(nd)
        try:
            data_len = int(length_str.decode())
        except Exception:
            logger.error(f"[USBConnection] Longitud inválida: {length_str!r}")
            raise ValueError("Error longitud bloque.")

        # 4) Leer payload binario
        payload = self._connection.read(data_len)

        # 5) Intentar leer CRLF final (opcional)
        tail = self._connection.read(2)
        if tail not in (b"", b"\r\n"):
            pass  # ignoramos, puede venir fragmentado

        logger.debug(f"[USBConnection] << BIN {data_len} bytes")
        return b"#" + ndigits_b + length_str + payload
    
    def read_until_idle(self, idle_ms=800, overall_ms=10000):
        """
        Lectura ASCII continua hasta que el dispositivo queda inactivo.
        """
        import time

        if not self._connection:
            return ""

        out = bytearray()
        deadline = time.time() + overall_ms / 1000.0
        last = time.time()

        while time.time() < deadline:
            waiting = self._connection.in_waiting if hasattr(self._connection, "in_waiting") else 0
            if waiting:
                out += self._connection.read(waiting)
                last = time.time()
            else:
                if (time.time() - last) * 1000 >= idle_ms:
                    break
                time.sleep(0.02)

        return out.decode("ascii", errors="ignore").strip()
