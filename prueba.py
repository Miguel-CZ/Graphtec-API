import serial

port = "COM3"
baudrate = 38400
bytesize = 8
stopbits = 1
parity = "N"
timeout =1
write_timeout=1

device = serial.Serial(
    port=port,
    baudrate=baudrate,
    bytesize=bytesize,
    parity=parity,
    stopbits=stopbits,
    timeout=timeout,
    write_timeout=write_timeout,
)

cmd = ":IF:NLCODE CR_LF\r\n"
device.write(cmd.encode())

command = "*IDN?\r\n".encode()
device.write(command)


response=device.read_until(expected=b"\r\n")
if response is not None:
    print("Respuesta:")
    print(response.decode())
