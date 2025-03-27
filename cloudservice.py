from cloudservice import CeosDevice, OcnosDevice, AzureService, Endpoint

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
    ceos1_client1 = Endpoint(ceos1, "Ethernet1/2")
    ceos1_client2 = Endpoint(ceos1, "Ethernet2/2")
    ceos2_client2 = Endpoint(ceos2, "Ethernet1/3")
    ceos3_client3 = Endpoint(ceos3, "Ethernet1/4")
    ceos4_client4 = Endpoint(ceos4, "Ethernet1/5")

    ocnos1_azure_pri_2 = Endpoint(ocnos1, "xe10")
    ocnos4_azure_sec_2 = Endpoint(ocnos4, "xe10")
    ocnos1_client1 = Endpoint(ocnos1, "co11")
    ocnos2_client2 = Endpoint(ocnos1, "co12")
    ocnos3_client3 = Endpoint(ocnos1, "co13")
    ocnos4_client4 = Endpoint(ocnos1, "co14")

    print("# EOS configs")
    print("## Service1 - primary on remote, secondary on local, delivered to single port\n")
    print_configs(AzureService([ceos4_client4], [ceos1_azure_pri_1, ceos4_azure_sec_1]).get_configs(s_tag=42, vlan=1234, service_key="SO123456", express_route_pair=1))

    print("## Service2 - primary and secondary on remote, delivered to single port\n")
    print_configs(AzureService([ceos3_client3], [ceos1_azure_pri_1, ceos4_azure_sec_1]).get_configs(s_tag=42, vlan=1234, service_key="SO123456", express_route_pair=1))

    print("## Service3 - primary and secondary on remote, delivered to different ports\n")
    print_configs(AzureService([ceos2_client2, ceos3_client3], [ceos1_azure_pri_1, ceos4_azure_sec_1]).get_configs(s_tag=42, vlan=1234, service_key="SO123456", express_route_pair=1))
