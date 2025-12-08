import os
import re
import csv
import struct
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any

from graphtec.io.decoder import (
    parse_head_block,
    extract_trans_data_block,
    convert_row_physical,
    build_column_names_with_units,
)

logger = logging.getLogger(__name__)

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None  # type: ignore


class GraphtecCapture:
    """
    Descarga archivos de medida del GL100 vía TRANS y genera:

        <nombre>/
            <nombre>.hdr   (header ASCII del GBD)
            <nombre>.bin   (datos puros concatenados, 16-bit big-endian)
            <nombre>.GBD   (GBD reconstruido según especificación oficial)
            <nombre>.csv   (timestamp + valores en unidades físicas)
            <nombre>.xlsx  (igual que CSV pero en Excel)

    Basado en:
      - GL100 Data Reception Specifications (TRANS / #6****** / status / checksum)
      - GL100 GBD File Specification Sheet (HeaderSiz, secciones Header/Data)
      - Binary translation of voltage data of 4ch voltage temperature (GS-4VT)
    """

    def __init__(self, connection):
        self.conn = connection

    # ============================================================
    # LISTADO DE ARCHIVOS
    # ============================================================
    def list_files(self, path: str = "\\MEM\\LOG\\", long: bool = True, filt: str = "OFF") -> List[str]:
        """
        Lista archivos en un directorio del dispositivo (DISK).

        Args:
            path: ruta en el Graphtec, ej. "\\MEM\\LOG\\"
            long: formato LONG (con tamaño/fecha) o SHORT
            filt: filtrar por extensión ("GBD") o "OFF"

        Returns:
            Lista de nombres de archivo (sin carpetas).
        """
        # Cambiar de carpeta
        self.conn.send(f':FILE:CD "{path}"')

        # Seleccionar formato de salida
        form = "LONG" if long else "SHORT"
        self.conn.send(f":FILE:LIST:FORM {form}")

        # Filtro
        if isinstance(filt, str) and filt.upper() != "OFF":
            ext = filt.strip()
            if not ext.startswith('"'):
                ext = f'"{ext}"'
            self.conn.send(f":FILE:LIST:FILT {ext}")
        else:
            self.conn.send(":FILE:LIST:FILT OFF")

        # Obtener listado
        raw = self.conn.query(":FILE:LIST?")

        if not isinstance(raw, str):
            try:
                raw = raw.decode("ascii", errors="ignore")
            except Exception:
                logger.error("[GraphtecCapture] list_files recibió datos no ASCII")
                return []

        return self._parse_file_list(raw)

    @staticmethod
    def _parse_file_list(list_text: str) -> List[str]:
        """
        Extrae los nombres entre comillas.
        Ignora carpetas (terminan en '\\').
        """
        if not list_text:
            return []

        if isinstance(list_text, bytes):
            list_text = list_text.decode("ascii", errors="ignore")

        items = re.findall(r'"([^"]+)"', list_text)
        if not items:
            return []

        clean: List[str] = []
        for it in items:
            if it.endswith("\\"):  # carpeta
                continue
            clean.append(it.split()[0])  # solo nombre limpio

        return clean

    # ============================================================
    # API PÚBLICA DE DESCARGA
    # ============================================================
    def download_file(self, path_in_gl: str, dest_folder: str) -> Optional[Dict[str, str]]:
        """
        Descarga un archivo de medida del GL100 y genera:

          - .hdr (header ASCII)
          - .bin (datos puros 16-bit big-endian)
          - .GBD (archivo GBD reconstruido, compatible con el software oficial)


        Args:
            path_in_gl: ruta completa en el GL100, p.ej. "\\MEM\\LOG\\251130-110423.GBD"
            dest_folder: carpeta local destino.
        """
        core = self._download_core(path_in_gl, dest_folder)
        if core is None:
            return None

        folder = core["folder"]
        base_name = core["base_name"]
        hdr_path = core["hdr_path"]
        bin_path = core["bin_path"]
        header_text = core["header_text"]
        data_bytes = core["data_bytes"]
        header_siz = core["header_siz"]

        gbd_path = os.path.join(folder, base_name + ".GBD")
        gbd_bytes = self._build_gbd_file(header_text, data_bytes, header_siz)
        with open(gbd_path, "wb") as fgbd:
            fgbd.write(gbd_bytes)
        logger.info(f"[GraphtecCapture] GBD reconstruido guardado en {gbd_path}")

        return {
            "folder": folder,
            "hdr": hdr_path,
            "bin": bin_path,
            "gbd": gbd_path,
        }

    def download_csv(self, path_in_gl: str, dest_folder: str) -> Optional[Dict[str, str]]:
        """
        Descarga un archivo de medida del GL100 y genera:

          - .hdr (header ASCII)
          - .bin (datos puros 16-bit big-endian)
          - .csv (datos en unidades físicas)

        NO genera GBD ni Excel.
        """
        core = self._download_core(path_in_gl, dest_folder)
        if core is None:
            return None

        folder = core["folder"]
        base_name = core["base_name"]
        hdr_path = core["hdr_path"]
        bin_path = core["bin_path"]

        csv_path = os.path.join(folder, base_name + ".csv")

        self._data_to_csv(
            data_bytes=core["data_bytes"],
            csv_path=csv_path,
            order=core["order"],
            counts=core["counts"],
            start_dt=core["start_dt"],
            delta=core["sample_delta"],
            amp_info=core["amp_info"],
            spans=core["spans"],
            module=core["module"],
        )
        logger.info(f"[GraphtecCapture] CSV generado en {csv_path}")

        return {
            "folder": folder,
            "hdr": hdr_path,
            "bin": bin_path,
            "csv": csv_path,
        }

    def download_excel(self, path_in_gl: str, dest_folder: str) -> Optional[Dict[str, str]]:
        """
        Descarga un archivo de medida del GL100 y genera:

          - .hdr (header ASCII)
          - .bin (datos puros 16-bit big-endian)
          - .xlsx (datos en unidades físicas, formato Excel)

        NO genera GBD ni CSV.
        """
        if Workbook is None:
            raise RuntimeError(
                "openpyxl no está instalado. "
                "Instala 'openpyxl' para poder usar download_excel()."
            )

        core = self._download_core(path_in_gl, dest_folder)
        if core is None:
            return None

        folder = core["folder"]
        base_name = core["base_name"]
        hdr_path = core["hdr_path"]
        bin_path = core["bin_path"]

        xlsx_path = os.path.join(folder, base_name + ".xlsx")

        self._data_to_excel(
            data_bytes=core["data_bytes"],
            xlsx_path=xlsx_path,
            order=core["order"],
            counts=core["counts"],
            start_dt=core["start_dt"],
            delta=core["sample_delta"],
            amp_info=core["amp_info"],
            spans=core["spans"],
            module=core["module"],
        )
        logger.info(f"[GraphtecCapture] Excel generado en {xlsx_path}")

        return {
            "folder": folder,
            "hdr": hdr_path,
            "bin": bin_path,
            "xlsx": xlsx_path,
        }

    # ============================================================
    # PIPELINE CORE: TRANS + HEADER + DATA
    # ============================================================
    def _download_core(self, path_in_gl: str, dest_folder: str) -> Optional[Dict[str, Any]]:
        """
        Lógica común de descarga vía TRANS:

          - Abre TRANS.
          - Lee header y lo guarda (.hdr).
          - Parsear metadatos (Order, Counts, Sample, Start, Amp, Span, UnitOrder).
          - Descarga datos puros y los guarda (.bin).
          - Cierra TRANS.

        Devuelve un diccionario con toda la info necesaria para
        generar GBD, CSV o Excel.
        """
        base = os.path.basename(path_in_gl)
        base_name = os.path.splitext(base)[0]

        out_dir = os.path.join(dest_folder, base_name)
        os.makedirs(out_dir, exist_ok=True)

        hdr_path = os.path.join(out_dir, base_name + ".hdr")
        bin_path = os.path.join(out_dir, base_name + ".bin")

        logger.info(f"[GraphtecCapture] Descargando {path_in_gl} → {out_dir}")

        # 1) Seleccionar archivo como fuente de TRANS
        self.conn.send(f':TRANS:SOUR DISK,"{path_in_gl}"')

        # 2) Abrir TRANS
        resp = self.conn.query(":TRANS:OPEN?")
        logger.debug(f"[GraphtecCapture] Respuesta apertura Trans: {resp}")
        ok = False
        if isinstance(resp, bytes) and len(resp) == 3:
            # bit 0 de tercer byte = error
            ok = not (resp[2] & 0x01)
        elif isinstance(resp, str):
            ok = "OK" in resp.upper()

        if not ok:
            logger.error(f"[GraphtecCapture] TRANS:OPEN? falló → {resp}")
            return None

        logger.info("[GraphtecCapture] TRANS abierto correctamente.")

        try:
            # 3) Leer header TRANS → .hdr
            header_text = self._read_header_trans()
            with open(hdr_path, "w", encoding="utf-8") as f:
                f.write(header_text)
            logger.info(f"[GraphtecCapture] Header guardado en {hdr_path}")

            # 4) Parsear metadatos del header
            order = self._extract_order(header_text)
            counts = self._extract_counts(header_text)
            sample_delta = self._extract_sample_delta(header_text)
            start_dt = self._extract_start_datetime(header_text)
            amp_info = self._extract_amp_info(header_text)
            spans = self._extract_spans(header_text)
            module = self._extract_module(header_text)
            header_siz = self._extract_header_size(header_text)

            if not order or counts <= 0:
                logger.error("[GraphtecCapture] Header sin Order o Counts válidos.")
                return None

            bytes_per_sample = len(order) * 2
            total_bytes_expected = counts * bytes_per_sample

            logger.info(
                "[GraphtecCapture] order=%s, counts=%d, bytes/row=%d, module=%s",
                order,
                counts,
                bytes_per_sample,
                module,
            )

            # 5) Descargar datos puros → .bin (sin cabecera #6, ni status, ni checksum)
            data_bytes = self._download_data_bytes(counts, bytes_per_sample)

            with open(bin_path, "wb") as fout_bin:
                fout_bin.write(data_bytes)
            logger.info(
                "[GraphtecCapture] BIN guardado en %s (%d bytes, esperado %d bytes)",
                bin_path,
                len(data_bytes),
                total_bytes_expected,
            )

            return {
                "folder": out_dir,
                "base_name": base_name,
                "hdr_path": hdr_path,
                "bin_path": bin_path,
                "header_text": header_text,
                "data_bytes": data_bytes,
                "order": order,
                "counts": counts,
                "sample_delta": sample_delta,
                "start_dt": start_dt,
                "amp_info": amp_info,
                "spans": spans,
                "module": module,
                "header_siz": header_siz,
            }

        finally:
            # 6) Cerrar TRANS siempre
            self.conn.send(":TRANS:CLOSE?")
            try:
                self.conn.read_ascii()
            except Exception:
                pass

    # ============================================================
    # LECTURA DEL HEADER TRANS (#6****** + header ASCII)
    # ============================================================
    def _read_header_trans(self) -> str:
        """
        Recibe el header vía :TRANS:OUTP:HEAD?.

        Formato (según Data Reception Specs):
            "#6******" + HEADER_ASCII

        Sin status ni checksum.
        """
        block = self.conn.query(":TRANS:OUTP:HEAD?")
        logger.debug(f"[GraphtecCapture] Bloque HEAD recibido: {block}")
        if not isinstance(block, bytes):
            raise RuntimeError("[GraphtecCapture] HEAD devolvió datos no binarios.")

        return parse_head_block(block)

    # ============================================================
    # PARSERS DE HEADER (GBD File Specification)
    # ============================================================
    @staticmethod
    def _extract_header_size(hdr: str) -> int:
        """
        HeaderSiz = tamaño de la región de cabecera en el fichero GBD
        (múltiplo de 2048). Por defecto, 4096.
        """
        m = re.search(r"HeaderSiz\s*=\s*(\d+)", hdr)
        return int(m.group(1)) if m else 4096

    @staticmethod
    def _extract_order(hdr: str) -> List[str]:
        """
        Extrae Order del bloque $$Data del header GBD.
        """
        m = re.search(
            r"\$\$Data(.*?)(?:\$\$|\$EndHeader)",
            hdr,
            flags=re.DOTALL | re.MULTILINE,
        )
        if not m:
            return []

        data_block = m.group(1)

        m2 = re.search(
            r"^\s*Order\s*=\s*(.+)$",
            data_block,
            flags=re.MULTILINE,
        )
        if not m2:
            return []

        raw = m2.group(1)
        return [x.strip() for x in raw.split(",") if x.strip()]

    @staticmethod
    def _extract_counts(hdr: str) -> int:
        m = re.search(r"Counts\s*=\s*(\d+)", hdr)
        return int(m.group(1)) if m else 0

    @staticmethod
    def _extract_sample_delta(hdr: str) -> timedelta:
        """
        Sample = 500ms, 1s, 10m, 1h, etc.
        """
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
        if unit.startswith("h"):
            return timedelta(hours=val)
        return timedelta(seconds=1)

    @staticmethod
    def _extract_start_datetime(hdr: str) -> Optional[datetime]:
        m = re.search(r"Start\s*=\s*([0-9\-]+)\s*,\s*([0-9:]+)", hdr)
        if not m:
            return None
        try:
            return datetime.strptime(
                m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            return None

    @staticmethod
    def _extract_amp_info(hdr: str) -> Dict[str, Dict[str, str]]:
        """
        Bloque $Amp:

          CH1        = VT   , DC   ,       5V, Off   ,    Off,      +0
          CH2        = VT   , DC   ,       5V, Off   ,    Off,      +0
          ...

        Devuelve:
            {
              "CH1": {"type": "VT", "input": "DC", "range": "5V"},
              ...
            }
        """
        amp: Dict[str, Dict[str, str]] = {}
        for ch in ["CH1", "CH2", "CH3", "CH4"]:
            m = re.search(
                rf"{ch}\s*=\s*([^,\n]+),\s*([^,\n]+),\s*([^,\n]+),.*",
                hdr,
            )
            if m:
                amp[ch] = {
                    "type": m.group(1).strip(),
                    "input": m.group(2).strip(),
                    "range": m.group(3).strip(),
                }
        return amp

    @staticmethod
    def _extract_spans(hdr: str) -> Dict[str, Tuple[int, int]]:
        """
        Bloque $$Span:

          CH1        =  -10000, +10000
          CH2        =  -10000, +10000
          ...

        Devuelve:
            {"CH1": (-10000, 10000), ...}
        """
        spans: Dict[str, Tuple[int, int]] = {}
        for ch in ["CH1", "CH2", "CH3", "CH4"]:
            m = re.search(rf"{ch}\s*=\s*(-?\d+)\s*,\s*\+?(-?\d+)", hdr)
            if m:
                spans[ch] = (int(m.group(1)), int(m.group(2)))
        return spans

    @staticmethod
    def _extract_module(hdr: str) -> str:
        """
        UnitOrder = 4VT
        -> "GS-4VT", etc.
        """
        m = re.search(r"UnitOrder\s*=\s*([A-Za-z0-9\-\_]+)", hdr)
        if not m:
            return "UNKNOWN"

        raw = m.group(1).strip().upper()

        mapping = {
            "4VT": "GS-4VT",
            "4TSR": "GS-4TSR",
            "3AT": "GS-3AT",
            "TH": "GS-TH",
            "LXUV": "GS-LXUV",
            "CO2": "GS-CO2",
            "DPA-AC": "GS-DPA-AC",
            "DPAC": "GS-DPA-AC",
        }

        return mapping.get(raw, raw)

    # ============================================================
    # DESCARGA DE DATOS PUROS (BIN) VÍA TRANS
    # ============================================================
    def _download_data_bytes(self, counts: int, bytes_per_sample: int) -> bytes:
        """
        Descarga la región de datos completa usando:

            :TRANS:OUTP:DATA <START>,<END>
            :TRANS:OUTP:DATA?

        y devuelve exclusivamente la parte de datos (Data) de los
        bloques #6****** (sin status ni checksum), concatenada.

        Se asegura de no devolver más de counts * bytes_per_sample bytes.
        """
        target_bytes = counts * bytes_per_sample
        buf = bytearray()

        first = 1
        chunk_samples = 1000  # tamaño razonable

        while first <= counts and len(buf) < target_bytes:
            last = min(first + chunk_samples - 1, counts)
            self.conn.send(f":TRANS:OUTP:DATA {first},{last}")
            block = self.conn.query(":TRANS:OUTP:DATA?")
            logger.debug(
                f"[GraphtecCapture] Bloque DATA recibido ({first}-{last}): {block}"
            )

            if not isinstance(block, bytes):
                logger.error(
                    "[GraphtecCapture] TRANS:OUTP:DATA? devolvió datos no binarios."
                )
                break

            data, status, checksum_ok = extract_trans_data_block(block)

            if not data:
                logger.warning(
                    "[GraphtecCapture] Bloque DATA vacío en rango %d-%d, deteniendo descarga.",
                    first,
                    last,
                )
                break

            buf.extend(data)

            first = last + 1

        # Ajustar a tamaño esperado
        if len(buf) > target_bytes:
            logger.warning(
                "[GraphtecCapture] Recibidos %d bytes, truncando a %d bytes.",
                len(buf),
                target_bytes,
            )
            buf = buf[:target_bytes]
        elif len(buf) < target_bytes:
            logger.warning(
                "[GraphtecCapture] Recibidos solo %d bytes (esperados %d).",
                len(buf),
                target_bytes,
            )

        return bytes(buf)

    # ============================================================
    # RECONSTRUCCIÓN DE GBD
    # ============================================================
    def _build_gbd_file(self, header_text: str, data_bytes: bytes, header_siz: int) -> bytes:
        """
        Reconstruye un archivo GBD:

          [Header region] + [Padding hasta HeaderSiz] + [Data region]

        Header region: texto ASCII tal cual devuelto por HEAD.
        Padding: espacios (0x20) hasta HeaderSiz bytes totales.
        """
        header_bytes = header_text.encode("ascii", errors="ignore")

        if len(header_bytes) > header_siz:
            logger.warning(
                "[GraphtecCapture] header_bytes (%d) > HeaderSiz (%d). "
                "Guardando sin recortar (puede no ser estándar).",
                len(header_bytes),
                header_siz,
            )
            padded = header_bytes
        else:
            pad_len = header_siz - len(header_bytes)
            padded = header_bytes + b" " * pad_len

        return padded + data_bytes

    # ============================================================
    # DECODIFICAR DATA → TABLA (timestamps + columnas + filas)
    # ============================================================
    def _decode_to_table(
        self,
        data_bytes: bytes,
        order: List[str],
        counts: int,
        start_dt: Optional[datetime],
        delta: timedelta,
        amp_info: Dict[str, Dict[str, str]],
        spans: Dict[str, Tuple[int, int]],
        module: str,
    ) -> Tuple[List[Optional[datetime]], List[str], List[List[Optional[float]]]]:
        """
        Convierte data_bytes (pure data, 16-bit big-endian) en una tabla:

            - lista de timestamps (o None)
            - lista de nombres de columna
            - lista de filas físicas

        Esta función es común para CSV y Excel.
        """
        n_items = len(order)
        bytes_per_sample = n_items * 2

        total_bytes = len(data_bytes)
        max_samples_from_bytes = total_bytes // bytes_per_sample
        n_samples = min(counts, max_samples_from_bytes)

        if max_samples_from_bytes < counts:
            logger.warning(
                "[GraphtecCapture] Solo hay datos para %d muestras (header indicaba %d).",
                max_samples_from_bytes,
                counts,
            )

        rows_phys: List[List[Optional[float]]] = []
        for i in range(n_samples):
            base = i * bytes_per_sample
            raw_row = struct.unpack_from(f">{n_items}h", data_bytes, base)
            phys_row = convert_row_physical(
                module=module,
                order=order,
                raw_row=raw_row,
                amp_info=amp_info,
                spans=spans,
            )
            rows_phys.append(phys_row)

        # timestamps
        if start_dt is None:
            timestamps: List[Optional[datetime]] = [None for _ in range(n_samples)]
        else:
            timestamps = [start_dt + i * delta for i in range(n_samples)]

        cols = build_column_names_with_units(order, amp_info)

        return timestamps, cols, rows_phys

    # ============================================================
    # GENERACIÓN DEL CSV
    # ============================================================
    def _data_to_csv(
        self,
        data_bytes: bytes,
        csv_path: str,
        order: List[str],
        counts: int,
        start_dt: Optional[datetime],
        delta: timedelta,
        amp_info: Dict[str, Dict[str, str]],
        spans: Dict[str, Tuple[int, int]],
        module: str,
    ) -> None:
        """
        Genera un CSV a partir de los datos crudos y la metadata.
        """
        timestamps, cols, rows_phys = self._decode_to_table(
            data_bytes=data_bytes,
            order=order,
            counts=counts,
            start_dt=start_dt,
            delta=delta,
            amp_info=amp_info,
            spans=spans,
            module=module,
        )

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["TimeStamp"] + cols)
            for ts, row in zip(timestamps, rows_phys):
                if ts is None:
                    w.writerow([""] + list(row))
                else:
                    w.writerow([ts.isoformat()] + list(row))

    # ============================================================
    # GENERACIÓN DEL EXCEL
    # ============================================================
    def _data_to_excel(
        self,
        data_bytes: bytes,
        xlsx_path: str,
        order: List[str],
        counts: int,
        start_dt: Optional[datetime],
        delta: timedelta,
        amp_info: Dict[str, Dict[str, str]],
        spans: Dict[str, Tuple[int, int]],
        module: str,
    ) -> None:
        """
        Genera un Excel (.xlsx) a partir de los datos crudos y la metadata.
        """
        if Workbook is None:
            raise RuntimeError(
                "openpyxl no está instalado. "
                "Instala 'openpyxl' para poder usar _data_to_excel()."
            )

        timestamps, cols, rows_phys = self._decode_to_table(
            data_bytes=data_bytes,
            order=order,
            counts=counts,
            start_dt=start_dt,
            delta=delta,
            amp_info=amp_info,
            spans=spans,
            module=module,
        )

        wb = Workbook()
        ws = wb.active
        if ws is not None:
            ws.title = "Data"

            # Cabecera
            ws.append(["TimeStamp"] + cols)

            # Filas
            for ts, row in zip(timestamps, rows_phys):
                ts_str = ts.isoformat() if ts is not None else ""
                ws.append([ts_str] + list(row))

        wb.save(xlsx_path)
