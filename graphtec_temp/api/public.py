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

from graphtec.connection import GraphtecConnection
from graphtec.core.device import GraphtecDevice
from graphtec.io.realtime import GraphtecRealtime
from graphtec.io.capture import GraphtecCapture
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
            #! Se deja en la arquitectura conexión LAN para futuras actualizaciones si se desea.
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
    def connect(self):#*Testeado
        """Abre la conexión con el GL100."""
        self.conn.open()
        self.connected = True
        logger.info(f"[Graphtec] Conectado vía {self.conn_type.upper()}")

        #Inicializar dispositivo
        #self.channels = self.update_channels()

    def disconnect(self):#*Testeado
        """Cierra la conexión con el GL100."""
        if not self.connected:
            logger.warning("[Graphtec] Desconexión ignorada: no hay conexión activa.")
            return
        self.conn.close()
        self.connected = False
        logger.info("[Graphtec] Conexión cerrada correctamente.")

    def is_connected(self) -> bool:#*Testeado
        """Devuelve True si hay conexión activa."""
        return self.connected
    

    # =========================================================
    # Funcionalidades comunes
    # =========================================================
    def get_id(self):#*Testeado
        """Devuelve el ID del dipositivo."""
        return self.device.common.get_id()
    
    def save_settings(self):
        """Guarda la configuración en la memoria del dispositivo."""
        return self.device.common.save_settings()
    
    def clear(self):
        """Limpia el estado interno (buffer,errores, etc)"""
        return self.device.common.clear()
    
    
    
    # =========================================================
    # Configuración y gestión de canales
    # =========================================================
    def get_channels(self):#*Testeado
        """Devuelve la configuración de los canales."""
        return self.device.amp.get_channels()
    
    def set_channel(self, channel: int, ch_type:str="", ch_input:str="", ch_range:str=""):#*Testeado
        """
        Configura el tipo de un canal:
        Args:
            channel (int): Número de canal (1-4).
            ch_type (str): Tipo de canal ("VOLT", "TEMP", etc).
        
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
        START / STOP / OFF
        """
        return self.device.trigger.set_trigger(status)
    
    def get_trigger(self):
        """Devuelve el estado del trigger."""
        return self.device.trigger.get_trigger()
    
    def set_trigger_source(self, source,datetime=""):
        """
        Configura la fuente del trigger.
        AMP
        ALAR
        DATE
        """
        return self.device.trigger.set_trigger_source(source,datetime)
    
    def get_trigger_source(self):
        """Devuelve la fuente del trigger."""
        return self.device.trigger.get_trigger_source()
    
    def set_trigger_comb(self,logic):
        """Para el trigger en LEVEL, se emplea AND o OR"""
        return self.device.trigger.set_trigger_comb(logic)
    
    def set_trigger_channel(self,ch,mode,value=""):
        """Configura el canal del trigger."""
        return self.device.trigger.set_trigger_channel(ch,mode,value)
    
    def get_trigger_channel(self,ch):
        """Devuelve la configuración del canal del trigger."""
        return self.device.trigger.get_trigger_channel(ch)
    
    def set_pretrigger(self,level):
        """Configura el nivel de pretrigger."""
        return self.device.trigger.set_pretrigger(level)
    
    def get_pretrigger(self):
        """Devuelve el nivel de pretrigger."""
        return self.device.trigger.get_pretrigger()
    
    def get_trigger_comb(self):
        """Devuelve la combinación lógica del trigger."""
        return self.device.trigger.get_trigger_comb()
    

    # =========================================================
    # Configuración de Logic
    # =========================================================
    def set_logic_type(self,mode):
        """Configura el modo lógico de todos los canales."""
        return self.device.logic.set_logic_type(mode)
    
    def get_logic_type(self):
        """Devuelve el modo lógico de todos los canales."""
        return self.device.logic.get_logic_type()
    
    def set_logic(self,channel:int,mode:str):
        """Configura el modo lógico de un canal específico."""
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
        """Configura el modo de alarma."""
        return self.device.alarm.set_alarm_mode(mode)
    
    def set_alarm_level(self, channel, mode, level):
        """Configura el nivel de alarma para un canal específico."""
        return self.device.alarm.set_alarm_level(channel, mode, level)

    def get_alarm(self):
        """Devuelve el estado de la alarma."""
        return self.device.alarm.get_alarm_mode()
    
    def get_alarm_level(self, channel):
        """Devuelve el nivel de alarma de un canal específico."""
        return self.device.alarm.get_alarm_level(channel)
    

    # =========================================================
    # Configuración de parámetros de captura de datos
    # =========================================================
    def set_data_location(self, location:str):
        """Configura la localización de los datos."""
        return self.device.data.set_data_location(location)
    
    def set_data_destination(self, dest:str):
        """Configura el destino de los datos."""
        return self.device.data.set_data_destination(dest)
    
    def set_data_size(self, size:int):
        """Configura el tamaño de memoria para datos."""
        return self.device.data.set_data_size(size)
    
    def set_data_submode(self, mode:str):
        """PEAK, AVE, RMS"""
        return self.device.data.set_data_submode(mode)
    
    def set_data_sub(self, status:str):
        """ON/OFF del Data Sub"""
        return self.device.data.set_data_sub(status)
    
    def set_sampling(self, sample:int):
        """Configura la tasa de muestreo."""
        return self.device.data.set_data_sampling(sample)
    
    def get_sampling(self) -> int:
        """Devuelve la tasa de muestreo configurada."""
        return self.device.data.get_data_sampling()
    
    def set_capture_mode(self, mode:str):
        """Configura el modo de captura de datos."""
        return self.device.data.set_data_capture_mode(mode)
    
    def get_capture_mode(self) -> str:
        """Devuelve el modo de captura de datos configurado."""
        return self.device.data.get_data_capture_mode()
    

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
    def get_power_voltage(self):
        """Devuelve el estado de voltaje de la batería."""
        return self.device.status.get_power_voltage()
    
    def get_power_source(self):
        """Devuelve la fuente de alimentación actual."""
        return self.device.status.get_power_source()
    
    def get_power_status(self):
        """Devuelve el estado de alimentación."""
        return self.device.status.get_power_status()
    
    def get_status(self):
        """Devuelve el estado general del dispositivo."""
        return self.device.status.get_status()
    
    def get_info(self):
        """Devuelve la información del dispositivo."""
        return self.device.status.get_info()
    
    def get_communication_status(self):
        """Devuelve el estado de comunicación."""
        return self.device.status.get_communication_status()
    
    def get_sensor_status(self):
        """Devuelve el estado de los sensores."""
        return self.device.status.get_sensor_status()
    
    def get_error_status(self):
        """Devuelve el estado de errores."""
        return self.device.status.get_error_status()
    

    # =========================================================
    # Opciones del dispositivo
    # =========================================================
    def reset_fabric(self,option):
        """Restaura la configuración de fábrica."""
        return self.device.option.reset_fabric(option)
    
    def set_name(self,name):
        """Configura el nombre del dispositivo."""
        name = f'"{name}"'
        return self.device.option.set_name(name)
    
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
    
    def set_screen_eco(self,mode):
        """Configura el modo de ahorro de pantalla."""
        return self.device.option.set_screen_eco(mode)
    
    def set_temp_unit(self,unit):
        """Configura la unidad de temperatura."""
        return self.device.option.set_temp_unit(unit)
    
    def set_burnout(self,mode):
        """Configura el modo burnout."""
        return self.device.option.set_burnout(mode)
    
    def set_acc_unit(self,unit):
        """Configura la unidad de acelerómetro."""
        return self.device.option.set_acc_unit(unit)
    
    def set_room_temp(self,mode):
        """
        Configura la corrección de la temperatura del entorno.
        ON es INTERNO // OFF es Externo
        """
        return self.device.option.set_room_temp(mode)
    
    def get_name(self):
        """Devuelve el nombre del dispositivo."""
        return self.device.option.get_name()
    
    def get_datetime(self):
        """Devuelve la fecha y hora del dispositivo."""
        return self.device.option.get_datetime()
    
    def get_screen_eco(self):
        """Devuelve el modo de ahorro de pantalla."""
        return self.device.option.get_screen_eco()
    
    def get_temp_unit(self):
        """Devuelve la unidad de temperatura."""
        return self.device.option.get_temp_unit()
    
    def get_burnout(self):
        """Devuelve el modo burnout."""
        return self.device.option.get_burnout()
    
    def get_acc_unit(self):
        """Devuelve la unidad de acelerómetro."""
        return self.device.option.get_acc_unit()
    
    def get_room_temp(self):
        """Devuelve el idioma del dispositivo."""
        return self.device.option.get_room_temp()
    

    # =========================================================
    # Configuración de la interfaz de comunicación
    # =========================================================
    def set_baudrate(self, baud):
        """Configura el baudrate de la conexión serie."""
        return self.device.interface.set_baudrate(baud)
    
    def set_parity(self, parity):
        """Configura la paridad de la conexión serie."""
        return self.device.interface.set_parity(parity)
    
    def set_databits(self, n):
        """Configura los databits de la conexión serie."""
        return self.device.interface.set_databits(n)
    
    def set_stopbits(self, n):
        """Configura los stopbits de la conexión serie."""
        return self.device.interface.set_stopbits(n)
    
    def set_flow(self, flow):
        """Configura el flujo de la conexión serie."""
        return self.device.interface.set_flow(flow)
    
    def set_timeout(self, timeout):
        """Configura el timeout de la conexión."""
        return self.device.interface.set_timeout(timeout)
    
    def set_nlcode(self, nlcode):
        """Configura el NLCode de la conexión."""
        return self.device.interface.set_nlcode(nlcode)
    
    def get_baudrate(self):
        """Devuelve el baudrate de la conexión serie."""
        return self.device.interface.get_baudrate()
    
    def get_parity(self):
        """Devuelve la paridad de la conexión serie."""
        return self.device.interface.get_parity()
    
    def get_databits(self):
        """Devuelve los databits de la conexión serie."""
        return self.device.interface.get_databits()
    
    def get_stopbits(self):
        """Devuelve los stopbits de la conexión serie."""
        return self.device.interface.get_stopbits()
    
    def get_flow(self):
        """Devuelve el flujo de la conexión serie."""
        return self.device.interface.get_flow()
    
    def get_timeout(self):
        """Devuelve el timeout de la conexión."""
        return self.device.interface.get_timeout()
    
    def get_nlcode(self):
        """Devuelve el NLCode de la conexión."""
        return self.device.interface.get_nlcode()
    
