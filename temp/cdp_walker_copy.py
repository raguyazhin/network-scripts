from pysnmp.hlapi import *
import shlex
import binascii


def snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid):
    result_array = []

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    usm_user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    iterator = nextCmd(
        SnmpEngine(),
        usm_user,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    for response in iterator:
        error_indication, error_status, error_index, var_binds = response

        if error_indication:
            print(f"SNMP query failed: {error_indication}")
            break
        elif error_status:
            print(f"SNMP query failed: {error_status.prettyPrint()}")
            break
        else:
            for var_bind in var_binds:
                result_array.append(var_bind[1])

    return result_array

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

def snmp_walk_v3_cdp_ip(ip_address, username, auth_protocol, auth_password, oid):
    result_array = []

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    usm_user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    iterator = nextCmd(
        SnmpEngine(),
        usm_user,
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    for response in iterator:
        error_indication, error_status, error_index, var_binds = response

        if error_indication:
            print(f"SNMP query failed: {error_indication}")
            break
        elif error_status:
            print(f"SNMP query failed: {error_status.prettyPrint()}")
            break
        else:
            for varBind in var_binds:
                value = varBind[1]
                result_array.append(hex_to_binary(convert_mac(value)))

    return result_array

# Example usage

ip_address = '172.20.1.110'
username = 'network'
auth_protocol = 'MD5'
auth_password = r'$nN3tw0rK'
oid = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'  # Example OID for system description

oid_local_index = '1.3.6.1.4.1.9.9.23.1.2.1.1.3'  # cdpCacheDeviceIndex
oid_remote_ip = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'  # cdpCacheIfIndex
oid_remote_name = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'  # cdpCachePlatform
oid_remote_port = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'  # cdpCacheDevicePort
oid_local_platform = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'  # cdpCachePortId

#print(shlex.quote(auth_password))

cdp_remote_ip = snmp_walk_v3_cdp_ip(ip_address, username, auth_protocol, auth_password, oid_remote_ip)

# for res in  cdp_remote_ip:
#     print(res) 


cdp_remote_name = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_remote_name)

cdp_remote_port = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_remote_port)

cdp_local_platform = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_local_platform)

cdp_array = []

for remo_ip,remo_name,remo_port,remo_plat in zip(cdp_remote_ip,cdp_remote_name,cdp_remote_port,cdp_local_platform):
    ip_binary_arr = (split_string_by_count(remo_ip,8))
    cdp_array.append([binary_to_decimal(ip_binary_arr),remo_name,remo_port,remo_plat])

for val in cdp_array:

    ip_address = val[0]
    print(ip_address)
    cdp_remote_ip = snmp_walk_v3_cdp_ip(ip_address, username, auth_protocol, auth_password, oid_remote_ip)

    cdp_remote_name = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_remote_name)

    cdp_remote_port = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_remote_port)

    cdp_local_platform = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid_local_platform)

    for remo_ip,remo_name,remo_port,remo_plat in zip(cdp_remote_ip,cdp_remote_name,cdp_remote_port,cdp_local_platform):
        ip_binary_arr = (split_string_by_count(remo_ip,8))
        ip = binary_to_decimal(ip_binary_arr)
        if not ip in val:
            cdp_array.append([ip,remo_name,remo_port,remo_plat])

            print(cdp_array)



# result = snmp_walk_v3(ip_address, username, auth_protocol, auth_password, oid)
# for value in result:
#     print(value)
