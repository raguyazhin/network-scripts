from pysnmp.hlapi import *

# SNMP parameters
community = 'snmain'  # SNMP community string
switch_ip = '172.20.9.250'  # Switch IP address
port_number = 1  # Port number to identify

# OID definitions
bridge_port_oid = '1.3.6.1.2.1.17.4.3.1.2'
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'
if_index_oid = '1.3.6.1.2.1.2.2.1.1'
port_name_oid = '1.3.6.1.2.1.31.1.1.1.1'
local_port_oid = '1.3.6.1.2.1.17.1.4.1.2'
vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
vlan_name_oid = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
arp_ip_add_oid = '1.3.6.1.2.1.4.22.1.3'
arp_mac_add_oid = '1.3.6.1.2.1.3.1.1.2'

# Retrieve the bridge port number for the specified port
bridge_port_number = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(bridge_port_oid + '.' + str(port_number))),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            bridge_port_number = var_bind[1]
            break

if bridge_port_number is None:
    print("Failed to retrieve bridge port number.")
    exit()

# Retrieve the MAC address associated with the bridge port number
mac_address = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(mac_address_oid + '.' + str(bridge_port_number))),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            mac_address = var_bind[1].prettyPrint()
            break

if mac_address is None:
    print("Failed to retrieve MAC address.")
    exit()

# Retrieve the ifIndex for the MAC address
if_index = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(if_index_oid + '.' + mac_address)),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            if_index = var_bind[1]
            break

if if_index is None:
    print("Failed to retrieve ifIndex.")
    exit()

# Retrieve the port name for the ifIndex
port_name = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(port_name_oid + '.' + str(if_index))),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            port_name = var_bind[1]
            break

if port_name is None:
    print("Failed to retrieve port name.")
    exit()

# Retrieve the VLAN ID for the port
vlan_id = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(vlan_oid + '.' + str(bridge_port_number))),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            vlan_id = var_bind[1]
            break

if vlan_id is None:
    print("Failed to retrieve VLAN ID.")
    exit()

# Retrieve the VLAN name for the VLAN ID
vlan_name = None

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(vlan_name_oid + '.' + str(vlan_id))),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            vlan_name = var_bind[1]
            break

if vlan_name is None:
    print("Failed to retrieve VLAN name.")
    exit()

# Retrieve the ARP IP addresses
arp_ip_addresses = []

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(arp_ip_add_oid)),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            arp_ip_addresses.append(var_bind[1].prettyPrint())

# Retrieve the ARP MAC addresses
arp_mac_addresses = []

iterator = nextCmd(
    SnmpEngine(),
    CommunityData(community),
    UdpTransportTarget((switch_ip, 161)),
    ContextData(),
    ObjectType(ObjectIdentity(arp_mac_add_oid)),
    lexicographicMode=False
)

for error_indication, error_status, error_index, var_binds in iterator:
    if error_indication:
        print(f"Error: {error_indication}")
        break
    elif error_status:
        print(f"Error: {error_status}")
        break
    else:
        for var_bind in var_binds:
            arp_mac_addresses.append(var_bind[1].prettyPrint())

# Match MAC address with IP address
ip_address = None

for mac, ip in zip(arp_mac_addresses, arp_ip_addresses):
    if mac_address.lower() == mac.lower():
        ip_address = ip
        break

# Print the results
print(f"Port Number: {port_number}")
print(f"Port Name: {port_name}")
print(f"VLAN ID: {vlan_id}")
print(f"VLAN Name: {vlan_name}")
print(f"MAC Address: {mac_address}")
print(f"IP Address: {ip_address}")

