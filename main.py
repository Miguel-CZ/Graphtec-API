import time
from graphtec import Graphtec,setup_logging

#setup_logging(level="DEBUG")

def main():
    start_time = time.time()
    # ------------------------------------------------------
    # 1) Inicializar comunicación
    # ------------------------------------------------------
    device = Graphtec(
        connection_type="serie",
        port="COM3",
        baudrate=38400,
        timeout=1,
        write_timeout=1)
    print("Iniciando conexión...")
    device.connect()
    print("Conexión establecida.")

    print("Prueba de is_connected():", device.is_connected())

    # ------------------------------------------------------
    # 2) ID
    # ------------------------------------------------------
    try:
        idn = device.get_id()
        for key, value in idn.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error al obtener ID: {e}")
    
    # ------------------------------------------------------
    # 2) Canales
    # ------------------------------------------------------

    # Primera lectura de canales
    print("1ra Lectura de canales:")
    try:
        channels = device.get_channels()
        for channel,cfg in channels.items():
            print(f"Canal_{channel}:")
            for key, value in cfg.items():
                print(f"\t{key}: {value}")
    except Exception as e:
        print(f"Error al obtener canales: {e}")

    # Cambiar la configuración de los canales
    print("Configurando canales:")
    for channel in range(1,5):
        print(f"\tConfigurando canal {channel}...")
        try:
            device.set_channel(channel, ch_type="V", ch_input="DC_V", ch_range="10V")
        except Exception as e:
            print(f"Error al configurar canal{channel}: {e}")
    
    # Segunda lectura de canales
    print("2da Lectura de canales:")
    try:
        channels = device.get_channels()
        for channel,cfg in channels.items():
            print(f"Canal_{channel}:")
            for key, value in cfg.items():
                print(f"\t{key}: {value}")
    except Exception as e:
        print(f"Error al obtener canales: {e}")
    
    # ------------------------------------------------------
    # 3) LOGIC
    # ------------------------------------------------------
    print("Configurando lógicas:")

    print("Configurando tipo de lógica...")
    try:
        device.set_logic_type("PULSE")
    except Exception as e:
        print(f"Error al configurar el tipo de lógicas:{e}")

    for ch in range(1, 5):
        print(f"Configurando lógica canal {ch}...")
        try:
            device.set_logic(ch,"ON")
        except Exception as e:
            print(f"Error al configurar lógica canal {ch}: {e}")

    logics = device.get_logics()
    for channel, cfg in logics.items():
        print(f"Canal {channel}:")
        for key, value in cfg.items():
            print(f"\t{key}: {value}")
    
    # ------------------------------------------------------
    # 3) TRIGGER
    # ------------------------------------------------------
    print("Configurando Triggers...")

    device.set_trigger_source("AMP")
    for ch in range(1,5):
        print(f"\tConfiguración del trigger del canal {ch}...")
        device.set_trigger_channel(ch,"HI","10")

    print("Configurando combinación lógica...")
    device.set_trigger_comb("OR")
    logic_comb = device.get_trigger_comb()
    print(f"\t Combinación lógica: {logic_comb}")

    print(f"Arrancando trigger...")
    device.set_trigger("START")
    trigger_status=device.get_trigger()
    print(f"Estado del trigger: {trigger_status}")

    print(f"Parando trigger...")
    device.set_trigger("STOP")
    trigger_status=device.get_trigger()
    print(f"Estado del trigger: {trigger_status}")

    # ------------------------------------------------------
    # 3) Other
    # ------------------------------------------------------
    print(f"\nConfigurando fecha y hora...")
    device.set_datetime_now()
    datetime = device.get_datetime()
    print(f"\tFecha y hora: {datetime}")

    print(f"\nConfigurando nombre...")
    device.set_name("TheGL100")
    name = device.get_name()
    print(f"\tNombre del dispositivo: {name}")

    print(f"\nConfigurando Modo de ahorro de pantalla...")
    device.set_screen_eco("OFF")
    screen_eco = device.get_screen_eco()
    print(f"\tModo de ahorro de pantalla: {screen_eco}")

    print(f"\nConfigurando unidad de temperatura...")
    device.set_temp_unit("FAHR")
    temp_unit = device.get_temp_unit()
    print(f"\tUnidad de temperatura:{temp_unit}")

    print(f"\nConfigurando correción de temperatura...")
    device.set_room_temp("OFF")
    temp_unit = device.get_room_temp()
    print(f"\tUnidad de temperatura:{temp_unit}")

    print(f"\nConfigurando modo burnout...")
    device.set_burnout("OFF")
    burnout = device.get_burnout()
    print(f"\tModo Burnout: {burnout}")

    print(f"\nConfigurando unidad de aceleración...")
    device.set_acc_unit("G")
    acc_unit = device.get_acc_unit()
    print(f"\tUnidad de aceleración: {acc_unit}")

    device.clear()
    device.disconnect()
    end_time = time.time()
    print(f"Tiempo total de ejecución: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()