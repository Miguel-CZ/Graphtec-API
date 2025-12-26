from __future__ import annotations


def build_responses() -> dict[str, bytes]:
    """
    Mapa comando->respuesta.
    """
    return {
        # =========================
        # Common / Identificación
        # =========================
        "*IDN?": b"*IDN GRAPHTEC,GL100,0,01.45\r\n",
        "*CLS": b"OK\r\n",
        "*SAV": b"OK\r\n",

        # =========================
        # Option
        # =========================
        ':OPT:NAME?': b':OPT:NAME "GL100"\r\n',
        ':OPT:DATE?': b':OPT:DATE "2014-01-01 00:13:31"\r\n',
        ":OPT:TUNIT?": b":OPT:TUNIT CELS\r\n",
        ":OPT:BURN?": b":OPT:BURN OFF\r\n",
        ":OPT:ACCUNIT?": b":OPT:ACCUNIT NONE\r\n",
        ":OPT:LANG?": b"\r\n",
        ":OPT:TEMP?": b":OPT:TEMP ON\r\n",

        # =========================
        # Status
        # =========================
        "STAT:POW:BATTVAL?": b"\r\n",
        ":STAT:POW:BATTSOUR?": b"\r\n",
        ":STAT:POW?": b":STAT:POW USB\r\n",
        ":STAT:COND?": b":STAT:COND 0\r\n",
        ":STAT:INFO?": b"\r\n",
        ":STAT:COMM?": b"\r\n",
        ":STAT:SENSOR?": b"\r\n",
        ":STAT:ERR?": b":STAT:ERR 32,0,0\r\n",

        # =========================
        # Interface
        # =========================
        ":IF:VER?": b"\r\n",
        ":IF:RESET": b"OK\r\n",
        ":IF:INFO?": b"\r\n",
        ":IF:TYPE?": b"\r\n",
        ":IF:STAT?": b"\r\n",
        ":IF:NLCODE?": b":IF:NLC CR_LF\r\n",
        ":IF:BAUD?": b"\r\n",
        ":IF:PARITY?": b"\r\n",
        ":IF:DATABITS?": b"\r\n",
        ":IF:STOPBITS?": b"\r\n",
        ":IF:FLOW?": b"\r\n",
        ":IF:TIMEOUT?": b"\r\n",

        # =========================
        # AMP (ejemplo CH1-CH4)
        # =========================
        ":AMP:CH1:INP?": b":AMP:CH1:INP DC_V\r\n",
        ":AMP:CH2:INP?": b":AMP:CH2:INP DC_V\r\n",
        ":AMP:CH3:INP?": b":AMP:CH3:INP OFF\r\n",
        ":AMP:CH4:INP?": b":AMP:CH4:INP OFF\r\n",

        ":AMP:CH1:RANG?": b":AMP:CH1:RANG 20V\r\n",
        ":AMP:CH2:RANG?": b":AMP:CH2:RANG 20V\r\n",
        ":AMP:CH3:RANG?": b":AMP:CH3:RANG NONE\r\n",
        ":AMP:CH4:RANG?": b":AMP:CH4:RANG NONE\r\n",

        ":AMP:CH1:TYP?": b":AMP:CH1:TYP VT\r\n",
        ":AMP:CH2:TYP?": b":AMP:CH2:TYP VT\r\n",
        ":AMP:CH3:TYP?": b":AMP:CH3:TYP VT\r\n",
        ":AMP:CH4:TYP?": b":AMP:CH4:TYP VT\r\n",

        ":AMP:CH1:CLAMPM?": b":AMP:CH1:CLAMPM NONE\r\n",
        ":AMP:CH2:CLAMPM?": b":AMP:CH2:CLAMPM NONE\r\n",
        ":AMP:CH3:CLAMPM?": b":AMP:CH3:CLAMPM NONE\r\n",
        ":AMP:CH4:CLAMPM?": b":AMP:CH4:CLAMPM NONE\r\n",

        ":AMP:CH1:VOLT?": b":AMP:CH1:VOLT NONE\r\n",
        ":AMP:CH2:VOLT?": b":AMP:CH2:VOLT NONE\r\n",
        ":AMP:CH3:VOLT?": b":AMP:CH3:VOLT NONE\r\n",
        ":AMP:CH4:VOLT?": b":AMP:CH4:VOLT NONE\r\n",

        ":AMP:CH1:ACCCAL:FUNC?": b":AMP:CH1:ACCCAL:FUNC NONE\r\n",
        ":AMP:CH2:ACCCAL:FUNC?": b":AMP:CH2:ACCCAL:FUNC NONE\r\n",
        ":AMP:CH3:ACCCAL:FUNC?": b":AMP:CH3:ACCCAL:FUNC NONE\r\n",
        ":AMP:CH4:ACCCAL:FUNC?": b":AMP:CH4:ACCCAL:FUNC NONE\r\n",

        ":AMP:CH1:PF?": b":AMP:CH1:PF NONE\r\n",
        ":AMP:CH2:PF?": b":AMP:CH2:PF NONE\r\n",
        ":AMP:CH3:PF?": b":AMP:CH3:PF NONE\r\n",
        ":AMP:CH4:PF?": b":AMP:CH4:PF NONE\r\n",

        # =========================
        # DATA
        # =========================
        ":DATA:SAMP?": b":DATA:SAMP 500\r\n",
        ":DATA:MEM?": b"\r\n",
        ":DATA:DEST?": b":DATA:DEST MEM\r\n",
        ":DATA:POINT?": b":DATA:POINT 0\r\n",
        ":DATA:CAPTM?": b":DATA:CAPTM CONT\r\n",
        ':DATA:CAPT?': b':DATA:CAPT "NONE","NONE"\r\n',
        ":DATA:SUBS:PEAKAVERMS?": b"\r\n",

        # =========================
        # MEAS (incluye binario)
        # =========================
        ":MEAS:START": b"OK\r\n",
        ":MEAS:STOP": b"OK\r\n",
        ":MEAS:OUTP:ONE?": b"\r\n",
        # Bloque binario (ejemplo de tu dump)
        ":MEAS:OUTP:DATA?": b"#6000014\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ':MEAS:TIME?': b':MEAS:TIME "2014-01-01 00:13:53","2014-01-01 00:13:54","2014-01-01 00:13:54"\r\n',
        ":MEAS:CAPT?": b":MEAS:CAPT 0\r\n",
        ":MEAS:OUTP:HEAD?": b"\r\n",
        ":MEAS:OUTP:MODE?": b"\r\n",

        # =========================
        # TRANS (binario)
        # =========================
        ":TRANS:OPEN?": b"\x00",
        ":TRANS:OUTP:HEAD?": b":TRANS:OUTP:HEAD NONE\r\n",
        ":TRANS:OUTP:SIZE?": b":TRANS:OUTP:SIZE NONE\r\n",
        ":TRANS:OUTP:DATA?": b"#6000000\x00\x01",
        ":TRANS:CLOSE?": b"\x00\x01",

        # =========================
        # FILE
        # =========================
        ':FILE:LIST?': b':FILE:LIST "MEM\\"\r\n',
        ":FILE:NUM?": b":FILE:NUM 0\r\n",
        ':FILE:CD?': b':FILE:CD "\\\\"\r\n',
        ":FILE:SPACE?": b":FILE:SPACE NONE\r\n",

        # =========================
        # ALAR
        # =========================
        ":ALAR:CH1?": b"\r\n",
        ":ALAR:CH2?": b":ALAR:CH2:SET OFF,+0.000V\r\n",
        ":ALAR:CH3?": b":ALAR:CH3:SET OFF,+0.000V\r\n",
        ":ALAR:CH4?": b":ALAR:CH4:SET OFF,+0.000V\r\n",
        ":ALAR:FUNC?": b":ALAR:FUNC LEVEL\r\n",
        ":ALAR:CH1:SET?": b":ALAR:CH1:SET OFF,+0.000V\r\n",
        ":ALAR:CH2:SET?": b":ALAR:CH2:SET OFF,+0.000V\r\n",
        ":ALAR:CH3:SET?": b":ALAR:CH3:SET OFF,+0.000V\r\n",
        ":ALAR:CH4:SET?": b":ALAR:CH4:SET OFF,+0.000V\r\n",
        ":ALAR:EXEC?": b":ALAR:EXEC OFF\r\n",

        # =========================
        # TRIG
        # =========================
        ":TRIG:FUNC?": b":TRIG:FUNC OFF\r\n",
        ":TRIG:COND:SOUR?": b":TRIG:COND:SOUR OFF\r\n",
        ":TRIG:COND:CH1:SET?": b":TRIG:COND:CH1:SET OFF,+0.000V\r\n",
        ":TRIG:COND:CH2:SET?": b":TRIG:COND:CH2:SET OFF,+0.000V\r\n",
        ":TRIG:COND:CH3:SET?": b":TRIG:COND:CH3:SET OFF,+0.000V\r\n",
        ":TRIG:COND:CH4:SET?": b":TRIG:COND:CH4:SET OFF,+0.000V\r\n",
        ":TRIG:COND:PRET?": b":TRIG:COND:PRET 0\r\n",

        # =========================
        # LOGIPUL
        # =========================
        ":LOGIPUL:FUNC?": b":LOGIPUL:FUNC LOGI\r\n",
        ":LOGIPUL:CH1:FUNC?": b":LOGIPUL:CH1:FUNC OFF\r\n",
        ":LOGIPUL:CH2:FUNC?": b":LOGIPUL:CH2:FUNC OFF\r\n",
        ":LOGIPUL:CH3:FUNC?": b":LOGIPUL:CH3:FUNC OFF\r\n",
        ":LOGIPUL:CH4:FUNC?": b":LOGIPUL:CH4:FUNC OFF\r\n",
    }
