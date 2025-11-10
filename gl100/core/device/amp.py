from gl100.core.device.base import BaseModule
from gl100.core.commands import *
from gl100.utils.logger import logger

class AmpModule(BaseModule):
    """Grupo AMP: Configuración de canales"""
    def __init__(self,device):
        super().__init__(device)
        self.channels = {}

    def get_channels(self)->dict:
        self.channels.clear()
        for channel in range(1,5):
            channel_type = self.get_channel_type(channel)
            channel_input = self.get_channel_input(channel)
            channgel_range = self.get_channel_range(channel)
            #Esto lo he movido a las funciones individuales. Es redundante en principio.
            #!Probar con el dispositivo y borrar si no es necesario.
            self.channels[channel] = {
                "type": channel_type,
                "input": channel_input,
                "range": channgel_range
            }
        return self.channels
    
    def get_channel_type(self,channel):
        self.connection.send(GET_CHANNEL_TYPE.format(ch=channel))
        input_type=self._get_last_token(self.connection.receive_until().decode())

        # Modificamos el estado interno con la consulta más reciente
        self.channels[channel]["type"]=input_type
    
    def get_channel_input(self, channel):
        self.connection.send(GET_CHANNEL_INPUT.format(ch=channel))
        input_type=self._get_last_token(self.connection.receive_until().decode())

        # Modificamos el estado interno con la consulta más reciente
        self.channels[channel]["input"]=input_type

        return input_type
    
    def get_channel_range(self, channel):
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