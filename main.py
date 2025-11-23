import graphtec
from graphtec import Graphtec

print("Iniciando ejemplo de uso del API de Graphtec GL100")

logger = graphtec.setup_logging("INFO", logfile="debug.log")

device = Graphtec(conn_type="usb", port="COM3")

device.connect()

device.is_connected()
device.get_id()

device.update_channels()

""" channels = device.get_channels()

for key, value in channels.items():
    print(f"Canal {key}: Tipo={value['type']}, Entrada={value['input']}, Rango={value['range']}") """

""" import time
for i in range(10):
    read = device.read()
    for key, value in read.items():
        print(f"Canal {key}: {value} V")
    time.sleep(0.1) """

files=device.list_files(path="\\MEM\\LOG\\", long=True, filt="GBD")
print("Archivos en \\MEM\\LOG\\ con extensión GBD:")
for file in files:
    print(file)

device.download_file(path_in_gl="\\MEM\\LOG\\240517-171044.GBD", dest_folder=r".\data")
device.disconnect()
