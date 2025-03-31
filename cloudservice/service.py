import abc
from .device import BaseDevice
from .endpoint import Endpoint

type Devices = list[BaseDevice]
type Endpoints = list[Endpoint]


class CloudService(abc.ABC):
    """
    super naive implementation of a cloud service for testing purposes

    the underlying network config is EVPN with VXLAN overlay

    customer: customer port(s)
    cni: cloud NNI (can be a single or multiple devices/ports)
         with Azure it is always 2 ports
    """

    def __init__(self, customer: Endpoints, cni: Endpoints, renderer) -> None:
        self.customer = customer
        self.renderer = renderer
        self.cni = cni

    @abc.abstractmethod
    def get_configs(self, s_tag: int, vlan: int, service_key: int) -> dict:
        """
        this should return a dictionary of configs for each device
        """
        return ""

    def __str__(self):
        return f"{self.customer} -> {self.cni}"

    def __repr__(self):
        return f"{self.customer} -> {self.cni}"


class AzureService(CloudService):
    """
    Azure cloud service

    Azure will always have 2 endpoints - primary and secondary.
    """

    def __init__(self, customer: Endpoints, cni: Endpoints, renderer) -> None:
        self.name = "Azure"
        # assume we always have 2 Azure endpoints
        assert len(cni) == 2

        super().__init__(customer, cni, renderer)
        self.primary_cni_endpoint, self.secondary_cni_endpoint = cni
        # also assume primary and secondary are on 2 different devices
        # this doesn't how to be strictly true but would be weird
        # if it was the case.
        assert self.primary_cni_endpoint != self.secondary_cni_endpoint

    def _get_vni(self, express_route_pair: int, path: str, vlan: int) -> str:
        """
        get the VNI based on the s_tag and vlan
        """
        path_map = {"primary": 1, "secondary": 2, "combined": 3}

        return f"{express_route_pair}{path_map[path]}9{int(vlan):02d}"

    def get_configs(
        self, s_tag: int, vlan: int, service_key: str, express_route_pair: int
    ) -> dict:
        """
        this should return a dictionary of configs for each device
        """

        ret = {}

        variables = {
            "s_tag": s_tag,
            "vlan": vlan,
            "service_key": service_key,
            "vni": "XXXXXX",
            "vlan_bundle": "YYYYYYYYY",
        }

        vlan_bundle_prefix = f"azure-er-{str(express_route_pair)}"
        bundle_name = None

        ## now there are a few different scenarios to consider.
        ## some of them can be determined here
        ###
        ## if there's only one customer port then it's 'combined'
        if len(self.customer) == 1:
            bundle_name = "combined"

        # process cloud NNI ports (Azure)
        # these use the same template
        for endpoint in self.cni:
            device, interface = endpoint.device, endpoint.interface
            variables["interface"] = interface
            variables["template"] = "tagged_cni_interface.j2"

            if bundle_name == "combined":
                variables["vni"] = self._get_vni(express_route_pair, "combined", vlan)
            else:
                if endpoint == self.primary_cni_endpoint:
                    variables["vni"] = self._get_vni(express_route_pair, "primary", vlan)
                else:
                    variables["vni"] = self._get_vni(express_route_pair, "secondary", vlan)

            if bundle_name is None:
                # if there are multiple customer ports, then the bundle name is the same
                # as the CNI port
                if endpoint == self.primary_cni_endpoint:
                    variables["vlan_bundle"] = f"{vlan_bundle_prefix}-primary"
                else:
                    variables["vlan_bundle"] = f"{vlan_bundle_prefix}-secondary"
            else:
                variables["vlan_bundle"] = f"{vlan_bundle_prefix}-{bundle_name}"

            device_name = str(device)
            if device_name in ret:
                ret[device_name] += "\n" + device.render_config(self.renderer, **variables)
            else:
                ret[device_name] = device.render_config(self.renderer, **variables)

        for endpoint in self.customer:
            device, interface = endpoint.device, endpoint.interface
            device_name = str(device)
            variables["interface"] = interface

            if bundle_name is None:
                # if there are multiple customer ports, then the bundle name is the same
                # as the CNI port
                # if it's the first port then make it the primary
                if endpoint == self.customer[0]:
                    variables["vlan_bundle"] = f"{vlan_bundle_prefix}-primary"
                    variables["vni"] = self._get_vni(express_route_pair, "primary", vlan)
                # second port will be secondary
                else:
                    variables["vlan_bundle"] = f"{vlan_bundle_prefix}-secondary"
                    variables["vni"] = self._get_vni(express_route_pair, "secondary", vlan)
            else:
                variables["vlan_bundle"] = f"{vlan_bundle_prefix}-{bundle_name}"
                variables["vni"] = self._get_vni(express_route_pair, "combined", vlan)

            if device in (
                self.primary_cni_endpoint.device,
                self.secondary_cni_endpoint.device,
            ):
                variables["template"] = "tagged_customer_local_interface.j2"
                config = device.render_config(self.renderer, **variables)
            else:
                variables["template"] = "tagged_customer_remote_interface.j2"
                config = device.render_config(self.renderer, **variables)

            if device_name in ret:
                ret[device_name] += "\n" + config
            else:
                ret[device_name] = config

        return ret
