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

cdp_remote_ip = snmp_walk_cdp_ip(community, ip_address, port, oid_remote_ip)

cdp_remote_name = snmp_walk(community, ip_address, port, oid_remote_name)

cdp_remote_port = snmp_walk(community, ip_address, port, oid_remote_port)

cdp_local_platform = snmp_walk(community, ip_address, port, oid_local_platform)

cdp_array = []

cdp_array.append(["172.20.1.75","SNMAIN","Fa0/9","C2950"])
for remo_ip,remo_name,remo_port,remo_plat in zip(cdp_remote_ip,cdp_remote_name,cdp_remote_port,cdp_local_platform):
    ip_binary_arr = (split_string_by_count(remo_ip,8))
    cdp_array.append([binary_to_decimal(ip_binary_arr),remo_name,remo_port,remo_plat])

for val in cdp_array:

    ip_address = val[0]
    #print(ip_address)
    cdp_remote_ip = snmp_walk_cdp_ip(community, ip_address, port, oid_remote_ip)
    #print(ip_address,"cdp_remote_ip")

    cdp_remote_name = snmp_walk(community, ip_address, port, oid_remote_name)
    #print(ip_address,"cdp_remote_name")

    cdp_remote_port = snmp_walk(community, ip_address, port, oid_remote_port)
    #print(ip_address,"cdp_remote_port")

    cdp_local_platform = snmp_walk(community, ip_address, port, oid_local_platform)
    #print(ip_address,"cdp_local_platform")

    for remo_ip,remo_name,remo_port,remo_plat in zip(cdp_remote_ip,cdp_remote_name,cdp_remote_port,cdp_local_platform):
        print("for loop 1")
        ip_binary_arr = (split_string_by_count(remo_ip,8))
        print("for loop 2")
        ip = binary_to_decimal(ip_binary_arr)
        print("for loop 3")
        ip_exist = search_value(cdp_array,ip)
        print(ip)

        if (ip == '172.20.1.209'):
            print(cdp_array)

        if not (ip_exist):
            print("IF loop")
            cdp_array.append([ip,remo_name,remo_port,remo_plat])

            #print(cdp_array)

print("LOOP END")
for res in  cdp_array:
    print(res)          




# for result1,result2 in zip(cdp_remote_name,cdp_remote_port):
#     print(result1,result2)