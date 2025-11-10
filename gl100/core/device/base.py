class BaseModule:
    def __init__(self, device):
        self.device = device
        self.connection = device.connection