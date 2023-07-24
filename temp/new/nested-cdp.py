from pysnmp.hlapi import *
import binascii
import json

cdp_details = {}

def check_value_in_json(json_data, target_value):
    # Parse the JSON data
    data = json.loads(json_data)

    # Iterate through the JSON object
    for key, value in data.items():
        # Check if the current value matches the target value
        if value == target_value:
            return True

        # If the value is another nested JSON object, recursively check it
        if isinstance(value, dict):
            if check_value_in_json(json.dumps(value), target_value):
                return True

        # If the value is a list of JSON objects, recursively check each item
        if isinstance(value, list):
            for item in value:
                if check_value_in_json(json.dumps(item), target_value):
                    return True

    return False

def convert_mac(mac):
    return binascii.hexlify(mac.asOctets()).decode('utf-8').upper()

def snmp_walk(community, ip_address, port, oid, username, auth_protocol, auth_password):
    
    results = []

    target_v2 = SnmpEngine()
    community = CommunityData(community, mpModel=1) 
    transport_v2 = UdpTransportTarget((ip_address, port)) 


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
                    continue
                
                elif errorStatus_v3:
                    print(f"SNMPv3 Error: {errorStatus_v3.prettyPrint()} at {errorIndex_v3 and varBinds_v3[int(errorIndex_v3) - 1][0] or '?'}")
                    continue
                
                else:
                    for varBind in varBinds_v3:
                        results.append(varBind[1])
        
        elif errorStatus_v2:
            print(f"SNMPv2 Error: {errorStatus_v2.prettyPrint()} at {errorIndex_v2 and varBinds_v2[int(errorIndex_v2) - 1][0] or '?'}")
            continue
        
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


def get_connected_devices(community, group, username, auth_protocol, auth_password):

    global cdp_details

    oid_cdp_devid = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
    oid_cdp_ipaddr = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'

    cdp_json = json.dumps(cdp_details)

    groupnode = 'group' + str(group)
    groupdata = json.loads(cdp_json)

    cdp_group_id = group + 1
    cdp_group_name = 'group' + str(cdp_group_id)
    cdp_details[cdp_group_name] = []

    print(len(groupdata[groupnode]))
   
    if(len(groupdata[groupnode]) > 0): 
        
        for data in groupdata[groupnode]:

            
            print("getting data for - " + str(data['ipaddress']))

            if(str(data['ipaddress']) != ""):

                device_ids = snmp_walk(community, data['ipaddress'], 161, oid_cdp_devid, username, auth_protocol, auth_password)
                ip_addresses = snmp_walk(community, data['ipaddress'], 161, oid_cdp_ipaddr, username, auth_protocol, auth_password)

                num_entries = len(ip_addresses)

                if (
                    num_entries == len(device_ids)
                ):
                    
                    if num_entries > 0:

                        
                        for i in range(num_entries):
            
                            device_id = device_ids[i].prettyPrint()
                            vip_add = ip_addresses[i]
                
                            ip_add = binary_to_decimal(split_string_by_count(hex_to_binary(convert_mac(vip_add)),8))
                        
                            if not check_value_in_json(cdp_json, ip_add):

                                cdp_details[cdp_group_name].append({'id': device_id, 'ipaddress': ip_add, 'parentDeviceid': data['id']})

    
        get_connected_devices(community, cdp_group_id, username, auth_protocol, auth_password)

    return cdp_details


# Example usage
community = 'snmain'
ip_address = '172.20.1.110'

username = 'network'
auth_protocol = 'MD5'
auth_password = r'$nN3tw0rK'

cdp_details["group0"] = []
cdp_details["group0"].append({'id': 'Core_Switch', 'ipaddress': ip_address})

cdp_details = get_connected_devices(community, 0, username, auth_protocol, auth_password)

#cdp_details = get_cdp_details(ip_address, community, username, auth_protocol, auth_password)

jsonString = json.dumps(cdp_details)
print(jsonString)
