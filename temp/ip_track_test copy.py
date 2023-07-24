from pysnmp.hlapi import *
import binascii

## OID for SNMP walk
# vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
# mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'



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

def snmp_get(community, ip_address, port, oid):
    # Initialize an empty array to store the results
    result_array = []

    # Perform SNMP GET
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip_address, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    # Check for SNMP errors
    if errorIndication:
        print(f'Error: {errorIndication}')
    elif errorStatus:
        print(f'Error: {errorStatus.prettyPrint()}')
    else:
        for varBind in varBinds:
            value = varBind[1]
            result_array.append(value)

    return result_array


def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

# Example usage
community = 'snmain'
ip_address = '172.20.9.250'
port = 161

# OID for SNMP walk
vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'
bridge_port_oid = '1.3.6.1.2.1.17.4.3.1.2'
if_index_oid = '1.3.6.1.2.1.2.2.1.1'
port_name_oid = '1.3.6.1.2.1.31.1.1.1.1'
local_port_oid = '1.3.6.1.2.1.17.1.4.1.2'
trunck_port_oid = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'
vlan_name_oid = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
arp_ip_add = '1.3.6.1.2.1.4.22.1.3'
arp_mac_add = '1.3.6.1.2.1.3.1.1.2'

vlan_id = snmp_walk(community, ip_address, port, vlan_oid)



if_index_value = snmp_walk(community, ip_address, port, if_index_oid)

bridge_port_value = snmp_walk(community, ip_address, port, bridge_port_oid)

#local_port_value = snmp_walk(community, ip_address, port, local_port_oid + '.' + str(bridge_port))

unique_array = list(set(vlan_id))

#print(unique_array)

for vlan_value in unique_array:
    result = snmp_walk(community + '@' + str(vlan_value), ip_address, port, mac_address_oid)
    for mac_value in result:
       print("Vlan ID=" + str(vlan_value) + " MAC ID =" + str(convert_mac(mac_value)) )



for if_index in if_index_value:
    #print(if_index)
    trunck_port_oid_v = trunck_port_oid + '.' + str(if_index)
    trunck_port_value = snmp_get(community, ip_address, port, trunck_port_oid_v)
    #print(trunck_port_value)
    for trunk_port in trunck_port_value:
        print("if_index=" + str(if_index) + " trunk_port =" + str(trunk_port) )
        

unique_array_bridge = list(set(bridge_port_value))

for bridge_port in unique_array_bridge:

    void=local_port_oid + '.' + str(bridge_port)

    local_port_value = snmp_get(community, ip_address, port, void)

    for local_port in local_port_value:
        
        port_name_oid_v = port_name_oid + '.' + str(local_port)
        port_name_value = snmp_get(community, ip_address, port, port_name_oid_v)

        for port_name in port_name_value:
            #print(bridge_port,local_port,port_name)
            print("bridge_port=" + str(bridge_port) + " local_port=" + str(local_port) + " port_name=" + str(port_name) )
