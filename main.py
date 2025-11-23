from gl100 import GL100 as gl


device = gl(conn_type='usb', port='COM3')

device.connect()

device.set_nlcode()

print(device.is_connected())

print(device.get_id())

print(device.save_settings())

device.disconnect()