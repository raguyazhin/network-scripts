from pysnmp.hlapi import *
from concurrent.futures import ThreadPoolExecutor

# List of network devices to poll
devices = [
    {'host': '172.20.1.89', 'community': 'snmain', 'if_oid': '1.3.6.1.2.1.2.1.0'},
    {'host': '172.20.9.13', 'community': 'snmain', 'if_oid': '1.3.6.1.2.1.2.1.0'},
    # Add more devices here
]




# SNMP poller function
def snmp_poller(device):
    host = device['host']
    community = device['community']
    if_oid = device['if_oid']

    # SNMP parameters
    params = CommunityData(community)

    # SNMP OID to fetch the number of interfaces
    oid_num_interfaces = ObjectType(ObjectIdentity(if_oid))

    # SNMP request to fetch the number of interfaces
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(), params, UdpTransportTarget((host, 161)), ContextData(), oid_num_interfaces)
    )

    # Process SNMP response for the number of interfaces
    if error_indication:
        print(f"Error: {error_indication}")
        return
    elif error_status:
        print(f"Error: {error_status.prettyPrint()}")
        return

    num_interfaces = var_binds[0][1]
    if num_interfaces is None:
        print(f"Error: Number of interfaces not found")
        return

    print(f"Number of interfaces for {host}: {num_interfaces}")

    if isinstance(num_interfaces, str):
        try:
            num_interfaces = int(num_interfaces)
        except ValueError:
            print(f"Error: Invalid number of interfaces format")
            return
    elif isinstance(num_interfaces, int):
        num_interfaces = num_interfaces
    else:
        print(f"Error: Invalid number of interfaces format")
        return

    # SNMP OID to fetch interface status
    oid_interface_status = ObjectType(ObjectIdentity('IF-MIB', 'ifOperStatus'))

    # SNMP request to fetch interface status for each interface
    error_indication, error_status, error_index, var_binds = next(
        bulkCmd(SnmpEngine(), params, UdpTransportTarget((host, 161)), ContextData(), 0, num_interfaces, oid_interface_status, lookupNames=True, lookupValues=True)
    )

    # Process SNMP response for interface status
    if error_indication:
        print(f"Error: {error_indication}")
        return
    elif error_status:
        print(f"Error: {error_status.prettyPrint()}")
        return

    print(f"Interface status for {host}:")
    for var_bind in var_binds:
        name, index, status = var_bind[0][0], var_bind[0][1], var_bind[1]

        print(f"Interface {name}.{index}: {status}")

# Poll multiple devices in parallel
with ThreadPoolExecutor() as executor:
    # Submit SNMP poller function for each device
    futures = [executor.submit(snmp_poller, device) for device in devices]

    # Wait for all futures to complete
    for future in futures:
        future.result()
