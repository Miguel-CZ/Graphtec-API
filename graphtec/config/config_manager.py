# gl100/config/config_manager.py
import json
import logging
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self._data = {
            "device_info": {},
            "channels": {},
            "alarms": {},
            "triggers": {},
            "logipul": {},
            "system": {},
        }

    # -----------------------------------------------------
    # Inicialización
    # -----------------------------------------------------
    def load_from_device(self, device):
        """Consulta y guarda los datos iniciales del dispositivo."""
        logger.debug("[ConfigManager] Cargando datos iniciales del dispositivo...")
        try:
            self._data["device_info"]["id"] = device.get_id()
            self._data["device_info"]["system_info"] = device.get_system_info()
            self._data["device_info"]["version"] = device.get_version()
            # ... se pueden añadir más según los módulos implementados
        except Exception as e:
            logger.error(f"[ConfigManager] Error al inicializar datos: {e}")

    # -----------------------------------------------------
    # Actualización dinámica
    # -----------------------------------------------------
    def update(self, key_path: str, value):
        """
        Actualiza una clave del JSON. 
        Ejemplo key_path: 'channels.CH1.range'
        """
        parts = key_path.split('.')
        d = self._data
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = value
        logger.debug(f"[ConfigManager] Actualizado: {key_path} = {value}")

    def get(self, key_path: str, default=None):
        parts = key_path.split('.')
        d = self._data
        for p in parts:
            d = d.get(p, {})
        return d or default

    # -----------------------------------------------------
    # Exportar / Guardar
    # -----------------------------------------------------
    def to_json(self, filepath=None):
        """Devuelve o guarda la configuración completa en JSON."""
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4)
            logger.info(f"[ConfigManager] Configuración guardada en {filepath}")
        return json.dumps(self._data, indent=4)

    # -----------------------------------------------------
    # Cargar y aplicar configuración
    # -----------------------------------------------------
    def load_json(self, filepath, device=None):
        """Carga configuración desde un JSON y aplica los SET al dispositivo."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
        logger.info(f"[ConfigManager] Configuración cargada desde {filepath}")

        if device:
            logger.debug("[ConfigManager] Aplicando configuración al dispositivo...")
            self.apply_to_device(device)

    def apply_to_device(self, device):
        """Envía los comandos SET al dispositivo según la configuración cargada."""
        for ch, cfg in self._data.get("channels", {}).items():
            if "range" in cfg:
                device.connection.send(f":AMP:{ch}:RANG {cfg['range']}")
            if "input" in cfg:
                device.connection.send(f":AMP:{ch}:INP {cfg['input']}")
        # Igual para triggers, alarmas, etc.

    # -----------------------------------------------------
    def as_dict(self):
        return self._data
