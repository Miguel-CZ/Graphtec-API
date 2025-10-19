# gl100/io/capture.py
import os
from gl100.utils.log import logger


class GL100Capture:
    """
    Maneja la transferencia de datos capturados (guardados en memoria o SD).

    Comandos principales:
        :TRANS:SOUR DISK,"<path>"
        :TRANS:OPEN?
        :TRANS:OUTP:DATA <START>,<END>
        :TRANS:OUTP:DATA?
        :TRANS:CLOSE?
    """

    def __init__(self, connection):
        self.conn = connection

    # =========================================================
    # Descarga completa
    # =========================================================
    def download(self, dest_path: str, start: int = 1, end: int | None = None):
        """
        Descarga los datos capturados del GL100 y los guarda en un archivo binario.

        Args:
            dest_path (str): ruta del archivo local donde guardar.
            start (int): punto inicial de lectura.
            end (int): punto final de lectura (si no se especifica, hasta el final).
        """
        logger.info(f"[GL100Capture] Descargando datos a {dest_path}...")

        self.conn.send(':TRANS:SOUR DISK,"/"')
        ok = self.conn.query(":TRANS:OPEN?")
        if "OK" not in ok.upper():
            logger.error(f"[GL100Capture] Error al abrir medio: {ok}")
            return None

        # Determinar tamaño total si no se indica END
        if end is None:
            total = self.conn.query(":TRANS:OUTP:SIZE?")
            try:
                end = int(total.strip())
            except Exception:
                end = start + 1000  # fallback

        # Solicitar rango
        self.conn.send(f":TRANS:OUTP:DATA {start},{end}")
        raw = self.conn.receive(65536)

        # Guardar a archivo local
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(raw)

        self.conn.send(":TRANS:CLOSE?")
        logger.info("[GL100Capture] Descarga completada.")
        return dest_path

    # =========================================================
    # 📖 Lectura directa
    # =========================================================
    def read_header(self):
        """Lee los metadatos del archivo actual (orden de canales, tipos, etc.)."""
        header = self.conn.query(":TRANS:OUTP:HEAD?")
        logger.debug(f"[GL100Capture] Cabecera recibida:\n{header}")
        return header
