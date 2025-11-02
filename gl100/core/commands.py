"""
Alias de comandos IF del GL100.
"""
# Comandos comunes 
GET_IDN = "*IDN?"
GET_IDN_2 = ":COMMON:IDN?"

GET_SYSTEM_INFO = ":COMMON:INFO?"
GET_DEVICE_STATE = ":STAT:ALL?"

SAVE_SETTINGS = "*SAV"
SAVE_SETTINGS_2 = ":COMMON:SAV" # Guarda la config en la EEPROM

CLEAR = "*CLS"
CLEAR_2 = ":COMMON:CLS"

GET_VERSION = ":COMMON:VER?"
GET_MODEL = ":COMMON:MODEL?"
GET_SERIES = ":COMMON:SERIAL?"

GET_GENERAL_STATUS = ":COMMON:STAT?" #Ready / Busy
RESET_GENERAL = ":COMMON:RESET"

GET_CONN_VERSION = ":IF:VER?"
GET_CONN_MAC = ":IF:MAC?"

#Opciones del sistema
RESET_FABRIC = ":OPT:INIT {mode}" #ALL o PART

SET_NAME = ":OPT:NAME {name}" # Asigna un nombre identificativo
SET_DATE = ":OPT:DATE {date}" #Formato YYYY/MM/DD,hh:mm:ss
SET_SCREEN_ECO = ":OPT:SCREENS {mode}" #ON/OFF
SET_SCREEN_BRIGHT = ":OPT:SCREENS:BRIGHT {level}" #0-10

SET_TEMP_UNIT = ":OPT:TUNIT {unit}" #C o F
SET_BURNOUT = ":OPT:BURN {mode}" # ON/OFF
SET_ACC_UNIT = ":OPT:ACCUNIT {unit}" #G m/s2

GET_NAME = ":OPT:NAME?"
GET_DATE = ":OPT:DATE?"
GET_TEMP_UNIT = ":OPT:TUNIT?"
GET_TEMP_BURNOUT = ":OPT:BURN?" 
GET_ACC_UNIT = ":OPT:ACCUNIT?"

SET_OPT_LANGUAGE = ":OPT:LANG {lang}"  # ENG, JPN
GET_OPT_LANGUAGE = ":OPT:LANG?"

#Calibración de T interna del GS-3AT
SET_OPT_TEMP_CAL = ":OPT:TEMP {value}"
GET_OPT_TEMP_CAL = ":OPT:TEMP?"


# STATUS
GET_POWER_VOLTAGE = "STAT:POW:BATTVAL?"
GET_POWER_SOURCE = ":STAT:POW:BATTSOUR?"
GET_POWER_STATUS = ":STAT:POW?"

GET_STATUS = ":STAT:COND?" #Estado de operación general: STOP,REC,ARMED,SLEEP
GET_STATUS = ":STAT:INFO?"
GET_COM_STATUS = ":STAT:COMM?"
GET_SENSOR_STATUS = ":STAT:SENSOR?"
GET_ERROR_STATUS = ":STAT:ERR?" #0: Sin error, 100: Error SD, 200: Error COMM, 300: Error de sensor, 400: Error de comando inválido

# Configuración -> Interfaz (IF)
RESET_CONN = ":IF:RESET"

SET_CONN_NLCODE =":IF:NLCODE {code}" # code: En principio CR_LF. Pero si no elegir entre CR o LF
SET_CONN_BAUDRATE = ":IF:BAUD {baud}"
SET_CONN_PARITY = ":IF:PARITY {parity}" #None / EVEN / ODD
SET_CONN_DATABITS = ":IF:DATABITS {n}"
SET_CONN_STOPBITS = ":IF:STOPBITS {n}"
SET_CONN_FLOW = ":IF:FLOW {flow}" # NONE, RTSCTS, XONXOFF
SET_CONN_TIMEOUT = ":IF:TIMEOUT {timeout}"

GET_CONN_INFO = ":IF:INFO?"
GET_CONN_TYPE = ":IF:TYPE?"
GET_CONN_STATUS = ":IF:STAT?"

GET_CONN_NLCODE = ":IF:NLCODE?"
GET_CONN_BAUDRATE = ":IF:BAUD?"
GET_CONN_PARITY = ":IF:PARITY?"
GET_CONN_DATABITS = ":IF:DATABITS?"
GET_CONN_STOPBITS = ":IF:STOPBITS?"
GET_CONN_FLOW = ":IF:FLOW?" 
GET_CONN_TIMEOUT = ":IF:TIMEOUT?"

# Configuración -> Parámetros de medición (AMP)
SET_CHANNEL_ALL = ":AMP:ALL {command}" #! Probar en profundidad. Command-> TEMP
SET_CHANNEL_ALL_RANGE = ":AMP:ALL:RANG {range}"

SET_CHANNEL_INPUT = ":AMP:CH{ch}:INP {mode}" #Tipo de entrada del canal
SET_CHANNEL_RANGE = ":AMP:CH{ch}:RANG {value}" #Rango de medida según entrada
SET_CHANNEL_TYPE =":AMP:CH{ch}:TYP {type}" # Tipo del sensor

SET_CHANNEL_CLAMP = ":AMP:CH{ch}:CLAMPM {mode}" #Modo clampeo ON/OFF
SET_CHANNEL_VOLTAGE_REF = ":AMP:CH{n}:VOLT {value}" #Valor de referencia de voltaje
SET_CHANNEL_PF = ":AMP:CH{n}:PF" #Valor del fdp para AC

SET_CHANNEL_ACC_CALIBRATE = ":AMP:CH{n}:ACCCAL:FUNC {mode}" #Estado de Calibracion del acelerómetro ON/OFF
SET_CHANNEL_ACC_CALIBRATE_EXEC = ":AMP:CH{n}:ACCCAL:EXEC" #Ejecuta la calibración del acelerómetro
SET_CHANNEL_CO2_CALIBRATE = ":AMP:CH{n}:CO2CAL" #Calibración del sensor CO2 ON/OFF

SET_CHANNEL_COUNT_HIGHLOW = ":AMP:CH{ch}:COUNT:HILO" # Configura la detección alto/bajo del contador lógico
SET_CHANNEL_COUNT_LEVEL = ":AMP:CH{ch}:COUNT:LEV" # Nivel de umbral para conteo

GET_CHANNEL_INPUT = ":AMP:CH{ch}:INP?" #Devuelve el tipo de entrada
GET_CHANNEL_RANGE = ":AMP:CH{ch}:RANG?" #Devuelve el rango
GET_CHANNEL_TYPE = ":AMP:CH{ch}:TYP?" #Devuelve el tipo de sensor

GET_CHANNEL_CLAMP = ":AMP:CH{ch}:CLAMPM?" # Estado del Clamp
GET_CHANNEL_VOLTAGE_REF = ":AMP:CH{ch}:VOLT?" #Devuelve el offset del voltaje (referencia)
GET_CHANNEL_ACC = ":AMP:CH{ch}:ACCCAL:FUNC?" #Estado de la calibración
GET_CHANNL_PF = ":AMP:CH{ch}:PF?"

#Configuración de DATA
SET_DATA_MEAS_LOCATION = ":DATA:MEAS {location}" # MEM para memoria, DIR para directa (streaming)
SET_DATA_MEMORY_SIZE = ":DATA:MEM {size}" # Auto / Sino tamaño de captura
SET_DATA_DESTINATION = ":DATA:DEST {dest}" # MEM para memoria / SD para tarjetaSD

SET_DATA_SAMPLING = ":DATA:SAMP {interval}" #10MS, 20MS, 50MS, 100MS, 200MS, 500MS, 1S, 2S, 5S, 10S, 30S, 1M, 2M, 5M, 10M, 30M, 1H
SET_DATA_SUB = ":DATA:SUBS:OFFON {status}" #ON/OFF
SET_DATA_SUB_MODE = ":DATA:SUBS:PEAKAVERMS {type}" #PEAK: Valores Pico, #AVE: Promedio, #RMS Cuadrático medio

SET_DATA_CAPTURE_MODE = ":DATA:CAPTM {mode}" # Manual (MEAS:START) / TRIG (Cuando hay evento de trigger)

GET_DATA_SAMPLING = ":DATA:SAMP?"
GET_DATA_MEMORY_SIZE = ":DATA:MEM?"
GET_DATA_DESTINATION = ":DATA:DEST?"
GET_DATA_POINTS = ":DATA:POINT?"
GET_DATA_CAPTURE_MODE = ":DATA:CAPTM?"
GET_DATA_CAPTURE_STATE = ":DATA:CAPT?"
GET_DATA_SUB_MODE = ":DATA:SUBS:PEAKAVERMS?"

# Medición
START_MEASUREMENT = ":MEAS:START"
STOP_MEASUREMENT = ":MEAS:STOP"
READ_ONCE = ":MEAS:OUTP:ONE?"
READ_CONT = ":MEAS:OUTP:DATA?"

SET_DATA_FORMAT = ":MEAS:OUTP:MODE {mode}" #Text o Binary
#! En texto devolvería valores CSV, sino sería tramas binarias

GET_LAST_DATETIME = ":MEAS:TIME?"
GET_CAPTURE_POINTS  = ":MEAS:CAPT?"
GET_HEADERS = ":MEAS:OUTP:HEAD?"
GET_DATA_FORMAT = ":MEAS:OUTP:MODE?"

#Transferencia de Archivos
SET_TRANS_SOURCE = ":TRANS:SOUR {source},{path}" # DISK,<path> // MEM,<path>
TRANS_OPEN = ":TRANS:OPEN?"
TRANS_SEND_HEADER = ":TRANS:OUTP:HEAD?"
TRANS_SIZE = ":TRANS:OUTP:SIZE?"

SET_TRANS_DATA = ":TRANS:OUTP:DATA {start},{end}"
TRANS_SEND_DATA = ":TRANS:OUTP:DATA?"

TRANS_CLOSE = ":TRANS:CLOSE?"


#File
FILE_LS = ":FILE:LIST?"
FILE_LS_FILTER = ":FILE:LIST:FILT {patron}" #Filtrar por txt, GBD, etc
FILE_LS_NUM = ":FILE:NUM?"

FILE_CD = ":FILE:CD {path}" 
FILE_PWD = ":FILE:CD?"
FILE_MKDIR = ":FILE:MD {path}" 
FILE_RMDIR = "FILE:RD {path}"
FILE_RM = "FILE:RM {filename}"
FILE_CP = "FILE:CP {filename} {copyname}"
FILE_MV = "FILE:MV {filepath} {new_path}"

FILE_SPACE = ":FILE:SPACE?" #Devuelve el espacio en bytes

SAVE_SETTINGS = ":FILE:SAVE {filename}"
LOAD_SETTINGS = ":FILE:LOAD {filename}"

# Trigger
SET_TRIG_STATUS = ":TRIG:FUNC {status}" #START, STOP, OFF
SET_TRIG_SOURCE = ":TRIG:COND:SOUR {source}" # OFF, AMP, ALARM, DATE
SET_TRIG_COMBINATION = ":TRIG:COND:COMB {comb}" # AND, OR
SET_TRIG_PRETRIGGER = ":TRIG:COND:PRET {value}" # 0-100 %
SET_TRIG_HIGHLOW = ":TRIG:COND:CH{ch}:OFFHILO {mode}" #OFF, HIGH, LOW 
SET_TRIG_LEVEL = ":TRIG:COND:CH{ch}:LEV {value}" # Nivel de detección del canal (dependiente del sensor)
SET_TRIG_DATE = ":TRIG:COND:SOUR:DATE {date}" #Formato YYYY/MM/DD,hh:mm:ss
SET_TRIG_ALARM = ":TRIG:COND:SOUR:ALARM" #Trigger por evento de alarma.
SET_TRIG_ANALOGIC = ":TRIG:COND:SOUR:AMP {value}" #Trigger por nivel analógico. Valores dependientes del sensorr.
SET_TRIG_OFF = ":TRIG:COND:SOUR:OFF" #Desactiva el trigger

GET_TRIG_STATUS = ":TRIG:FUNC?" 
GET_TRIG_SOURCE = ":TRIG:COND:SOUR?"
GET_TRIG_LEVEL = ":TRIG:COND:CH{ch}:LEV?"
GET_TRIG_PRETRIGGER = ":TRIG:COND:PRET?"


# Alarma
SET_ALARM = ":ALAR:FUNC {mode}" #ON/OFF

SET_ALARM_MODE = ":ALAR:CH{ch}:OFFHILO {mode}" #High, Low, Off
SET_ALARM_LEVEL = ":ALAR:CH{ch}:LEV {level}" # Valor umbral
SET_ALARM_CHANNEL = ":ALAR:CH{ch}:OUTP {mode}" #ON/OFF
SET_ALARM_EXEC = ":ALAR:EXEC {mode}" #ON/OFF

GET_ALARM_STATUS = ":ALAR:CH{ch}:STAT?"
GET_ALARM = ":ALAR:FUNC?" 
GET_ALARM_MODE = ":ALAR:CH{ch}:OFFHILO?"
GET_ALARM_LEVEL = ":ALAR:CH{ch}:LEV?"
GET_ALARM_CHANNEL = ":ALAR:CH{ch}:OUTP?"
GET_ALARM_EXEC = ":ALAR:EXEC?"

# Logic
SET_ALL_LOGIC = ":LOGIPUL:FUNC {mode}" #LOGIC/PULSE/OFF
SET_LOGIC = ":LOGIPUL:CH{ch}:FUNC {mode}"
SET_LOGIC_COUNT = ":LOGIPUL:CH{ch}:TYPE {type}" #Tipo de conteo COUNT/FREQ/RPM/WIDTH
SET_LOGIC_EDGE = ":LOGIPUL:CH:EDGE {edge}" #RISE, FALL, BOTH
SET_LOGIC_DEBOUNCE = ":LOGIPUL:CH{ch}:DEBOUNCE {value}" #0-100 ms

GET_ALL_LOGIC = ":LOGIPUL:FUNC?" #LOGIC/PULSE/OFF
GET_LOGIC = ":LOGIPUL:CH{ch}:FUNC?" #? Existe?
GET_LOGIC_EDGE = ":LOGIPUL:CH:EDGE?" #RISE, FALL, BOTH
GET_LOGIC_COUNT = ":LOGIPUL:CH{ch}:TYPE? {type}" #
GET_LOGIC_DEBOUNCE = ":LOGIPUL:CH{ch}:DEBOUNCE {value}" #0-100 ms



"""
Opciones según el módulo enganchado:

Módulo GS-4VT (4 channel, Voltage / Thermocouple Terminal)
- DC: Medición de voltaje DC mode: 
    -- 20mV,50mV, 100mV, 200mV, 500mV, 1V, 2V, 5V, 10V, 20V, 50V
- TC: Medición de Temperatura con termopar
    -- TC-K, TC-T
- OFF: Canal desactivado

Módulo GS-4TSR (4 channel, Thermistor Terminal)
- TSR (TEMP): Medición de temperatura con termistor
    --103AT,103JT
- OFF: Canal desactivado

Módulo GS-3AT (3-axis Acceleration / Temperature Terminal)
- ACC: Medición de aceleración (X/Y/Z)
    -- 2G, 5G, 10G
- TEMP: Medición de temperatura interna
    --: -10_50 (Valor fijo en °C)
- OFF: Canal desactivado

Módulo GS-TH (Temperature / Humidity Terminal)
- TEMP: Medición de temperatura
    -- -20_85 °C
- HUM: Medición de humedad
    -- 0_100 %RH
- DEW: Medición de punto de rocío
    -- -20_85 °C
- OFF: Canal desactivado

Módulo GS-LXUV (Light / UV Terminal)
- LUX: Iluminancia
    -- 0_200000 Lx
- UV: Radiación ultravioleta
    -- 0_30 mW/cm2
- OFF: Canal desactivado

Módulo GS-CO2 (CO2 Terminal)
- CO2: Concentración de CO2
    -- 0_9999 ppm
- OFF: Canal desactivado

Módulo GS-DPA-AC (AC Current / Power Adapter Terminal)
    -- En función del modelo GS-50AC, GS-100AC, GS-200AC el rango varía en 50A,100A o 200A
- AC1W: Monofásico 1 hilo
- AC2W: Monofásico 3 hilos
- AC3W: Trifásico 3 hilos
- OFF: Canal desactivado

"""
