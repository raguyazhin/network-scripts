from pysnmp.hlapi import *

def snmp_walk(community, ip_address, port, oid):
    result_array = []
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
    for response in iterator:
        errorIndication, errorStatus, errorIndex, varBinds = response
        if errorIndication:
            print(f'Error: {errorIndication}')
            break
        elif errorStatus:
            print(f'Error: {errorStatus.prettyPrint()}')
            break
        else:
            for varBind in varBinds:
                value = varBind[1]
                result_array.append(value)
    return result_array

# Example usage
community = 'snmain'
ip_address = '172.20.8.131'
port = 161

# OIDs for SNMP walks to retrieve MAC addresses and corresponding port IDs
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'  # OID for MAC addresses
port_id_oid = '1.3.6.1.2.1.2.2.1.2'  # OID for interface names (port IDs)
trunk_port_oid = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'  # OID for trunk port status

mac_addresses = snmp_walk(community, ip_address, port, mac_address_oid)
port_ids = snmp_walk(community, ip_address, port, port_id_oid)
trunk_ports = snmp_walk(community, ip_address, port, trunk_port_oid)

mac_port_mapping = {}

# Filter out trunk ports and bridge ports
for mac, port in zip(mac_addresses, port_ids):
    try:
        port_id = int(port)
        if port_id not in trunk_ports:
            mac_hex = ":".join(f"{x:02x}" for x in mac)
            mac_port_mapping[port_id] = mac_hex
    except ValueError:
        # Skip non-integer port IDs
        continue

# Print the MAC address to port mapping
for port_id, mac_address in mac_port_mapping.items():
    print(f"Port ID: {port_id}, MAC Address: {mac_address}")
