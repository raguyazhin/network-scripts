from pysnmp.hlapi import *

def snmp_walk(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = []

    # Perform SNMP walk
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    # Process the SNMP walk iterator
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


def snmp_walk_vlan(community, ip_address, port, oid):
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
                value = varBind[1].prettyPrint()
                result_array.append(value)
    return result_array

def snmp_walk_index(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = {}

    # Perform SNMP walk
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_address, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    # Process the SNMP walk iterator
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
                result_array[varBind[0]] = varBind[1]

    return result_array


# Example usage
community = 'public'
ip_address = '172.20.8.16'
port = 161

# OIDs for SNMP walks to retrieve MAC addresses and corresponding port IDs
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'  # OID for MAC addresses
port_id_oid = '1.3.6.1.2.1.2.2.1.2'  # OID for interface names (port IDs)
trunk_port_oid = '1.3.6.1.2.1.17.7.1.4.3.1.2'  # OID for trunk port status
bridge_port_oid = '1.3.6.1.2.1.17.4.3.1.2'

result_array = []

trunk_ports = snmp_walk_vlan(community, ip_address, port, trunk_port_oid)

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def hex_to_binary(hex_string):
    binary_digit = ''
    for hex in hex_string:
        # print(hex)
        binary_digit = str(binary_digit) + str(bin(int(hex, 16))[2:].zfill(4))
    return binary_digit

def string_to_array(string):
    # Convert string to array
    return [char for char in string]

def get_matching_positions(arrays):
    # Get positions of matching elements
    positions = []
    for idx, items in enumerate(zip(*arrays)):
        if all(x == items[0] for x in items):
            positions.append(idx+1)
    return positions

tag_port_array = []
for index in trunk_ports:
    #print(index[2:])
    #tag_port_array.append(string_to_array(hex_to_binary(index[2:])))
    tag_port_array.append(hex_to_binary(index[2:]))

tag_port_value = []
tag_port_value = get_matching_positions(tag_port_array)

print(tag_port_array)



bridge_port_value = snmp_walk_index(community, ip_address, port, bridge_port_oid)

bridge_port_value_copy = {}

mac_address_value = snmp_walk_index(community, ip_address, port, mac_address_oid)

for index in bridge_port_value:
    if bridge_port_value[index] in tag_port_value:        
        bridge_port_key = (list(bridge_port_value.keys())[list(bridge_port_value.values()).index(bridge_port_value[index])])
        #del bridge_port_value_copy[index]
    else:
       #print(bridge_port_value[index])  
        bridge_port_value_copy[index]  = bridge_port_value[index]

        #del bridge_port_value[index]
for index in bridge_port_value_copy:
    print(index,bridge_port_value_copy[index])
#print(bridge_port_value)



