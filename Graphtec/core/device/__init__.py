from graphtec.core.device.base import BaseModule
from graphtec.core.device.common import CommonModule
from graphtec.core.device.interface import InterfaceModule
from graphtec.core.device.status import StatusModule
from graphtec.core.device.amp import AmpModule
from graphtec.core.device.data import DataModule
from graphtec.core.device.measure import MeasureModule
from graphtec.core.device.transfer import TransferModule
from graphtec.core.device.file import FileModule
from graphtec.core.device.trigger import TriggerModule
from graphtec.core.device.alarm import AlarmModule
from graphtec.core.device.logic import LogicModule
from graphtec.config.config_manager import ConfigManager
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

        logger.debug(f"[GL100Device] Inicializado")


        #self.config.load_from_device(self)

    def get_channels(self):
        channels = self.amp.get_channels()
        return channels