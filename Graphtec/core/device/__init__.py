from Graphtec.core.device.base import BaseModule
from Graphtec.core.device.common import CommonModule
from Graphtec.core.device.interface import InterfaceModule
from Graphtec.core.device.status import StatusModule
from Graphtec.core.device.amp import AmpModule
from Graphtec.core.device.data import DataModule
from Graphtec.core.device.measure import MeasureModule
from Graphtec.core.device.transfer import TransferModule
from Graphtec.core.device.file import FileModule
from Graphtec.core.device.trigger import TriggerModule
from Graphtec.core.device.alarm import AlarmModule
from Graphtec.core.device.logic import LogicModule
from Graphtec.config.config_manager import ConfigManager
import logging
logger = logging.getLogger(__name__)

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

        logger.debug(f"[GL100Device] Inicializado con {self.connection}")

        #self.config.load_from_device(self)
