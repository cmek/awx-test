```plaintext
              client1            client2          client3         client4              
               eth1/2             eth1/3           eth1/4          eth1/5              
             ┌───────┐         ┌───────┐        ┌───────┐        ┌───────┐             
 azure-pri-1 │       │         │       │        │       │        │       │ azure-sec-1
   eth1/1    │ ceos1 │         │ ceos2 │        │ ceos3 │        │ ceos4 │    eth1/1
aws-1 eth2/1 │       │         │       │        │       │        │       │ aws-2 eth2/1 
             └───────┘         └───────┘        └───────┘        └───────┘             
            192.168.1.1       192.168.1.2      192.168.1.3      192.168.1.4            


            192.168.1.21     192.168.1.22     192.168.1.23     192.168.1.24            
            ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐            
azure-pri-2 │          │     │          │     │          │     │          │ azure-sec-2
  ce10      │  ocnos1  │     │  ocnos2  │     │  ocnos3  │     │  ocnos4  │     ce10
aws-3 po123 │          │     │          │     │          │     │          │ aws-4 po123
            └──────────┘     └──────────┘     └──────────┘     └──────────┘            
              client1         client2           client3           client4              
                 co11            co12              co13              co14               


using the following variables:
- vlan - 667
- s_tag - 42
- service_key = "SO123456"
- express_route_pair = 1

```
    

# Tagged configs
## EOS configs

### Service 1 - primary (ceos1 eth1/1) on remote, secondary (ceos4 eth1/1) on local, delivered to single port. Client on ceos4 eth1/5

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65001
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
```

Config for ceos4(192.168.1.4):
______________________________
```
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
```

### Service 2 - primary (ceos1 eth1/1) and secondary (ceos4 eth1/1) on remote, delivered to single port (ceos3 eth1/4)

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65001
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
```

Config for ceos4(192.168.1.4):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65004
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
```

Config for ceos3(192.168.1.3):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/4
   switchport mode trunk
   switchport trunk allowed vlan add 42
   switchport vlan translation 667 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 139667
router bgp 65003
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
```

### Service 3 - primary (ceos1 eth1/1) and secondary (ceos4 eth1/1) on remote, delivered to different ports - ceos2 eth1/3 and ceos3 eth1/4

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 119667
router bgp 65001
   vlan-aware-bundle azure-er-1-primary
      vlan add 42
```

Config for ceos4(192.168.1.4):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 129667
router bgp 65004
   vlan-aware-bundle azure-er-1-secondary
      vlan add 42
```

Config for ceos2(192.168.1.2):
______________________________
```
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
```

Config for ceos3(192.168.1.3):
______________________________
```
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
```

## OCNOS configs
### Service 1 - primary (ocnos1 ce10) on local, secondary (ocnos4 ce10) on remote, delivered to single port. Client on ocnos1 xe11

Config for ocnos1(192.168.1.21):
________________________________
```
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
```

Config for ocnos4(192.168.1.24):
________________________________
```
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
```

### Service 2 - primary (ocnos1 ce10) and secondary (ocnos4 ce10) on remote, delivered to single port (ocnos3 xe13)

Config for ocnos1(192.168.1.21):
________________________________
```
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
```

Config for ocnos4(192.168.1.24):
________________________________
```
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
```

Config for ocnos3(192.168.1.23):
________________________________
```
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
```

### Service 3 - primary (ocnos1 ce10) and secondary (ocnos4 ce10) on local, delivered to split ports (ocnos2 ce12) and (ocnos3 ce13)

Config for ocnos1(192.168.1.21):
________________________________
```
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
```

Config for ocnos4(192.168.1.24):
________________________________
```
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
```

Config for ocnos2(192.168.1.22):
________________________________
```
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
```

Config for ocnos3(192.168.1.23):
________________________________
```
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
```

## Mixed OCNOS&Arista configs
### CNI on Arista (ceos1 eth1/1, ceos4 eth1/1) and customer on IPI (ocnos3 ce10)

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 239042
router bgp 65001
   vlan-aware-bundle azure-er-2-combined
      vlan add 42
```

Config for ceos4(192.168.1.4):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 239042
router bgp 65004
   vlan-aware-bundle azure-er-2-combined
      vlan add 42
```

Config for ocnos3(192.168.1.23):
________________________________
```
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
```

### CNI on IPI (ocnos1 ce10, ocnos4 ce10) and customer on Arista (ceos2 eth1/3)

Config for ocnos1(192.168.1.21):
________________________________
```
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
```

Config for ocnos4(192.168.1.24):
________________________________
```
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
```

Config for ceos2(192.168.1.2):
______________________________
```
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
```

### CNI on Arista (ceos1 eth1/1, ceos4 eth1/1) and customer on 2 IPI devices (ocnos2 xe12, ocnos3 xe13)

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 219042
router bgp 65001
   vlan-aware-bundle azure-er-2-primary
      vlan add 42
```

Config for ceos4(192.168.1.4):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 229042
router bgp 65004
   vlan-aware-bundle azure-er-2-secondary
      vlan add 42
```

Config for ocnos2(192.168.1.22):
________________________________
```
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
```

Config for ocnos3(192.168.1.23):
________________________________
```
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
```

### CNI on IPI (ocnos1 ce10, ocnos4 ce10) and customer on 2 Arista ports (ceos2 eth1/3, ceos3 eth1/4)

Config for ocnos1(192.168.1.21):
________________________________
```
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
```

Config for ocnos4(192.168.1.24):
________________________________
```
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
```

Config for ceos2(192.168.1.2):
______________________________
```
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
```

Config for ceos3(192.168.1.3):
______________________________
```
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
```

# Un-tagged configs - GCP
### Arista customer (ceos2 eth1/3) to OCNOS CNI (ocnos4 ce20)

Config for ocnos4(192.168.1.24):
________________________________
```
mac vrf 15169
 evpn-vlan-service vlan-aware-bundle
 rd 37195:15169
 route-target both 37195:15169

nvo vxlan id 15169667 ingress-replication
 vxlan host-reachability-protocol evpn-bgp 15169

interface po123.667 switchport
 encapsulation dot1q 667
 description SO123456
 access-if-evpn
  map vpn-id 15169667
```

Config for ceos2(192.168.1.2):
______________________________
```
vlan 667
  name SO123456

Interface Ethernet1/3
   switchport trunk allowed vlan add 667

interface Vxlan1
   vxlan vlan 667 vni 15169667

router bgp 65002
   vlan-aware-bundle 15169
      rd 37195:15169
      route-target both 37195:15169
      redistribute learned
      redistribute static
      vlan 667
```

#### Delete templates

Config for ocnos4(192.168.1.24):
________________________________
```
no interface po123.667 switchport
no nvo vxlan id 15169667
```

Config for ceos2(192.168.1.2):
______________________________
```
interface Ethernet1/3
  switchport trunk allowed vlan remove 667

router bgp 65002
  vlan-aware-bundle 15169
    no vlan 667

interface Vxlan1
  no vxlan vlan 667 vni 15169

no vlan 667
```

### IPInfusion customer (ocnos4 ce14) to local IPInfusion CNI (ocnos4 po123)

Config for ocnos4(192.168.1.24):
________________________________
```
mac vrf 15169
 evpn-vlan-service vlan-aware-bundle
 rd 37195:15169
 route-target both 37195:15169

nvo vxlan id 15169667 ingress-replication
 vxlan host-reachability-protocol evpn-bgp 15169

interface po123.667 switchport
 encapsulation dot1q 667
 description SO123456
 access-if-evpn
  map vpn-id 15169667
interface xe14.667 switchport
  encapsulation dot1q 667
  access-if-evpn
    map vpn-id 15169667
```

#### Delete templates

Config for ocnos4(192.168.1.24):
________________________________
```
no interface po123.667 switchport
no nvo vxlan id 15169667
no interface xe14.667 switchport
no nvo vxlan id 15169667
```

### IPInfusion customer (ocnos2 xe12) to remote IPInfusion CNI (ocnos4 po123)

Config for ocnos4(192.168.1.24):
________________________________
```
mac vrf 15169
 evpn-vlan-service vlan-aware-bundle
 rd 37195:15169
 route-target both 37195:15169

nvo vxlan id 15169667 ingress-replication
 vxlan host-reachability-protocol evpn-bgp 15169

interface po123.667 switchport
 encapsulation dot1q 667
 description SO123456
 access-if-evpn
  map vpn-id 15169667
```

Config for ocnos2(192.168.1.22):
________________________________
```
mac vrf 15169
 evpn-vlan-service vlan-aware-bundle
 rd 37195:15169
 route-target both 37195:15169

nvo vxlan id 15169667 ingress-replication
 vxlan host-reachability-protocol evpn-bgp 15169

interface xe12.667 switchport
 encapsulation dot1q 667
 access-if-evpn
  map vpn-id 15169667
```

#### Delete templates

Config for ocnos4(192.168.1.24):
________________________________
```
no interface po123.667 switchport
no nvo vxlan id 15169667
```

Config for ocnos2(192.168.1.22):
________________________________
```
no interface xe12.667 switchport
no nvo vxlan id 15169667
```

