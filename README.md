```plaintext
              client1            client2          client3         client4              
               eth1/2             eth1/3           eth1/4          eth1/5              
             ┌───────┐         ┌───────┐        ┌───────┐        ┌───────┐             
 azure-pri-1 │       │         │       │        │       │        │       │ azure-sec-1 
   eth1/1    │ ceos1 │         │ ceos2 │        │ ceos3 │        │ ceos4 │    eth1/1   
             │       │         │       │        │       │        │       │             
             └───────┘         └───────┘        └───────┘        └───────┘             
            192.168.1.1       192.168.1.2      192.168.1.3      192.168.1.4            


            192.168.1.21     192.168.1.22     192.168.1.23     192.168.1.24            
            ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐            
azure-pri-2 │          │     │          │     │          │     │          │ azure-sec-2
  xe10      │  ocnos1  │     │  ocnos2  │     │  ocnos3  │     │  ocnos4  │     xe10   
            │          │     │          │     │          │     │          │            
            └──────────┘     └──────────┘     └──────────┘     └──────────┘            
              client1         client2           client3           client4              
                 co11            co12              co13              co14               
```
    
# EOS configs
## Service1 - primary on remote, secondary on local, delivered to single port

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 1191234
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
   vxlan vlan 42 vni 1291234
router bgp 65004
   vlan-aware-bundle azure-er-1-primary
      vlan add 42
interface Ethernet1/5
  switchport trunk allowed vlan add 42
  switchport mode trunk
  switchport vlan translation 1234 dot1q-tunnel 42
```

## Service2 - primary and secondary on remote, delivered to single port

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 1191234
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
   vxlan vlan 42 vni 1291234
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
   switchport vlan translation 1234 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 1291234
router bgp 65003
   vlan-aware-bundle azure-er-1-combined
      vlan add 42
```

## Service3 - primary and secondary on remote, delivered to different ports

Config for ceos1(192.168.1.1):
______________________________
```
vlan 42
   name SO123456
interface Ethernet1/1
  switchport trunk allowed vlan add 42
interface Vxlan1
   vxlan vlan 42 vni 1191234
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
   vxlan vlan 42 vni 1291234
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
   switchport vlan translation 1234 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 1291234
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
   switchport vlan translation 1234 dot1q-tunnel 42
interface Vxlan1
   vxlan vlan 42 vni 1291234
router bgp 65003
   vlan-aware-bundle azure-er-1-secondary
      vlan add 42
```

