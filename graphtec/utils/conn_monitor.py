
import threading
import time
import serial.tools.list_ports

class SerialPortMonitor:
    def __init__(self, port_name, check_interval=2.0, on_disconnect=None):
        self.port_name = port_name
        self.check_interval = check_interval
        self.on_disconnect = on_disconnect  # función callback
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)

    def start(self):
        self._stop_event.clear()
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            if not self.is_port_present():
                print(f"[Monitor] Puerto {self.port_name} ha desaparecido.")
                if self.on_disconnect:
                    self.on_disconnect(self.port_name)
                break
            time.sleep(self.check_interval)

    def is_port_present(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return self.port_name in ports

# Ejemplo de uso:
def handle_disconnect(port):
    print(f"¡Alerta! El puerto {port} se ha desconectado. Puedes lanzar ResponseError aquí.")

monitor = SerialPortMonitor("COM3", check_interval=1.0, on_disconnect=handle_disconnect)
monitor.start()

# ... tu programa principal aquí ...
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
