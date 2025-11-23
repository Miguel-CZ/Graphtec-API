import struct
import logging

logger = logging.getLogger(__name__)


class GL100Realtime:
    """
    Módulo de lectura en tiempo real del GL100.
    """

    def __init__(self, device):
        """
        Args:
            device (GL100Device): instancia del núcleo del dispositivo.
        """
        self.device = device

    # =========================================================
    # Lectura RAW usando device.measure
    # =========================================================
    def read_raw(self) -> bytes:
        """
        Realiza la lectura RAW de un bloque de datos binarios.
        """
        raw = self.device.measure.read_one_measurement()

        if not raw:
            logger.warning("[GL100Realtime] No se recibió ningún dato.")
            return b""

        return raw

    # =========================================================
    # Parse del bloque binario según protocolo
    # =========================================================
    def _strip_prefix(self, data: bytes) -> bytes:
        """
        El GL100 envía datos con cabecera tipo: #6xxxxxx

        # → indica formato binario
        6 → nº de dígitos que indican la longitud
        xxxxxx → longitud de la sección de datos

        Este método elimina esa cabecera y deja únicamente los bytes
        del DATA REGION.

        Returns:
            bytes: sección de datos binarios pura.
        """
        if isinstance(data, str):
            data = data.encode("latin-1")

        print(f"data:{data}")
        if not data.startswith(b"#6"):
            # No hay cabecera → devolvemos todo el bloque
            return data

        # Número de bytes de longitud expresado en ASCII (6 dígitos)
        length_field = data[2:8]

        try:
            data_len = int(length_field.decode())
        except ValueError:
            logger.error("[GL100Realtime] Cabecera inválida, no se pudo leer longitud.")
            return data

        # DATA comienza justo después de "#6xxxxxx" (8 bytes)
        payload = data[8:8 + data_len]

        return payload

    # =========================================================
    # Parse genérico de valores
    # =========================================================
    def parse(self, payload: bytes, *, bytes_per_value=2):
        """
        Convierte la secuencia binaria en una lista de valores enteros.

        Args:
            payload (bytes): datos binarios sin cabecera.
            bytes_per_value (int): 2 para 16-bit, 4 para 32-bit.

        Returns:
            list[int]: valores convertidos.
        """
        if not payload:
            return []

        if bytes_per_value not in (2, 4):
            raise ValueError("bytes_per_value debe ser 2 o 4.")

        values = []
        step = bytes_per_value

        # Recorrer bloque en múltiplos exactos
        usable = len(payload) - (len(payload) % step)

        for i in range(0, usable, step):
            chunk = payload[i:i + step]

            if bytes_per_value == 2:
                values.append(struct.unpack(">h", chunk)[0])
            else:
                values.append(struct.unpack(">i", chunk)[0])

        return values

    # =========================================================
    # API de alto nivel
    # =========================================================
    def read(self, *, bytes_per_value=2):
        """
        Lectura completa:
            raw → eliminar cabecera → parseo

        Returns:
            list[int]: valores de medición ya convertidos.
        """
        raw = self.read_raw()
        payload = self._strip_prefix(raw)
        return self.parse(payload, bytes_per_value=bytes_per_value)
