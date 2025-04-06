import os
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
from cloudservice import (
    EosDevice,
    OcnosDevice,
    AzureService,
    GCPService,
    Endpoint,
    JinjaRenderer,
    AWXRenderer,
)

load_dotenv()


class TestCloudService(unittest.TestCase):
    def configs_to_str(self, configs):
        r = ""
        for device, config in configs.items():
            r += f"""Config for {device}:
{"_" * (12 + len(device))}
{config}
"""
        return r

    def setUp(self):
        self.maxDiff = None
        ceos1 = EosDevice("ceos1", "192.168.1.1")
        ceos2 = EosDevice("ceos2", "192.168.1.2")
        ceos3 = EosDevice("ceos3", "192.168.1.3")
        ceos4 = EosDevice("ceos4", "192.168.1.4")

        ocnos1 = OcnosDevice("ocnos1", "192.168.1.21")
        ocnos2 = OcnosDevice("ocnos2", "192.168.1.22")
        ocnos3 = OcnosDevice("ocnos3", "192.168.1.23")
        ocnos4 = OcnosDevice("ocnos4", "192.168.1.24")

        self.renderer = JinjaRenderer("templates")

        self.ceos1_azure_pri_1 = Endpoint(ceos1, "Ethernet1/1")
        self.ceos4_azure_sec_1 = Endpoint(ceos4, "Ethernet1/1")
        self.ceos1_client1 = Endpoint(ceos1, "Ethernet1/2")
        self.ceos1_client2 = Endpoint(ceos1, "Ethernet2/2")
        self.ceos2_client2 = Endpoint(ceos2, "Ethernet1/3")
        self.ceos3_client3 = Endpoint(ceos3, "Ethernet1/4")
        self.ceos4_client4 = Endpoint(ceos4, "Ethernet1/5")
        self.ocnos1_azure_pri_2 = Endpoint(ocnos1, "ce10")
        self.ocnos4_azure_sec_2 = Endpoint(ocnos4, "ce10")
        self.ocnos1_client1 = Endpoint(ocnos1, "xe11")
        self.ocnos2_client2 = Endpoint(ocnos2, "xe12")
        self.ocnos3_client3 = Endpoint(ocnos3, "xe13")
        self.ocnos4_client4 = Endpoint(ocnos4, "xe14")

    def test_arista_primary_on_remote_secondary_on_local_single_port(self):
        configs = AzureService(
            [self.ceos4_client4],
            [self.ceos1_azure_pri_1, self.ceos4_azure_sec_1],
            self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=1)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ceos1(192.168.1.1):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65001
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
Config for ceos4(192.168.1.4):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65004
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
interface Ethernet1/5
  switchport trunk allowed vlan add 42
  switchport mode trunk
  switchport vlan translation 667 dot1q-tunnel 42
""",
        )

    def test_arista_primary_and_secondary_on_remote_to_2_ports(self):
        configs = AzureService(
            [self.ceos2_client2, self.ceos3_client3],
            [self.ceos1_azure_pri_1, self.ceos4_azure_sec_1],
            self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=1)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ceos1(192.168.1.1):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 119667
router bgp 65001
   vlan-aware-bundle azure-er-1-primary
      vlan add 42
Config for ceos4(192.168.1.4):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 129667
router bgp 65004
   vlan-aware-bundle azure-er-1-secondary
      vlan add 42
Config for ceos2(192.168.1.2):
______________________________
vlan 42
   name SO123456
interface Ethernet1/3
   switchport mode trunk
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 119667
router bgp 65002
   vlan-aware-bundle azure-er-1-primary
      vlan add 42
Config for ceos3(192.168.1.3):
______________________________
vlan 42
   name SO123456
interface Ethernet1/4
   switchport mode trunk
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 129667
router bgp 65003
   vlan-aware-bundle azure-er-1-secondary
      vlan add 42
""",
        )

    def test_ocnos_primary_on_local_secondary_on_remote_to_single_port(self):
        configs = AzureService(
            [self.ocnos1_client1],
            [self.ocnos1_azure_pri_2, self.ocnos4_azure_sec_2],
            self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ocnos1(192.168.1.21):
________________________________
mac vrf SO123456
  rd 37186:239667
  route-target both 37186:239667

nvo vxlan id 239667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 239667
interface xe11.667
  description 
  encapsulation dot1q 667
  rewrite push 42
  access-if-evpn
    map vpn-id 239667
Config for ocnos4(192.168.1.24):
________________________________
mac vrf SO123456
  rd 37186:239667
  route-target both 37186:239667

nvo vxlan id 239667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 239667
""",
        )

    def test_ocnos_primary_and_secondary_on_remote_to_single_port(self):
        configs = AzureService(
            [self.ocnos3_client3],
            [self.ocnos1_azure_pri_2, self.ocnos4_azure_sec_2],
            self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ocnos1(192.168.1.21):
________________________________
mac vrf SO123456
  rd 37186:239667
  route-target both 37186:239667

nvo vxlan id 239667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 239667
Config for ocnos4(192.168.1.24):
________________________________
mac vrf SO123456
  rd 37186:239667
  route-target both 37186:239667

nvo vxlan id 239667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 239667
Config for ocnos3(192.168.1.23):
________________________________
mac vrf SO123456
  rd 37186:239667
  route-target both 37186:239667

nvo vxlan id 239667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface xe13.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 239667
""",
        )

    def test_ocnos_primary_and_secondary_on_local_to_two_ports(self):
        configs = AzureService(
            [self.ocnos2_client2, self.ocnos3_client3],
            [self.ocnos1_azure_pri_2, self.ocnos4_azure_sec_2],
            renderer=self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ocnos1(192.168.1.21):
________________________________
mac vrf SO123456
  rd 37186:219667
  route-target both 37186:219667

nvo vxlan id 219667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 219667
Config for ocnos4(192.168.1.24):
________________________________
mac vrf SO123456
  rd 37186:229667
  route-target both 37186:229667

nvo vxlan id 229667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  access-if-evpn
    map vpn-id 229667
Config for ocnos2(192.168.1.22):
________________________________
mac vrf SO123456
  rd 37186:219667
  route-target both 37186:219667

nvo vxlan id 219667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface xe12.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 219667
Config for ocnos3(192.168.1.23):
________________________________
mac vrf SO123456
  rd 37186:229667
  route-target both 37186:229667

nvo vxlan id 229667 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface xe13.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 229667
""",
        )

    # Mixed test cases

    def test_cni_on_arista_to_client_on_ocnos(self):
        configs = AzureService(
            [self.ocnos3_client3],
            [self.ceos1_azure_pri_1, self.ceos4_azure_sec_1],
            renderer=self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ceos1(192.168.1.1):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 239042
router bgp 65001
   vlan-aware-bundle azure-er-2-combined
      vlan add 42
Config for ceos4(192.168.1.4):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 239042
router bgp 65004
   vlan-aware-bundle azure-er-2-combined
      vlan add 42
Config for ocnos3(192.168.1.23):
________________________________
mac vrf azure-er-2-combined
  rd 37186:192003
  route-target both 37186:192003

nvo vxlan id 239042 ingress-replication
  vxlan host-reachability-protocol evpn-bgp azure-er-2-combined

interface xe13.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 239042
""",
        )

    def test_cni_on_ocnos_to_client_on_arista(self):
        configs = AzureService(
            [self.ceos2_client2],
            [self.ocnos1_azure_pri_2, self.ocnos4_azure_sec_2],
            renderer=self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ocnos1(192.168.1.21):
________________________________
mac vrf SO123456
  rd 37186:123456
  route-target both 37186:123456

nvo vxlan id 123456 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  rewrite pop
  access-if-evpn
    arp-cache disable
    nd-cache disable
    map vpn-id 123456
Config for ocnos4(192.168.1.24):
________________________________
mac vrf SO123456
  rd 37186:123456
  route-target both 37186:123456

nvo vxlan id 123456 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  rewrite pop
  access-if-evpn
    arp-cache disable
    nd-cache disable
    map vpn-id 123456
Config for ceos2(192.168.1.2):
______________________________
vlan 42
  name SO123456

Interface Ethernet1/3
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42

interface Vxlan1
   vxlan vlan 42 vni 123456

router bgp 65002
   vlan-aware-bundle SO123456
      rd 37195:123456
      route-target both 37195:123456
      redistribute learned
      redistribute static
      vlan 42
""",
        )

    # 2 clients
    def test_cni_on_arista_to_client_on_ocnos_2endpoints(self):
        configs = AzureService(
            [self.ocnos2_client2, self.ocnos3_client3],
            [self.ceos1_azure_pri_1, self.ceos4_azure_sec_1],
            renderer=self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ceos1(192.168.1.1):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 219042
router bgp 65001
   vlan-aware-bundle azure-er-2-primary
      vlan add 42
Config for ceos4(192.168.1.4):
______________________________
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 229042
router bgp 65004
   vlan-aware-bundle azure-er-2-secondary
      vlan add 42
Config for ocnos2(192.168.1.22):
________________________________
mac vrf azure-er-2-secondary
  rd 37186:192002
  route-target both 37186:192002

nvo vxlan id 219042 ingress-replication
  vxlan host-reachability-protocol evpn-bgp azure-er-2-primary

interface xe12.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 219042
Config for ocnos3(192.168.1.23):
________________________________
mac vrf azure-er-2-secondary
  rd 37186:192002
  route-target both 37186:192002

nvo vxlan id 229042 ingress-replication
  vxlan host-reachability-protocol evpn-bgp azure-er-2-secondary

interface xe13.667 switchport
  description SO123456
  encapsulation dot1q 667
  rewrite push dot1q 42
  access-if-evpn
    map vpn-id 229042
""",
        )

    def test_cni_on_ocnos_to_client_on_arista_2endpoints(self):
        configs = AzureService(
            [self.ceos2_client2, self.ceos3_client3],
            [self.ocnos1_azure_pri_2, self.ocnos4_azure_sec_2],
            renderer=self.renderer,
        ).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2)
        configs_str = self.configs_to_str(configs)
        self.assertEqual(
            configs_str,
            """Config for ocnos1(192.168.1.21):
________________________________
mac vrf SO123456
  rd 37186:123456
  route-target both 37186:123456

nvo vxlan id 123456 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  rewrite pop
  access-if-evpn
    arp-cache disable
    nd-cache disable
    map vpn-id 123456
Config for ocnos4(192.168.1.24):
________________________________
mac vrf SO123456
  rd 37186:123456
  route-target both 37186:123456

nvo vxlan id 123456 ingress-replication
  vxlan host-reachability-protocol evpn-bgp SO123456

interface ce10.42 switchport
  description SO123456
  encapsulation dot1q 42
  rewrite pop
  access-if-evpn
    arp-cache disable
    nd-cache disable
    map vpn-id 123456
Config for ceos2(192.168.1.2):
______________________________
vlan 42
  name SO123456

Interface Ethernet1/3
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42

interface Vxlan1
   vxlan vlan 42 vni 123456

router bgp 65002
   vlan-aware-bundle SO123456
      rd 37195:123456
      route-target both 37195:123456
      redistribute learned
      redistribute static
      vlan 42
Config for ceos3(192.168.1.3):
______________________________
vlan 42
  name SO123456

Interface Ethernet1/4
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42

interface Vxlan1
   vxlan vlan 42 vni 123456

router bgp 65003
   vlan-aware-bundle SO123456
      rd 37195:123456
      route-target both 37195:123456
      redistribute learned
      redistribute static
      vlan 42
""",
        )


class TestAWXRenderer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.ceos1 = EosDevice("ceos1", "192.168.1.1")
        self.ocnos1 = OcnosDevice("ocnos1", "192.168.1.21")
        self.renderer = AWXRenderer(
            os.getenv("AWX_URL", ""),
            os.getenv("AWX_USERNAME", ""),
            os.getenv("AWX_PASSWORD", ""),
        )

    @patch("towerlib.entities.job.JobTemplate.launch")
    def test_awx_render(self, tower_launch_mock):
        self.ceos1.render_config(
            self.renderer,
            template="azure_interface",
            interface="Ethernet1",
            s_tag=42,
            service_key="SO123456",
            vni=1001,
            vlan_bundle="azure-er-1-combined",
            asn=65001,
        )

        tower_launch_mock.assert_called_once()

    def test_awx_render_ceos(self):
        self.ceos1.render_config(
            self.renderer,
            template="tagged_cni_interface",
            interface="Ethernet1",
            s_tag=42,
            service_key="SO123456",
            vni=1001,
            vlan_bundle="azure-er-1-combined",
            asn=65001,
        )

    def test_awx_render_ocnos(self):
        self.ocnos1.render_config(
            self.renderer,
            template="tagged_cni_interface",
            interface="xe13",
            s_tag=42,
            service_key="SO123456",
            vni=1001,
            vlan_bundle="azure-er-1-combined",
            asn=65001,
        )


if __name__ == "__main__":
    unittest.main()
