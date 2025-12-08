"""
Alias de comandos IF del GL100.
"""

# =========================================================
# Grupo COMMON
# ========================================================= 
GET_IDN = "*IDN?" #* Implementado
SAVE_SETTINGS = "*SAV" #* Implementado
CLEAR = "*CLS" #* Implementado


# =========================================================
# Grupo OPT (Opciones)
# =========================================================
RESET_FABRIC = ":OPT:INIT {mode}" #ALL o PART #* Implementado

SET_NAME = ":OPT:NAME {name}" # Asigna un nombre identificativo #* Implementado
SET_DATETIME = ":OPT:DATE {datetime}" #Formato YYYY/MM/DD,hh:mm:ss #* Implementado
SET_SCREEN_ECO = ":OPT:SCREENS {mode}" #ON/OFF #* Implementado

SET_TEMP_UNIT = ":OPT:TUNIT {unit}" #C o F #* Implementado
SET_BURNOUT = ":OPT:BURN {mode}" # ON/OFF #* Implementado


GET_NAME = ":OPT:NAME?" #* Implementado
GET_DATETIME = ":OPT:DATE?" #* Implementado
GET_SCREEN_ECO = ":OPT:SCREENS?" #* Implementado

GET_TEMP_UNIT = ":OPT:TUNIT?" #* Implementado
GET_BURNOUT = ":OPT:BURN?"  #* Implementado

# Unidad de aceleración 
SET_ACC_UNIT = ":OPT:ACCUNIT {unit}" # G/MPSS
GET_ACC_UNIT = ":OPT:ACCUNIT?"

#Room Temperature correction (4VT)
SET_ROOM_TEMP = ":OPT:TEMP {mode}" #ON/OFF
GET_ROOM_TEMP = ":OPT:TEMP?"


# =========================================================
# Grupo STATUS
# =========================================================
GET_POWER_VOLTAGE = "STAT:POW:BATTVAL?" #* Implementado
GET_POWER_SOURCE = ":STAT:POW:BATTSOUR?" #* Implementado
GET_POWER_STATUS = ":STAT:POW?" #* Implementado

GET_STATUS = ":STAT:COND?" #Estado de operación general: STOP,REC,ARMED,SLEEP #* Implementado
GET_INFO = ":STAT:INFO?" #* Implementado
GET_COM_STATUS = ":STAT:COMM?" #* Implementado
GET_SENSOR_STATUS = ":STAT:SENSOR?" #* Implementado
GET_ERROR_STATUS = ":STAT:ERR?" #0: Sin error, 100: Error SD, 200: Error COMM, 300: Error de sensor, 400: Error de comando inválido #* Implementado

# =========================================================
# Grupo IF (Interfaz)
# =========================================================
GET_CONN_VERSION = ":IF:VER?" #* Implementado
RESET_CONN = ":IF:RESET" #* Implementado

SET_CONN_NLCODE =":IF:NLCODE {code}" # code: En principio CR_LF. Pero si no elegir entre CR o LF #* Implementado
SET_CONN_BAUDRATE = ":IF:BAUD {baud}" #* Implementado
SET_CONN_PARITY = ":IF:PARITY {parity}" #None / EVEN / ODD #* Implementado
SET_CONN_DATABITS = ":IF:DATABITS {n}" #* Implementado
SET_CONN_STOPBITS = ":IF:STOPBITS {n}" #* Implementado
SET_CONN_FLOW = ":IF:FLOW {flow}" # NONE, RTSCTS, XONXOFF #* Implementado
SET_CONN_TIMEOUT = ":IF:TIMEOUT {timeout}" #* Implementado

GET_CONN_INFO = ":IF:INFO?" #* Implementado
GET_CONN_TYPE = ":IF:TYPE?" #* Implementado
GET_CONN_STATUS = ":IF:STAT?" #* Implementado

GET_CONN_NLCODE = ":IF:NLCODE?" #* Implementado
GET_CONN_BAUDRATE = ":IF:BAUD?" #* Implementado
GET_CONN_PARITY = ":IF:PARITY?" #* Implementado
GET_CONN_DATABITS = ":IF:DATABITS?" #* Implementado
GET_CONN_STOPBITS = ":IF:STOPBITS?" #* Implementado
GET_CONN_FLOW = ":IF:FLOW?" #* Implementado
GET_CONN_TIMEOUT = ":IF:TIMEOUT?" #* Implementado


# =========================================================
# Grupo AMP
# =========================================================
SET_CHANNEL_ALL = ":AMP:ALL {command}" #! Probar en profundidad. Command-> TEMP
SET_CHANNEL_ALL_RANGE = ":AMP:ALL:RANG {range}"

SET_CHANNEL_INPUT = ":AMP:CH{ch}:INP {mode}" #Tipo de entrada del canal #*Implementado
SET_CHANNEL_RANGE = ":AMP:CH{ch}:RANG {value}" #Rango de medida según entrada #*Implementado
SET_CHANNEL_TYPE =":AMP:CH{ch}:TYP {ch_type}" # Tipo del sensor #*Implementado

SET_CHANNEL_CLAMP = ":AMP:CH{ch}:CLAMPM {mode}" #Modo clampeo ON/OFF
SET_CHANNEL_VOLTAGE_REF = ":AMP:CH{n}:VOLT {value}" #Valor de referencia de voltaje
SET_CHANNEL_PF = ":AMP:CH{n}:PF" #Valor del fdp para AC

SET_CHANNEL_ACC_CALIBRATE = ":AMP:CH{n}:ACCCAL:FUNC {mode}" #Estado de Calibracion del acelerómetro ON/OFF
SET_CHANNEL_ACC_CALIBRATE_EXEC = ":AMP:CH{n}:ACCCAL:EXEC" #Ejecuta la calibración del acelerómetro
SET_CHANNEL_CO2_CALIBRATE = ":AMP:CH{n}:CO2CAL" #Calibración del sensor CO2 ON/OFF

SET_CHANNEL_COUNT_HIGHLOW = ":AMP:CH{ch}:COUNT:HILO" # Configura la detección alto/bajo del contador lógico
SET_CHANNEL_COUNT_LEVEL = ":AMP:CH{ch}:COUNT:LEV" # Nivel de umbral para conteo

GET_CHANNEL_INPUT = ":AMP:CH{ch}:INP?" #Devuelve el tipo de entrada #*Implementado
GET_CHANNEL_RANGE = ":AMP:CH{ch}:RANG?" #Devuelve el rango #*Implementado
GET_CHANNEL_TYPE = ":AMP:CH{ch}:TYP?" #Devuelve el tipo de sensor #*Implementado

GET_CHANNEL_CLAMP = ":AMP:CH{ch}:CLAMPM?" # Estado del Clamp
GET_CHANNEL_VOLTAGE_REF = ":AMP:CH{ch}:VOLT?" #Devuelve el offset del voltaje (referencia)
GET_CHANNEL_ACC = ":AMP:CH{ch}:ACCCAL:FUNC?" #Estado de la calibración
GET_CHANNL_PF = ":AMP:CH{ch}:PF?"


# =========================================================
# Grupo DATA
# =========================================================
SET_DATA_LOCATION = ":DATA:MEAS {location}" # MEM para memoria, DIR para directa (streaming) #*Implementado
SET_DATA_MEMORY_SIZE = ":DATA:MEM {size}" # Auto / Sino tamaño de captura #*Implementado
SET_DATA_DESTINATION = ":DATA:DEST {dest}" # MEM para memoria / SD para tarjetaSD #*Implementado

SET_DATA_SAMPLING = ":DATA:SAMP {interval}" #10MS, 20MS, 50MS, 100MS, 200MS, 500MS, 1S, 2S, 5S, 10S, 30S, 1M, 2M, 5M, 10M, 30M, 1H #*Implementado

SET_DATA_SUB = ":DATA:SUBS:OFFON {status}" #ON/OFF #*Implementado
SET_DATA_SUB_MODE = ":DATA:SUBS:PEAKAVERMS {type}" #PEAK: Valores Pico, #AVE: Promedio, #RMS Cuadrático medio #*Implementado

SET_DATA_CAPTURE_MODE = ":DATA:CAPTM {mode}" # Manual (MEAS:START) / TRIG (Cuando hay evento de trigger) #*Implementado

GET_DATA_SAMPLING = ":DATA:SAMP?" #*Implementado
GET_DATA_MEMORY_SIZE = ":DATA:MEM?" #*Implementado
GET_DATA_DESTINATION = ":DATA:DEST?" #*Implementado
GET_DATA_POINTS = ":DATA:POINT?" #*Implementado
GET_DATA_CAPTURE_MODE = ":DATA:CAPTM?" #*Implementado
GET_DATA_CAPTURE_STATE = ":DATA:CAPT?" #*Implementado
GET_DATA_SUB_MODE = ":DATA:SUBS:PEAKAVERMS?" #*Implementado


# =========================================================
# Grupo MEASURE
# =========================================================
START_MEASUREMENT = ":MEAS:START" #*Implementado
STOP_MEASUREMENT = ":MEAS:STOP" #*Implementado
READ_ONCE = ":MEAS:OUTP:ONE?" #*Implementado
READ_CONT = ":MEAS:OUTP:DATA?" #*Implementado

SET_MEAS_FORMAT = ":MEAS:OUTP:MODE {mode}" #Text o Binary #*Implementado
#! En texto devolvería valores CSV, sino sería tramas binarias

GET_LAST_DATETIME = ":MEAS:TIME?"  #*Implementado
GET_CAPTURE_POINTS  = ":MEAS:CAPT?"  #*Implementado
GET_HEADERS = ":MEAS:OUTP:HEAD?"  #*Implementado
GET_DATA_FORMAT = ":MEAS:OUTP:MODE?"  #*Implementado


# =========================================================
# Grupo TRANSFER
# =========================================================
SET_TRANS_SOURCE = ":TRANS:SOUR {source},{path}" # DISK,<path> // MEM,<path> #*Implementado
TRANS_OPEN = ":TRANS:OPEN?" #*Implementado
TRANS_SEND_HEADER = ":TRANS:OUTP:HEAD?" #*Implementado
TRANS_SIZE = ":TRANS:OUTP:SIZE?" #*Implementado

SET_TRANS_DATA = ":TRANS:OUTP:DATA {start},{end}" #*Implementado
TRANS_SEND_DATA = ":TRANS:OUTP:DATA?" #*Implementado

TRANS_CLOSE = ":TRANS:CLOSE?" #*Implementado



# =========================================================
# Grupo FILE
# =========================================================
FILE_LS = ":FILE:LIST?" #*Implementado
FILE_LS_FILTER = ":FILE:LIST:FILT {pattern}" #Filtrar por txt, GBD, etc #*Implementado
FILE_LS_NUM = ":FILE:NUM?" #*Implementado

FILE_CD = ":FILE:CD {path}" #*Implementado
FILE_PWD = ":FILE:CD?" #*Implementado
FILE_MKDIR = ":FILE:MD {path}"  #*Implementado
FILE_RMDIR = "FILE:RD {path}" #*Implementado
FILE_RM = "FILE:RM {filename}" #*Implementado
FILE_CP = "FILE:CP {filename} {copyname}" #*Implementado
FILE_MV = "FILE:MV {filepath} {new_path}" #*Implementado

FILE_SPACE = ":FILE:SPACE?" #Devuelve el espacio en bytes

SAVE_FILE_SETTINGS = ":FILE:SAVE {filename}" #*Implementado
LOAD_FILE_SETTINGS = ":FILE:LOAD {filename}" #*Implementado


# =========================================================
# Grupo TRIGGER
# =========================================================
SET_TRIG_STATUS = ":TRIG:FUNC {status}" #START, STOP, OFF #*Implementado

SET_TRIG_SOURCE = ":TRIG:COND:SOUR {source}" # OFF, AMP, ALAR, DATE,datetime #*Implementado
SET_TRIG_SOURCE_DATE = ":TRIG:COND:SOUR DATE,{datetime}" #*Implementado

SET_TRIG_COMBINATION = ":TRIG:COND:COMB {comb}" # AND, OR #*Implementado
SET_TRIG_CHANNEL = ":TRIG:COND:CH{ch}:SET {mode},{value}" #OFF, HIGH, LOW , Nivel de detección #*Implementado

SET_TRIG_PRETRIGGER = ":TRIG:COND:PRET {value}" # 0-100 % #*Implementado

GET_TRIG_STATUS = ":TRIG:FUNC?" #*Implementado
GET_TRIG_SOURCE = ":TRIG:COND:SOUR?" #*Implementado
GET_TRIG_COMBINATION = ":TRIG:COND:COMB?" #*Implementado
GET_TRIG_CHANNEL = ":TRIG:COND:CH{ch}:SET?" #*Implementado
GET_TRIG_PRETRIGGER = ":TRIG:COND:PRET?" #*Implementado


# =========================================================
# Grupo ALARM
# =========================================================
SET_ALARM_MODE = ":ALAR:FUNC {mode}" #ON/OFF #*Implementado
SET_ALARM_LEVEL = ":ALAR:CH{ch}:SET {mode},{level}" #High, Low, Off #*Implementado
SET_ALARM = ":ALAR:EXEC {mode}" #ON/OFF #*Implementado

GET_ALARM_STATUS = ":ALAR:CH{ch}?"
GET_ALARM_MODE = ":ALAR:FUNC?" #*Implementado
GET_ALARM_LEVEL = ":ALAR:CH{ch}:SET?" #*Implementado
GET_ALARM = ":ALAR:EXEC?" #*Implementado

# =========================================================
# Grupo LOGIPUL
# =========================================================
SET_LOGIC_TYPE = ":LOGIPUL:FUNC {mode}" #LOGIc/PULse/OFF
SET_LOGIC = ":LOGIPUL:CH{ch}:FUNC {mode}"#Tipo de conteo ON/INST/COUNT/OFF

GET_LOGIC_TYPE = ":LOGIPUL:FUNC?" #LOGIC/PULSE/OFF
GET_LOGIC = ":LOGIPUL:CH{ch}:FUNC?" 




"""
Opciones según el módulo enganchado:
Type: tipo de modulo físico, input: tipo de cada canal, range: Rango de medición

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
