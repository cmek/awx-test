from cloudservice import (CeosDevice,
                          OcnosDevice,
                          AzureService,
                          AWSService,
                          GCPService,
                          Endpoint,
                          JinjaRenderer)

def print_configs(configs):
    for device, config in configs.items():
        print(f"Config for {device}:\n{'_'*(12+len(device))}\n```\n{config}\n```\n")

if __name__ == "__main__":
    print("""```plaintext
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
    """)

    ceos1 = CeosDevice("ceos1", "192.168.1.1")
    ceos2 = CeosDevice("ceos2", "192.168.1.2")
    ceos3 = CeosDevice("ceos3", "192.168.1.3")
    ceos4 = CeosDevice("ceos4", "192.168.1.4")

    ocnos1 = OcnosDevice("ocnos1", "192.168.1.21")
    ocnos2 = OcnosDevice("ocnos2", "192.168.1.22")
    ocnos3 = OcnosDevice("ocnos3", "192.168.1.23")
    ocnos4 = OcnosDevice("ocnos4", "192.168.1.24")

    ceos1_azure_pri_1 = Endpoint(ceos1, "Ethernet1/1")
    ceos4_azure_sec_1 = Endpoint(ceos4, "Ethernet1/1")
    ceos1_aws_1 = Endpoint(ceos1, "Ethernet2/1")
    ceos4_aws_2 = Endpoint(ceos4, "Ethernet2/1")

    ceos1_client1 = Endpoint(ceos1, "Ethernet1/2")
    ceos1_client2 = Endpoint(ceos1, "Ethernet2/2")
    ceos2_client2 = Endpoint(ceos2, "Ethernet1/3")
    ceos3_client3 = Endpoint(ceos3, "Ethernet1/4")
    ceos4_client4 = Endpoint(ceos4, "Ethernet1/5")

    ocnos1_azure_pri_2 = Endpoint(ocnos1, "ce10")
    ocnos4_azure_sec_2 = Endpoint(ocnos4, "ce10")
    ocnos1_aws_3 = Endpoint(ocnos1, "po123")
    ocnos4_aws_4 = Endpoint(ocnos4, "po123")
    ocnos1_client1 = Endpoint(ocnos1, "xe11")
    ocnos2_client2 = Endpoint(ocnos2, "xe12")
    ocnos3_client3 = Endpoint(ocnos3, "xe13")
    ocnos4_client4 = Endpoint(ocnos4, "xe14")

    renderer = JinjaRenderer("templates")
    
    print("""
# Tagged configs
## EOS configs
""")
    print("### Service 1 - primary (ceos1 eth1/1) on remote, secondary (ceos4 eth1/1) on local, delivered to single port. Client on ceos4 eth1/5\n")
    print_configs(AzureService([ceos4_client4], [ceos1_azure_pri_1, ceos4_azure_sec_1], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=1))

    print("### Service 2 - primary (ceos1 eth1/1) and secondary (ceos4 eth1/1) on remote, delivered to single port (ceos3 eth1/4)\n")
    print_configs(AzureService([ceos3_client3], [ceos1_azure_pri_1, ceos4_azure_sec_1], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=1))

    print("### Service 3 - primary (ceos1 eth1/1) and secondary (ceos4 eth1/1) on remote, delivered to different ports - ceos2 eth1/3 and ceos3 eth1/4\n")
    print_configs(AzureService([ceos2_client2, ceos3_client3], [ceos1_azure_pri_1, ceos4_azure_sec_1], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=1))

    print("""## OCNOS configs""")
    print("### Service 1 - primary (ocnos1 ce10) on local, secondary (ocnos4 ce10) on remote, delivered to single port. Client on ocnos1 xe11\n")
    print_configs(AzureService([ocnos1_client1], [ocnos1_azure_pri_2, ocnos4_azure_sec_2], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2))

    print("### Service 2 - primary (ocnos1 ce10) and secondary (ocnos4 ce10) on remote, delivered to single port (ocnos3 xe13)\n")
    print_configs(AzureService([ocnos3_client3], [ocnos1_azure_pri_2, ocnos4_azure_sec_2], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2))

    print("### Service 3 - primary (ocnos1 ce10) and secondary (ocnos4 ce10) on local, delivered to split ports (ocnos2 ce12) and (ocnos3 ce13)\n")
    print_configs(AzureService([ocnos2_client2, ocnos3_client3], [ocnos1_azure_pri_2, ocnos4_azure_sec_2], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2))

    print("## Mixed OCNOS&Arista configs")

    print("### CNI on Arista (ceos1 eth1/1, ceos4 eth1/1) and customer on IPI (ocnos3 ce10)\n")
    print_configs(AzureService([ocnos3_client3], [ceos1_azure_pri_1, ceos4_azure_sec_1], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2))

    print("### CNI on IPI (ocnos1 ce10, ocnos4 ce10) and customer on Arista (ceos2 eth1/3)\n")
    print_configs(AzureService([ceos2_client2], [ocnos1_azure_pri_2, ocnos4_azure_sec_2], renderer=renderer).get_configs(s_tag=42, vlan=667, service_key="SO123456", express_route_pair=2))


    print("# Un-tagged configs - GCP")
    print("### Arista customer (ceos2 eth1/3) to OCNOS CNI (ocnos4 ce20)\n")
    print_configs(GCPService([ceos2_client2], [ocnos4_aws_4], renderer=renderer).get_configs(vlan=667, service_key="SO123456"))

    print("### IPInfusion customer (ocnos4 ce14) to local IPInfusion CNI (ocnos4 po123)\n")
    print_configs(GCPService([ocnos4_client4], [ocnos4_aws_4], renderer=renderer).get_configs(vlan=667, service_key="SO123456"))

    print("### IPInfusion customer (ocnos2 xe12) to remote IPInfusion CNI (ocnos4 po123)\n")
    print_configs(GCPService([ocnos2_client2], [ocnos4_aws_4], renderer=renderer).get_configs(vlan=667, service_key="SO123456"))
