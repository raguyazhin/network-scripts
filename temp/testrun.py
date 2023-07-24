from pysnmp.hlapi import *
import binascii

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def hex_to_binary(hex_string):
    binary_digit = ''
    for hex in hex_string:
        # print(hex)
        binary_digit = str(binary_digit) + str(bin(int(hex, 16))[2:].zfill(4))
    return binary_digit

def binary_to_decimal(binary_arr):
    decimal_value = ''
    for binary in binary_arr:
        decimal_value = str(decimal_value) + str(int(binary, 2)) + '.'
    return decimal_value[:-1]

def split_string_by_count(string,count):
    chunks = [string[i:i+8] for i in range(0, len(string), count)]
    return chunks

def snmp_walk_cdp_ip(community, ip_address, port, oid):
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
                result_array.append(hex_to_binary(convert_mac(value)))

    return result_array

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

def search_value(array, value):
    for subarray in array:
        if subarray[0] == value:
            return True
    return False

# Usage example
community = 'snmain'  # Replace with the SNMP community string
ip_address = '172.20.1.75'  # Replace with the IP address of the Cisco switch
port = 161  # Replace with the SNMP port (default is 161)
# oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'  # Replace with the OID range you want to walk
# oid = '1.3.6.1.4.1.9.9.23.1.2.1.1'  # OID for cdpCacheDeviceId
# oid_if_index = '1.3.6.1.4.1.9.9.23.1.2.1.1.2'  # OID for cdpCacheDevicePort
oid_local_index = '1.3.6.1.4.1.9.9.23.1.2.1.1.3'  # cdpCacheDeviceIndex
oid_remote_ip = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'  # cdpCacheIfIndex
oid_remote_name = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'  # cdpCachePlatform
oid_remote_port = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'  # cdpCacheDevicePort
oid_local_platform = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'  # cdpCachePortId

#cdp_remote_ip = snmp_walk_cdp_ip(community, ip_address, port, oid_remote_ip)

cdp_ip_array = []

cdp_ip_array.append("172.20.1.209")

for cdp_ip in cdp_ip_array:

    print(cdp_ip)
    #if (cdp_ip != '172.20.1.209'):
    cdp_remote_ip = snmp_walk_cdp_ip(community, cdp_ip, port, oid_remote_ip)

    for remote_ip in cdp_remote_ip:

        ip_binary_arr = (split_string_by_count(remote_ip,8))
        ip = binary_to_decimal(ip_binary_arr)

        if not ip in cdp_ip_array:
            cdp_ip_array.append(ip)

print(cdp_ip_array)
