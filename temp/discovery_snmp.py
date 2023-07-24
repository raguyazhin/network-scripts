from pysnmp.hlapi import *
import concurrent.futures

def snmp_get(device):
    ip = device['ip']
    community = device['community']

    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('1.3.6.1.2.1.2.1.0')))
    )

    if error_indication:
        print(f"Error: {error_indication}")
    elif error_status:
        print(f"Error: {error_status.prettyPrint()}")
    else:
        for var_bind in var_binds:
            print(var_binds)
            num_indexes = var_bind[1]
            print(f"Device: {ip}, Number of Indexes: {num_indexes}")


# Define the IP range and SNMP community
ip_range = ['172.20.1.89', '172.20.9.250','172.20.8.131']  # Replace with your IP range
community = 'snmain'

# Create a list of device dictionaries
devices = [{'ip': ip, 'community': community} for ip in ip_range]

# Perform SNMP GET requests in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(snmp_get, device) for device in devices]

    for future in concurrent.futures.as_completed(futures):
        future.result()
