import Graphtec
from Graphtec import GL100

print("Iniciando ejemplo de uso del API de Graphtec GL100")

logger = Graphtec.setup_logging("DEBUG")

device = GL100(conn_type="usb", port="COM3")

device.connect()

device.is_connected()
device.get_id()

device.update_channels()

channels = device.get_channels()

for key, value in channels.items():
    print(f"Canal {key}: Tipo={value['type']}, Entrada={value['input']}, Rango={value['range']}")


print(device.read())

device.disconnect()
