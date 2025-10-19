"""
Plantillas y alias de comandos IF del GL100.
Basado en los documentos oficiales Graphtec.
"""
# Configuración de nueva línea
NLCODE =":IF:NLCODE {eol}" # eol: En principio CR_LF


# Medición
START_MEASUREMENT = ":MEAS:STAR"
STOP_MEASUREMENT = ":MEAS:STOP"
READ_REALTIME = ":MEAS:OUTP:ONE?"

# Configuración
SET_SAMPLING = ":DATA:SAMP {interval}"
GET_SAMPLING = ":DATA:SAMP?"

"""
Opciones según el módulo enganchado:

Módulo GS-4VT (4 channel, Voltage / Thermocouple Terminal)
- DC: Medición de voltaje DC mode: 
    -- 20mV,50mV, 100mV, 200mV, 500mV, 1V, 2V, 5V, 10V, 20V, 50V
- TC: Medición de Temperatura con termopar
    -- TC-K, TC-T
- OFF: Canal desactivado

Módulo GS-4TSR (4 channel, Thermistor Terminal)
- TSR: Medición de temperatura con termistor
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
SET_INPUT_TYPE = ":AMP:CH{ch}:INP {mode}"
GET_INPUT_TYPE = ":AMP:CH{ch}:INP?"

SET_INPUT_RANGE = ":AMP:CH{ch}:RANG {value}"
GET_INPUT_RANGE = ":AMP:CH{ch}:RANG?"


# Trigger
SET_TRIG_SOURCE = ":TRIG:FUNC {source}"
SET_TRIG_LEVEL = ":TRIG:COND:CH{ch}:LEV {value}"

# Alarma
SET_ALARM_LEVEL = ":ALAR:CH{ch}:LEV {value}"
ENABLE_ALARM_OUT = ":ALAR:OUTP {state}"

# Sistema
GET_IDN = "*IDN?"
GET_STATUS = ":STAT:COND?"
CLEAR_STATUS = "*CLS"
GET_DATETIME = ":OPT:DATE?"
SET_DATETIME = ":OPT:DATE {datetime}"

# Archivos
LIST_FILES = ":FILE:LIST?"
SAVE_SETTINGS = ":FILE:SAVE {filename}"
LOAD_SETTINGS = ":FILE:LOAD {filename}"
DELETE_FILE = ":FILE:RM {filename}"
GET_FREE_SPACE = ":FILE:SPACE?"
