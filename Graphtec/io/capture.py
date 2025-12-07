import os
import re
import csv
import struct
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GraphtecCapture:
    """
    Descarga archivos GBD del GL100 usando TRANS y genera:

        <nombre>/
            <nombre>.hdr   (header ASCII del GBD)
            <nombre>.bin   (datos puros concatenados, 16-bit big-endian)
            <nombre>.gbd   (GBD reconstruido según especificación oficial)
            <nombre>.csv   (timestamp + valores en unidades físicas)

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
    def list_files(self, path="\\MEM\\LOG\\", long=True, filt="OFF"):
        """
        Lista archivos en un directorio del dispositivo (DISK).

        Args:
            path (str): ruta en el Graphtec, ej. "\\MEM\\LOG\\"
            long (bool): formato LONG (con tamaño/fecha) o SHORT
            filt (str|OFF): filtrar por extensión ("GBD") o OFF

        Returns:
            list[str]: nombres de archivo (sin carpetas)
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

        # Obtener list
        raw = self.conn.query(":FILE:LIST?")

        if not isinstance(raw, str):
            try:
                raw = raw.decode("ascii", errors="ignore")
            except Exception:
                logger.error("[GraphtecCapture] list_files recibió datos no ASCII")
                return []

        return self._parse_file_list(raw)

    @staticmethod
    def _parse_file_list(list_text: str):
        """
        Extrae los nombres entre comillas.
        Ignora carpetas (terminan en '\').
        """
        if not list_text:
            return []

        if isinstance(list_text, bytes):
            list_text = list_text.decode("ascii", errors="ignore")

        items = re.findall(r'"([^"]+)"', list_text)
        if not items:
            return []

        clean = []
        for it in items:
            if it.endswith("\\"):  # carpeta
                continue
            clean.append(it.split()[0])  # solo nombre limpio

        return clean

    # ============================================================
    # PIPELINE COMPLETO: HDR + BIN + GBD + CSV
    # ============================================================
    def download_file(self, path_in_gl: str, dest_folder: str):
        """
        Descarga un archivo de medida del GL100 vía TRANS y genera:
          - .hdr (header ASCII)
          - .bin (datos puros 16-bit big-endian)
          - .gbd (archivo GBD reconstruido, compatible con el software oficial)
          - .csv (datos en unidades físicas)

        Args:
            path_in_gl (str): ruta completa en el GL100, p.ej. "\\MEM\\LOG\\251130-110423.GBD"
            dest_folder (str): carpeta local destino.
        """
        base = os.path.basename(path_in_gl)
        name_no_ext = os.path.splitext(base)[0]

        out_dir = os.path.join(dest_folder, name_no_ext)
        os.makedirs(out_dir, exist_ok=True)

        hdr_path = os.path.join(out_dir, name_no_ext + ".hdr")
        bin_path = os.path.join(out_dir, name_no_ext + ".bin")
        gbd_path = os.path.join(out_dir, name_no_ext + ".GBD")
        csv_path = os.path.join(out_dir, name_no_ext + ".csv")

        logger.info(f"[GraphtecCapture] Descargando {path_in_gl} → {out_dir}")

        # 1) Seleccionar archivo como fuente de TRANS
        self.conn.send(f':TRANS:SOUR DISK,"{path_in_gl}"')

        # 2) Abrir TRANS
        resp = self.conn.query(":TRANS:OPEN?")
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
            # Cerrar TRANS antes de salir
            self.conn.send(":TRANS:CLOSE?")
            self.conn.read_ascii()
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

        # 6) Reconstruir GBD: header + padding + datos
        gbd_bytes = self._build_gbd_file(header_text, data_bytes, header_siz)
        with open(gbd_path, "wb") as fgbd:
            fgbd.write(gbd_bytes)
        logger.info(f"[GraphtecCapture] GBD reconstruido guardado en {gbd_path}")

        # 7) Generar CSV en unidades físicas
        self._data_to_csv(
            data_bytes=data_bytes,
            csv_path=csv_path,
            order=order,
            counts=counts,
            start_dt=start_dt,
            delta=sample_delta,
            amp_info=amp_info,
            spans=spans,
            module=module,
        )
        logger.info(f"[GraphtecCapture] CSV generado en {csv_path}")

        # 8) Cerrar TRANS
        self.conn.send(":TRANS:CLOSE?")
        self.conn.read_ascii()

        return {
            "folder": out_dir,
            "hdr": hdr_path,
            "bin": bin_path,
            "gbd": gbd_path,
            "csv": csv_path,
        }

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
        if not isinstance(block, bytes):
            raise RuntimeError("[GraphtecCapture] HEAD devolvió datos no binarios.")

        block = self._strip_noise(block)
        if not block.startswith(b"#"):
            raise ValueError("[GraphtecCapture] HEAD inválido (no empieza por '#').")

        nd = int(block[1:2])          # siempre '6'
        strlen = int(block[2:2 + nd]) # 6 dígitos de longitud
        text = block[2 + nd:2 + nd + strlen]
        return text.decode("ascii", errors="ignore")

    # ============================================================
    # PARSERS DE HEADER (GBD File Specification)
    # ============================================================
    @staticmethod
    def _extract_header_size(hdr: str) -> int:
        """
        HeaderSiz = 4096

        Tamaño de la región de cabecera en el fichero GBD
        (múltiplo de 2048).
        """
        m = re.search(r"HeaderSiz\s*=\s*(\d+)", hdr)
        return int(m.group(1)) if m else 4096

    @staticmethod
    def _extract_order(hdr: str):
        """
        Extrae Order del bloque $$Data del header GBD.

        $$Data
          Format    = BinaryData
          Type      = BigEndian, Short, Setup
          Order     = CH1  , CH2  , CH3  , CH4  , Logic, Alarm1 , AlarmLP, AlarmOut
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
        Sample = 500ms, 1s, 10m, etc.
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
        return timedelta(seconds=1)

    @staticmethod
    def _extract_start_datetime(hdr: str):
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
    def _extract_amp_info(hdr: str):
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
        amp = {}
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
    def _extract_spans(hdr: str):
        """
        Bloque $$Span:

          CH1        =  -10000, +10000
          CH2        =  -10000, +10000
          ...

        Devuelve:
            {"CH1": (-10000, 10000), ...}
        """
        spans = {}
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

            if not isinstance(block, bytes):
                # Si algo raro pasa, lo ignoramos y salimos
                logger.error("[GraphtecCapture] TRANS:OUTP:DATA? devolvió datos no binarios.")
                break

            data = self._extract_binary_data(block)
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
    # EXTRAER DATA PURA DE UN BLOQUE #6******
    # ============================================================
    def _extract_binary_data(self, block: bytes) -> bytes:
        """
        Bloque DATA (según Data Reception):

          "#6******" + STATUS(2) + DATA(N) + CHECKSUM(2)

        Donde ****** = N (tamaño de DATA).

        Esta función devuelve solo DATA.
        """
        block = self._strip_noise(block)

        if not block.startswith(b"#"):
            # ascii inesperado
            try:
                text = block.decode("ascii", errors="ignore").strip()
            except Exception:
                text = "?"
            logger.warning(f"[GraphtecCapture] bloque ascii recibido: {text}")
            return b""

        nd = int(block[1:2])          # '6'
        strlen = int(block[2:2 + nd]) # longitud de DATA en bytes
        offset = 2 + nd
        remaining = len(block) - offset

        # HEAD no tiene status/checksum: remaining == strlen
        if remaining == strlen:
            return block[offset:offset + strlen]

        # DATA: STATUS(2) + DATA(strlen) + CHECKSUM(2)
        if remaining >= strlen + 4:
            offset += 2  # saltar STATUS
            return block[offset:offset + strlen]

        logger.warning("[GraphtecCapture] bloque truncado.")
        return b""

    @staticmethod
    def _strip_noise(block: bytes) -> bytes:
        """
        Busca el primer '#' y descarta basura anterior.
        """
        idx = block.find(b"#")
        return block[idx:] if idx != -1 else block

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
    # CONVERSIÓN FÍSICA (GS-4VT Y RESTO)
    # ============================================================
    @staticmethod
    def _convert_4vt_voltage(raw_val: int, rng: str) -> float:
        """
        Conversión EXACTA según "2.2 Binary translation of voltage data
        of 4ch voltage temperature (GS-4VT)".

        1) Escalado base (1, 2, 5)
        2) Ajuste de punto decimal (V)

        Se asume que queremos siempre la salida en Voltios.
        """
        rng_norm = (rng or "").upper().replace(" ", "")

        # Factor base (1 / 2 / 4)
        base_factor = None
        # Rangos base '1': 100mV / 1V / 10V
        if rng_norm in ("100MV", "1V", "10V"):
            base_factor = 2
        # Rangos base '2': 20mV / 200mV / 2V / 20V
        elif rng_norm in ("20MV", "200MV", "2V", "20V"):
            base_factor = 1
        # Rangos base '5': 50mV / 500mV / 5V / 50V / 1-5V
        elif rng_norm in ("50MV", "500MV", "5V", "50V", "1-5V", "1TO5V", "1-5VDC"):
            base_factor = 4

        if base_factor is None:
            # Rango desconocido → devolvemos raw sin escalar
            return float(raw_val)

        # Ajuste de punto decimal (siempre a V)
        dec_factor = None
        if rng_norm == "20MV":
            dec_factor = 1_000_000
        elif rng_norm in ("50MV", "100MV", "200MV"):
            dec_factor = 100_000
        elif rng_norm in ("500MV", "1V", "2V"):
            dec_factor = 10_000
        elif rng_norm in ("5V", "10V", "20V", "1-5V", "1TO5V", "1-5VDC"):
            dec_factor = 1_000
        elif rng_norm == "50V":
            dec_factor = 100

        if dec_factor is None:
            return float(raw_val)

        return raw_val / (base_factor * dec_factor)

    def _convert_value(self, module, inp, rng, span, raw_val):
        """
        Conversión física unificada para todos los módulos GL100.

        - GS-4VT: fórmulas oficiales (sin spans)
        - Resto: conversión lineal por spans + ajustes heurísticos
        """
        module = (module or "UNKNOWN").upper()
        inp = (inp or "").upper()
        rng = (rng or "").upper()

        # ---------------------- GS-4VT ---------------------------
        if module.startswith("GS-4VT"):
            if inp in ("DC", "DC_V", "V", "VT", "MV"):
                return self._convert_4vt_voltage(raw_val, rng)

            # Temperatura por termopar (2.3 Temperature data):
            # [Temperature (°C)] = [Temperature data] / 10
            if inp == "TEMP":
                return raw_val / 10.0

            # Logic / Pulse / Alarm → devolver raw
            return float(raw_val)

        # ---------------------- Resto de módulos -----------------
        smin, smax = span

        # Conversión lineal Graphtec en unidades de ingeniería del span
        phys = smin + ((raw_val + 32768) * (smax - smin) / 65535.0)

        # GS-TH
        if module.startswith("GS-TH"):
            if inp == "TEMP":
                return phys / 100.0
            if inp in ("HUM", "HUMID", "RH"):
                return phys / 100.0
            if inp == "DEW":
                return phys / 100.0
            return phys

        # GS-3AT
        if module.startswith("GS-3AT"):
            if inp == "ACC":
                return phys / 1000.0
            if inp == "TEMP":
                return phys / 100.0
            return phys

        # GS-LXUV
        if module.startswith("GS-LXUV"):
            if inp in ("LUX", "UV"):
                return phys / 1000.0
            return phys

        # GS-CO2
        if module.startswith("GS-CO2"):
            return phys

        # GS-DPA-AC
        if module.startswith("GS-DPA-AC"):
            if "A" in inp:
                return phys / 1000.0
            return phys

        # GS-4TSR
        if module.startswith("GS-4TSR"):
            return phys / 100.0

        return phys

    def _convert_row_physical(self, module, order, raw_row, amp_info, spans):
        """
        Convierte una fila de datos crudos (lista de enteros 16-bit)
        en unidades físicas, respetando el Order del header.
        """
        out = []
        for name, raw_val in zip(order, raw_row):
            n = name.strip()

            # No canal (Logic, Alarm, etc.) → dejar raw
            if not n.startswith("CH"):
                out.append(raw_val)
                continue

            span = spans.get(n, (0, 1))
            info = amp_info.get(n, {})
            inp = info.get("input") or ""
            rng = info.get("range") or ""

            val = self._convert_value(
                module=module,
                inp=inp,
                rng=rng,
                span=span,
                raw_val=raw_val,
            )
            out.append(val)

        return out

    def _build_column_names_with_units(self, order, amp_info):
        cols = []
        for n in order:
            name = n.strip()
            if not name.startswith("CH"):
                cols.append(name)
                continue

            info = amp_info.get(name, {})
            inp = (info.get("input") or "").upper()

            if inp == "TEMP":
                cols.append(f"{name}_C")
            elif inp in ("DC", "DC_V", "V", "VT", "MV"):
                cols.append(f"{name}_V")
            elif inp == "ACC":
                cols.append(f"{name}_G")
            elif inp in ("HUM", "HUMID", "RH"):
                cols.append(f"{name}_RH")
            else:
                cols.append(name)

        return cols

    # ============================================================
    # GENERACIÓN DEL CSV
    # ============================================================
    def _data_to_csv(
        self,
        data_bytes: bytes,
        csv_path: str,
        order,
        counts: int,
        start_dt,
        delta,
        amp_info,
        spans,
        module,
    ):
        """
        Convierte data_bytes (pure data, 16-bit big-endian) en CSV.
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

        rows_phys = []
        for i in range(n_samples):
            base = i * bytes_per_sample
            raw_row = struct.unpack_from(f">{n_items}h", data_bytes, base)
            phys_row = self._convert_row_physical(module, order, raw_row, amp_info, spans)
            rows_phys.append(phys_row)

        # timestamps
        if start_dt is None:
            timestamps = ["" for _ in range(n_samples)]
        else:
            timestamps = [start_dt + i * delta for i in range(n_samples)]

        cols = self._build_column_names_with_units(order, amp_info)

        # escribir CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["TimeStamp"] + cols)
            for ts, row in zip(timestamps, rows_phys):
                if ts == "":
                    w.writerow([""] + list(row))
                else:
                    w.writerow([ts.isoformat()] + list(row))  # type: ignore
