# gl100/io/realtime.py
import struct
from gl100.utils.log import logger


class GL100Realtime:
    """
    Gestión de adquisición de datos en tiempo real del GL100.

    Usa el comando ':MEAS:OUTP:ONE?' para leer las muestras actuales
    directamente desde el buffer interno.
    """

    def __init__(self, connection):
        self.conn = connection

    # =========================================================
    # Lectura principal
    # =========================================================
    def read(self):
        """
        Envía el comando de lectura y decodifica los datos binarios recibidos.

        Returns:
            dict: valores físicos decodificados por canal.
        """
        logger.debug("[GL100Realtime] Leyendo datos en tiempo real...")
        self.conn.send(":MEAS:OUTP:ONE?")

        raw = self.conn.receive(4096)
        if not raw:
            logger.warning("[GL100Realtime] No se recibieron datos")
            return {}

        try:
            # Buscar encabezado '#6' (indicador de bloque binario)
            if raw.startswith(b"#6"):
                length = int(raw[2:8].decode())
                data = raw[8 : 8 + length]
            else:
                # Si no hay encabezado, asumimos que el buffer ya contiene solo datos
                data = raw

            decoded = self._decode_binary(data)
            return decoded

        except Exception as e:
            logger.error(f"[GL100Realtime] Error al decodificar: {e}")
            return {}

    # =========================================================
    # Decodificación básica
    # =========================================================
    def _decode_binary(self, data: bytes) -> dict:
        """
        Decodifica los valores binarios del GL100.
        El formato depende del sensor conectado. En general:
          - Cada canal es un entero de 16 bits (big endian).
          - Los valores especiales (0x7fff, 0x7ffd...) indican estados.
        """
        values = []
        for i in range(0, len(data), 2):
            if i + 1 >= len(data):
                break
            val = struct.unpack(">h", data[i : i + 2])[0]
            values.append(val)

        # Simulación básica: devolver CH1..CHn
        result = {f"CH{i+1}": v for i, v in enumerate(values)}

        logger.debug(f"[GL100Realtime] Datos decodificados: {result}")
        return result
