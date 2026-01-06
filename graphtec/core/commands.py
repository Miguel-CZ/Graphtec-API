
# commands.py
"""Alias de comandos IF del GL100."""

from types import SimpleNamespace

# =========================================================
# Grupo COMMON
# =========================================================
COMMON = SimpleNamespace(
    GET_IDN="*IDN?",
    SAVE_SETTINGS="*SAV",
    CLEAR="*CLS",
)
# =========================================================
# Grupo OPT (Opciones)
# =========================================================
OPT = SimpleNamespace(
    SET_NAME=":OPT:NAME {name}",                  # Asigna un nombre identificativo: "Nombre"
    GET_NAME=":OPT:NAME?",
    SET_DATETIME=":OPT:DATE {datetime}",          # Formato YYYY/MM/DD,hh:mm:ss
    GET_DATETIME=":OPT:DATE?",
    # Apagar pantalla por tiempo
    SET_SCREEN_SAVE=":OPT:SCREENS {time}",        # time: OFF/1/2/5/10/20/30/60 (MIN)
    GET_SCREEN_SAVE=":OPT:SCREENS?",
    # Unidades para temperatura
    SET_TEMP_UNIT=":OPT:TUNIT {unit}",            # CELS/FAHR
    GET_TEMP_UNIT=":OPT:TUNIT?",
    # Burnout (4VT)
    SET_BURNOUT=":OPT:BURN {mode}",               # ON/OFF
    GET_BURNOUT=":OPT:BURN?",
    # Unidad de aceleración
    SET_ACC_UNIT=":OPT:ACCUNIT {unit}",           # G/MPSS
    GET_ACC_UNIT=":OPT:ACCUNIT?",
    # Room Temperature correction (4VT)
    SET_ROOM_TEMP=":OPT:TEMP {mode}",             # ON/OFF
    GET_ROOM_TEMP=":OPT:TEMP?",
)
# =========================================================
# Grupo STATUS
# =========================================================
STATUS = SimpleNamespace(
    GET_POWER_STATUS=":STAT:POW?",
    GET_STATUS=":STAT:COND?",                     # Estado de operación
    GET_EXTENDED_STATUS=":STAT:EESR",
    GET_ERROR_STATUS=":STAT:ERR?",
    SET_STATUS_FILTER=":STAT:FILT{number} {value}",  # number:0-15 (bit) / value: NEV, RISE, FALL, BOTH
    GET_STATUS_FILTER=":STAT:FILT{number}?",
)
# =========================================================
# Grupo IF (Interfaz)
# =========================================================
IFACE = SimpleNamespace(
    SET_CONN_NLCODE=":IF:NLCODE {code}",          # CR_LF, CR, LF
    GET_CONN_NLCODE=":IF:NLCODE?",
)
# =========================================================
# Grupo AMP
# =========================================================
AMP = SimpleNamespace(
    SET_CHANNEL_ALL_RANGE=":AMP:ALL:RANG {range}",
    SET_CHANNEL_INPUT=":AMP:CH{ch}:INP {mode}",       # Tipo de entrada del canal
    SET_CHANNEL_RANGE=":AMP:CH{ch}:RANG {value}",     # Rango de medida según entrada
    SET_CHANNEL_CLAMP=":AMP:CH{ch}:CLAMPM {mode}",    # Modo clampeo ON/OFF
    SET_CLAMP_VOLTAGE_REF=":AMP:CH{n}:VOLT {value}",  # Valor de referencia de voltaje (offset)
    SET_CHANNEL_PF=":AMP:CH{n}:PF",                   # Valor del fdp para AC
    SET_CHANNEL_ACC_CALIBRATE=":AMP:CH{n}:ACCCAL:FUNC {mode}",  # Calibración acelerómetro ON/OFF
    SET_CHANNEL_ACC_CALIBRATE_EXEC=":AMP:CH{n}:ACCCAL:EXE",     # Ejecuta calibración acelerómetro
    SET_CHANNEL_CO2_CALIBRATE=":AMP:CH{n}:CO2CAL:FUNC {mode}",  # Calibración sensor CO2 ON/OFF
    SET_CHANNEL_COUNT=":AMP:CH{ch}:COUNT:LEV:{mode}.{value}",   # Detección alto/bajo del contador lógico

    GET_CHANNEL_INPUT=":AMP:CH{ch}:INP?",           # Devuelve el tipo de entrada
    GET_CHANNEL_RANGE=":AMP:CH{ch}:RANG?",          # Devuelve el rango
    GET_CHANNEL_TYPE=":AMP:CH{ch}:TYP?",            # Devuelve tipo de sensor
    GET_CHANNEL_CLAMP=":AMP:CH{ch}:CLAMPM?",        # Estado del Clamp
    GET_CLAMP_VOLTAGE_REF=":AMP:CH{ch}:VOLT?",      # Offset de voltaje
    GET_CHANNEL_PF=":AMP:CH{ch}:PF?",
    GET_CHANNEL_ACC_CALIBRATE=":AMP:CH{ch}:ACCCAL:FUNC?",  # Estado calibración
    GET_CHANNEL_CO2_CALIBRATE=":AMP:CH{ch}:CO2CAL:FUNC?",  # Estado calibración sensor CO2
    GET_CHANNEL_COUNT=":AMP:CH{ch}:COUNT:LEV?",     # Config de detección contador lógico
)
# =========================================================
# Grupo DATA
# =========================================================
DATA = SimpleNamespace(
    SET_DATA_LOCATION=":DATA:MEASUREM {location}",  # MEM / DIRE
    SET_DATA_MEMORY_SIZE=":DATA:MEMORYS {size}",    # 16/32/64/128
    SET_DATA_DESTINATION=":DATA:DEST {dest}",       # MEM / SD
    SET_DATA_SAMPLING=":DATA:SAMP {sample}",        # Ver tabla de valores por modo
    SET_DATA_SUB=":DATA:SUBS {mode},{sub_type}",    # MODE: ON/OFF TYPE: PEAK/AVE/RMS
    SET_DATA_CAPTURE_MODE=":DATA:CAPTM {mode}",     # CONT / 1H / 24H

    GET_DATA_LOCATION=":DATA:MEASUREM?",
    GET_DATA_MEMORY_SIZE=":DATA:MEMORYS?",
    GET_DATA_DESTINATION=":DATA:DEST?",
    GET_DATA_FILEPATH=":DATA:CAPT?",
    GET_DATA_POINTS=":DATA:POINT?",
    GET_DATA_SAMPLING=":DATA:SAMP?",
    GET_DATA_SUB=":DATA:SUBS?",
    GET_DATA_CAPTURE_MODE=":DATA:CAPTM?",
)
# =========================================================
# Grupo MEASURE
# =========================================================
MEAS = SimpleNamespace(
    START_MEASUREMENT=":MEAS:START",
    STOP_MEASUREMENT=":MEAS:STOP",
    READ_ONCE=":MEAS:OUTP:ONE?",
    GET_CAPTURE_POINTS=":MEAS:CAPT?",
    GET_MEASUREMENT_TIME=":MEAS:TIME?",            # started, ended and trigger time
)
# =========================================================
# Grupo TRANSFER
# =========================================================
TRANS = SimpleNamespace(
    SET_TRANS_SOURCE=":TRANS:SOUR {source},{path}", # DISK,<path> // MEM,<path>
    TRANS_OPEN=":TRANS:OPEN?",
    TRANS_SEND_HEADER=":TRANS:OUTP:HEAD?",
    TRANS_SIZE=":TRANS:OUTP:SIZE?",
    SET_TRANS_DATA=":TRANS:OUTP:DATA {start},{end}",
    TRANS_SEND_DATA=":TRANS:OUTP:DATA?",
    TRANS_CLOSE=":TRANS:CLOSE?",
)
# =========================================================
# Grupo FILE
# =========================================================
FILE = SimpleNamespace(
    FILE_SAVE=':FILE:SAVE {filepath}',              # "¥SD¥FOLDER¥SAVE.CND"
    FILE_LOAD=':FILE:LOAD {filepath}',              # "¥SD¥FOLDER¥SAVE.CND"
    FILE_CD=':FILE:CD {dirpath}',                   # "¥SD¥FOLDER¥SAVE¥"
    FILE_PWD=":FILE:CD?",
    FILE_MKDIR=':FILE:MD {dirpath}',
    FILE_RMDIR=':FILE:RD {dirpath}',
    FILE_RM=':FILE:RM {filepath}',
    FILE_MV=':FILE:MV {file_source},{file_dest}',
    FILE_CP=':FILE:CP {file_source},{file_dest}',
    FILE_SPACE=":FILE:SPACE?",                      # espacio en bytes
    FILE_LS_NUM=":FILE:NUM?",                       # nº de archivos en LOG
    FILE_LS=":FILE:LIST?",
    FILE_LS_FORMAT=":FILE:LIST:FORM {format}",      # LONG / SHORT
    FILE_LS_FILTER=":FILE:LIST:FILT {extension}",   # txt/GBD/etc. OFF para quitar
    GET_LS_FORMAT=":FILE:LIST:FORM?",
    GET_LS_FILTER=":FILE:LIST:FILT?",
)
# =========================================================
# Grupo TRIGGER
# =========================================================
TRIG = SimpleNamespace(
    SET_TRIG_STATUS=":TRIG:FUNC {status}",          # START, STOP, OFF
    SET_TRIG_SOURCE=":TRIG:COND:SOUR {source}",     # OFF, AMP, ALAR, DATE
    SET_TRIG_SOURCE_DATE=':TRIG:COND:SOUR DATE,{datetime}',
    SET_TRIG_COMBINATION=":TRIG:COND:COMB {comb}",  # AND, OR
    SET_TRIG_CHANNEL=":TRIG:COND:CH{ch}:SET {mode},{value}",  # OFF, HIGH, LOW, nivel
    SET_TRIG_PRETRIGGER=":TRIG:COND:PRET {value}",  # 0-100 %
    GET_TRIG_STATUS=":TRIG:FUNC?",
    GET_TRIG_SOURCE=":TRIG:COND:SOUR?",
    GET_TRIG_COMBINATION=":TRIG:COND:COMB?",
    GET_TRIG_CHANNEL=":TRIG:COND:CH{ch}:SET?",
    GET_TRIG_PRETRIGGER=":TRIG:COND:PRET?",
)
# =========================================================
# Grupo ALARM
# =========================================================
ALARM = SimpleNamespace(
    SET_ALARM_MODE=":ALAR:FUNC {mode}",             # LEVEL / OFF
    SET_ALARM_LEVEL=":ALAR:CH{ch}:SET {mode},{level}",  # High, Low, Off
    SET_ALARM_OUTPUT=":ALAR:OUTP {mode}",           # ON/OFF
    SET_ALARM=":ALAR:EXEC {mode}",                  # ON/OFF
    GET_ALARM_STATUS=":ALAR:CH{ch}?",
    GET_ALARM_MODE=":ALAR:FUNC?",
    GET_ALARM_LEVEL=":ALAR:CH{ch}:SET?",
    GET_ALARM=":ALAR:EXEC?",
    GET_ALARM_OUTPUT=":ALAR:OUTP?",
)
# =========================================================
# Grupo LOGIPUL
# =========================================================
LOGIPUL = SimpleNamespace(
    SET_LOGIC_TYPE=":LOGIPUL:FUNC {mode}",          # LOGIc/PULse/OFF
    SET_LOGIC=":LOGIPUL:CH{ch}:FUNC {mode}",        # ON/INST/COUNT/OFF
    GET_LOGIC_TYPE=":LOGIPUL:FUNC?",                # LOGIC/PULSE/OFF
    GET_LOGIC=":LOGIPUL:CH{ch}:FUNC?",
)

__all__ = [
    "COMMON", "OPT", "STATUS", "IFACE", "AMP", "DATA",
    "MEAS", "TRANS", "FILE", "TRIG", "ALARM", "LOGIPUL",
]


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
