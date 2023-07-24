from pysnmp.hlapi import *
import binascii
import json

executed = False

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()


def snmp_walk(community, ip_address, port, oid, username, auth_protocol, auth_password):
    
    results = []

    target_v2 = SnmpEngine()
    community = CommunityData(community, mpModel=1)  # Use the appropriate community string
    transport_v2 = UdpTransportTarget((ip_address, port))  # Replace with the IP address of your SNMP-enabled device

    # SNMPv3 parameters
    target_v3 = SnmpEngine()

    auth_proto_map = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol
    }

    auth_proto = auth_proto_map.get(auth_protocol)

    user = UsmUserData(
        userName=username,
        authProtocol=auth_proto,
        authKey=auth_password
    )

    
    transport_v3 = UdpTransportTarget((ip_address, port))  

    v_oid = ObjectType(ObjectIdentity(oid))

    iterator_v2 = nextCmd(target_v2, community, transport_v2, ContextData(), v_oid, lexicographicMode=False)

    for errorIndication_v2, errorStatus_v2, errorIndex_v2, varBinds_v2 in iterator_v2:

        if errorIndication_v2:

            print(f"SNMPv2 Error: {errorIndication_v2}")
            print("Switching to SNMPv3...")
            
            iterator_v3 = nextCmd(target_v3, user, transport_v3, ContextData(), v_oid, lexicographicMode=False)

            # Process the SNMPv3 walk response
            for errorIndication_v3, errorStatus_v3, errorIndex_v3, varBinds_v3 in iterator_v3:

                if errorIndication_v3:
                    print(f"SNMPv3 Error: {errorIndication_v3}")
                    return []
                
                elif errorStatus_v3:
                    print(f"SNMPv3 Error: {errorStatus_v3.prettyPrint()} at {errorIndex_v3 and varBinds_v3[int(errorIndex_v3) - 1][0] or '?'}")
                    return []
                
                else:
                    for varBind in varBinds_v3:
                        results.append(varBind[1])
        
        elif errorStatus_v2:
            print(f"SNMPv2 Error: {errorStatus_v2.prettyPrint()} at {errorIndex_v2 and varBinds_v2[int(errorIndex_v2) - 1][0] or '?'}")
            return []
        
        else:
            for varBind in varBinds_v2:
                results.append(varBind[1])

    return results


def snmp_walk_1(community, ip_address, port, oid):
  
    results = []

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
            print(f'SNMP query failed: {errorIndication}')
            return []

        if errorStatus:
            print(f'SNMP query failed: {errorStatus.prettyPrint()}')
            return []

        
        for var_bind in varBinds:
            results.append(var_bind[1])

    return results

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


def get_connected_devices(ip_address, community, device_id, group, username, auth_protocol, auth_password):

    oid_cdp_ipaddr = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
    oid_cdp_ios = '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
    oid_cdp_devid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
    oid_cdp_devport = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
    oid_cdp_devplat = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'

    cdp_details = {
        "id": device_id.prettyPrint(),
        "ipaddress": ip_address,
        "group": group,
        "connectedDevices": []
    }

    ip_addresses = snmp_walk(community, ip_address, 161, oid_cdp_ipaddr, username, auth_protocol, auth_password)
    ios_versions = snmp_walk(community, ip_address, 161, oid_cdp_ios, username, auth_protocol, auth_password)
    device_ids = snmp_walk(community, ip_address, 161, oid_cdp_devid, username, auth_protocol, auth_password)
    device_ports = snmp_walk(community, ip_address, 161, oid_cdp_devport, username, auth_protocol, auth_password)
    device_platforms = snmp_walk(community, ip_address, 161, oid_cdp_devplat, username, auth_protocol, auth_password)

    num_entries = len(ip_addresses)
    if (
        num_entries == len(ios_versions)
        == len(device_ids)
        == len(device_ports)
        == len(device_platforms)
    ):
        for i in range(num_entries):
            connected_device_id = binary_to_decimal(split_string_by_count(hex_to_binary(convert_mac(ip_addresses[i])),8)) 
            connected_device_group = group + 1
            connected_device = {
                "id": device_ids[i].prettyPrint(),
                "ipaddress": connected_device_id,
                "group": connected_device_group,
                "connectedDevices": []
            }

         
            cdp_details["connectedDevices"].append(connected_device)

            # global executed

            # print(executed)

            # if not executed:
            #     print('hioooooooooooo')
                
            #     print(device_ids[i].prettyPrint())
            #     print(connected_device_id)
        
            #     if(connected_device_id == "172.20.9.250"):

            #         executed = True
            #         connected_device_details = get_connected_devices(
            #             connected_device_id, community, device_ids[i], connected_device_group, username, auth_protocol, auth_password
            #         )

            #         print(cdp_details["connectedDevices"])
            #         print(connected_device_details)

            #         cdp_details["connectedDevices"].extend(connected_device_details)
            
    return cdp_details


def get_cdp_details(ip_address, community, username, auth_protocol, auth_password):

    oid_cdp_devid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
    oid_cdp_ipaddr = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'

    cdp_details = {}

    device_ids = snmp_walk(community, ip_address, 161, oid_cdp_devid, username, auth_protocol, auth_password)
    ip_addresses = snmp_walk(community, ip_address, 161, oid_cdp_ipaddr, username, auth_protocol, auth_password)

    num_entries = len(ip_addresses)

    if (
        num_entries == len(device_ids)
    ):

        if num_entries > 0:

            cdp_details["nodes"] = []

            for i in range(num_entries):

                device_id = device_ids[i]
                vip_add = ip_addresses[i]

                ip_add = binary_to_decimal(split_string_by_count(hex_to_binary(convert_mac(vip_add)),8))

                print('main-loop', ip_add)

                device_details = get_connected_devices(
                    ip_add, community, device_id, 1, username, auth_protocol, auth_password
                )

                cdp_details["nodes"].append(device_details)

    
    return cdp_details


# Example usage
community = 'snmain'
ip_address = '172.20.1.89'

username = 'network'
auth_protocol = 'MD5'
auth_password = r'$nN3tw0rK'

cdp_details = get_cdp_details(ip_address, community, username, auth_protocol, auth_password)


jsonString = json.dumps(cdp_details)
print(jsonString)
