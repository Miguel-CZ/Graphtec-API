import serial
import time
from graphtec.connection.base import BaseConnection
import logging

logger = logging.getLogger(__name__)


class SerialConnection(BaseConnection):
    """
    Implementación de la comunicación USB/Serial con el dispositivo.
    """

    def __init__(
        self,
        port="COM3",
        baudrate=38400,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=3,
        write_timeout=1,
    ):
        super().__init__()  # Inicializa la ABC.
        # TODO: Probar conexión USB en Linux?
        self.port = port  # Puerto serial (ej. "COM3" o "/dev/ttyUSB0")
        self.baudrate = baudrate  # Velocidad de transmisión
        self.bytesize = bytesize  # Tamaño de byte
        self.parity = parity  # Paridad: En nuestro caso siempre "N" (ninguna)
        self.stopbits = stopbits  # Bits de parada
        self.timeout = timeout  # Timeout de lectura
        self.write_timeout = write_timeout  # Timeout de escritura

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
            logger.info(f"[SerialConnection] Conexión abierta en {self.port}")

        except serial.SerialException as e:
            logger.error(f"[SerialConnection] Error al abrir {self.port}: {e}")
            raise

    def close(self):
        """
        Cierra el puerto serial.
        """
        if self._connection:
            try:
                self._connection.close()
                logger.info("[SerialConnection] Conexión cerrada")
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

        # Asegurar que los comandos terminen en CRLF.
        if isinstance(command, str):
            if not command.endswith("\r\n"):
                command = (command + "\r\n").encode()
            else:
                command = command.encode()
        elif isinstance(command, bytes) and not command.endswith(b"\r\n"):
            command += b"\r\n"

        if not self._connection:
            raise ConnectionError("[SerialConnection] Puerto Serial no abierto")

        self._connection.write(command)
        self._connection.flush()  # Asegurar que los datos se envíen enteros.
        logger.debug(f"[SerialConnection] << {command}")
        time.sleep(0.1)  # Pequeña pausa para no saturar el buffer

    # =========================================================
    # lectura de respuesta
    # =========================================================
    def receive(self, size=4096) -> bytes:
        """
        Lee n bytes de datos.
        Args:
            size (int): Número de bytes a leer.

        Returns:
            bytes: Datos recibidos.
        """
        if not self._connection:
            raise ConnectionError("[SerialConnection] Puerto Serial no abierto")

        response = self._connection.read(size)
        logger.debug(f"[SerialConnection] >> {response}")

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
            raise ConnectionError("[SerialConnection] Puerto Serial no abierto")

        response = self._connection.read_until(terminator)  # Lee hasta el terminador.
        logger.debug(f"[SerialConnection] >> {response}")
        return response

    def receive_line(self) -> bytes:
        """
        Lee una línea completa. Pyserial usa '\n' como terminador de línea.
        """
        if not self._connection:
            raise ConnectionError("[SerialConnection] Puerto USB no abierto")

        line = self._connection.readline()  # Lee hasta el terminador de línea.
        return line

    def query(self, command: str) -> bytes:
        self.send(command)

        cmd_up = command.upper()

        # Real-time
        if cmd_up.startswith(":MEAS:OUTP"):
            return self.read_binary()

        # Transferencia bloque binario de datos capturados (incluye status+checksum)
        if cmd_up.startswith(":TRANS:OUTP:DATA?"):
            return self.read_binary_trans_data()

        # Cabecera GBD (solo #6****** + header ASCII)
        if cmd_up.startswith(":TRANS:OUTP:HEAD?"):
            return self.read_binary()

        # Apertura TRANS → 3 bytes
        if cmd_up.startswith(":TRANS:OPEN?"):
            if self._connection is not None:
                resp = self._connection.read(3)
                logger.debug(f"[SerialConnection] >> {resp}")
                return resp
            else:
                return b""

        # Resto: ASCII
        return self.receive_until(b"\r\n")

    def _read_hash6_header(self):
        """
        Lee el prefijo '#6******' y devuelve:
            ndigits_b, length_str_b, data_len(int)
        """
        if not self._connection:
            raise RuntimeError("[SerialConnection] Serial no inicializado")

        # 1) Leer hasta encontrar '#'
        while True:
            b = self._connection.read(1)
            if not b:
                raise TimeoutError("[SerialConnection] Timeout esperando inicio de bloque (#)")
            if b == b"#":
                break  # encontrado inicio real

        # 2) Leer dígito que indica nº de dígitos del length
        ndigits_b = self._connection.read(1)
        if not ndigits_b or not ndigits_b.isdigit():
            logger.error(f"[SerialConnection] Cabecera binaria inválida: {ndigits_b!r}")
            raise ValueError("[SerialConnection] Cabecera binaria inválida (#6).")

        nd = int(ndigits_b.decode())

        # 3) Leer longitud ASCII
        length_str = self._connection.read(nd)
        try:
            data_len = int(length_str.decode())
        except Exception:
            logger.error(f"[SerialConnection] Longitud inválida en #6******: {length_str!r}")
            raise ValueError("Error longitud bloque (#6******).")

        return ndigits_b, length_str, data_len

    def read_binary(self):
        """
        Lee un bloque binario estilo #6xxxxxx del GL100 SIN status/checksum.
        Usado para:
          - :MEAS:OUTP:ONE?
          - :TRANS:OUTP:HEAD?
        """
        if not self._connection:
            raise RuntimeError("Serial no inicializado")

        ndigits_b, length_str, data_len = self._read_hash6_header()

        # 4) Leer payload binario (exactamente data_len bytes)
        payload = self._connection.read(data_len)

        logger.debug(f"[SerialConnection] << BIN {data_len} bytes")
        return b"#" + ndigits_b + length_str + payload

    def read_binary_trans_data(self):
        """
        Lee un bloque binario de :TRANS:OUTP:DATA?:

          '#6******' + STATUS(2) + DATA(N) + CHECKSUM(2)

        donde ****** = N (tamaño de DATA en bytes, SIN incluir status/checksum).
        Devuelve:
          b'#' + '6' + '******' + STATUS + DATA + CHECKSUM
        """
        if not self._connection:
            raise RuntimeError("[SerialConnection] Serial no inicializado")

        ndigits_b, length_str, data_len = self._read_hash6_header()

        # Necesitamos leer STATUS(2) + DATA(N) + CHECKSUM(2) = N + 4 bytes
        to_read = data_len + 4
        payload = self._connection.read(to_read)

        if len(payload) < to_read:
            logger.warning(
                "[SerialConnection] Bloque TRANS DATA truncado: "
                f"esperados {to_read} bytes, recibidos {len(payload)}."
            )

        return b"#" + ndigits_b + length_str + payload

    def read_until_idle(self, idle_ms=800, overall_ms=10000):
        """
        Lectura ASCII continua hasta que el dispositivo queda inactivo.
        """
        import time as _time

        if not self._connection:
            return ""

        out = bytearray()
        deadline = _time.time() + overall_ms / 1000.0
        last = _time.time()

        while _time.time() < deadline:
            waiting = (
                self._connection.in_waiting
                if hasattr(self._connection, "in_waiting")
                else 0
            )
            if waiting:
                out += self._connection.read(waiting)
                last = _time.time()
            else:
                if (_time.time() - last) * 1000 >= idle_ms:
                    break
                _time.sleep(0.02)

        return out.decode("ascii", errors="ignore").strip()

    def flush_buffer(self):
        """
        Limpia los buffers de entrada y salida.
        """
        if not self._connection:
            raise RuntimeError("[SerialConnection] Serial no inicializado")

        self._connection.reset_input_buffer()
        self._connection.reset_output_buffer()
