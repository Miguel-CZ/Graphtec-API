"""
API pública del GL100.

Ejemplo de funcionamiento:
    from graphtec import Graphtec #Importa directamente todos los módulos.

    gl = Graphtec(port="COM3") 
    gl.connect()
    gl.start_measurement()
    data = gl.read_realtime()
    gl.stop_measurement()
    gl.disconnect()

Autor: Miguel Chen Zheng
"""

from graphtec.connection  import GraphtecConnection
from graphtec.core.device import GraphtecDevice
from graphtec.io.realtime import GraphtecRealtime
from graphtec.io.capture  import GraphtecCapture
import logging
logger = logging.getLogger(__name__)


class Graphtec:
    """
    Clase fachada que encapsula todas las operaciones de alto nivel
    para interactuar con el dispositivo de Graphtec.
    """

    # =========================================================
    # Inicialización
    # =========================================================
    def __init__(self, connection_type="usb", **kwargs):
        """
        Inicializa la instancia del GL100.

        Args:
            conn_type (str): Tipo de conexión. "usb" o "lan".
            #! Se empezó la implementación con ambas opciones, pero luego se vio que el modelo no tiene
            #! conexión LAN. Se deja por si sirve en un futuro.
            **kwargs: Parámetros específicos del tipo de conexión.
                - USB: port, baudrate, timeout, etc.
                - LAN: address, tcp_port, timeout, etc.
        """
        self.conn_type = connection_type
        self.conn = GraphtecConnection(conn_type=connection_type, **kwargs)

        self.device = GraphtecDevice(self.conn)
        self.realtime = GraphtecRealtime(self.device)
        self.capture = GraphtecCapture(self.conn)
        
        self.connected = False
        self.channels = None


    # =========================================================
    # CONEXIÓN
    # =========================================================
    def connect(self):
        """Abre la conexión con el GL100."""
        self.conn.open()
        self.connected = True
        logger.info(f"[Graphtec] Conectado vía {self.conn_type.upper()}")

    def disconnect(self):
        """Cierra la conexión con el GL100."""
        if not self.connected:
            logger.warning("[Graphtec] Desconexión ignorada: no hay conexión activa.")
            return
        self.conn.close()
        self.connected = False
        logger.info("[Graphtec] Conexión cerrada correctamente.")

    def is_connected(self) -> bool:
        """Devuelve True si hay conexión activa."""
        return self.connected
    

    # =========================================================
    # Funcionalidades comunes
    # =========================================================
    def get_id(self):
        """Devuelve el ID del dipositivo."""

        logger.info("[Graphtec] Consulta de ID")
        return self.device.common.get_id()
    
    def save_settings(self):
        """Guarda la configuración en la memoria del dispositivo."""
        
        logger.info("[Graphtec] Guardado de ajustes.")
        return self.device.common.save_settings()
    
    def clear(self):
        """Limpia el estado interno (buffer,errores, etc)"""
        
        logger.info("[Graphtec] Limpieza del estado interno.")
        return self.device.common.clear()
    
    # =========================================================
    # Configuración y gestión de canales
    # =========================================================
    def get_channels(self):
        """Devuelve la configuración de los canales."""

        logger.info("[Graphtec] Consulta de canales.")
        channels = self.device.amp.get_channels()
        for channel in channels:
            logger.info(f"[Graphtec] Canal {channel}")
            for key,value in channel:
                logger.info(f"[Graphtec]\t {key}:{value}")
        return channels
    
    def set_channel(self, channel: int, ch_type:str="", ch_input:str="", ch_range:str=""):
        """
        Configura el tipo de un canal.
        Args:
            channel  (int): Número de canal (1-4).
            ch_type  (str): Tipo de canal ("DC_V", "TEMP", etc).
            ch_input (str): Entrada del canal ("VT","TC-K","TC-T",etc).
            ch_range (str): Rango de Medición ("20MV", "50MV","1V","5V",etc)
        
        Opciones de Canal:
            Sensor --  CH1  --  CH2  --  CH3  -- CH4
              TH   --  TEMP --   RH  --
              AT   --   X   --   Y   --   Z   -- 
              LU   -- ILLUM --   UV  --
              CO2  --  CO2  -- 
              AC   -- CURRENT1 -- CURRENT2 --
              TSR  --  CH1  --  CH2  --  CH3  -- CH4
              VT   --  CH1  --  CH2  --  CH3  -- CH4
            CO2_TH --  TEMP --  RH   --  CO2
            LU_TH  --  TEMP --  RH   -- ILLUM -- UV
            CO2_LU -- ILLUM --  UV   --  CO2  --
        
        Opciones de Input:
        TH / 3AT / CO2 / LXUV : No setting
        4VT: OFF / DC_V / TEMP
        4TSR: OFF / ON_A / ON_J
        AC: AC1_2 / AC1_3 / AC3_3

        Opciones de Range:
        Modulo 3AT:
            Acc. (G): 2G / 5G / 10G
            Acc. (m/s²): 20MPSS / 50MPSS / 100MPSS
        Modulo 4VT:
            DC: 20MV / 50MV / 100MV / 200MV / 500MV
                1V / 2V / 5V / 10V / 20V / 50V / 1_5V
            TEMP: TCT / TCK
        Modulo AC: 
            50A / 100A / 200A / OFF 
            (OFF solo está disponible cuando sea doble hilo monofásico)
        Modulo LXUV: 
            2000LX / 20000LX / 200000LX 
            (UV ray-> Rango fijo)
        Modulos TH / CO2 / 4TSR: No setting
                """
        #TODO limitaciones y validaciones
        if ch_type: 
            self.device.amp.set_channel_type(channel=channel,ch_type=ch_type)
        if ch_input: 
            self.device.amp.set_channel_input(channel=channel,ch_input=ch_input)
        if ch_range:
            self.device.amp.set_channel_range(channel=channel,ch_range=ch_range)

        return self.device.amp.get_channels()
    
    # =========================================================
    # Configuración de Trigger
    # =========================================================
    def set_trigger(self,status):
        """
        Configura el estado del trigger.
        Args:
            status (str): START / STOP / OFF
        """
        return self.device.trigger.set_trigger(status)
    
    def get_trigger(self):
        """Devuelve el estado del trigger."""
        return self.device.trigger.get_trigger()
    
    def set_trigger_source(self, source,datetime=""):
        """
        Configura la fuente del trigger.
        Args:
            source (str): AMP / ALAR / DATE
            datetime (str): Formato: "YYYY-MM-DD hh:mm:ss"
        """
        return self.device.trigger.set_trigger_source(source,datetime)
    
    def get_trigger_source(self):
        """Devuelve la fuente del trigger."""
        return self.device.trigger.get_trigger_source()
    
    def set_trigger_comb(self,logic):
        """
        Para el trigger en LEVEL, se emplea AND o OR
        Args:
            logic (str): AND / OR
        """
        return self.device.trigger.set_trigger_comb(logic)
    
    def get_trigger_comb(self):
        """Devuelve la combinación lógica del trigger."""
        return self.device.trigger.get_trigger_comb()
    
    def set_trigger_channel(self,channel,mode,value=""):
        """
        Configura el canal del trigger.
        Args:
            channel (int): 1-4
            mode (str): OFF / HIGH / LOW
            value (float): Valor de disparo  
        """
        return self.device.trigger.set_trigger_channel(channel,mode,value)
    
    def get_trigger_channel(self,channel):
        """Devuelve la configuración del canal del trigger."""
        return self.device.trigger.get_trigger_channel(channel)
    
    def set_pretrigger(self,level:int):
        """
        Configura el nivel de pretrigger.
        Args:
            level (int): Valor porcentual entre 0 y 100.
        """
        return self.device.trigger.set_pretrigger(level)
    
    def get_pretrigger(self):
        """Devuelve el nivel de pretrigger."""
        return self.device.trigger.get_pretrigger()

    # =========================================================
    # Configuración de Logic
    # =========================================================
    def set_logic_type(self,mode):
        """
        Configura el modo lógico de todos los canales.
        Args:
            mode (str): LOGI / PUL / OFF
        """
        return self.device.logic.set_logic_type(mode)
    
    def get_logic_type(self):
        """Devuelve el modo lógico de todos los canales."""
        return self.device.logic.get_logic_type()
    
    def set_logic(self,channel:int,mode:str):
        """
        Configura el modo lógico de un canal específico.
        Args:
            channel (int): 1-4
            mode (str): ON / INST / COUNT / OFF
        
        Opciones de mode:
        Si estamos en tipo logic -> ON / OFF
        Si estamos en tipo pulse -> INST / COUNT / OFF
        """
        return self.device.logic.set_logic(channel,mode)
    
    def get_logic(self,channel:int):
        """Devuelve el modo lógico de un canal específico."""
        return self.device.logic.get_logic(channel)
    
    def get_logics(self):
        return self.device.logic.get_logics()
    

    # =========================================================
    # Configuración de Alarmas
    # =========================================================
    def set_alarm(self, mode):
        """
        Activa/Desactiva la alarma.
        Args:
            mode (str): ON / OFF
        """
        return self.device.alarm.set_alarm_exec(mode)
    
    def get_alarm(self):
        """
        Devuelve el estado de la alarma.
        """
        return self.device.alarm.get_alarm_exec()
    
    def set_alarm_mode(self,mode):
        """
        Configura alarma por nivel o desactivado.

        Args:
            mode (mode): LEVEL / OFF
        """
        return self.device.alarm.set_alarm_mode(mode)
    
    def get_alarm_mode(self):
        """
        Devuelve el modo de la alarma.
        """
        return self.device.alarm.get_alarm_mode()
    
    def set_alarm_level(self, channel, mode, level):
        """
        Configura el nivel de alarma para un canal específico.
        Args:
            channel (int): 1-4
            mode (str): HI / LO / OFF
        """
        return self.device.alarm.set_alarm_level(channel, mode, level)

    def get_alarm_level(self, channel):
        """
        Devuelve el nivel de alarma de un canal específico.
        """
        return self.device.alarm.get_alarm_level(channel)
    
    def set_alarm_output(self,mode):
        """ 
        Configura el modo de salida de la alarma.
        Args:
            mode (str): ON / OFF
        """
        return self.device.alarm.set_alarm_output(mode)
    
    def get_alarm_output(self):
        """
        Devuelve el modo de salida de la alarma.
        """
        return self.device.alarm.get_alarm_output()
    
    # =========================================================
    # Configuración de parámetros de captura de datos
    # =========================================================
    def set_data_location(self, location:str):
        """
        Configura la localización de los datos.
        Args:
            location (str): MEM / DIRE
        
        """
        return self.device.data.set_data_location(location)
    
    def get_data_location(self):
        """Retorna la localización de los datos."""
        return self.device.data.get_data_location()
    
    def set_data_destination(self, dest:str):
        """
        Configura el destino de los datos.
        Args:
            dest (str): MEM / SD
        """
        return self.device.data.set_data_destination(dest)
    
    def get_data_destination(self):
        """retorna el destino de los datos."""
        return self.device.data.get_data_destination()

    def set_data_size(self, size:int):
        """
        Configura el tamaño de memoria para datos.
        Args:
            size (int): 16/32/64/128
        """
        return self.device.data.set_data_mem_size(size)
    
    def get_data_size(self):
        """Retorna el tamaño de los datos"""
        return self.device.data.get_data_mem_size()
    
    def set_data_submode(self, mode:str,sub_type:str):
        """
        Configura el sub-modo de datos.
        Args:
            mode: ON / OFF
            sub_type: PEAK / AVE / RMS 
        """
        return self.device.data.set_data_submode(mode,sub_type)

    def get_data_submode(self):
        """Retorna el sub-modo de datos"""
        return self.device.data.get_data_sub()
    
    def set_data_sampling(self, sample:int):
        """
        Configura la tasa de muestreo.
        Args:
            sample (int): Valor en MS o S

        Opciones de sample:\n
        Si estamos en memoria -> 5 / 10 / 20 / 50 (ms)\n
        Si estamos en directa -> 500(ms) / 1 / 2 / 5 / 10 / 20 / 30 / 
                                 60 / 120 / 300 / 600 
                                 1200 / 1800 / 3600 (s)

        """
        return self.device.data.set_data_sampling(sample)
    
    def get_data_sampling(self):
        """Devuelve la tasa de muestreo configurada."""
        return self.device.data.get_data_sampling()
    
    def set_data_capture_mode(self, mode:str):
        """
        Configura el modo de captura de datos.
        Args:
            mode (str): CONT / 1H / 24H
        """
        return self.device.data.set_data_capture_mode(mode)
    
    def get_capture_mode(self) -> str:
        """Devuelve el modo de captura de datos configurado."""
        return self.device.data.get_data_capture_mode()
    
    def get_data_filepath(self):
        """Devuelve la ruta en donde se guarda."""
        return self.device.data.get_data_filepath()
    
    def get_data_points(self):
        """Devuelve los puntos de datos capturados"""
        return self.device.data.get_data_points()

#! Debería estar bien, recordar última revision
    # =========================================================
    # Funcionalidades de lectura en tiempo real
    # =========================================================
    def read_measurement(self):
        """Lee un bloque de datos en tiempo real."""
        return self.realtime.read()
    
    def start_measurement(self):
        """Inicia la medición en tiempo real."""
        return self.device.measure.start_measurement()
    
    def stop_measurement(self):
        """Detiene la medición en tiempo real."""
        return self.device.measure.stop_measurement()
    
#! Debería estar bien, recordar última revision
    # =========================================================
    # Gestión de archivos de captura de datos
    # =========================================================
    def list_files(self, path="\\MEM\\LOG\\",long=True, filt="GBD"):
        """Lista los archivos de captura almacenados en el dispositivo."""
        return self.capture.list_files(path=path,long=long, filt=filt)

    def download_file(self, path_in_gl: str, dest_folder: str):
        """Descarga un archivo de captura desde el dispositivo.

        Args:
            filename (str): Nombre del archivo en el dispositivo.
            dest_path (str): Ruta local donde guardar el archivo.
        """
        return self.capture.download_file(path_in_gl, dest_folder)
    
    def download_csv(self, path_in_gl: str, dest_folder: str):
        """Descarga un archivo de captura desde el dispositivo.

        Args:
            filename (str): Nombre del archivo en el dispositivo.
            dest_path (str): Ruta local donde guardar el archivo.
        """
        return self.capture.download_csv(path_in_gl, dest_folder)
    
    def download_excel(self, path_in_gl: str, dest_folder: str):
        """Descarga un archivo de captura desde el dispositivo.

        Args:
            filename (str): Nombre del archivo en el dispositivo.
            dest_path (str): Ruta local donde guardar el archivo.
        """
        return self.capture.download_excel(path_in_gl, dest_folder)
    
    # =========================================================
    # Estado del dispositivo
    # =========================================================
    def get_power_status(self):
        """Devuelve el estado de alimentación."""
        return self.device.status.get_power_status()
    
    def get_status(self):
        """Devuelve el estado general del dispositivo."""
        return self.device.status.get_status_flags()
    
    def get_error_status(self):
        """Devuelve el estado de errores."""
        return self.device.status.get_error_status()
    
    def get_extended_status(self):
        """
        Devuelve el estado del dispositivo extendido.
        Cuando se ejecute el filtro, guarda los valores.
        """
        return self.device.status.get_extended_status_value()
    
    #Filtros
    def set_status_filter(self,bit_number:int,value:str):
        """
        Configuración del filtro de estado

        Args:
            bit_number (int): 0-15
            value (str): NEV / RISE / FALL / BOTH
        
        Opciones de bit_number:
            0: "REC"   ---  Capturando datos
            1: "MEM"   ---  Estado de entrada/salida en memoria
            2: "WTR"   ---  Esperando disparo
            3: "TRG"   ---  Disparado
            5: "ACS"   ---  Accediendo a disco
            9: "NUM"   ---  Se ha llegado al numero máximo de ficheros
            10: "SPC"  ---  Investigando capacidad de disco
            11: "FMT"  ---  Formateando disco
            12: "SET"  ---  Ejecutando setup
            13: "INIT" ---  Ejecutando inicialización
            14: "CAL"  ---  Ajuste del punto cero
        
        Opciones de value:
            NEV -> No hay detección
            RISE -> Flanco de subida
            FALL -> Flanco de bajada
            BOTH -> Ambos flancos
        """
        return self.device.status.set_status_filter(bit_number,value)
    
    def get_status_filter(self,bit_number):
        """
        Retorna el filtro según el número de bit.
        
        Args:
            bit_number (int): 0-15
        
        Opciones de bit_number:
            0: "REC"   ---  Capturando datos
            1: "MEM"   ---  Estado de entrada/salida en memoria
            2: "WTR"   ---  Esperando disparo
            3: "TRG"   ---  Disparado
            5: "ACS"   ---  Accediendo a disco
            9: "NUM"   ---  Se ha llegado al numero máximo de ficheros
            10: "SPC"  ---  Investigando capacidad de disco
            11: "FMT"  ---  Formateando disco
            12: "SET"  ---  Ejecutando setup
            13: "INIT" ---  Ejecutando inicialización
            14: "CAL"  ---  Ajuste del punto cero
        """
        return self.device.status.get_status_filter(bit_number)

    # =========================================================
    # Opciones del dispositivo
    # =========================================================
    def set_name(self,name):
        """
        Configura el nombre del dispositivo.

        Args:
            name (str): Nombre.
        """
        return self.device.option.set_name(name)
    
    def get_name(self):
        """Devuelve el nombre del dispositivo."""
        return self.device.option.get_name()
    
    def set_datetime(self,datetime):
        """
        Configura la fecha y hora del dispositivo.
        Formato: YYYY/MM/DD hh:mm:ss
        """
        return self.device.option.set_datetime(datetime)
    
    def set_datetime_now(self):
        """
        Configura la fecha y hora actual al dispositivo.
        """
        from datetime import datetime
        now = datetime.now()
        formatted = now.strftime('"%Y/%m/%d %H:%M:%S"')
        print(f"Ahora es: {formatted}")
        return self.device.option.set_datetime(formatted)
    
    def get_datetime(self):
        """Devuelve la fecha y hora del dispositivo."""
        return self.device.option.get_datetime()
    
    def set_screen_save(self,time):
        """
        Configura el modo de ahorro de pantalla.
        Args:
            time (str): OFF / 1 / 2 / 5 / 10 / 20 / 30 / 60 (min)
        """
        return self.device.option.set_screen_save(time)
    
    def get_screen_save(self):
        """Devuelve el modo de ahorro de pantalla."""
        return self.device.option.get_screen_save()
    
    def set_temp_unit(self,unit):
        """
        Configura la unidad de temperatura.
        
        Args:
            unit (str): CELS / FAHR
        """
        return self.device.option.set_temp_unit(unit)
    
    def get_temp_unit(self):
        """Devuelve la unidad de temperatura."""
        return self.device.option.get_temp_unit()
    
    def set_burnout(self,mode):
        """
        Configura el modo burnout.
        Args:
            mode (str): ON / OFF
        """
        return self.device.option.set_burnout(mode)
    
    def get_burnout(self):
        """Devuelve el modo burnout."""
        return self.device.option.get_burnout()
    
    def set_acc_unit(self,unit):
        """
        Configura la unidad de acelerómetro.
        Args:
            unit (str): G / MPSS
        
        Opciones de unit:
        G -> Gravedad
        MPSS -> m/s^2
        """
        return self.device.option.set_acc_unit(unit)
    
    def get_acc_unit(self):
        """Devuelve la unidad de acelerómetro."""
        return self.device.option.get_acc_unit()
    
    def set_room_temp(self,mode):
        """
        Configura la corrección de la temperatura del entorno.
        Args:
            mode (str): ON / OFF
        
        Opciones de mode:
        ON para temperatura de entorno interno
        OFF para temperatura de entorno externo
        """
        return self.device.option.set_room_temp(mode)
    
    def get_room_temp(self):
        """Devuelve el idioma del dispositivo."""
        return self.device.option.get_room_temp()
    

    # =========================================================
    # Configuración de la interfaz de comunicación
    # =========================================================
    def set_nlcode(self, code):
        """
        Configura el terminador de línea.
        Por defecto -> CRLF
        Args:
            code (str): CR_LF / CR / LF 
        """
        return self.device.interface.set_nlcode(code)
    
    def get_nlcode(self):
        """
        Devuelve el terminador de línea del dispositivo.
        """
        return self.device.interface.get_nlcode()
    
    # =========================================================
    # Gestion de archivos (FILE)
    # =========================================================
    def file_ls(self):
        """Lista archivos segun el formato/filtro configurado."""
        return self.device.file.file_ls()

    def file_ls_number(self):
        """Devuelve el numero de archivos segun la ruta actual."""
        return self.device.file.file_ls_number()

    def set_ls_format(self, fmt: str):
        """Configura el formato del listado: LONG o SHORT."""
        return self.device.file.set_ls_format(fmt)

    def get_ls_format(self):
        """Devuelve el formato del listado."""
        return self.device.file.get_ls_format()

    def set_ls_filter(self, extension: str):
        """Configura el filtro de listado por extension."""
        return self.device.file.set_ls_filter(extension)

    def get_ls_filter(self):
        """Devuelve el filtro de listado."""
        return self.device.file.get_ls_filter()

    def file_cd(self, dirpath: str = "."):
        """Cambia el directorio actual."""
        return self.device.file.file_cd(dirpath)

    def file_pwd(self):
        """Devuelve el directorio actual."""
        return self.device.file.file_pwd()

    def file_mkdir(self, dirpath: str):
        """Crea un directorio."""
        return self.device.file.file_mkdir(dirpath)

    def file_rmdir(self, dirpath: str):
        """Elimina un directorio."""
        return self.device.file.file_rmdir(dirpath)

    def file_rm(self, filepath: str):
        """Elimina un archivo."""
        return self.device.file.file_rm(filepath)

    def file_cp(self, file_source: str, file_dest: str):
        """Copia un archivo."""
        return self.device.file.file_cp(file_source, file_dest)

    def file_mv(self, file_source: str, file_dest: str):
        """Mueve o renombra un archivo."""
        return self.device.file.file_mv(file_source, file_dest)

    def get_free_space(self):
        """Devuelve el espacio libre en bytes."""
        return self.device.file.get_free_space()

    def save_file_settings(self, filepath: str):
        """Guarda la configuracion en un archivo."""
        return self.device.file.save_file_settings(filepath)

    def load_file_settings(self, filepath: str):
        """Carga la configuracion desde un archivo."""
        return self.device.file.load_file_settings(filepath)