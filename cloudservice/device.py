import abc
import os
from jinja2 import Environment, FileSystemLoader


class BaseDevice(abc.ABC):
    _os = None

    def __init__(
        self, name: str, ip_address: str, interface: str | None = None
    ) -> None:
        self.env = Environment(loader=FileSystemLoader("templates"))
        self.name = name
        self.ip_address = ip_address
        self._iface = self.validate_interface(interface) if interface else None

    def __eq__(self, other):
        if not isinstance(other, BaseDevice):
            return NotImplemented
        return self.name == other.name

    def __str__(self):
        return f"{self.name}({self.ip_address})"

    def __repr__(self):
        return self.name

    @property
    def asn(self):
        """
        ASN is defined as 65000 + last octet of the IP address
        """
        last_octet = int(self.ip_address.split(".")[-1])
        return f"65{last_octet:03d}"

    @property
    def iface(self):
        return self._iface

    @iface.setter
    def iface(self, interface: str):
        self._iface = self.validate_interface(interface)

    @iface.getter
    def iface(self):
        return self._iface

    def set_iface(self, interface: str):
        self.validate_interface(interface)
        self.interface = interface

    @abc.abstractmethod
    def validate_interface(self, interface: str) -> str:
        pass

    @property
    def os(self):
        return self._os

    @abc.abstractmethod
    def get_device_info(self):
        pass

    def render_config(self, **kwargs):
        template = self.env.get_template(os.path.join(self.os, kwargs.get("template")))
        kwargs["asn"] = self.asn
        kwargs["ip_address"] = self.ip_address
        kwargs["hostname"] = self.name
        return template.render(**kwargs)


class CeosDevice(BaseDevice):
    """ """

    _os = "eos"

    def validate_interface(self, interface: str) -> str:
        """
        ceos interface names:
        Ethernet1/1
        Port-Channel1
        """
        if not interface.startswith("Ethernet") and not interface.startswith(
            "Port-Channel"
        ):
            raise ValueError(f"Invalid interface name: {interface}")
        return interface

    def get_device_info(self):
        return "Arista device"


class OcnosDevice(BaseDevice):
    """ """

    os = "ocnos"

    def validate_interface(self, interface: str) -> str:
        """
        ocnos interface names:
        po20
        po20.123 (vlan?)
        ce10
        xe10
        xe10.123 (vlan?)
        """
        if (
            not interface.startswith("po")
            and not interface.startswith("ce")
            and not interface.startswith("xe")
        ):
            raise ValueError(f"Invalid interface name: {interface}")
        return interface

    def get_device_info(self):
        return "IPInfusion device"
