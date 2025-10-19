import serial
from core.logger import get_logger
from typing import Dict, Optional, Any, List
import struct
import time
import re
import os 
import csv

#Inicializa logger
logger = get_logger("DEBUG")

#Función auxiliar

def _decode_special(raw: int):
    """
    Interpreta valores especiales del GL100 según el manual 'Data Reception Specifications'.
    Estos valores indican estados de error o condiciones especiales del canal.
    """
    if raw == 0x7fff:   # Error de cálculo
        return None, "CalcError"
    if raw == 0x7ffe:   # Canal apagado (OFF)
        return None, "Off"
    if raw == 0x7ffd:   # Termopar quemado (burnout)
        return None, "Burnout"
    if raw == 0x7ffc:   # +FS (fuera de rango positivo)
        return None, "OverFS"
    if raw == -0x7fff:  # -FS (fuera de rango negativo)
        return None, "UnderFS"
    return raw, None

# Clase Principal
class gl:
    """
    Clase de comunicación con el registrador de datos GRAPHTEC GL100-N.
    Implementa los comandos SCPI documentados en 'GL100 IF Command Manual'
    y funciones de transferencia binaria según 'Data Reception Specifications'.
    """

    ###! Constructor
    def __init__(self, id, port="COM3", bytesize=8, parity='N', stopbits=1,
                baudrate=38400, timeout=1.0, write_timeout=1.0):
        self.id = id
        self.port = port
        # Abre puerto serie con parámetros del dispositivo
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            write_timeout=write_timeout
        )
        # Diccionario con la configuración de canales detectados
        self.channels: Dict[int, Dict[str, str]] = {}

        # Establece salto de línea CR+LF (requerido por Windows y SCPI)
        try:
            self.send_command(":IF:NLCODE CR_LF")
            time.sleep(0.15)
        except Exception:
            pass

    ###! Funciones de envío y recepción de comandos
    def send_command(self, cmd: str):
        """
        Envía un comando SCPI al GL100.
        Agrega CR+LF si no está incluido y lo escribe por el puerto serie.
        """
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        logger.debug(f"[{self.id}] >> {cmd.rstrip()}")
        if self.serial:
            self.serial.write(cmd.encode("ascii"))


    def read_response(self) -> Optional[str]:
        """
        Lee una línea ASCII de respuesta del GL100 (modo texto).
        Utilizado con comandos de tipo 'Query' (terminan en '?').
        """
        if self.serial:
            response = self.serial.readline().decode("ascii", errors="ignore").strip()
            if response:
                logger.debug(f"[{self.id}] << {response}")
            else:
                logger.debug(f"[{self.id}] << <no data>")
            return response
        return None


    def read_until_idle(self, idle_ms: int = 800, overall_ms: int = 10000) -> str:
        """
        Lee datos ASCII hasta que el dispositivo queda inactivo por `idle_ms` milisegundos.
        Útil para respuestas largas como :FILE:LIST?.
        """
        if not self.serial:
            return ""

        out = bytearray()
        deadline = time.time() + overall_ms / 1000.0
        last_activity = time.time()

        while time.time() < deadline:
            waiting = self.serial.in_waiting if hasattr(self.serial, "in_waiting") else 0
            if waiting:
                out += self.serial.read(waiting)
                last_activity = time.time()
            else:
                # Si no llega nada por un tiempo, se detiene
                if (time.time() - last_activity) * 1000 >= idle_ms:
                    break
                time.sleep(0.02)

        text = out.decode("ascii", errors="ignore").strip()
        if text:
            logger.debug(f"[{self.id}] << {text}")
        return text


    def read_binary_response(self) -> bytes:
        """
        Lee una respuesta binaria del tipo #6xxxxxx... utilizada en:
        :MEAS:OUTP:ONE? o :TRANS:OUTP:DATA?
        """
        def read_exact(n: int) -> bytes:
            """Lee exactamente n bytes, lanzando TimeoutError si no llegan todos."""
            buf = bytearray()
            while len(buf) < n:
                if not self.serial:
                    raise RuntimeError("Puerto serie no inicializado o cerrado")
                chunk = self.serial.read(n - len(buf))
                if not chunk:
                    raise TimeoutError(f"Timeout leyendo {n} bytes; recibidos {len(buf)}")
                buf += chunk
            return bytes(buf)

        # Espera el prefijo '#' que indica inicio del bloque binario
        first = read_exact(1)
        while first != b"#":
            first = read_exact(1)

        # Número de dígitos que indica la longitud del bloque
        ndigits_b = read_exact(1)
        if not ndigits_b.isdigit():
            raise ValueError(f"Formato inválido: # seguido de {ndigits_b!r}")
        nd = int(ndigits_b.decode())

        # Leer la longitud y los datos binarios
        length_str = read_exact(nd).decode()
        length = int(length_str)
        payload = read_exact(length)

        # Leer el final (CRLF o vacío)
        if self.serial is not None:
            tail = self.serial.read(2)
        if tail not in (b"", b"\r\n"):
            logger.debug(f"Tail no-CRLF tras bloque: {tail!r}")

        logger.debug(f"[{self.id}] << [binario {len(payload)} bytes]")
        return payload

    ##! Funciones de decodificacion
    def decode_payload(self, payload: bytes) -> Dict[str, Any]:
        """
        Decodifica un paquete binario recibido de :MEAS:OUTP:ONE?.
        Convierte los datos crudos según el tipo de canal configurado.
        """
        result = {}

        if not self.channels:
            raise RuntimeError("No se han detectado canales. Llama a detect_channels() primero.")

        offset = 0
        for ch, cfg in self.channels.items():
            inp = cfg["input"].upper()
            rng = cfg["range"].upper()

            if inp in ("OFF", ""):
                continue

            # ----- Sensores de temperatura tipo termopar -----
            if inp == "TEMP" and rng in ("TCT", "TCK"):
                raw = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = _decode_special(raw)
                result[f"CH{ch}_Temp_{rng}_C"] = None if val is None else val / 10.0
                if flag:
                    result[f"CH{ch}_Temp_{rng}_Flag"] = flag

            # ----- Entradas DC_V -----
            elif inp == "DC_V":
                raw = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = _decode_special(raw)
                if val is not None:
                    try:
                        result[f"CH{ch}_V"] = self._convert_voltage(val, rng)
                    except Exception:
                        result[f"CH{ch}_raw"] = val
                if flag:
                    result[f"CH{ch}_V_Flag"] = flag

            # ----- Sensor de CO2 -----
            elif inp == "CO2":
                raw = struct.unpack_from(">H", payload, offset)[0]
                offset += 2
                result[f"CH{ch}_CO2_ppm"] = raw / 4.0  # según GBD Spec p.12

            # ----- Sensor de temperatura y humedad -----
            elif inp == "TH":
                # GS-TH tiene 5 valores: Temp, Hum, Dew, AccTempH, AccTempL
                temp, rh, dew, atempH, atempL = struct.unpack_from(">5H", payload, offset)
                offset += 12  # 5 palabras = 10 bytes, pero algunos firmwares añaden 2 extra
                result[f"CH{ch}_Temp_C"] = temp / 10.0
                result[f"CH{ch}_Humidity_%"] = rh / 200.0
                result[f"CH{ch}_DewPoint_C"] = dew / 100.0
                result[f"CH{ch}_AccumTemp"] = ((atempH << 16) | atempL) / 100.0

            # ----- Cualquier otro tipo de canal -----
            else:
                raw = struct.unpack_from(">h", payload, offset)[0]
                offset += 2
                val, flag = _decode_special(raw)
                result[f"CH{ch}_raw_{inp}"] = val
                if flag:
                    result[f"CH{ch}_raw_{inp}_Flag"] = flag

        # Al final vienen banderas de estado y alarmas
        alarm, alarm_out, status = struct.unpack_from(">3H", payload, offset)
        result["Flags"] = {
            "Alarms": {f"CH{i}": bool(alarm & (1 << (i - 1))) for i in range(1, 5)},
            "AlarmOut": {"Main": bool(alarm_out & 1)},
            "Status": {
                "Recording": bool(status & (1 << 0)),
                "MemoryIO": bool(status & (1 << 1)),
                "TriggerWait": bool(status & (1 << 2)),
                "Triggered": bool(status & (1 << 3)),
                "DiskAccess": bool(status & (1 << 5)),
                "FileNumLimit": bool(status & (1 << 9)),
                "DiskCheck": bool(status & (1 << 10)),
                "Formatting": bool(status & (1 << 11)),
                "Setting": bool(status & (1 << 12)),
                "Initializing": bool(status & (1 << 13)),
                "Calibrating": bool(status & (1 << 14)),
                "Raw": status,
            },
        }
        return result


    def _convert_voltage(self, raw: int, rng: str) -> float:
        """
        Convierte un valor crudo de tensión según el rango activo.
        Fórmulas extraídas del manual 'GBD File Specification Sheet' p.6.
        """
        rng = rng.upper()

        # Determina divisor base (1,2 o 4) según rango
        if rng in ("100MV", "1V", "10V"):
            divisor = 2
        elif rng in ("20MV", "200MV", "2V", "20V"):
            divisor = 1
        elif rng in ("50MV", "500MV", "5V", "50V", "1_5V"):
            divisor = 4
        else:
            raise ValueError(f"Rango no soportado: {rng}")

        # Escala según magnitud del rango (tabla del manual)
        if rng == "20MV":
            scale = 1e6
        elif rng in ("50MV", "100MV", "200MV"):
            scale = 1e5
        elif rng in ("500MV", "1V", "2V"):
            scale = 1e4
        elif rng in ("5V", "10V", "20V", "1_5V"):
            scale = 1e3
        elif rng == "50V":
            scale = 1e2
        else:
            scale = 1.0

        # Valor final en voltios
        return raw / divisor / scale

    ###! Cierre
    def close(self):
        """Cierra el puerto serie limpiamente."""
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
                logger.debug(f"[{self.id}] Serial port closed.")
        finally:
            self.serial = None


    ###! Funcion ID
    def get_device_id(self):
        """
        Devuelve información del dispositivo vía *IDN?.
        Respuesta típica: '*IDN GRAPHTEC,GL100,0,01.45'
        """
        self.send_command("*IDN?")
        response = self.read_response()
        parsed = response.split(",") if response else []
        if parsed:
            parsed.pop(0)  # elimina 'GRAPHTEC'
        return parsed

    ###! Deteccion de canales
    def detect_channels(self):
        """
        Consulta configuración de canales activos (input/range) vía :AMP:CHx:INP? y :RANG?.
        """
        def get_last_token(resp: Optional[str]) -> str:
            if not resp:
                return ""
            resp = resp.replace(",", " ").strip()
            parts = resp.split()
            return parts[-1] if parts else ""

        self.channels.clear()
        for ch in range(1, 5):
            self.send_command(f":AMP:CH{ch}:INP?")
            inp = get_last_token(self.read_response())
            time.sleep(0.1)
            self.send_command(f":AMP:CH{ch}:RANG?")
            rng = get_last_token(self.read_response())
            time.sleep(0.1)
            self.channels[ch] = {"input": inp, "range": rng}
        return self.channels


    def read_channels(self):
        """
        Solicita una muestra instantánea de todas las entradas activas.
        Implementa el comando ':MEAS:OUTP:ONE?'.
        """
        if self.serial:
            self.serial.reset_input_buffer()
        self.send_command(":MEAS:OUTP:ONE?")
        return self.read_binary_response()

    ###! Listado de ficheros
    def list_files(self, path="\\MEM\\LOG\\", long=True, filt="OFF") -> str:
        """
        Lista los archivos almacenados en el dispositivo (memoria interna o SD).
        Usa los comandos del grupo FILE:
            - :FILE:CD "<path>"        → cambia de carpeta
            - :FILE:LIST:FORM LONG|SHORT
            - :FILE:LIST:FILT "ext" o OFF
            - :FILE:LIST?              → obtiene la lista

        Retorna la respuesta textual cruda (línea SCPI con comillas y comas).
        """
        form = "LONG" if long else "SHORT"
        if self.serial:
            self.serial.reset_input_buffer()

        # Cambia al directorio LOG y configura formato de salida
        self.send_command(f':FILE:CD "{path}"');      time.sleep(0.15)
        self.send_command(f":FILE:LIST:FORM {form}"); time.sleep(0.15)

        # Filtro: extensión o 'OFF'
        if isinstance(filt, str) and filt.upper() != "OFF":
            ext = filt.strip()
            if not (ext.startswith('"') and ext.endswith('"')):
                ext = f'"{ext}"'
            self.send_command(f":FILE:LIST:FILT {ext}")
        else:
            self.send_command(":FILE:LIST:FILT OFF")
        time.sleep(0.15)

        # Solicita la lista
        self.send_command(":FILE:LIST?")
        text = self.read_until_idle(idle_ms=800, overall_ms=10000)
        logger.debug(f"[{self.id}] << {text if text else '<no data>'}")
        return text


    @staticmethod
    def parse_file_list(list_text: str) -> List[str]:
        """
        Convierte la respuesta textual de :FILE:LIST? en una lista de nombres de archivo.
        Ejemplo:
            ':FILE:LIST "001.GBD","002.GBD","TEMP\\"'
        Retorna solo archivos, ignorando carpetas.
        """
        if not list_text:
            return []
        items = re.findall(r'"([^"]+)"', list_text)
        if not items:
            return []

        clean = []
        for it in items:
            if it.endswith("\\"):   # carpeta → se ignora
                continue
            clean.append(it.split()[0])  # extrae solo el nombre
        return clean


    def file_count_in_log(self, drive="MEM") -> int:
        """
        Devuelve el número total de archivos en la carpeta LOG del medio seleccionado.
        Comando: :FILE:NUM?
        """
        drive = drive.upper()
        base = "\\MEM\\" if drive == "MEM" else "\\SD\\"
        self.send_command(f':FILE:CD "{base}LOG\\"')
        time.sleep(0.15)
        self.send_command(":FILE:NUM?")
        resp = self.read_response() or ""
        try:
            return int(resp.replace(":FILE:NUM", "").strip())
        except Exception as e:
            logger.error(f"Error parsing file count from response '{resp}': {e}")
            return -1

    ###! Descarga de archivos gbd
    def download_gbd(self, filename: str, dest_path: str, to_csv: bool = True):
        """
        Descarga un archivo GBD del GL100 usando los comandos TRANS:
            :TRANS:SOUR DISK,"<ruta>"
            :TRANS:OPEN?
            :TRANS:OUTP:HEAD?     → encabezado ASCII
            :TRANS:OUTP:DATA?     → datos binarios
            :TRANS:CLOSE?

        Guarda los resultados en una subcarpeta con el nombre del archivo.
        Opcionalmente convierte el binario a CSV.
        """
        if not self.serial:
            raise RuntimeError("Puerto serie no inicializado")

        # Crea carpeta con el nombre del archivo (sin extensión)
        name_no_ext = os.path.splitext(filename)[0]
        folder_path = os.path.join(dest_path, name_no_ext)
        os.makedirs(folder_path, exist_ok=True)

        # Define rutas de salida (.hdr, .bin, .csv)
        hdr_path = os.path.join(folder_path, f"{name_no_ext}.hdr")
        bin_path = os.path.join(folder_path, f"{name_no_ext}.bin")
        csv_path = os.path.join(folder_path, f"{name_no_ext}.csv")

        logger.info(f"[{self.id}] Iniciando descarga de {filename}...")

        try:
            # --- Selecciona el archivo fuente (LOG) ---
            self.send_command(f':TRANS:SOUR DISK,"\\MEM\\LOG\\{filename}"')
            time.sleep(0.3)

            # --- Abre el medio de transferencia ---
            self.send_command(":TRANS:OPEN?")
            resp = self.serial.read(3)  # la respuesta son 3 bytes binarios
            if len(resp) != 3:
                raise TimeoutError(f"OPEN? incompleto: {resp!r}")
            # bit0 del tercer byte = 0 OK, 1 error
            if (resp[2] & 0x01) != 0:
                raise RuntimeError(f"TRANS:OPEN? NG: {resp!r}")
            logger.info(f"[{self.id}] Medio TRANS abierto correctamente")

            # --- Lee el encabezado ASCII ---
            self.send_command(":TRANS:OUTP:HEAD?")
            header_text = self._read_head_ascii()
            with open(hdr_path, "w", encoding="utf-8") as f:
                f.write(header_text)
            logger.info(f"[{self.id}] Encabezado guardado: {hdr_path}")

            # --- Extrae información clave del header ---
            def _counts_from_header(text):
                m = re.search(r"Counts\s*=\s*(\d+)", text)
                return int(m.group(1)) if m else 0

            def _order_from_header(text):
                m = re.search(r"Order\s*=\s*(.+)", text)
                return [x.strip() for x in m.group(1).split(",")] if m else []

            def _bytes_per_sample(order):
                b = 0
                for o in order:
                    b += 4 if o.upper().startswith(("HCH", "LCH")) else 2
                return b

            total_counts = _counts_from_header(header_text)
            order = _order_from_header(header_text)
            bytes_per = _bytes_per_sample(order)
            logger.info(f"[{self.id}] {total_counts} registros x {bytes_per} bytes")

            # --- Descarga de bloques de datos ---
            def _read_trans_block():
                """Lee un bloque binario con cabecera #6******, estado y checksum."""
                def read_exact(n):
                    buf = b""
                    while len(buf) < n:
                        if self.serial is not None:
                            chunk = self.serial.read(n - len(buf))
                        if not chunk:
                            raise TimeoutError("Timeout leyendo bloque TRANS")
                        buf += chunk
                    return buf

                if read_exact(1) != b"#":
                    raise ValueError("Bloque sin '#' inicial")
                nd = int(read_exact(1))
                length = int(read_exact(nd).decode())
                status = struct.unpack(">H", read_exact(2))[0]
                data = read_exact(length)
                checksum = struct.unpack(">H", read_exact(2))[0]
                return status, data, checksum

            # Lee en bloques (por defecto 1000 registros)
            chunk_size = 1000
            with open(bin_path, "wb") as fout:
                first = 1
                while first <= total_counts:
                    last = min(first + chunk_size - 1, total_counts)
                    self.send_command(f":TRANS:OUTP:DATA {first},{last}")
                    time.sleep(0.1)
                    self.send_command(":TRANS:OUTP:DATA?")
                    status, data, checksum = _read_trans_block()
                    fout.write(data)
                    logger.debug(f"Bloque {first}-{last} ({len(data)} bytes)")
                    first = last + 1

            logger.info(f"[{self.id}] Datos binarios guardados: {bin_path}")

        finally:
            # --- Cierra la transferencia ---
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.send_command(":TRANS:CLOSE?")
            close_resp = self.read_response() or ""
            logger.debug(f"[{self.id}] TRANS:CLOSE => {close_resp}")

        # --- Conversión opcional a CSV ---
        if to_csv:
            try:
                self._gbd_to_csv(hdr_path, bin_path, csv_path)
                logger.info(f"[{self.id}] Archivo CSV generado: {csv_path}")
            except Exception as e:
                logger.error(f"Error convirtiendo a CSV: {e}")

        return csv_path if to_csv else bin_path


    def _read_head_ascii(self) -> str:
        """
        Lee el encabezado ASCII tras :TRANS:OUTP:HEAD?.
        Formato: #6xxxxxx<texto><CRLF>
        """
        if self.serial is not None:
            c = self.serial.read(1)
            while c and c != b"#":
                c = self.serial.read(1)
            if not c:
                raise TimeoutError("No se encontró '#' en HEAD")

            ndigits = int(self.serial.read(1))
            length_str = self.serial.read(ndigits).decode("ascii")
            length = int(length_str)
            header_text = self.serial.read(length).decode("ascii", errors="ignore")
        return header_text.strip()

    ###! Conversión a CSV
    def _gbd_to_csv(self, header_file: str, bin_file: str, csv_file: str, include_alarm=True):
        """
        Convierte un archivo GBD (binario) a CSV legible.
        Se basa en la línea 'Order =' del encabezado.
        Implementa los formatos definidos en 'GBD File Specification Sheet'.
        """
        import io

        # --- 1) Lee encabezado y extrae 'Order' y 'Counts' ---
        with open(header_file, "r", encoding="utf-8") as f:
            header_text = f.read()

        m_order = re.search(r'(?mi)^\s*Order\s*=\s*(.+)$', header_text)
        if not m_order:
            raise ValueError("No se encontró la línea 'Order =' en el encabezado")

        order_tokens = [t.strip() for t in m_order.group(1).split(",") if t.strip()]
        m_counts = re.search(r'(?mi)^\s*Counts\s*=\s*(\d+)\s*$', header_text)
        counts = int(m_counts.group(1)) if m_counts else None

        # --- 2) Construye plan de columnas ---
        columns = []
        plan = []
        skip_next = False
        i = 0
        while i < len(order_tokens):
            tok = order_tokens[i]
            if skip_next:
                skip_next = False
                i += 1
                continue
            u = tok.upper()
            if u.startswith("HCH") and i + 1 < len(order_tokens) and order_tokens[i+1].upper().startswith("LCH"):
                # Combina hCH/lCH → valor de 32 bits
                ch_name = u[1:]  # quita la 'H'
                col_name = f"{ch_name}_ACC32"
                columns.append(col_name)
                plan.append(("u32", col_name))
                skip_next = True
            else:
                if not include_alarm and (u.startswith("ALARM") or u.startswith("ALARMOUT")):
                    plan.append(("u16_skip", tok))
                else:
                    columns.append(tok)
                    plan.append(("u16", tok))
            i += 1

        # --- 3) Lee binario completo ---
        with open(bin_file, "rb") as f:
            data = f.read()

        words_per_sample = len(order_tokens)
        bytes_per_sample = 2 * words_per_sample
        total_samples = len(data) // bytes_per_sample

        if counts is not None and counts != total_samples:
            logger.warning(f"Counts={counts}, bin tiene {total_samples}. Usando el menor.")
            total_samples = min(counts, total_samples)

        # --- 4) Decodifica y genera CSV ---
        def read_u16_be(buf, off): return struct.unpack_from(">H", buf, off)[0]
        def read_i16_be(buf, off): return struct.unpack_from(">h", buf, off)[0]
        def read_u32_be(buf, off): return struct.unpack_from(">I", buf, off)[0]

        with open(csv_file, "w", newline="", encoding="utf-8") as csvf:
            w = csv.writer(csvf)
            w.writerow(columns)

            for i in range(total_samples):
                base = i * bytes_per_sample
                row = []
                word_index = 0
                p = 0
                while p < len(plan):
                    kind = plan[p][0]
                    if kind == "u16":
                        off = base + word_index * 2
                        raw = read_i16_be(data, off)
                        val, _ = _decode_special(raw)
                        row.append("" if val is None else val)
                        word_index += 1
                        p += 1
                    elif kind == "u16_skip":
                        word_index += 1
                        p += 1
                    elif kind == "u32":
                        off_h = base + word_index * 2
                        off_l = base + (word_index + 1) * 2
                        hi = read_u16_be(data, off_h)
                        lo = read_u16_be(data, off_l)
                        u32 = (hi << 16) | lo
                        row.append(u32)
                        word_index += 2
                        p += 1
                w.writerow(row)


# Main de pruebas
def main():
    """
    Programa principal de prueba y ejemplo de uso:
    - Conecta al GL100
    - Identifica el dispositivo
    - Lista los archivos LOG
    - Descarga uno o más GBD y genera CSV
    """
    device = gl(id="GL_100", port="COM3", write_timeout=5.0, timeout=5.0)

    try:
        idn = device.get_device_id()
        logger.info(f"Device: {idn}")

        device.send_command(":DATA:DEST?")
        logger.info(f"DATA:DEST? => {device.read_response()}")

        # --- Lista archivos en memoria ---
        logger.info("=== Archivos en MEM/LOG (LONG) ===")
        raw_long = device.list_files("\\MEM\\LOG\\", long=True, filt=".GBD")
        files_long = device.parse_file_list(raw_long)
        for file in files_long:
            logger.info(f"- {file}")

        logger.info("=== Conteo de archivos en MEM/LOG ===")
        count = device.file_count_in_log("MEM")
        logger.info(f"Archivos: {count}")

        # --- Descarga de ejemplo ---
        flag = 0
        os.makedirs("./downloads", exist_ok=True)
        for file in files_long:
            try:
                if flag >= 2:  # (Ejemplo: omite los 2 primeros)
                    logger.info(f"Descargando {file}...")
                    device.download_gbd(file, "./downloads/")
                flag += 1
            except Exception as e:
                logger.error(f"Error descargando {file}: {e}")

    finally:
        device.close()


# Punto de entrada estándar de Python
if __name__ == "__main__":
    main()
