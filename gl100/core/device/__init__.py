from gl100.core.device.base import BaseModule
from gl100.core.device.common import CommonModule
from gl100.core.device.interface import InterfaceModule
from gl100.core.device.status import StatusModule
from gl100.core.device.amp import AmpModule
from gl100.core.device.data import DataModule
from gl100.core.device.measure import MeasureModule
from gl100.core.device.transfer import TransferModule
from gl100.core.device.file import FileModule
from gl100.core.device.trigger import TriggerModule
from gl100.core.device.alarm import AlarmModule
from gl100.core.device.logic import LogicModule
from gl100.config.config_manager import ConfigManager
from gl100.utils.logger import logger

class GL100Device:
    def __init__(self, connection):
        self.connection = connection
        self.config = ConfigManager()

        # Inicializa módulos
        self.common = CommonModule(self)
        self.interface = InterfaceModule(self)
        self.status = StatusModule(self)
        self.amp = AmpModule(self)
        self.data = DataModule(self)
        self.measure = MeasureModule(self)
        self.transfer = TransferModule(self)
        self.file = FileModule(self)
        self.trigger = TriggerModule(self)
        self.alarm = AlarmModule(self)
        self.logic = LogicModule(self)

        logger.debug(f"[GL100Device] Inicializado con {connection}")

        #self.config.load_from_device(self)

        try:
            self.connection.send(":IF:NLCODE CR_LF")
        except Exception as e:
            logger.error(f"[GL100Device] Error al configurar EOL: {e}")
