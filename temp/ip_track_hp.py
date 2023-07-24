from pysnmp.hlapi import *
import binascii

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
                print(value)
                result_array.append(value)

    return result_array


def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

# SNMP configuration
community = 'snmain'
ip_address = '172.20.8.131'
port = 161

# VLAN Base MAC Address OID
vlan_base_mac_oid = '1.3.6.1.2.1.17.7.1.4.5.1.1'
vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
mac_address_oid = '1.3.6.1.2.1.17.4.3.1.1'
bridge_port_oid = '1.3.6.1.2.1.17.4.3.1.2'
if_index = '1.3.6.1.2.1.2.2.1.1'
port_name_oid = '1.3.6.1.2.1.31.1.1.1.1'
local_port_oid = '1.3.6.1.2.1.17.1.4.1.2'
trunk_port_oid = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'
vlan_name_oid = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
arp_ip_add = '1.3.6.1.2.1.4.22.1.3'
arp_mac_add = '1.3.6.1.2.1.3.1.1.2'


# Perform SNMP walk for VLAN base MAC address
result = snmp_walk(community, ip_address, port, mac_address_oid)


unique_array = list(set(result))

#print(unique_array)

#for vlan_value in unique_array:
result = snmp_walk(community, ip_address, port, mac_address_oid)
for mac_value in result:
    print(" MAC ID =" + str(convert_mac(mac_value)) )
