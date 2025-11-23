from Graphtec.core.device.base import BaseModule
from Graphtec.core.commands import *
import logging
logger = logging.getLogger(__name__)

class AmpModule(BaseModule):
    """Grupo AMP: Configuración de canales"""
    def __init__(self,device):
        super().__init__(device)
        self.channels = {ch: {"type": "", "input": None, "range": None}
                         for ch in range(1, 5)}
    

    def get_channels(self)->dict:
        """Devuelve la configuración de los canales."""
        return self.channels
    
    def update_channels(self)->dict:
        for channel in range(1,5):
            self.update_channel_type(channel)
            self.update_channel_input(channel)
            self.update_channel_range(channel)
        return self.channels
    
    def update_channel_type(self,channel):
        self.connection.send(GET_CHANNEL_TYPE.format(ch=channel))

        input_type=self._get_last_token(self.connection.receive_until().decode())
        
        # Modificamos el estado interno con la consulta más reciente
        self.channels[channel]["type"]=input_type
        return input_type
    
    def update_channel_input(self, channel):
        self.connection.send(GET_CHANNEL_INPUT.format(ch=channel))
        input_type=self._get_last_token(self.connection.receive_until().decode())

        # Modificamos el estado interno con la consulta más reciente
        self.channels[channel]["input"]=input_type

        return input_type
    
    def update_channel_range(self, channel):
        self.connection.send(GET_CHANNEL_RANGE.format(ch=channel))
        input_type=self._get_last_token(self.connection.receive_until().decode())

        # Modificamos el estado interno con la consulta más reciente
        self.channels[channel]["range"]=input_type

        return input_type
    
    def set_channel_type(self,channel,ch_type):
        cmd = SET_CHANNEL_TYPE.format(ch=channel, ch_type = ch_type)
        self.connection.send(cmd)

    def set_channel_input(self, channel, mode):
        cmd = SET_CHANNEL_INPUT.format(ch=channel, mode=mode)
        self.connection.send(cmd)

    def set_channel_range(self, channel, value):
        cmd = SET_CHANNEL_RANGE.format(ch=channel, value=value)
        self.connection.send(cmd)
    
    def _get_last_token(self,response: str | None)-> str:
            if response:
                response = response.replace(","," ").strip()
                parts = response.split()
                return parts[-1] if parts else ""
            else:
                return ""