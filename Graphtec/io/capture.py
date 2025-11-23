import os
import re
import csv
import struct
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class GL100Capture:
    """
    descarga archivos gbd del gl100 y genera:
        <nombre>/
            <nombre>.gbd   (bloques trans crudos)
            <nombre>.hdr   (header trans)
            <nombre>.bin   (data pura concatenada)
            <nombre>.csv   (timestamp + valores en unidades físicas)
    """

    def __init__(self, connection):
        self.conn = connection

    # ============================================================
    # list files
    # ============================================================
    def list_files(self, path="\\MEM\\LOG\\", long=True, filt="OFF"):
        """
        Lista archivos en un directorio del GL100.

        Args:
            path (str): ruta en el GL100, ej. "\\MEM\\LOG\\"
            long (bool): formato LONG (con tamaño/fecha) o SHORT
            filt (str|OFF): filtrar por extensión ("GBD") o OFF

        Returns:
            list[str]: nombres de archivo (sin carpetas)
        """

        # 1) Cambiar de carpeta
        self.conn.send(f':FILE:CD "{path}"')

        self.conn.send(f':FILE:LIST?')
        print(self.conn.receive_line())
        
        # 2) Seleccionar formato de salida
        form = "LONG" if long else "SHORT"
        self.conn.send(f":FILE:LIST:FORM {form}")

        # 3) Filtro
        if isinstance(filt, str) and filt.upper() != "OFF":
            ext = filt.strip()
            if not ext.startswith('"'):
                ext = f'"{ext}"'
            self.conn.send(f":FILE:LIST:FILT {ext}")
        else:
            self.conn.send(":FILE:LIST:FILT OFF")

        # 4) Obtener texto list
        raw = self.conn.query(":FILE:LIST?")

        if not isinstance(raw, str):
            try:
                raw = raw.decode("ascii", errors="ignore")
            except Exception:
                logger.error("[GL100Capture] list_files recibió datos no ASCII")
                return []

        return self._parse_file_list(raw)


    @staticmethod
    def _parse_file_list(list_text: str):
        """
        Parser original adaptado.
        Extrae los nombres entre comillas.
        Ignora carpetas (terminan en '\').
        """

        if not list_text:
            return []

        # asegurar que es str
        if isinstance(list_text, bytes):
            list_text = list_text.decode("ascii", errors="ignore")

        items = re.findall(r'"([^"]+)"', list_text)
        if not items:
            return []

        clean = []
        for it in items:
            if it.endswith("\\"):   # carpeta
                continue
            clean.append(it.split()[0])  # solo nombre limpio

        return clean


    # ============================================================
    # descarga completa (gbd + hdr + bin + csv)
    # ============================================================
    def download_file(self, path_in_gl: str, dest_folder: str):
        base = os.path.basename(path_in_gl)
        name_no_ext = os.path.splitext(base)[0]

        out_dir = os.path.join(dest_folder, name_no_ext)
        os.makedirs(out_dir, exist_ok=True)

        gbd_path = os.path.join(out_dir, name_no_ext + ".GBD")
        hdr_path = os.path.join(out_dir, name_no_ext + ".hdr")
        bin_path = os.path.join(out_dir, name_no_ext + ".bin")
        csv_path = os.path.join(out_dir, name_no_ext + ".csv")

        logger.info(f"[GL100Capture] Descargando {path_in_gl} → {out_dir}")

        # 1) seleccionar archivo
        self.conn.send(f':TRANS:SOUR DISK,"{path_in_gl}"')

        # 2) abrir trans
        resp = self.conn.query(":TRANS:OPEN?")
        ok = False
        if isinstance(resp, bytes) and len(resp) == 3:
            ok = not (resp[2] & 0x01)
        elif isinstance(resp, str):
            ok = "OK" in resp.upper()

        if not ok:
            logger.error(f"TRANS:OPEN? falló → {resp}")
            return None

        logger.info("TRANS abierto correctamente.")

        # 3) leer header trans
        header_text = self._read_header_trans()
        with open(hdr_path, "w", encoding="utf-8") as f:
            f.write(header_text)
        logger.info(f"Header guardado en {hdr_path}")

        # 4) parsear metadatos reales
        order = self._extract_order(header_text)
        counts = self._extract_counts(header_text)
        sample_delta = self._extract_sample_delta(header_text)
        start_dt = self._extract_start_datetime(header_text)

        amp_info = self._extract_amp_info(header_text)
        spans = self._extract_spans(header_text)

        if not order or counts <= 0:
            logger.error("header sin order o counts válidos.")
            return None

        bytes_per_sample = len(order) * 2
        logger.info(f"order={order}, samples={counts}, bytes/row={bytes_per_sample}")

        # 5) guardar gbd crudo (bloques sin tocar)
        with open(gbd_path, "wb") as fout_gbd:
            self._download_full_gbd(fout_gbd, counts)
        logger.info(f"GBD guardado en {gbd_path}")

        # 6) guardar data pura en bin
        with open(bin_path, "wb") as fout_bin:
            self._download_data_only(fout_bin, counts)
        logger.info(f"BIN guardado en {bin_path}")

        # 7) generar csv con timestamps y unidades físicas
        self._bin_to_csv(
            bin_path=bin_path,
            csv_path=csv_path,
            order=order,
            bytes_per_sample=bytes_per_sample,
            counts=counts,
            start_dt=start_dt,
            delta=sample_delta,
            amp_info=amp_info,
            spans=spans,
        )
        logger.info(f"CSV generado en {csv_path}")

        # 8) cerrar trans
        self.conn.send(":TRANS:CLOSE?")
        self.conn.read_ascii()

        return {
            "folder": out_dir,
            "gbd": gbd_path,
            "hdr": hdr_path,
            "bin": bin_path,
            "csv": csv_path
        }

    # ============================================================
    # leer header trans (#6xxxxxx ascii)
    # ============================================================
    def _read_header_trans(self) -> str:
        block = self.conn.query(":TRANS:OUTP:HEAD?")
        if not isinstance(block, bytes):
            raise RuntimeError("HEAD devolvió datos no binarios.")

        block = self._strip_noise(block)
        if not block.startswith(b"#"):
            raise ValueError("HEAD inválido (no empieza por '#').")

        nd = int(block[1:2])
        strlen = int(block[2:2 + nd])
        text = block[2 + nd:2 + nd + strlen]
        return text.decode("ascii", errors="ignore")

    # ============================================================
    # parsers de header
    # ============================================================
    @staticmethod
    def _extract_order(hdr: str):
        # capturar bloque entre order y sample (multi-línea)
        m = re.search(r"Order\s*=\s*(.+?)\n\s*Sample", hdr, flags=re.DOTALL)
        if not m:
            return []
        raw = m.group(1)
        return [x.strip() for x in raw.split(",")]

    @staticmethod
    def _extract_counts(hdr: str):
        m = re.search(r"Counts\s*=\s*(\d+)", hdr)
        return int(m.group(1)) if m else 0

    @staticmethod
    def _extract_sample_delta(hdr: str) -> timedelta:
        m = re.search(r"Sample\s*=\s*([0-9]+)\s*([a-zA-Z]+)", hdr)
        if not m:
            return timedelta(seconds=1)
        val = int(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith("ms"):
            return timedelta(milliseconds=val)
        if unit.startswith("s"):
            return timedelta(seconds=val)
        if unit.startswith("m"):
            return timedelta(minutes=val)
        return timedelta(seconds=1)

    @staticmethod
    def _extract_start_datetime(hdr: str):
        m = re.search(r"Start\s*=\s*([0-9\-]+)\s*,\s*([0-9:]+)", hdr)
        if not m:
            return None
        try:
            return datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    @staticmethod
    def _extract_amp_info(hdr: str):
        """
        parsea bloque $Amp:
            CH1 = VT , TEMP , 10V, Off , TC_K, +0
        devuelve dict:
            {"CH1": {"type":"VT","input":"TEMP","range":"10V","tc":"TC_K"}, ...}
        """
        amp = {}
        for ch in ["CH1", "CH2", "CH3", "CH4"]:
            m = re.search(rf"{ch}\s*=\s*([^,\n]+),\s*([^,\n]+),\s*([^,\n]+),.*", hdr)
            if m:
                amp[ch] = {
                    "type": m.group(1).strip(),
                    "input": m.group(2).strip(),
                    "range": m.group(3).strip(),
                }
        return amp

    @staticmethod
    def _extract_spans(hdr: str):
        """
        parsea $$Span:
            CH1 = -2000, +20000
        devuelve dict {"CH1": (-2000, 20000), ...}
        """
        spans = {}
        for ch in ["CH1", "CH2", "CH3", "CH4"]:
            m = re.search(rf"{ch}\s*=\s*(-?\d+)\s*,\s*\+?(-?\d+)", hdr)
            if m:
                spans[ch] = (int(m.group(1)), int(m.group(2)))
        return spans

    # ============================================================
    # descarga gbd completo (bloques crudos)
    # ============================================================
    def _download_full_gbd(self, fout, total):
        first = 1
        chunk = 1000
        while first <= total:
            last = min(first + chunk - 1, total)
            self.conn.send(f":TRANS:OUTP:DATA {first},{last}")
            block = self.conn.query(":TRANS:OUTP:DATA?")
            fout.write(block)
            first = last + 1

    # ============================================================
    # descarga solo data pura para bin
    # ============================================================
    def _download_data_only(self, fout, total):
        first = 1
        chunk = 1000
        while first <= total:
            last = min(first + chunk - 1, total)
            self.conn.send(f":TRANS:OUTP:DATA {first},{last}")
            block = self.conn.query(":TRANS:OUTP:DATA?")
            data = self._extract_binary_data(block)
            fout.write(data)
            first = last + 1

    # ============================================================
    # extraer data pura de un bloque #6xxxxxx
    # ============================================================
    def _extract_binary_data(self, block: bytes) -> bytes:
        block = self._strip_noise(block)

        if not block.startswith(b"#"):
            # ascii inesperado
            try:
                text = block.decode("ascii", errors="ignore").strip()
            except Exception:
                text = "?"
            logger.warning(f"[GL100Capture] bloque ascii recibido: {text}")
            return b""

        nd = int(block[1:2])
        strlen = int(block[2:2 + nd])
        offset = 2 + nd
        remaining = len(block) - offset

        # caso a: solo data
        if remaining == strlen:
            return block[offset:offset + strlen]

        # caso b: status + data + checksum
        if remaining >= strlen + 4:
            offset += 2  # saltar status
            return block[offset:offset + strlen]

        logger.warning("[GL100Capture] bloque truncado.")
        return b""

    @staticmethod
    def _strip_noise(block: bytes) -> bytes:
        idx = block.find(b"#")
        return block[idx:] if idx != -1 else block

    # ============================================================
    # conversión física por tipo (opción b)
    # ============================================================
    def _convert_row_physical(self, order, raw_row, amp_info, spans):
        out = []
        for name, raw_val in zip(order, raw_row):
            n = name.strip()

            # alarmas u otros → sin conversión
            if not n.startswith("CH"):
                out.append(raw_val)
                continue

            # si no hay span, devolver crudo
            if n not in spans:
                out.append(raw_val)
                continue

            smin, smax = spans[n]

            # conversión lineal graphtec en unidades de ingeniería del span
            phys = smin + ((raw_val + 32768) * (smax - smin) / 65535)

            # ajustar según tipo/rango si hace falta
            info = amp_info.get(n, {})
            inp = (info.get("input") or "").upper()
            rng = (info.get("range") or "").upper()

            # temp → el span ya está en ºc según gl100
            if inp == "TEMP":
                out.append(phys / 100.0 if abs(smax) > 1000 else phys)  # heurística típica graphtec
                continue

            # dc / voltaje → span ya está en voltios o milivoltios
            if inp in ("DC", "DC_V", "V"):
                # si el rango es mV, pasamos a voltios
                if "MV" in rng:
                    out.append(phys / 1000.0)
                else:
                    out.append(phys / 1000.0 if abs(smax) > 1000 else phys)
                continue

            # acc, humid, etc. quedan como phys
            out.append(phys)

        return out

    def _build_column_names_with_units(self, order, amp_info):
        cols = []
        for n in order:
            if not n.startswith("CH"):
                cols.append(n.strip())
                continue

            info = amp_info.get(n.strip(), {})
            inp = (info.get("input") or "").upper()
            rng = (info.get("range") or "").upper()

            if inp == "TEMP":
                cols.append(f"{n.strip()}_C")
            elif inp in ("DC", "DC_V", "V"):
                cols.append(f"{n.strip()}_V")
            elif inp == "ACC":
                cols.append(f"{n.strip()}_G")
            else:
                cols.append(n.strip())

        return cols

    # ============================================================
    # generar csv final
    # ============================================================
    def _bin_to_csv(
        self,
        bin_path,
        csv_path,
        order,
        bytes_per_sample,
        counts,
        start_dt,
        delta,
        amp_info,
        spans,
    ):
        with open(bin_path, "rb") as f:
            raw = f.read()

        # leer filas crudas
        rows_raw = []
        pos = 0
        for _ in range(counts):
            if pos + bytes_per_sample > len(raw):
                break
            row = []
            for i in range(len(order)):
                val = struct.unpack_from(">h", raw, pos + i * 2)[0]
                row.append(val)
            rows_raw.append(row)
            pos += bytes_per_sample

        # convertir a físicas
        rows_phys = [
            self._convert_row_physical(order, r, amp_info, spans)
            for r in rows_raw
        ]

        # timestamps
        if start_dt is None:
            timestamps = ["" for _ in range(len(rows_phys))]
        else:
            timestamps = [start_dt + i * delta for i in range(len(rows_phys))]

        cols = self._build_column_names_with_units(order, amp_info)

        # escribir csv limpio
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["TimeStamp"] + cols)
            for ts, row in zip(timestamps, rows_phys):
                if ts == "":
                    w.writerow([""] + row)
                else:
                    w.writerow([ts.isoformat()] + row)
