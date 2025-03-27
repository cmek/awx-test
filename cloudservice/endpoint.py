from .device import BaseDevice


class Endpoint:
    def __init__(self, device: BaseDevice, interface: str):
        self.device = device
        self.interface = interface

    def __str__(self):
        return f"{self.device} - {self.interface}"

    def __eq__(self, other):
        if not isinstance(other, Endpoint):
            return NotImplemented
        return self.device == other.device and self.interface == other.interface
